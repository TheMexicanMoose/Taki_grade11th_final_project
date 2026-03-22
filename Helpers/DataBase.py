

import pickle
import os
import secrets
import hashlib
import random
from datetime import datetime, timedelta


USERS_FILE = "../users.pkl"



PEPPER_FILE = "../pepper.txt"


def generate_pepper():
   with open(PEPPER_FILE, "w") as f:
       pepper_bytes = secrets.token_bytes(32)
       pepper_str = pepper_bytes.hex()
       f.write(pepper_str)

def get_pepper():
   with open(PEPPER_FILE, "r") as f:
       return f.read().strip()




def generate_salt():
   # 16 bytes random salt
   return secrets.token_hex(16)




def hash_password(password, salt):
   pepper = get_pepper()
   combined = password + salt + pepper
   return hashlib.sha256(combined.encode()).hexdigest()


def load_users():
   if os.path.exists(USERS_FILE):
       try:
           with open(USERS_FILE, "rb") as f:
               users = pickle.load(f)
       except (EOFError, pickle.UnpicklingError):
           users = {}
   else:
       users = {}
   return users




def save_users(users):
   with open(USERS_FILE, "wb") as f:
       pickle.dump(users, f)




def add_user(users, username, password, name, email):
   if username in users:
       return False, "username already exists"


   salt = generate_salt()
   hashed = hash_password(password, salt)


   data_dict = {
       "username": username,
       "password": hashed,
       "salt": salt,
       "name": name,
       "email": email
   }


   users[username] = data_dict
   save_users(users)
   return True, f"saved user {username}"




def login_user(users, async_mgr, sock, username, password):
   if username not in users:
       return False, "User does not exist"


   user_data = users[username]
   salt = user_data["salt"]


   hashed_password = hash_password(password, salt)


   if hashed_password != user_data["password"]:
       return False, "Wrong password"


   async_mgr.user_by_sock[sock] = username
   async_mgr.sock_by_user[username] = sock
   return True, "Login successful"


class ResetPass:
   def __init__(self):
       self.code = ""
       self.timer = None


   def generate_code(self):
       for i in range(0,6):
           self.code += str(random.randint(0, 9))


   def start_timer(self):
       self.timer = datetime.now() + timedelta(minutes=5)


   def get_timer(self):
       return self.timer


   def get_code(self):
       return self.code


def reset_password():
   number = ResetPass()
   number.generate_code()
   number.start_timer()
   return number


def chack_email(users,email):
   for user in users:
       if users[user]["email"] == email:
           return True
   return False

