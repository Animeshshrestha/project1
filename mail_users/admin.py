from django.contrib import admin
from .models import *

# admin.site.register(UserEmail)
@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ("sender", "subject" , "is_read" , "is_archived")
    list_filter = ("is_read", "is_archived" )