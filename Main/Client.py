import socket
import sys
import threading
import pygame

from Helpers.tcp_by_size import *
from Helpers.UIChange import *
from Encryption.AES import *
from Encryption.RSA import *
from UI.GUI.Main_menu import MainMenu
from globals import *
import base64

#global
is_in_game = False
is_connected = False
current_username = ""
current_email = ""
chat_frame_instance = None
reset_email_sent = False
reset_code_verified = False
key_exchanged = False
key = generate_key()
dh_private_key = None
ui_request = []

def listen_to_server(sock: socket.socket,screen):
    global is_connected
    global current_username, chat_frame_instance
    global reset_email_sent, reset_code_verified
    global current_email, key_exchanged, key

    while is_connected:
        try:
            reply = recv_by_size(sock)
            if reply == b'':
                break

            if key_exchanged:
                reply = decrypt(key, reply).decode()
                print("reply: " + reply)
                fields = reply.split("|")
                code = fields[0]
            else:
                fields = reply.split(b"|", 1)
                code = fields[0].decode()

            if code == "PUBKEY":
                public_key_bytes = base64.b64decode(fields[1])
                public_key = public_key_from_bytes(public_key_bytes)
                encrypted_key = rsa_encrypt(public_key, key)
                encrypted_key_b64 = base64.b64encode(encrypted_key).decode()
                send_with_size(sock, f"KEY|{encrypted_key_b64}")

            elif code == "RKEY":
                key_exchanged = True
                print("key exchanged")


            elif code == "RLGN":
                if fields[1] == "Login successful":
                    current_username = fields[2]
                elif fields[1] in ("User does not exist", "Wrong password", "user already logged in"):
                    if fields[1] == "User does not exist":
                        fields[1] = "User does \n not exist"
                    #ui_queue.put({"where":"login","action":"messagebox","title":"Error","message":fields[1]})
                    ui_request.append(UIChange(
                        where="login",
                        action="messagebox",
                        title="Error",
                        message=fields[1]
                    ))

            elif code == "ERPR":
                if fields[1] == "email does not exist":
                    pass
                    current_email = ""
                elif fields[1] == "got Reset Code":
                    pass

            elif code == "GRPR":
                if fields[1] == "code expired":
                    pass
                elif fields[1] == "wrong code, try again":
                    pass
                elif fields[1] == "code received":
                    pass

            elif code == "ERR":
                pass

        except Exception as e:
            print(f"listen_to_server error: {e}")
            is_connected = False
            break




def main(ip):
    global is_connected, key, is_in_game,ui_request

    sock = socket.socket()

    try:
        sock.connect((ip, 1233))
        is_connected = True
        print("Connection successful")
        send_with_size(sock, f"RSA")
    except Exception as e:
        print("Connection failed:", e)
        return

    screen = pygame.display.set_mode((SIZE_WIDTH * scale, SIZE_HEIGHT * scale))

    threading.Thread(
        target=listen_to_server,
        args=(sock,screen),
        daemon=True
    ).start()

    clock = pygame.time.Clock()
    while is_connected:
        if key_exchanged and not is_in_game:
            is_in_game = True
            MainMenu(screen, sock, key,ui_request)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_connected = False

        pygame.display.flip()
        clock.tick(60)

    sock.close()



if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        this_ip = input("Please enter the server ip>>> ")
        main(this_ip)
