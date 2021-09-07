from django.contrib import admin
from .models import Show, Requests, Votes

admin.site.register(Show)
admin.site.register(Requests)
admin.site.register(Votes)
# Register your models here.
