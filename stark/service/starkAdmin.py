# Author: harry.cai
# DATE: 2018/8/6
from django.urls import re_path, reverse
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.db.models import Q, ForeignKey, ManyToManyField
from .page import Pagination


class ShowList(object):
    def __init__(self, request, data_list, config):
        self.request = request
        self.data_list = data_list
        self.config = config
        # 获取当前页
        current_page = self.request.GET.get('page', 1)
        # 数据总量
        data_count = self.data_list.count()
        # 请求的URL
        base_url = self.request.path
        # 分页功能
        self.pager = Pagination(data_count, current_page, self.request.GET, base_url, per_page=10, max_show=10)
        try:
            self.page_data = self.data_list[self.pager.start:self.pager.end]
        except Exception as e:
            self.page_data = []

    def get_header(self):
        # 构建表头
        header_list = []
        for field in self.config.get_new_list_display():
            # 如果字段是一个函数，那么执行这个函数
            if callable(field):
                val = field(self, head=True)
                header_list.append(val)
            else:
                if field == '__str__':
                    header_list.append(self.config.model._meta.model_name.upper())
                else:
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)
        return header_list

    def get_list(self):
        # 构建表数据
        data = []
        for obj in self.page_data:
            temp = []
            for filed in self.config.get_new_list_display():
                if callable(filed):
                    value = filed(self.config, obj)
                else:
                    try:   # 如果filed __str__ 需要捕捉异常处理
                        field_obj = self.config.model._meta.get_field(filed)

                        # 多对多字段展示方法
                        if isinstance(field_obj, ManyToManyField):
                            ret = getattr(obj, filed).all()
                            t = []
                            for mobj in ret:
                                t.append(str(mobj))
                            value = ",".join(t)
                        else:
                            # 捕获choices字段
                            if field_obj.choices:
                                value = getattr(obj, "get_"+filed+"_display")
                            else:
                                value = getattr(obj, filed)
                            # 如果字段是一个link类型字段那么给它构建一个a标签
                            if filed in self.config.list_display_links:
                                _url = self.config.change_url(obj)
                                value = mark_safe("<a href='%s'>%s</a>" % (_url, value))
                    except Exception:
                        value = getattr(obj, filed)
                temp.append(value)
            data.append(temp)

        return data

    def get_actions(self):
        '''
        构建actions
        :return:
        '''
        temp = []
        for action in self.config.actions:
            temp.append({
                'name': action.__name__,
                'desc': action.short_description
            })
        return temp

    def get_filter_link_tags(self):
        '''
        根据字段构建过滤a标签
        :return: 构建后的标签
        '''
        link_dic ={}
        import copy
        for filter_field in self.config.list_filter:
            params = copy.deepcopy(self.request.GET)
            cid = self.request.GET.get(filter_field, 0)
            filter_field_obj = self.config.model._meta.get_field(filter_field)

            # 处理普通字段
            if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                data_list = filter_field_obj.related_model.objects.all()
            else:
                data_list = self.config.model.objects.all()
            temp = []

            # 处理全部内容标签
            if params.get(filter_field):
                del params[filter_field]
                temp.append("<a href='?%s'>全部内容</a>" % params.urlencode())
            else:
                temp.append("<a href='?%s'>全部内容</a>" % params.urlencode())
            # 构建标签
            for obj in data_list:
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    val = obj.pk
                    text = str(obj)
                else:
                    val = getattr(obj, filter_field)
                    text = getattr(obj, filter_field)

                params[filter_field] = str(val)

                _url = params.urlencode()
                if cid == str(val) or cid == text:
                    link_tag = "<a class='active' href='?%s'>%s</a>" % (_url, text)
                else:
                    link_tag = "<a href='?%s'>%s</a>" % (_url, str(obj))
                temp.append(link_tag)
            link_dic[filter_field] = temp
        return link_dic


class StarkModel(object):
    list_display = ['__str__']
    list_display_links = []
    search_field = []
    actions = []
    keyword = ''
    model_form = None
    list_filter = []

    def __init__(self, model, site):
        self.model = model
        self.site = site


    @property
    def deep_urls(self):
        return self.get_deep_urls(), None, None

    def get_deep_urls(self):
        temp = []
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        temp.append(re_path(r"^add", self.add, name="%s_%s_add" % (app_label, model_name)))
        temp.append(re_path(r"^(\d+)/delete/", self.delete, name="%s_%s_delete" % (app_label, model_name)))
        temp.append(re_path(r"^(\d+)/change/", self.change, name="%s_%s_change" % (app_label, model_name)))
        temp.append(re_path(r"^$", self.list_view, name="%s_%s_list" % (app_label, model_name)))
        temp.extend(self.extra_url())

        return temp

    def get_new_form(self, form):
        for bfield in form:
            print(bfield.field)  # 字段对象
            print("name", bfield.name)  # 字段名（字符串）
            print(type(bfield.field))  # 字段类型
            from django.forms.models import ModelChoiceField
            if isinstance(bfield.field, ModelChoiceField):
                try:
                    bfield.is_pop = True
                    related_model_name = bfield.field.queryset.model._meta.model_name
                    related_app_label = bfield.field.queryset.model._meta.app_label
                    _url = reverse("%s_%s_add" % (related_app_label, related_model_name))
                    bfield.url = _url + "?pop_res_id=id_%s" % bfield.name
                except Exception:
                    pass

        return form

    def add(self, request):
        '''
        添加数据功能
        :param request:
        :return:
        '''
        model_form_class = self.get_model_form()
        form = model_form_class()
        new_form = self.get_new_form(form)
        self.get_new_form(form)
        if request.method == "POST":
            form = model_form_class(request.POST)
            if form.is_valid():
                obj = form.save()
                pop_res_id = request.GET.get("pop_res_id")
                if pop_res_id:
                    res = {'pk': obj.pk, 'text': str(obj), 'response_id': pop_res_id}
                    return render(request, 'pop.html', {'res':res})
                else:
                    _url = self.list_url()
                    return redirect(_url)

        return render(request, 'add_view.html', locals())

    def delete(self, request, nid):
        url = self.list_url()
        if request.method == 'POST':
            self.model.objects.filter(pk=nid).delete()
            return redirect(url)
        return render(request, 'deltet.html', locals())

    def list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list" % (app_label, model_name))
        return _url

    def change_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change" % (app_label, model_name),args=(obj.pk,))
        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_add" % (app_label, model_name))
        return _url

    def extra_url(self):
        return []

    def edit(self, obj=None, head=False):
        '''
        构建编辑a标签
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return "操作"
        _url = self.change_url(obj)
        return mark_safe("<a href=%s>编辑</a>" % _url)

    def choice(self, obj=None, head=False):
        '''
        构建checkbox标签
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return mark_safe("<input class='choice_all' type='checkbox'></input>")
        return mark_safe("<input class='choice_item' type='checkbox' name='selected_pk' value='%s'></input>" % obj.pk)

    def delete_item(self, obj=None, head=False):
        '''
        构建删除标签
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return "删除"
        _url = self.get_delete_url(obj)
        return mark_safe("<a href=%s>删除</a>" % _url)

    def get_new_list_display(self):
        temp = []
        temp.append(StarkModel.choice)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(StarkModel.edit)
        temp.append(StarkModel.delete_item)
        return temp

    def search_condition(self, request):
        '''
        搜索条件过滤
        :param request:
        :return:
        '''
        keyword = request.GET.get('q', '')
        self.keyword = keyword
        q_search = Q()
        if keyword:
            q_search.connector = 'or'
            for field in self.search_field:
                q_search.children.append((field + '__contains', keyword))

        return q_search

    def filter_condition(self, request):
        '''
        根据字段条件进行过滤
        :param request:
        :return:
        '''
        q_filter = Q()
        for field, val in request.GET.items():
            if field != 'page':
                q_filter.children.append((field, val))

        return q_filter

    def get_model_form(self):
        '''
        构建一个model from类
        :return:
        '''
        if self.model_form:
            return self.model_form
        else:
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
            return ModelFormDemo

    def list_view(self, request):
        '''
        查看页面
        :param request:
        :return:
        '''
        if request.method == 'POST':
            action_name = request.POST.get('actions')
            select_pk = request.POST.getlist('selected_pk')
            action_fun = getattr(self, action_name)
            query_set = self.model.objects.filter(pk__in=select_pk)
            ret = action_fun(query_set)
            return ret
        # 搜索
        search_condition = self.search_condition(request)

        # 过滤
        filter_condition = self.filter_condition(request)

        data_list = self.model.objects.filter(search_condition).filter(filter_condition)
        show_list_obj = ShowList(request, data_list, self)
        header_list = show_list_obj.get_header()

        add_url = self.get_add_url()
        return render(request, "lisv_view.html", locals())

    def change(self, request, nid):
        '''
        编辑页面
        :param request:
        :param nid:
        :return:
        '''
        model_form_class = self.get_model_form()
        edit_obj = self.model.objects.filter(pk=nid).first()
        form = model_form_class(instance=edit_obj)
        if request.method == "POST":
            form = model_form_class(request.POST, instance=edit_obj)
            if form.is_valid():
                obj = form.save()
                _url = self.list_url()
                return redirect(_url)
            return render(request, 'edit_view.html', locals())
        return render(request, 'edit_view.html', locals())


class StarkSite(object):
    def __init__(self):
        self.registry = {}

    def register(self, model, stark_class=None):
        if not stark_class:
            stark_class = StarkModel
        self.registry[model] = stark_class(model, self)

    @property
    def urls(self):
        return self.get_urls(), None, None

    def get_urls(self):
        temp = []
        for model, stark_class_obj in self.registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            temp.append(re_path(r'^%s/%s/' % (app_label, model_name), stark_class_obj.deep_urls))
        return temp


site = StarkSite()
