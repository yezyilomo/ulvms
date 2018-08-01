from django.shortcuts import render
from aris.models import Student
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
import random
# Create your views here.

def paginate(data, page_num, request):
    paginator = Paginator(data, page_num)
    page = request.GET.get('page')
    paginateddata = paginator.get_page(page)
    return paginateddata

def students(request):
    all_students=Student.objects.all()
    students=paginate(all_students, 13, request)
    return render(request, "student_list.html", {'students': students})

def toggle_status(request):
    reg_no=request.GET['reg_no']
    STATUS_CHOICES = ['discontinued', 'continuous', 'postponed', 'completed']
    student=Student.objects.filter(reg_no=reg_no)
    if student.count() == 1:
        student= student.get()
        current_status=student.status
        STATUS_CHOICES.remove(current_status)
        new_status=random.choice(STATUS_CHOICES)
        student.status=new_status
        student.save()
        return HttpResponse(new_status)
    return HttpResponse()

def get_status(request):
    reg_no=request.GET['reg_no']
    student=Student.objects.filter(reg_no=reg_no)
    if student.count() == 1:
        student= student.get()
        return HttpResponse(student.status)
