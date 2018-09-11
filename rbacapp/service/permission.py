# Author: harry.cai
# DATE: 2018/7/31


def initial_session(user,  request):
    '''
    初始化session 把用户拥有的权限放到session
    :param user:
    :param request:
    :return:
    '''

    permissions = user.roles.all().values("permissions__url", "permissions__group_id", 'permissions__action')

    permission_dict = {}
    for item in permissions:
        gid = item.get('permissions__group_id')
        if gid not in permission_dict:
            permission_dict[gid] = {
                'urls': [item['permissions__url'], ],
                "actions": [item['permissions__action'], ]
            }
        else:
            permission_dict[gid]['urls'].append(item['permissions__url'])
            permission_dict[gid]['actions'].append(item['permissions__action'])

    permission_menu = user.roles.all().values("permissions__url", "permissions__title", 'permissions__action')
    menu = []
    for item in permission_menu:
        if item["permissions__action"] == "list":
            menu.append((item["permissions__url"], item["permissions__title"]))

    request.session['menu'] = menu
    request.session['permission'] = permission_dict