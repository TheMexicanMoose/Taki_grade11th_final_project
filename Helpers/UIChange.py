class UIChange:
    def __init__(self, where, action, title="", message="", username=""):
        self.where = where
        self.action = action
        self.title = title
        self.message = message
        self.username = username

    def get_where(self):
        return self.where

    def get_action(self):
        return self.action

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message

    def get_username(self):
        return self.username