import threading
import pickle
from Encryption.AES import *




class Async:
   """
   Thread-safe async message manager with user support via pickle files.
   """


   USERS_FILE = "../users.pkl"


   def __init__(self):
       self.lock = threading.Lock()


       # socket -> [messages]
       self.async_msgs = {}


       # username -> socket
       self.sock_by_user = {}


       # socket -> username
       self.user_by_sock = {}


       # username -> user data
       self.users = {}


       self._load_users()


   def _load_users(self):
       if os.path.exists(self.USERS_FILE):
           try:
               with open(self.USERS_FILE, "rb") as f:
                   if f.read(1):
                       f.seek(0)
                       self.users = pickle.load(f)
           except EOFError:
               pass


   def add_new_socket(self, sock):
       with self.lock:
           self.async_msgs[sock] = []


   def delete_socket(self, sock):
       with self.lock:
           if sock in self.user_by_sock:
               username = self.user_by_sock.pop(sock)
               self.sock_by_user.pop(username, None)
           self.async_msgs.pop(sock, None)


   def login(self, sock, username, password):
       if username not in self.users:
           return False
       if self.users[username]["password"] != password:
           return False


       with self.lock:
           self.sock_by_user[username] = sock
           self.user_by_sock[sock] = username
       return True


   def put_msg_to_socket(self, data, sock):
       with self.lock:
           if sock in self.async_msgs:
               self.async_msgs[sock].append(data)


   def put_msg_by_user(self, data, username,key):
       with self.lock:
           sock = self.sock_by_user.get(username)
           if sock:
               to_send = data
               to_send = to_send.encode("utf-8")
               to_send = pad_massage(to_send)
               encrypted_to_send = encrypt(to_send, key)
               self.async_msgs[sock].append(encrypted_to_send)


   def put_msg_to_all(self, data,key):
       with self.lock:
           for sock in self.async_msgs:
               to_send = data
               to_send = to_send.encode("utf-8")
               to_send = pad_massage(to_send)
               encrypted_to_send = encrypt(to_send, key)
               self.async_msgs[sock].append(encrypted_to_send)


   def get_async_messages_to_send(self, sock):
       with self.lock:
           msgs = self.async_msgs.get(sock, []).copy()
           self.async_msgs[sock] = []
           return msgs
