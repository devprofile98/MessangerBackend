from django.db import models
from registration.models import User
import datetime
import uuid

class profile(models.Model):
    owner           = models.OneToOneField("registration.User",on_delete=models.CASCADE)
    picture         = models.ImageField(blank = True,null = True)
    biography       = models.CharField(max_length=255,null=True,blank=True,default=True)
    firstname       = models.CharField(max_length=30,null=False,blank=False,default=None)
    lastname        = models.CharField(max_length=50,null=True,blank=True,default=None)


class messageModel(models.Model):
    text            = models.CharField(max_length = 1024,blank=True,null = True,default = None)
    type            = models.CharField(max_length = 10)
    # media           = 
    sender          = models.ForeignKey('registration.User',on_delete=models.SET_NULL,null=True)
    # replyTo         = models.ForeignKey('self',on_delete=models.SET_DEFAULT,dafault = "deletedmessage")
    messageId       = models.AutoField(primary_key = True)
    send_date_time  = models.DateTimeField(auto_now_add=datetime.datetime.now())

     
class groupAbs(models.Model):
    id              = models.AutoField(primary_key=True)
    creator         = models.ForeignKey("registration.User",on_delete=models.SET_NULL,null = True,related_name = "creator",blank = True,unique = False)
    last_activity   = models.DateTimeField(null=True,blank=True)


    class Meta:
        abstract = True
        

class pvChat(groupAbs):
    pv_name         = models.CharField(max_length= 510,blank = False,unique = True)
    first           = models.ForeignKey("registration.User",on_delete=models.SET_NULL,related_name="fist",null=True)
    second          = models.ForeignKey("registration.User",on_delete=models.SET_NULL,related_name="second",null=True)

    class Meta:
        db_table = "private_chats"



    



