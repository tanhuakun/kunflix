from django.contrib import admin
from .models import Invites, Applications, RegisterAttempts, ForgetPassword

class ApplicationsAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

class RegisterAttemptsAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(Applications,ApplicationsAdmin)
admin.site.register(RegisterAttempts, RegisterAttemptsAdmin)
admin.site.register(Invites)
admin.site.register(ForgetPassword)

