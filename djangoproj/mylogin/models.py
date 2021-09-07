from django.db import models
from django.conf import settings

class Invites(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length = 20)
    email = models.CharField(max_length=100)

class RegisterAttempts(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=80)
    date = models.DateTimeField(auto_now_add=True)

class Applications(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    approved = models.BooleanField(default = False)
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=80)

class ForgetPassword(models.Model):
    id = models.AutoField(primary_key=True)
    requser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key1 = models.CharField(max_length=10)
    key2 = models.CharField(max_length=6)
    date = models.DateTimeField(auto_now_add=True)



# Create your models here.
