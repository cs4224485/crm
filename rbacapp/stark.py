# Author: harry.cai
# DATE: 2018/8/27
from stark.service import starkAdmin
from .models import *

starkAdmin.site.register(User)
starkAdmin.site.register(Role)

class PermissionConfig(starkAdmin.StarkModel):
    list_display = ['title', 'url', 'group', 'action']


starkAdmin.site.register(Permission, PermissionConfig)
starkAdmin.site.register(PermissionGroup)
