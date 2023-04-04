from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.login, name = 'login'),
    path('pass_check',views.authenticate,name = 'pass'),
    path('login/reg',views.register, name = 'reg'),
    path('user_home',views.user_home,name='user_home')
]