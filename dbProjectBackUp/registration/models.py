from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from datetime import datetime
from datetime import timedelta
import random


class UserManager(BaseUserManager):
    # def create_user(self,email,passsword=None):
    #     if not email:
    #         raise ValueError("any user must have an email !")
    #     if not passsword:
    #         raise ValueError("any user account must have a password")
        
    #     user = self.model(
    #         email = self.normalize_email(email)
    #     )
    #     user.set_password(passsword)
    #     user.verified = False
    #     user.verification_code = random.randint(10_000_000,99_999_999)
    pass

class User(AbstractBaseUser):
    email = models.EmailField(max_length = 255,unique = True)
    verified = models.BooleanField(default=0) 
    verification_code =models.CharField(max_length=8,unique = True)
    verification_code_expire_time = models.DateTimeField()
    username = models.CharField(max_length = 255,unique = True,default=None,blank = True,null=True)
    token = models.CharField(max_length = 255,unique = True,default = None,blank = True,null=True )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = []


    objects = UserManager()



    def __str__(self):
        return self.email

    @property
    def is_verified(self):
        return self.verified

    @property 
    def expireTime(self):
        return self.verification_code_expire_time

    class Meta:
        #clients
        db_table = 'c_users'


