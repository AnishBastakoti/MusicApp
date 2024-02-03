# session_management.py

from flask import session

def set_user_session(user):
    session['user'] = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email
    }

def clear_user_session():
    session.clear()
