from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, SessionAuthentication,  TokenAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .models import User
from dotenv import load_dotenv
from .tools import tools
from .rag_utils import llm, get_session_history
from .forms import UserRegistrationForm
import requests
from django.http import HttpResponse
from langchain_core.runnables.history import RunnableWithMessageHistory

# API to sign up a new user
class UserRegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
            
        serializer = UserRegisterSerializer(data=data)
       

        if serializer.is_valid():
            # Save user data to PostgreSQL
            user_data = serializer.validated_data
            user = User.objects.create_user(
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                password=user_data['password1']
            )
            # Generate token
            token = Token.objects.create(user=user)
            
            response = {
                'success': True,
                'user': serializer.data,
                'user_id': user.id,
                'token': token.key
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
                    'user_id': {user.id},
                    'token': token.key
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
       
        user_id = int(request.data['user_id'])
        token = Token.objects.get(user_id=user_id)
        logout(request)
        token.delete()

        return Response({"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK)
    
class RagAgent(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    load_dotenv()

    prompt = hub.pull("hwchase17/openai-tools-agent")
    prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
            "You are a helpful assistant who will help with chatting and providing accurate information to the  users. You are provided the tools for dealing with the resource that the user has provided. Only use tools if the query asks for a specific data."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        output_messages_key="output",
        history_messages_key="chat_history",
    )
    def post(self, request, format=None):
        resource = request.data['resource']
        user_query = request.data['query']
        user_id = request.data['user_id']
        
        response = self.agent_with_history.invoke({"input":f"user_query: {user_query} url:{resource} user_id:{user_id}"}, {"configurable":{"session_id":request.session.session_key}})
        return Response({'response': response['output']})
    

def register(request):
    return render(request, 'signup.html')

def homepage(request):
    return render(request, "index.html")
def login_user(request):
    return render(request,'login.html')
def chat(request):
    return render(request, 'chat.html')

