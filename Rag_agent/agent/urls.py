from django.urls import path 
from .views import UserRegisterAPIView, UserLoginAPIView, UserLogoutAPIView, RagAgent

urlpatterns = [
  path('api/signup/', UserRegisterAPIView.as_view(), name='signup'),
  path('api/signin/', UserLoginAPIView.as_view(), name='signin'),
  path('api/logout/', UserLogoutAPIView.as_view(), name='logout'),
  path('api/qna/', RagAgent.as_view(), name="qna")
]