from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
import asyncio
from django.db import connection
from channels.auth import login,logout
from channels.db import database_sync_to_async  
from registration.models import User
# from django.contrib.auth.models import User 


class ChatConsumer(AsyncWebsocketConsumer):
    
    def registerOnConnect(self,token):
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT id,email FROM c_users  WHERE token = '%s' "%(str(token)))
            result = cursor.fetchone()
            # print(User.objects.filter(email="ahmadmansuri3@gmail.com"))
            self.email  = result[1]
            # res= User.objects.get(token=str(token))
            
            login(self.scope,User.objects.filter(email=self.email))
            self.scope["session"].save()
    

    def saveMessageOnReceive(self):
        pass

    def createGroupList(self,token):
        with connection.cursor() as cursor:
            # print("daui goooogoooooo")
            cursor.execute("select id from c_users where token ='%s' "%(str(token)))
            userId = cursor.fetchone()
            if userId is not None:
                cursor.execute("select pv_name from private_chats where first_id='%d' or second_id='%s'"%(int(userId[0]),int(userId[0])))
                result = cursor.fetchall()
                groupNameList = []
                if result is not None:
                    for i in result:
                        groupNameList.append(result[0])
            # print (groupNameList)
            return groupNameList

        

    # async def addChannelToGroupsOnConnect(self,token):
    #     groupNameList2 = self.createGroupList(token)
    #     print("this is my grouplist : ",groupNameList2)
    #     for i in groupNameList2:
    #         await self.channel_layer.group_add(
    #             str(i),
    #             self.channel_name
    #         )
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

    def createPvChat(self,username,email):
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

    # def put(self,request):
    #     token = request.data.get('token')
    #     username = request.data.get('username')
    #     email = request.data.get('email_address')
    #     if self.checkToken(email,token):
    #         result = self.createPvChat(request,username,email)
    #         if result is not False:
    #             return Response({'status':"api_create_chat_ok"})
    #         else:
    #             return Response({'status':"api_create_chat_failed"})
    #     else:
    #         return Response({'status':"api_disconnect"})

    async def connect(self):
        print(self.scope["user"])
        # await self.addChannelToGroupsOnConnect('0706a3c0da537a63bdf372c7c32176d6c2c1ea1c')
        grouplist = database_sync_to_async(self.createGroupList)('0706a3c0da537a63bdf372c7c32176d6c2c1ea1c')
        print(grouplist)
        await self.channel_layer.group_add(
                "mamad",
                self.channel_name
            )
        await self.accept()

    async def disconnect(self, code):
        database_sync_to_async(logout)(self.scope)






    async def receive(self,text_data):
        # await database_sync_to_async(self.createGroupList)("0706a3c0da537a63bdf372c7c32176d6c2c1ea1c")
#
        r_data = json.loads(text_data)
        print(r_data)
        if str(r_data["type"])=="register":
            await database_sync_to_async(self.registerOnConnect)(str(r_data["token"]))

            print(self.email)
        

        elif str(r_data["type"]=="realtime_create_chat"):
            token = r_data['token']
            email = r_data['email_address']
            username = r_data['username']
            if self.checkToken(email,token):
                result = await database_sync_to_async(self.createPvChat)(username,email)
                if result is not False:
                    
                    self.send(text_data=json.dumps({
                            "type":"realtime_create_chat_ok"
                    }))
                else:
                    self.send(text_data = json.dumps({
                        "type":"realtime_create_chat_failed",
                    }))
            else:
                self.send(text_data = json.dumps({
                   "type":"realtime_disconnect" 
                }))

        else:
            if self.email==None:
                print("hamid")
                await self.disconnect(None)

            else:
                await self.channel_layer.group_send(
                    # r_data['d_group'],
                    "mamad",
                    {
                        'type':"messageHandler",
                        'message':str(r_data['text_message']),
                        'username':str(r_data['sender_username'])
                    }
                )


    async def messageHandler(self,event):
        message =event['message']
        senderUsername = event['username']

        await self.send(text_data=json.dumps(
            {
                'text_message':str(message),
                'sender_username':str(senderUsername)
            }
        ))
            
    async def createNewChat(self,event):
        pass