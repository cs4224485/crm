# Author: harry.cai
# DATE: 2018/8/20
import datetime
from .models import *
from stark.service import starkAdmin
from django.utils.safestring import mark_safe
from django.urls import path, re_path
from django.shortcuts import redirect,HttpResponse, render
starkAdmin.site.register(Department)
starkAdmin.site.register(Course)
starkAdmin.site.register(School)


class ConsultRecordConfig(starkAdmin.StarkModel):
    list_display = ['customer', 'consultant', 'date', 'note']


starkAdmin.site.register(ConsultRecord, ConsultRecordConfig)


class ClassListConfig(starkAdmin.StarkModel):
    list_display = ['school', 'course', 'teachers']


starkAdmin.site.register(ClassList, ClassListConfig)


class CustomerConfig(starkAdmin.StarkModel):

    def display_gender(self, obj=None, head=False):
        if head:
            return '性别'
        return obj.get_gender_display()

    def display_course(self, obj=None, head=False):
        '''
        自定制客户咨询课程显示标签
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return '咨询课程'
        course_list = obj.course.all()
        temp = []
        for course in course_list:

                tag = '<a style="border:1px solid #369; padding:3px 6px" href="cancel_course/%s/%s"><span>' \
                      '%s</span></a>' % (obj.pk, course.pk, course.name)
                temp.append(tag)
        return mark_safe(' '.join(temp))

    def cancel_course(self, request, customer_id, course_id):
        '''
        取消客户咨询课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        '''
        obj = Customer.objects.filter(pk=customer_id).first()
        obj.course.remove(course_id)
        _url = self.list_url()
        return redirect(_url)

    def extra_url(self):

        temp = []
        temp.append(re_path('cancel_course/(\d+)/(\d+)', self.cancel_course))
        temp.append(re_path('public/', self.public_customer))
        temp.append(re_path('further/(\d+)', self.further))
        temp.append(re_path("mycustomer", self.my_customer))
        return temp

    def public_customer(self, request):
        '''
        公共客户， 三天未跟进或者15天为成单转换为公共客户
        :return:
        '''

        from django.db.models import Q
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=3)

        customer_list = Customer.objects.filter(
            Q(last_consult_date__lt=now-delta_day3) |
            Q(recv_date__lt=now-delta_day15),
            status=2)
        return render(request, 'public.html', locals())

    def further(self, request, customer_id):
        user_id = 2  # 获取user_id request.session.get('user_id')
        # 为该客户更改课程顾问和对应的时间
        from django.db.models import Q
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=3)

        ret = Customer.objects.filter(pk=customer_id).filter(Q(last_consult_date__lt=now-delta_day3) | Q(recv_date__lt=now-delta_day15)).\
            update(consultant=user_id, last_consult_date=now, recv_date=now)
        if not ret:
            return HttpResponse('已经有人跟进！')
        CustomerDistribute.objects.create(customer_id=customer_id, consultant_id=user_id, date=now, status=1)

        return HttpResponse('确认跟进')

    def my_customer(self, request):
        '''
        查看当前登录用户下的客户
        :param request:
        :return:
        '''
        user_id = 2
        customer_distribute_list = CustomerDistribute.objects.filter(consultant_id=user_id)
        return render(request, 'my_customer.html', locals())

    list_display = ['name', display_gender, display_course]


starkAdmin.site.register(Customer, CustomerConfig)


class CourseRecordConfig(starkAdmin.StarkModel):

    def patch_study_record(self, query_set):
        '''
        批量生成上课记录
        :param query_set: 所有上课记录集合
        :return:
        '''
        temp = []
        for course_record_obj in query_set:
            student_list = Student.objects.filter(class_list__id=course_record_obj.class_obj.pk)
            for student_obj in student_list:
                obj = StudyRecord(student=student_obj, course_record=course_record_obj)
                temp.append(obj)
        StudyRecord.objects.bulk_create(temp)
        return HttpResponse('ok')

    def record(self, obj=None, head=False):
        '''
        过滤出当节课程相关的学习记录
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return '操作记录'
        return mark_safe("<a href='/stark/mycrm/studyrecord/?course_record=%s'>记录</a>" % obj.pk)

    def extra_url(self):
        temp = []
        temp.append(re_path("record_score/(\d+)", self.score))
        return temp

    def score(self, request, record_id):
        '''
        录入成绩功能
        :return:
        '''
        if request.method == "POST":
            print(request.POST)
            '''
            方式一
                for key, value in request.POST.items():
                    if key == "csrfmiddlewaretoken":
                        continue
                    field, pk = key.rsplit('_', 1)
                    if field == 'score':
                        StudyRecord.objects.filter(pk=pk).update(score=value)
                    elif field == "homework_note":
                        StudyRecord.objects.filter(pk=pk).update(homework_note=value)
            '''
            # 方式二 构建一个字典
            record_dic = {}
            for key, value in request.POST.items():
                for key, value in request.POST.items():
                    if key == "csrfmiddlewaretoken":
                        continue
                    field, pk = key.rsplit('_', 1)
                    if pk in record_dic:
                        record_dic[pk][field] = value
                    else:
                        record_dic[pk] = {field: value}

            for pk, update in record_dic.items():
                StudyRecord.objects.filter(pk=pk).update(**update)

            return redirect(request.path)
        study_record_list = StudyRecord.objects.filter(course_record=record_id)
        score_choices = StudyRecord.score_choices
        return render(request, 'score.html', locals())

    def record_score(self, obj=None, head=False):
        '''
        录入成绩
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return "录入成绩"
        return mark_safe("<a href='record_score/%s'>录入成绩</a>" % obj.pk)

    patch_study_record.short_description = '批量生成学习记录'
    list_display = ['class_obj', "day_num", 'teacher', record, record_score]
    actions = [patch_study_record]


starkAdmin.site.register(CourseRecord, CourseRecordConfig)


class StudyRecordConfig(starkAdmin.StarkModel):

    def patch_late(self,  queryset):
        queryset.update(record='late')
        return redirect(self.list_url())
    patch_late.short_description = '迟到'
    list_filter = ['course_record']
    list_display = ['student', 'course_record', 'record', 'score', ]
    actions = [patch_late]


starkAdmin.site.register(StudyRecord, StudyRecordConfig)


class StudentConfig(starkAdmin.StarkModel):

    def extra_url(self):
        temp = []
        temp.append(re_path(r"score_view/(\d+)", self.score_view))
        return temp

    def score_view(self, request, student_id):
        '''
        通过ajax显示每天每门课的成绩柱状图
        :param request:
        :param student_id:
        :return:
        '''
        if request.is_ajax():
            sid = request.GET.get("sid")
            cid = request.GET.get("cid")
            course_record_list = StudyRecord.objects.filter(student=sid, course_record__class_obj=cid)
            data_list = []
            for study_record in course_record_list:
                day_num = study_record.course_record.day_num
                data_list.append(["day%s" % day_num, study_record.score])
            from django.http import JsonResponse
            return JsonResponse(data_list, safe=False)
        student = Student.objects.filter(pk=student_id).first()
        class_list = student.class_list.all()

        return render(request, 'student_score.html', locals())

    def score_show(self, obj=None, head=False):
        '''
        查看学生成绩
        :param obj:
        :param head:
        :return:
        '''
        if head:
            return "查看成绩"
        return mark_safe("<a href='score_view/%s'>查看成绩</a>" % obj.pk)
    list_display = ['customer', 'class_list', score_show]


starkAdmin.site.register(Student, StudentConfig)
starkAdmin.site.register(UserInfo)


