__author__ = "Noam"

import socket
import threading
import traceback
import queue
import time
import random as rnd
import json
import ast


from Helpers.tcp_by_size import recv_by_size, send_with_size
from Helpers.Async import Async

from Helpers.send_mail import *
from Encryption.AES import *
from Encryption.RSA import *

all_to_die = False
async_mgr = Async()
request_queue = queue.Queue()
private_key = None
rooms = []

from Helpers.DataBase import *

REQUEST_COUNT = 5

async_mgr.users = load_users()

reset_codes = {}
log_in_users = []

socket_state = {}
lock = threading.Lock()


def get_state(sock):
    with lock:
        if sock not in socket_state:
            socket_state[sock] = {'key': b'', 'has_key': False, "room":None}
        return socket_state[sock]


def delete_state(sock):
    with lock:
        socket_state.pop(sock, None)


def create_user(username, password, name, email):
    success, msg = add_user(async_mgr.users, username, password, name, email)
    return msg


def login(sock, username, password):
    success, msg = login_user(async_mgr.users, async_mgr, sock, username, password)
    with lock:
        if success and username in log_in_users:
            msg = f'user already logged in'
        elif success and username not in log_in_users:
            log_in_users.append(username)
    return msg


def new_password(username, password):
    salt = async_mgr.users[username]["salt"]
    async_mgr.users[username]["password"] = hash_password(password, salt)
    save_users(async_mgr.users)


def get_new_reset_pass_code(email):
    does_exist = chack_email(async_mgr.users, email)
    if does_exist:
        code_instance = reset_password()
        with lock:
            reset_codes[email] = code_instance
        return [code_instance, "got Reset Code"]
    return [None, "email does not exist"]



class Room(threading.Thread):
    def __init__(self, sock, max_players, room_name):
        super().__init__(daemon=True)
        self.room_name = room_name
        self.sock = sock
        self.max_players = max_players
        self.lock = lock
        self.players = {}#playerName:{socket:sock,is_host:bool,cards:[],id = int}
        self.current_card = None
        self.play_queue = queue.Queue()
        self.skip_next = False
        self.two_next = False
        self.draw_four = False
        self.number = 1
        self.reverse = False
        self.reverse_player = ""

        self.pile = []
        colors = ["RED", "GREEN", "BLUE","YELLOW"]
        for color in colors:

            for i in range(1,10):
                self.pile.append((color, i))
                self.pile.append((color, i))

            for action in ['SKIP', 'REVERSE', 'DRAW_TWO']:
                self.pile.append((color, action))
                self.pile.append((color, action))

        for i in range (4):
            self.pile.append(('WILD','CHANGE'))
            self.pile.append(('WILD','DRAW_FOUR'))

    def add_player(self, username,sock,state):
        with self.lock:
            if len(self.players) >= self.max_players:
                return 'room is full'
            ids = len(self.players)
            self.players[username] = {"socket":sock,"is_host":False,"state":state,"cards":[],"id":ids}
            if len(self.players) == 1:
                self.players[username]["is_host"] = True
            for i, (player, info) in enumerate(self.players.items()):
                if player != username:
                    async_mgr.put_msg_by_user(f"NEW|{username}|{ids}", player, info["state"]["key"])
            return 'successfully joined'

    def del_player(self, username,state):
        with self.lock:
            if username in self.players:
                del self.players[username]

        with lock:
            state["room"] = None

        if self.is_empty():
            with lock:
                print(self in rooms)
                if self in rooms:
                    rooms.remove(self)

    def is_empty(self):
        with self.lock:
            return len(self.players) <= 0

    def start_game(self):
        rnd.shuffle(self.pile)
        for i in range(8):
            for player in self.players.values():
                player["cards"].append(self.pile.pop(0))
        for p, inf in self.players.items():
            async_mgr.put_msg_by_user(f"CARDS|{inf["cards"]}", p, inf["state"]["key"])
        self.current_card = self.pile.pop(0)
        for p, inf in self.players.items():
            async_mgr.put_msg_by_user(f"CPLY|the new card is|{self.current_card}", p, inf["state"]["key"])
        self.main()

    def player_count(self):
        with self.lock:
            return len(self.players)

    def get_name(self):
        return self.room_name

    def main(self):
        playing = True
        players_list = list(self.players.items())

        while playing:
            if self.reverse:
                players_list.reverse()
                self.reverse = False

            for i, (player, info) in enumerate(players_list):
                if self.reverse_player != player and self.reverse_player != "":
                    continue
                elif self.reverse_player == player:
                    self.reverse_player = ""
                    continue
                elif self.skip_next:
                    self.skip_next = False

                elif self.two_next:
                    if any(c[1] == "DRAW_TWO" for c in info["cards"]):
                        async_mgr.put_msg_by_user("TURN", player, info["state"]["key"])
                        card = self.play_queue.get()[1]
                        if card[1] == 'DRAW_TWO':
                            info["cards"].remove(card)
                            self.number += 1
                            self.two_next = True
                        else:
                            async_mgr.put_msg_by_user("CANT", player, info["state"]["key"])
                    else:
                        for _ in range(2 * self.number):
                            info["cards"].append(self.pile.pop(0))
                        self.number = 1
                        self.two_next = False

                elif self.draw_four:
                    for _ in range(4):
                        info["cards"].append(self.pile.pop(0))
                    self.draw_four = False

                else:
                    for p,inf in self.players.items():
                        async_mgr.put_msg_by_user("STOP",p, inf["state"]["key"])

                    for p,inf in self.players.items():
                        async_mgr.put_msg_by_user(f"CARDS|{inf["cards"]}",p, inf["state"]["key"])

                    for p, inf in self.players.items():
                        counts = {}
                        for player_name, player_info in self.players.items():
                            counts[player_name] = len(player_info["cards"])

                        async_mgr.put_msg_by_user(
                            f"PCOUNT|{counts}",p,inf["state"]["key"]
                        )

                    async_mgr.put_msg_by_user("TURN", player, info["state"]["key"])
                    print("hooo")
                    action = self.play_queue.get()

                    if action == "ADD":
                        info["cards"].append(self.pile.pop(0))
                        continue

                    card = ast.literal_eval(action[1][0])

                    if card[0] == self.current_card[0] or card[1] == self.current_card[1]:
                        info["cards"].remove(card)
                        for p, inf in self.players.items():
                            async_mgr.put_msg_by_user(f"CARDS|{inf["cards"]}", p, inf["state"]["key"])

                        if len(info["cards"]) == 0:
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"WIN|{p}",p, inf["state"]["key"])
                            playing = False
                            break

                        if card[1] == 'SKIP':
                            next_player = players_list[(i + 1) % len(players_list)][0]
                            for p, inf in self.players.items():
                                async_mgr.put_msg_by_user(f"SKIP|{next_player}",p, inf["state"]["key"])
                            self.current_card = card
                            self.skip_next = True
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"CPLY|the new card is|{card}",p, inf["state"]["key"])

                        elif card[1] == 'DRAW_TWO':
                            self.two_next = True
                            self.current_card = card
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"CPLY|the new card is|{card}",p, inf["state"]["key"])

                        elif card[1] == 'REVERSE':
                            self.reverse = True
                            self.reverse_player = player
                            self.current_card = card
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"CPLY|the new card is|{card}",p, inf["state"]["key"])
                            break

                        else:
                            self.current_card = card
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"CPLY|the new card is|{card}",p, inf["state"]["key"])
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"STOP",p, inf["state"]["key"])

                    elif card[0] == 'WILD':
                        info["cards"].remove(card)
                        for p, inf in self.players.items():
                            async_mgr.put_msg_by_user(f"CARDS|{inf["cards"]}", p, inf["state"]["key"])

                        if card[1] == 'CHANGE':
                            async_mgr.put_msg_by_user("CHANGE", player, info["state"]["key"])
                            color = self.play_queue.get()[1]
                            color_map = {
                                "yellow": ("YELLOW", -1),
                                "red": ("RED", -1),
                                "blue": ("BLUE", -1),
                                "green": ("GREEN", -1),
                            }
                            self.current_card = color_map.get(color, self.current_card)

                        elif card[1] == 'DRAW_FOUR':
                            async_mgr.put_msg_by_user("CHANGE", player, info["state"]["key"])
                            color = self.play_queue.get()[1]
                            color_map = {
                                "yellow": ("YELLOW", -1),
                                "red": ("RED", -1),
                                "blue": ("BLUE", -1),
                                "green": ("GREEN", -1),
                            }
                            self.current_card = color_map.get(color, self.current_card)
                            self.draw_four = True


                        if len(info["cards"]) == 0:
                            for p,inf in self.players.items():
                                async_mgr.put_msg_by_user(f"WIN|{p}", p, inf["state"]["key"])
                            playing = False
                            break

                    else:
                        async_mgr.put_msg_by_user("CANT", player, info["state"]["key"])



    def handle_data(self,sock,fields,state):
        request_code = fields[0]
        if request_code == "DEL":
            self.del_player(fields[1],state)
            for p,inf in self.players.items():
                print("blob")
                async_mgr.put_msg_by_user(f"DELP|{fields[1]}",p, inf["state"]["key"])
        if request_code == "STR":
            for p,inf in self.players.items():
                async_mgr.put_msg_by_user(f"RSTR|the game has started",p, inf["state"]["key"])
            self.start_game()
        elif request_code == "PLAY":
            self.play_queue.put(("PLAY",fields[1:]))
        elif request_code == "CHCO":
            self.play_queue.put(("CHCO",fields[1:]))
        elif request_code == "ADD":
            self.play_queue.put("ADD")


        return None




class Request:
    def __init__(self, sock, data):
        self.sock = sock
        self.data = data


class HandleData:
    def __init__(self, data, sock):
        self.data = data
        self.sock = sock
        self.state = get_state(sock)

    @property
    def handle_data(self):
        global log_in_users, private_key, rooms

        state = self.state
        has_key = state['has_key']

        if has_key:
            decrypted_data = decrypt(state['key'], self.data).decode("utf-8")
            print("recv>>>" + decrypted_data)
            fields_in_data = decrypted_data.split("|")
        else:
            fields_in_data = self.data.decode().split("|")

        if state['room'] is not None:
            state['room'].handle_data(self.sock, fields_in_data,self.state)

        request_code = fields_in_data[0].strip()
        to_ret = ""

        if request_code == "RSA":
            with lock:
                private_key, public_key = load_rsa_keys()
            public_key_bytes = get_public_key_bytes(public_key)
            pub_b64 = base64.b64encode(public_key_bytes).decode()
            return f"PUBKEY|{pub_b64}".encode()

        elif request_code == "KEY":
            encrypted_key = base64.b64decode(fields_in_data[1])
            state['key'] = rsa_decrypt(private_key, encrypted_key)
            state['has_key'] = True
            return "RKEY".encode()

        elif request_code == "SGN":
            to_ret = "RSGN|" + create_user(fields_in_data[1], fields_in_data[2],
                                           fields_in_data[3], fields_in_data[4])

        elif request_code == "LGN":
            to_ret = ("RLGN|" + login(self.sock, fields_in_data[1], fields_in_data[2]) + "|"
                      + fields_in_data[1] + "|" + fields_in_data[2])

        elif request_code == "ERP":
            should_work = get_new_reset_pass_code(fields_in_data[1])
            if should_work[0] is None:
                to_ret = "ERPR|" + should_work[1] + "|" + fields_in_data[1]
            else:
                code = should_work[0]
                email_receiver = fields_in_data[1]
                with lock:
                    reset_codes[email_receiver] = code
                subject = "password reset"
                body = (f"your password reset code is {code.get_code()}, "
                        f"it will work for 5 muinits")
                send_email(email_receiver, subject, body)
                to_ret = "ERPR|" + should_work[1] + "|" + fields_in_data[1]

        elif request_code == "GRP":
            code = None
            email = ""

            for uname, value in reset_codes.items():
                if fields_in_data[1] == value.get_code():
                    with lock:
                        code = reset_codes[uname]
                    email = uname

            if code is None:
                to_ret = "GRPR|wrong code, try again"
            elif datetime.now() > code.get_timer():
                to_ret = "GRPR|code expired"
            else:
                with lock:
                    del reset_codes[email]
                to_ret = "GRPR|code received"

        elif request_code == "RNP":
            username = ""
            for uname, value in async_mgr.users.items():
                if value["email"] == fields_in_data[2]:
                    username = value["username"]
            new_password(username, fields_in_data[1])
            return self.encrypt_response("RRMP|reset password")

        elif request_code == "PUB":
            if self.sock not in async_mgr.user_by_sock:
                return self.encrypt_response("ERR|Not logged in")

            async_mgr.put_msg_to_all(f'MSG|{fields_in_data[1]}|{fields_in_data[2]}', state['key'])
            to_ret = "REP"

        elif request_code == "OUT":
            if fields_in_data[1] in log_in_users:
                with lock:
                    log_in_users.remove(fields_in_data[1])

            async_mgr.put_msg_to_all(f'OMSG|{fields_in_data[1]} has left the chat', state['key'])
            to_ret = "REP"

        elif request_code == "PRV":
            if self.sock not in async_mgr.user_by_sock:
                return self.encrypt_response("ERR|Not logged in")

            if fields_in_data[2] not in async_mgr.users:
                return self.encrypt_response("ERR|User does not exist")

            if fields_in_data[2] not in async_mgr.sock_by_user:
                return self.encrypt_response("ERR|User is not online")

            async_mgr.put_msg_by_user(f"PMSG|{fields_in_data[1]}|{fields_in_data[3]}",
                                      fields_in_data[2], state['key'])
            to_ret = "REP"

        elif request_code == "CRR":
            if self.sock not in async_mgr.user_by_sock:
                return self.encrypt_response("ERR|Not logged in")
            room = Room(self.sock, 4, f"{fields_in_data[1]}'s room")
            room.start()
            room.add_player(fields_in_data[1], self.sock,self.state)
            with lock:
                rooms.append(room)
                state['room'] = room
            players = {name: info["id"] for name, info in room.players.items()}
            return self.encrypt_response("RCRR|room created|" + json.dumps(players))

        elif request_code == "JOIN":
            if self.sock not in async_mgr.user_by_sock:
                return self.encrypt_response("ERR|Not logged in")
            for room in rooms:
                if room.get_name() == fields_in_data[1]:
                    username = async_mgr.user_by_sock[self.sock]
                    msg = room.add_player(username, self.sock, self.state)
                    with lock:
                        self.state['room'] = room
                    if msg != 'successfully joined':
                        return self.encrypt_response(f"ERR|{msg}")

                    players = {name: info["id"] for name, info in room.players.items()}
                    return self.encrypt_response(f"RJOI|{fields_in_data[1]}|" + json.dumps(players))
            return self.encrypt_response("ERR|Unknown room")



        elif request_code == "ROOMS":
            room_list = {}
            for room in rooms:
                room_list[room.get_name()] = room.player_count()
            return self.encrypt_response("ROOML|" + json.dumps(room_list))

        else:
            to_ret = "ERR|Unknown request"

        return self.encrypt_response(to_ret)

    def encrypt_response(self, msg):
        state = self.state
        data = msg.encode("utf-8")
        if state['has_key']:
            data = pad_massage(data)
            return encrypt(data, state['key'])
        return data


class ClientHandler(threading.Thread):
    def __init__(self, sock, cid, addr):
        super().__init__(daemon=True)
        self.sock = sock
        self.cid = cid
        self.addr = addr
        self.finish = False

    def run(self):
        async_mgr.add_new_socket(self.sock)
        get_state(self.sock)
        sender_thread = threading.Thread(target=self.client_sender, daemon=True)
        sender_thread.start()

        print(f"Got client number {self.cid}, from address {self.addr}")

        while not self.finish and not all_to_die:
            try:
                data = recv_by_size(self.sock)
                if data == b'':
                    print("Client suddenly disconnected")
                    break
                if data == "qq":
                    print("Client disconnected")
                    break
                else:
                    request_queue.put(Request(self.sock, data))

            except socket.error as sock_err:
                print(f"Socket error: {sock_err}")
                break
            except Exception as e:
                print(f"Exception: {e}")
                break

        with lock:
            async_mgr.delete_socket(self.sock)
            delete_state(self.sock)
            print(f"Closing sock {self.cid}")
            self.sock.close()

    def client_sender(self):
        while not all_to_die and not self.finish:
            try:
                msgs = async_mgr.get_async_messages_to_send(self.sock)
                for msg in msgs:
                    send_with_size(self.sock, msg)

                time.sleep(0.05)
            except socket.error:
                break
            except Exception:
                break


def handle_request():
    while True:
        request = request_queue.get()
        try:

            to_send = HandleData(request.data, request.sock).handle_data
            if to_send:
                try:
                    send_with_size(request.sock, to_send)
                except socket.error as sock_err:
                    print("got error", sock_err)
                    traceback.print_exc()
        except Exception as e:
            print("got Exception:", e)
            traceback.print_exc()
        finally:
            request_queue.task_done()




def main():
    global all_to_die

    threads = []
    srv_sock = socket.socket()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f'your ip address is: {ip_address}')

    port = 1233

    srv_sock.bind((ip_address, port))
    srv_sock.listen(20)

    for j in range(REQUEST_COUNT):
        t = threading.Thread(target=handle_request, daemon=True)
        t.start()

    i = 1
    while True:
        cli, addr = srv_sock.accept()

        t = ClientHandler(cli, i, addr)
        t.start()
        i += 1
        threads.append(t)
        if i > 10000000:
            break

    all_to_die = True
    print("breaking server ")
    for t in threads:
        t.join()
    srv_sock.close()
    print("bye...")


if __name__ == '__main__':
    main()
