from django.shortcuts import render
from django.views import View
from registration.passwordManager import checkPassword
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

class UserLogin(APIView):
    authentication_classes = []
    def databaseConn(self,Email,password):
        with connection.cursor() as cursor:
            cursor.execute("select email,password,token from c_users")
            data_back = cursor.fetchone()
            data = None
            print(data_back)
            
            if data_back[0] == str(Email) and checkPassword(str(password),data_back[1]):
                data = data_back[1]
            
            if not data:
                status  = "api_login_failed"
                token   = None
                
                return {"login_status":status,
                        "auth_token":token
                }

            else:
                status  = "api_login_ok"
                token   = str(data_back[2])

                return {"login_status":status,
                        "auth_token":token
                }

        
    def post(self,request):
        Email       = request.POST["email_address"]
        password    = request.POST["password"]

        if Email and password:
            database_respond = self.databaseConn(Email,password)
            if database_respond['login_status'] == "api_login_ok":
                
                return Response(data = {"status":"api_login_ok",
                                        "auth_token":str(database_respond["auth_token"])
                                        })
               
            # elif database_respond['login_status']=="api_login_failed":
            else:
                return Response(data = {
                    "status":"api_login_failed",
                    "auth_token":"Null"
                })
        else:
            return Response(data = {
                    "status":"api_login_failed",
                    "auth_token":"Null"

            })
                
