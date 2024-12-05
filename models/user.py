from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Simulation d'une base d'utilisateurs avec un admin et un utilisateur client
users = {
    'admin': {'password': 'password123'},
    'client': {'password': 'clientpass'}
}
