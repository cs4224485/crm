from django.contrib import admin

# Register your models here.
from .models import *
#
class PermissionConfig(admin.ModelAdmin):
    list_display = ['title', 'url', 'group', 'action']

admin.site.register(User)
admin.site.register(Permission, PermissionConfig)
admin.site.register(Role)
admin.site.register(PermissionGroup)
