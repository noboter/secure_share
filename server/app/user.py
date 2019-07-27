class User:
    def __init__(self, name, active=True):
        self.name = name
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active