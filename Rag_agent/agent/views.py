from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, SessionAuthentication,  TokenAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .models import User
from dotenv import load_dotenv
from .tools import tools
from .rag_utils import llm

# API to sign up a new user
class UserRegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            response = {
                'success': True,
                'user': serializer.data,
                'token': Token.objects.get(user=User.objects.get(username=serializer.data['username'])).key
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)
    
class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            response = {
                "username":{
                    "detail": "User Does not exist"
                }
            }

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request,user)
                 
                token,created = Token.objects.get_or_create(user=user)
                response = {
                    'success': True,
                    'username': user.username,
                    'email': user.email,
                    'token': token.key
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        print(request.user.id)
        token = Token.objects.get(user_id=request.user.id)
        logout(request)
        token.delete()

        return Response({"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK)
    
class RagAgent(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    load_dotenv()

    prompt = hub.pull("hwchase17/openai-tools-agent")
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    def post(self, request, format=None):
        resource = request.data.get('resource')
        # pdf_file = request.FILES.get('pdf_file')
        user_query = request.data.get('query')
        user_id = request.POST.get('user_id')
        print("user_id",user_id)
        response = self.agent_executor.invoke({"input":f"user_query: {user_query} url:{resource} user_id:{user_id}"})
        return Response({'response': response['output']})
    