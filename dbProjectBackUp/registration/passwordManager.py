from django.contrib.auth.hashers import (
    make_password,
    check_password
    )



def createPassword(password):
    created_password = make_password(password)
    return created_password

def checkPassword(raw_pass,hashed_pass):
    is_same = check_password(raw_pass,hashed_pass)
    return is_same