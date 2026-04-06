class UIChange:
    def __init__(self, where, action,new="", title="", message=""):
        self.where = where
        self.action = action
        self.new = new
        self.title = title
        self.message = message

    def get_where(self):
        return self.where

    def get_action(self):
        return self.action

    def get_new(self):
        return self.new

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message
