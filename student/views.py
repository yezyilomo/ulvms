from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import pyexcel
from universityloanoffice.models import User
from aris.models import Student
from universityloanoffice.models import Student as Loanbeneficiary
from universityloanoffice.models import SigningSession

# Create your views here.

def permit_student(function):
    def wrap(request, *args, **kwargs):
        if request.user.role != "student":
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

@permit_student
@login_required
def profile(request):
    user=User.objects.get(id=request.session['_auth_user_id'])
    if '_auth_user_id' in request.session and user.role=='student':
        reg_no=user.username
        student=Student.objects.get(reg_no=reg_no)
        loanbeneficiary=Loanbeneficiary.objects.get(reg_no=reg_no)
        web_notification=""
        if SigningSession.objects.filter(student=loanbeneficiary, status="unsigned"):
            with open("universityloanoffice/files/notifications/web_notification", "r") as f:
                web_notification=f.read()
        return render(request, 'student.html', {'student': student, 'loanbeneficiary': loanbeneficiary, 'web_notification': web_notification})
    else:
        raise Http404('Not allowed')

def logoutuser(request):
    logout(request)
    return redirect('/')
