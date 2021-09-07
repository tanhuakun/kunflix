from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name = 'start'),
    path('login/', views.loginpage, name = 'login'),
    path('register/', views.register, name = 'register'),
    path('apply', views.apply, name = 'apply'),
    path('check_login/', views.check_login, name = 'check_login'),
    path('check_apply', views.check_apply, name = 'check_apply'),
    path('check_register', views.check_register, name = 'check_register'),
    path('applied', views.applied, name = 'applied'),
    path('registered/', views.registered, name = 'registered'),
    path('forget', views.forget_password, name = 'forget'),
    path('forgotmypass/<key1>/<key2>/<name>', views.reset_password, name = 'reset'),
    path('approve', views.approve, name='approve')
]