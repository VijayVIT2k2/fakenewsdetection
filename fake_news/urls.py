from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.login, name = 'login'),
    path('pass_check',views.authenticate,name = 'pass'),
    path('login/reg',views.register, name = 'reg'),
    path('user_home',views.user_home,name='user_home'),
    path('add_news', views.add_news, name = 'add_news'),
    path('pro_news', views.pro_news, name = 'pro_news'),
    path('check_news', views.check_news, name = "check_news"),
    path('download_csv/', views.download_csv, name='download'),
    path('upload', views.upload_csv,name='upload'),
    path('update_models',views.update, name="update")
]