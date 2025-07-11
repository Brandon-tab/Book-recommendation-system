from django.urls import path,include
from myApp import views


urlpatterns = [
    path("home/",views.home,name='home'),
    path("login/",views.login,name='login'),
    path("logOut/", views.logOut, name='logOut'),
    path("register/",views.register,name='register'),
    path("selfInfo/", views.selfInfo, name='selfInfo'),
    path("titleCloud/", views.titleCloud, name='titleCloud'),
    path("summaryCloud/", views.summaryCloud, name='summaryCloud'),
    path("recomBook/", views.recomBook, name='recomBook')
]