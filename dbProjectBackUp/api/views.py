from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,UpdateAPIView,CreateAPIView
from registration.models import User
from django.db import connection
from rest_framework.response import Response
from .serializers import (UserGroupSerializers,
                          CreateUserProfileApi
                         )
from realtime.models import pvChat,profile



class UserGroups(ListAPIView):
    authentication_classes = []

    http_method_names = ['put','post','get']
    # serializer_class = UserGroupSerializers
    # queryset = pvChat.objects.raw("select id,pv_name,last_activity from private_chats where first_id = '4' or second_id = '4'")
    # queryset = pvChat.objects.raw("select creator_id)
    def findChatMembers(self,token,pvname=None):
        with connection.cursor() as cursor:
            cursor.execute("select id from c_users where token = '%s'"%(str(token)))
            usreid = cursor.fetchone()
            cursor.execute("select pv_name,first_id,second_id,creator_id from private_chats where first_id = '%d' or second_id = '%d'"%(int(usreid[0]),int(usreid[0])))
            result = cursor.fetchall()
                        
            info_list = []
            for i in result:
                wanted = i[2] if i[2]!=usreid[0] else i[1]
                cursor.execute("select firstname,lastname,biography from realtime_profile inner join c_users on c_users.id = realtime_profile.owner_id where c_users.id = '%d'"%int(wanted))
                info_list.append(cursor.fetchone())

            for i in range(len(result)):
                result[i]+=info_list[i]
            usernamelist = []
            for i in range(len(result)):
                wanted = result[i][2] if result[i][2]!=usreid[0] else result[i][1]
                
                print("this is the problem !:",result,wanted)
                cursor.execute("select username from c_users where id ='%s'"%(int(wanted)))
                usernamelist.append(cursor.fetchone())

            for i in range(len(result)):
                result[i]+=usernamelist[i]
            dic=[]
            
            for i in result:
                currentdic = {}
                currentdic.update({'name':i[4],'family':i[5],"username":i[7],"biography":i[6],"pv_name":i[0]})
                dic.append(currentdic)
            return dic
                
    def put(self,request,*args, **kwargs):
       return Response()

    def post(self,request,*args, **kwargs):
        token = request.data.get("token")
        return Response({"data":self.findChatMembers(token),"status":"api_get_chats_ok"})

class UserPvChat(ListAPIView):
    http_method_names =['put','post','get']
    authentication_classes = []

    def checkToken(self,email,token):
        with connection.cursor() as cursor:
            cursor.execute("select id from c_users where email = '%s' and token ='%s'"%(str(email),str(token)))
            result = cursor.fetchone()
            if result is not None:
                return True
            else:
                return False

    def serachUser(self,request,username):

        with connection.cursor() as cursor:
            cursor.execute("select email from c_users where username = '%s'"%(str(username)))
            foundUser = cursor.fetchone()
            if foundUser is not None:
                cursor.execute("select last_login,firstname,lastname,biography from realtime_profile inner join c_users on c_users.id = realtime_profile.owner_id where c_users.username = '%s' "%(str(username)))
                user = cursor.fetchone()
                if user is not None:
                    return {"response":"succeful","data":user}
                # else:
                #     return {"response":"anonymosUser","data":None}
            else:
                return {"response":"targetUserDoesntExistsAnymore","data":None}

    def createPvChat(self,request,username,email):
        
        with connection.cursor() as cursor:
            cursor.execute("select email,id from c_users where username = '%s'"%(str(username)))
            found = cursor.fetchone()
            if found is not None:
                cursor.execute("select email,id from c_users where email = '%s'"%(str(email)))
                found2 = cursor.fetchone()
                if found2 is not None:
                    emails = [found[0],email]
                    emails.sort()
                    pvName = str(emails[0])+str(emails[1])
                    cursor.execute("insert into private_chats values (DEFAULT,DEFAULT,'%s','%d','%d','%d')"%(str(pvName),int(found2[1]),int(found2[1]),int(found[1])))
                    return True
                else:
                    return False
            else:
                return False

    def put(self,request):
        token = request.data.get('token')
        username = request.data.get('username')
        email = request.data.get('email_address')
        if self.checkToken(email,token):
            result = self.createPvChat(request,username,email)
            if result is not False:
                return Response({'status':"api_create_chat_ok"})
            else:
                return Response({'status':"api_create_chat_failed"})
        else:
            return Response({'status':"api_disconnect"})


    def post(self,request):
        token       = request.data.get('token')
        username    = request.data.get('username')
        result = self.serachUser(request,username)
        
        if result['response'] == "succeful":
            return Response({"status":"api_search_user_ok","firstname":str(result["data"][1]),"lastname":str(result["data"][2]),"biography":str(result["data"][3]),"last_activity":str(result["data"][0])})

        elif result["response"]=="targetUserDoesntExistsAnymore":
            return Response({"status":"api_search_user_failed"})



class UserProfilePut(APIView):
    http_method_names = ['put','post','delete','get']
    authentication_classes = []

    # queryset = profile.objects.raw("select * from realtime_profile")
    # serializer_class = CreateUserProfileApi
    def databaseconn(self,email,token,biography=None,firstname=None,lastname=None,username=None):
        with connection.cursor() as cursor:
            cursor.execute("select email,token,id from c_users where email = '%s'"%(str(email)))
            data_back = cursor.fetchone()
            print(email,data_back[0])
            print(token,data_back[1])
            if data_back[0] == str(email) and data_back[1] == str(token):
                print(data_back[2])
                cursor.execute("insert into realtime_profile values(DEFAULT,DEFAULT,'%s','%s','%s',%d)"%(str(biography) if biography!=None else 'DEFAULT',str(firstname)if firstname!=None else 'DEFAULT',str(lastname) if lastname!=None else 'DEFAULT',data_back[2]))
                if username is not None:
                    cursor.execute("update c_users set username='%s' where email='%s'"%(username,email))
                    return True
                return True
            else:
                return False
            
     


    def put(self,request):
        token = request.data.get('token')
        email = request.data.get('email_address')
        # firstname = request.PUT['firstname']
        # lastname = request.PUT['lastname']
        # biography = request.PUT['biography']
        if token and email:
            print(request.data["biography"])
            if self.databaseconn(email,token,request.data.get("biography"),request.data.get("firstname"),request.data.get("lastname"),request.data.get("username")):
                return Response(data = {"status":"api_update_profile_ok"})
            else:
                print("b fuck")
                return Response(data = {"status":"api_update_profile_failed"})
        else:
            return Response({"errror":"errror"})
            
    def get(self,request):
        return Response(data = {"status":"b fuck"})
        
