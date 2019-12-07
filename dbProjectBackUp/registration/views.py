from django.shortcuts import render
from django.core.mail import send_mail
from django.db import connection
import datetime
import random
from .models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from .passwordManager import checkPassword,createPassword
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt 


class SignUp(APIView):
    authentication_classes = []
    def databaseConn(self,password,Email):
        with connection.cursor() as cursor:
            # cursor.execute("SELECT username FROM p_users WHERE EXISTS username=%s"%str(username))
            cursor.execute("SELECT email FROM c_users")
            data_back = cursor.fetchall()
            data = None
            print(data_back)
            for i in data_back:
                if i[0]==str(Email):
                    data = str(Email)
                    break

            if not data:
                verification_code = random.randint(10_000_000,99_999_999)
                cursor.execute('''INSERT INTO c_users VALUES (DEFAULT,'%s',DEFAULT,'%s',FALSE,'%s','%s',DEFAULT)'''%( 
                    # str(username),
                   str(createPassword(password)),
                    str(Email),
                    str(verification_code),
                    str(datetime.datetime.now()+datetime.timedelta(minutes=5))
                    )
                    )
                return {'operation_status':"api_signup_ok",
                        'verification_code':verification_code
                }
            else:
                return {'operation_status':"api_signup_bad",'verification_code':None}
                
    def post(self,request):
        if request.POST['password'] == request.POST['pass_confirmation']:
            database_response = self.databaseConn(request.POST["password"],request.POST["email_address"])
            if database_response['operation_status'] =="api_signup_ok":
                html_message = '''
                    <div>
                    <h1>verification code is :%s</h1>
                    
                    </div>
                '''%database_response['verification_code']
                # print("---------- BEFORE SENDING EMAIL ---------")

                user = authenticate(request,username = request.POST["email_address"],password = request.POST["password"])
                # print("---------- AFTER SENDING EMAIL ---------")

                print("the user trying to authenticate is : ",user)
                login(request,user)
                print ("is authenticated",request.user)
                print("---------- BEFORE SENDING EMAIL ---------")
                # send_mail("Verify Your Account","dayigoloo",from_email="ahmadmansooripv@gmail.com",recipient_list=[request.POST["email_address"]],fail_silently=False,html_message=html_message)
                print("---------- AFTER SENDING EMAIL ---------")
                return Response(data={"status":"successful"},status=HTTP_200_OK)
            elif database_response['operation_status'] =="api_signup_bad":
                print("user exists!")
                return Response(data={'status':"failed_user_exists"})
        else:
            return Response(data={'status':"failed"},status=HTTP_200_OK)




class verificator(APIView):
    authentication_classes = []
    def dbconnection(self,email,verification_code):
        with connection.cursor() as cursor:
            cursor.execute("SELECT verified,verification_code,verification_code_expire_time FROM c_users WHERE email='%s'"%str(email))
            db_result = cursor.fetchone()
            
            if len(db_result) and not db_result[0] and db_result[1]==verification_code and datetime.datetime.strptime(str(db_result[2])[:19],"%Y-%m-%d %H:%M:%S")>=datetime.datetime.now():
                generated_token = str ( Token.objects.get_or_create( user=User.objects.get( email=email ))[0].key  )
                cursor.execute("UPDATE c_users SET verified = TRUE ,token = '%s' WHERE email = '%s'"%(generated_token,str(email)))
                # cursor.fetchone()
                # 
                return "api_verification_ok",generated_token
            
            elif datetime.datetime.strptime(str(db_result[2])[:19],"%Y-%m-%d %H:%M:%S")<=datetime.datetime.now():
                return "api_verification_expired",None
            
            elif not db_result[1]==verification_code:
                return "api_verification_bad",None


    
    def newVerificationCode(self,verification_code):
        pass
    def post(self,request):
        email = request.POST["email_address"]
        # email = request.POST.get("email_address")
        # verification_code = request.POST.get("verification_code")
        verification_code = request.POST["verification_code"]
        print(email,verification_code)

        if email and verification_code:
            check_code,token = self.dbconnection(email,verification_code)
            if check_code == "api_verification_ok":
                return Response({"status":"verification_successful","auth_token":token})

            elif check_code =="api_verification_expired" :
                return Response({"status":"verification_code_expired","auth_token":"Null"})
            
            elif check_code =="api_verification_bad":
                return Response({"status":"wrong_verification_code","auth_token":"Null"})

            else:
                return Response({"status":"Null","auth_token":"Null"})
        else:
            
            return Response({"status":"verification_failed","auth_token":"Null"})

