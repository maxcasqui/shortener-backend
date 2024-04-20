import re
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
UserModel = get_user_model()

def validate_data(data):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    ##
    if not email:
        raise ValidationError("Email cannot be empty.")
    if not password:
        raise ValidationError("Password cannot be empty.")
    if not username:
        raise ValidationError("User Name cannot be empty.")
    if email_exists(email):
        raise ValidationError("This email address is already in use.")
    ##
    return data

def email_exists(email):
    if UserModel.objects.filter(email=email).exists():
        return True
    return False

def match_password_regex(password):
    pass

def validate_url(data):
    url = data.get('original_url')
    regex = r"(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    if not bool(re.match(regex, url)):
        None
    return data

def validate_token(authorization_header):
    if authorization_header and authorization_header.startswith('Bearer '):
        return authorization_header.split(' ')[1]
    return None