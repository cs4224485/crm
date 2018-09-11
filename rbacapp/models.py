from django.db import models

# Create your models here.


class User(models.Model):
    '''
    用户表
    '''
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    roles = models.ManyToManyField(to="Role")

    def __str__(self):
        return self.name


class Role(models.Model):
    '''
    角色表
    '''
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to='Permission')

    def __str__(self):
        return self.title


class Permission(models.Model):
    '''
    权限表
    '''
    action = models.CharField(max_length=32, default='list')
    group = models.ForeignKey("PermissionGroup", default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class PermissionGroup(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return  self.title