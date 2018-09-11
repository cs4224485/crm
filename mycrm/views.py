from django.shortcuts import render,HttpResponse
from .models import *
from rbacapp.models import *
from rbacapp.service.permission import initial_session
# Create your views here.


def login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(name=username, pwd=password).first()
        if user_obj:
            request.session['user_id'] = user_obj.pk
            initial_session(user_obj, request)
            return HttpResponse('登录成功')
    return render(request, 'login.html')
