# Author: harry.cai
# DATE: 2018/8/25

from django import template

register = template.Library()


@register.inclusion_tag("menu_html.html")
def get_menu(request):
    # 获取权限菜单
    print('menu')
    menu_list = request.session['menu']

    return {'menu_list': menu_list}