from django.urls import path 
from .views import UserRegisterAPIView, UserLoginAPIView, UserLogoutAPIView, RagAgent, register,login_user, chat, homepage

urlpatterns = [
  path('api/signup/', UserRegisterAPIView.as_view(), name='signup'),
  path('api/signin/', UserLoginAPIView.as_view(), name='signin'),
  path('api/logout/', UserLogoutAPIView.as_view(), name='logout'),
  path('api/qna/', RagAgent.as_view(), name="qna"),
  path('register/', register, name='register'),
  path('login/', login_user),
  path('chat/', chat),
  path('', homepage),
]