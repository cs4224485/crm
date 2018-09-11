# Author: harry.cai
# DATE: 2018/7/31

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect
from crm用户关系管理.urls import urlpatterns
import re


class ValidPermission(MiddlewareMixin):
    '''
    通过一个中间件验证当前用户是否有权限

    1 获取当前用户请求的URL
    2 获取当前用户在session中保存的权限列表['/cutomer/list', '/customer/list/(?P<cid>\\d+)/']
    '''

    def process_request(self, request):

        # 当前访问路径
        current_path = request.path_info

        # 检查是否属于白名单
        valid_url_list = ["/login/",  "/reg/", "/admin/.*"]
        for valid in valid_url_list:
            ret = re.match(valid, current_path)
            if ret:
                return None

        permission_dict = request.session.get('permission', {})
        current_path = request.path_info

        user_id = request.session.get('user_id')
        if not user_id:
            return redirect("/login/")

        for item in permission_dict.values():
            urls = item['urls']
            for url in urls:

                reg = "^%s$" % url
                ret = re.match(reg, current_path)
                if ret:
                    request.actions = item['actions']
                    return None
      
        return HttpResponse('没有访问权限')
