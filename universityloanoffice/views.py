import os
import random
import time
import mimetypes
import json
import barcode
import pyexcel
import threading
import requests
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.staticfiles.views import serve
from django.core.exceptions import PermissionDenied
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from universityloanoffice.models import User
from student import views as student
from loanboard import views as loanboard
from universityloanoffice.models import Student as Loanbeneficiary
from universityloanoffice.models import SigningSession
from aris.models import Student, College, Degree;


################### Filling data backup ################################################
def filldata(request):
    filldata1() #Fill Colleges
    filldata2() #Fill Course
    filldata3() #Fill Students
    #filldata4()
    filldata5()  #Fill users
    requests.get("http://127.0.0.1:8000/loanboard/fill-data/")
    return HttpResponse("Data filled successfully!")

def filldata4():
    fs = FileSystemStorage('universityloanoffice/files')
    file_name=fs.path('')+'/'+'data2.xls'
    fl=pyexcel.iget_records(file_name=file_name)
    loanbeneficiary=None;
    for record in fl:
        if record['Registration Number'] != "" and not Loanbeneficiary.objects.filter(reg_no=record['Registration Number']):
            loanbeneficiary=Loanbeneficiary(
                reg_no=record['Registration Number'],
                form_four_index_no=record['F4Index'],
                status=Student.objects.get(reg_no=record['Registration Number']).status,
                account_no=record['account number'],
                bank_name=record['Bank name'],
                tuition_fee=record['Tuition fee'],
                accomodation=record['Accommodation'],
                special_faculty=record['special faculty'],
                field=record['field'],
                project_and_research=record['project and reseach']
            )
            loanbeneficiary.save()
    return True

def filldata3():
    fs = FileSystemStorage('universityloanoffice/files')
    file_name=fs.path('')+'/'+'data.xls'
    fl=pyexcel.iget_records(file_name=file_name)
    university_student=None;
    for record in fl:
        if record['Registration Number'] != "" and not Student.objects.filter(reg_no=record['Registration Number']):
            university_student=Student(
                reg_no=record['Registration Number'],
                first_name=record['First Name'],
                middle_name=record['Middle Name'],
                last_name=record['Last Name'],
                form_four_index_no=record['F4Index'],
                year_of_study=record['yos'],
                programe_name=Degree.objects.get(programe_name=record['Course']),
                status=record['Status'],
                gender=record['gender'],
            )
            university_student.save()
    return True

def filldata2():
    fs = FileSystemStorage('universityloanoffice/files')
    file_name=fs.path('')+'/'+'data.xls'
    fl=pyexcel.iget_records(file_name=file_name)
    degree=None;
    for record in fl:
        if record['Course'] != "" and not Degree.objects.filter(programe_name=record['Course']):
            degree=Degree(
                programe_name=record['Course'],
                tuition_fee=1500000,
                college_name=College.objects.get(college_name=record['College'])
            )
            degree.save()
    return True

def filldata1():
    fs = FileSystemStorage('universityloanoffice/files')
    file_name=fs.path('')+'/'+'data.xls'
    fl=pyexcel.iget_records(file_name=file_name)
    college=None;
    for record in fl:
        if record['College'] != "" and not College.objects.filter(college_name=record['College']):
            college=College(
                college_name=record['College'],
            )
            print(record['Course'])
            college.save()
    return True
################################### End of data filling #############################################

############################### Creating all important users ############################################
def create_user(*args):
    user=User.objects.create_user(args[0], args[1], args[2])
    user.role=args[3]
    user.save()


def filldata5():
    if not User.objects.filter(username='uloanofficer'):
        create_user('uloanofficer', 'uloanofficer@gmail.com', 'staffuserone', 'universityloanofficer')
    if not User.objects.filter(username='lbloanofficer'):
        create_user('lbloanofficer', 'lbloanofficer@gmail.com', 'staffusertwo', 'loanboardofficer')
    superusers=User.objects.filter(is_superuser='t')
    if superusers:
        for superuser in superusers:
            superuser.role='superuser'
            superuser.save()

    students=Loanbeneficiary.objects.all()
    for std in students:
        std=Student.objects.filter(reg_no=std.reg_no)
        create_user(std.get().reg_no, std.get().first_name+"@"+'gmail.com', 'studentpassword', 'student')
    return True;
################################### End of creating users #################################################

def permit_uloanofficer(function):
    def wrap(request, *args, **kwargs):
        if request.user.role != "universityloanofficer":
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def home(request):
    if '_auth_user_id' in request.session:
        user_role=request.user.role
        if user_role=='student':
            return redirect('/student/profile')
        elif user_role=='universityloanofficer':
            return redirect('university/profile')
        elif user_role=='loanboardofficer':
            return redirect('/loanboard/profile')
        elif user_role=='superuser':
            return redirect('/admin')
        else:
            raise Http404('Invalid user')
    else:
        return redirect('/login')

def loginpage(request):
    message=""
    return render(request, 'login.html', {'message': message})

def processlogin(request):
    if request.method != 'POST':
        raise PermissionDenied

    username=request.POST['username']
    password=request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        user_role=User.objects.get(username=username).role
        if user_role=='student':
            return redirect('/student/profile')
        elif user_role=='universityloanofficer':
            return redirect('/university/profile')
        elif user_role=='loanboardofficer':
            return redirect('/loanboard/profile')
        elif user_role=='superuser':
            return redirect('/admin')
        else:
            raise Http404('Invalid user')
    else:
        message='Wrong credentials. Please check your credentials and try again.'
        templete_data={
        'message': message,
        }
        return render(request, 'login.html', templete_data)

@permit_uloanofficer
@login_required
def profile(request):
    user_role=User.objects.get(id=request.session['_auth_user_id']).role
    if user_role=='universityloanofficer':
        fs = FileSystemStorage('universityloanoffice/files/signing')
        files=fs.listdir('')[1]
        notification=0
        for file in files:
            if file.startswith('New_'):
                notification+=1

        data=SigningSession.objects.all()
        signed_num=SigningSession.objects.filter(status='signed').count()
        unsigned_num=SigningSession.objects.filter(status='unsigned').count()
        complete=Loanbeneficiary.objects.filter(status="completed").count()
        changes=status_changes()
        manage_notfication=bool(complete or changes)
        file_names=FileSystemStorage('universityloanoffice/files/initial').listdir('')[1]
        count_new_initial_files=len( list( filter(lambda a: a.startswith("New_"), file_names) ) )

        continuous=Loanbeneficiary.objects.filter(status="continuous").count()
        discontinued=Loanbeneficiary.objects.filter(status="discontinued").count()
        postpone=Loanbeneficiary.objects.filter(status="postponed").count()

        templete_data={
        'notification': notification,
        'data': data,
        'signed_num': signed_num,
        'unsigned_num': unsigned_num,
        'manage_notfication': manage_notfication,
        'initial_notfication': count_new_initial_files,
        'continuous': continuous,
        'discontinued': discontinued,
        'postpone': postpone,
        'complete': complete,
        }
        return render(request, 'loanofficer.html', templete_data)
    else:
        raise Http404('Page does not exist')

def logoutuser(request):
    logout(request)
    return redirect('/')

@permit_uloanofficer
@login_required
def notifications(request):
    user_role=User.objects.get(id=request.session['_auth_user_id']).role
    if user_role=='universityloanofficer':
        fs = FileSystemStorage('universityloanoffice/files/signing')
        files=sorted(Path(fs.path('')).iterdir(), key=lambda f: f.stat().st_mtime)
        notification=0
        for fl in files:
            if fl.name.startswith('New_'):
                os.rename(fl, fs.path('')+'/'+fs.get_available_name(fl.name[4:]) )

        files=filter(
        lambda a: not a.name.startswith(".") and a.is_file(),
        sorted(Path(fs.path('')).iterdir(), key=lambda f: f.stat().st_mtime)
        )
        files = paginate(list(files), 13, request)
        templete_data={
        'notification': notification,
        'files': files
        }
        return render(request, 'uninotifications.html', templete_data)
    else:
        raise Http404('Page does not exist')

def excel_data(file_path):
    fl=pyexcel.get_book_dict(file_name=file_path)
    data=None
    for sheet in fl:
        if isinstance(fl[sheet], list):
               data=fl[sheet]
    return data

@permit_uloanofficer
@login_required
def showfile(request, file_name):
    fs = FileSystemStorage('universityloanoffice/files/')
    file_path=fs.path('')+'/'+file_name
    data=excel_data(file_path)
    templete_data={
    'data':data,
    'filename': file_name.split("/")[1],
    }
    return render(request, 'unifile.html', templete_data)

@permit_uloanofficer
@login_required
def searchstudent(request):
    if request.method == 'POST':
        reg_no = request.POST['reg_no']
        try:
            student=Student.objects.get(reg_no=reg_no)
            loanbeneficiary=Loanbeneficiary.objects.get(reg_no=reg_no)
        except Exception as e:
            student=False
            loanbeneficiary=False
        templete_data={
        'student': student,
        'loanbeneficiary': loanbeneficiary,
        }
        return render(request, 'student_profile.html', templete_data)

@permit_uloanofficer
@login_required
def signing_progress(request):
    data=SigningSession.objects.all().order_by("student")
    signed_num=SigningSession.objects.filter(status='signed').count()
    unsigned_num=SigningSession.objects.filter(status='unsigned').count()
    data = paginate(data, 10, request)
    templete_data={
    'data': data,
    'signed_num': signed_num,
    'unsigned_num': unsigned_num,
    }
    return render(request, 'signing_progress.html', templete_data )

@permit_uloanofficer
@login_required
def toggle_signing_status(request, reg_no):
    record=SigningSession.objects.get(student=Loanbeneficiary.objects.get(reg_no=reg_no))
    if record.status=="signed":
        record.status="unsigned"
    else:
        record.status="signed"
    record.save()
    return redirect('/university/signing-progress')

@csrf_exempt
def sign(request):
    if request.method != 'POST':
        return HttpResponse("Invalid http method")

    reg_no=request.POST['barcode_id']
    try:
        c_std=Student.objects.get(reg_no=reg_no)
        std_name=c_std.first_name+"  "+c_std.middle_name+"  "+c_std.last_name
    except Exception as e:
        std_name=""
    try:
        record=SigningSession.objects.get(student=Loanbeneficiary.objects.get(reg_no=reg_no))

    except Exception as e:
        response=JsonResponse({'message': 'Sorry you are not allowed to sign', 'reg_no': reg_no, 'name': std_name})
        return response

    if record.status=="signed":
        response=JsonResponse({'message': 'You have signed already', 'reg_no': reg_no, 'name': std_name})
        return response
    else:
        record.status="signed"
        record.save()
        response=JsonResponse({'message': 'You have signed successfully', 'reg_no': reg_no, 'name': std_name})
        return response

@permit_uloanofficer
@login_required
def import_for_signing(request, file_name):
    if SigningSession.objects.all().count() != 0:
        raise Exception("Export first before importing!...")

    fs = FileSystemStorage('universityloanoffice/files/signing')
    file_name=fs.path('')+'/'+file_name
    fl=pyexcel.iget_records(file_name=file_name)
    for record in fl:
        if record['Registration Number'] != "":
            try:
                std=Loanbeneficiary.objects.get(reg_no=record['Registration Number'])
                signature_id=Student.objects.get(reg_no=record['Registration Number'])
            except Exception as e:
                continue
            session=SigningSession(student=std, signature_id=signature_id, status='unsigned')
            session.save()

            sendingemailthread=threading.Timer(0, sendemails)
            sendingemailthread.start()
    return redirect('/university/signing-progress')

def sendemails():
    email_content=""
    web_notification=""
    with open("universityloanoffice/files/notifications/email", "r") as f:
        email_content=f.read()
    with open("universityloanoffice/files/notifications/web_notification", "r") as f:
        web_notification=f.read()
    session=SigningSession.objects.all()
    emails=['yezileliilomo@gmail.com',]
    for std in session:
        if std.signature_id.email:
            emails.append(std.signature_id.email)
    send_email('yezileliilomo@hotmail.com', emails, 'University Loan Office', email_content)

def serve_file(file_full_path, ):
    with open(file_full_path,'rb') as f:
        data = f.read()
    response = HttpResponse(data, content_type=mimetypes.guess_type(file_full_path)[0])
    response['Content-Disposition'] = "attachment; filename={0}".format("Ulvms_file.xls")
    response['Content-Length'] = os.path.getsize(file_full_path)
    return response

def export_file(export_criteria):
    req_data=None
    if export_criteria=='all':
        req_data=SigningSession.objects.filter()
    else:
        req_data=SigningSession.objects.filter(status=export_criteria)

    file_name='universityloanoffice/files/exported/emptyfile.xls'
    sheet = pyexcel.get_sheet(file_name=file_name, name_columns_by_row=0)
    sheet.row += ['First Name', 'Middle Name', 'Last Name', 'Registration Number', 'Bank Account Number', 'Bank Name', 'Amount']
    for std in req_data:
        stdnt=std.signature_id
        sheet.row += [
            stdnt.first_name,
            stdnt.middle_name,
            stdnt.last_name,
            stdnt.reg_no,
            std.student.account_no,
            std.student.bank_name,
            std.student.accomodation,
        ]
    sheet.save_as("universityloanoffice/files/exported/exported_sheet.xls")
    return True

@permit_uloanofficer
@login_required
def export_signed(request):
    if not export_file('signed'):
        raise("Error during export!..")
    fs = FileSystemStorage('universityloanoffice/files/exported')
    file_full_path=fs.path('')+'/'+'exported_sheet.xls'
    return serve_file(file_full_path)

@permit_uloanofficer
@login_required
def export_unsigned(request):
    if not export_file('unsigned'):
        raise("Error during export!..")
    fs = FileSystemStorage('universityloanoffice/files/exported')
    file_full_path=fs.path('')+'/'+'exported_sheet.xls'
    return serve_file(file_full_path)

@permit_uloanofficer
@login_required
def export_all(request):
    if not export_file('all'):
        raise("Error during export!..")
    fs = FileSystemStorage('universityloanoffice/files/exported')
    file_full_path=fs.path('')+'/'+'exported_sheet.xls'
    return serve_file(file_full_path)

@permit_uloanofficer
@login_required
def end_signing_session(request):
    data=SigningSession.objects.all()
    data.delete()
    return redirect('/')

@permit_uloanofficer
@login_required
def fill_random_data(request):
    data=SigningSession.objects.all()
    for record in data:
        record.status=random.choice(['signed', 'unsigned'])
        record.save()
    return redirect('/university/signing-progress')

@permit_uloanofficer
@login_required
def send_updates(request):
    reg_nos=Loanbeneficiary.objects.all()
    req_data=Student.objects.filter(reg_no__in=reg_nos)
    file_name='universityloanoffice/files/exported/emptyfile.xls'
    sheet = pyexcel.get_sheet(file_name=file_name, name_columns_by_row=0)
    sheet.row += ['First Name', 'Middle Name', 'Last Name', 'Registration Number', 'Form 4 Index Number', 'Status']
    for stdnt in req_data:
        sheet.row += [
            stdnt.first_name,
            stdnt.middle_name,
            stdnt.last_name,
            stdnt.reg_no,
            stdnt.form_four_index_no,
            stdnt.status,
        ]
    fs = FileSystemStorage('loanboard/files')
    sheet.save_as("loanboard/files/"+fs.get_available_name("New_exported_sheet.xls") )
    return render(request, 'file_sending_response.html')

def paginate(data, page_num, request):
    paginator = Paginator(data, page_num)
    page = request.GET.get('page')
    paginateddata = paginator.get_page(page)
    return paginateddata

@permit_uloanofficer
@login_required
def aggregate_info(request, status):
    reg_nos=Loanbeneficiary.objects.all().values_list('reg_no')
    if status=='all':
        req_data=Student.objects.filter(reg_no__in=reg_nos)
    else:
        req_data=Student.objects.filter(reg_no__in=reg_nos, status=status)
    data = paginate(req_data, 12, request)
    templete_data={
    'beneficiaries': data,
    }
    return render(request,'loanbeneficiary_updates.html', templete_data )

def status_changes():
    list_to_be_updated=[]
    loanbeneficiary=Loanbeneficiary.objects.all()
    for std in loanbeneficiary:
        if std.status != Student.objects.get(reg_no=std.reg_no).status:
            list_to_be_updated.append( ( std, Student.objects.get(reg_no=std.reg_no) ) ) #Loanbeneficiary_info, Student_info
    return list_to_be_updated

@permit_uloanofficer
@login_required
def manage_loanbeneficiary(request):
    complete_loanbeneficiary=Loanbeneficiary.objects.filter(status="completed")
    reg_nos=Loanbeneficiary.objects.all().values_list('reg_no')
    req_data=Student.objects.filter(reg_no__in=reg_nos)
    continuous=Loanbeneficiary.objects.filter(status="continuous").count()
    discontinued=Loanbeneficiary.objects.filter(status="discontinued").count()
    postpone=Loanbeneficiary.objects.filter(status="postponed").count()
    complete=complete_loanbeneficiary.count()
    req_data = paginate(req_data, 10, request)

    templete_data={
    'updates': status_changes(),
    'complete_loanbeneficiary': complete_loanbeneficiary,
    'beneficiaries': req_data,
    'continuous': continuous,
    'discontinued': discontinued,
    'postpone': postpone,
    'complete': complete,
    }
    update_status(request, 'all')
    #delete_students_with_complete_status(request, 'all')
    return render(request, 'manage_loanbeneficiary.html', templete_data)

@permit_uloanofficer
@login_required
def view_changes(request):
    templete_data={
    'updates': status_changes()
    }
    return render(request, 'view_updates.html', templete_data)

@permit_uloanofficer
@login_required
def update_status(request, reg_no):
    if reg_no=="all":
        for lbfry, std in status_changes():
            lbfry.status=std.status
            lbfry.save()
    else:
        beneficiary=Loanbeneficiary.objects.get(reg_no=reg_no)
        beneficiary.status=Student.objects.get(reg_no=reg_no).status
        beneficiary.save()
    templete_data={
    'updates': status_changes(),
    }
    return render(request, 'view_updates.html', templete_data)

@permit_uloanofficer
@login_required
def randomize_student_status(request):
    stds=Student.objects.all()
    for std in stds:
        std.status=random.choice(['discontinued', 'continuous', 'postponed', 'completed' ])
        std.save()
    return HttpResponse("Status randomized successfully!..")

def complete():
    list_to_be_deleted=[]
    loanbeneficiary=Loanbeneficiary.objects.filter(status="completed")
    for std in loanbeneficiary:
        if std.status == Student.objects.get(reg_no=std.reg_no).status:
            list_to_be_deleted.append( ( std, Student.objects.get(reg_no=std.reg_no) ) ) #Loanbeneficiary_info, Student_info
    return list_to_be_deleted

@permit_uloanofficer
@login_required
def view_complete(request):
    templete_data= {
    'complete_loanbeneficiary': complete(),
    }
    return render(request, 'view_complete.html', templete_data)

@permit_uloanofficer
@login_required
def delete_students_with_complete_status(request, reg_no):
    if reg_no=="all":
        complete_loanbeneficiary=Loanbeneficiary.objects.filter(status="completed")
        for user in complete_loanbeneficiary:
            usr=User.objects.filter(username=user.reg_no)
            usr.delete()
        complete_loanbeneficiary.delete()
    else:
        complete_loanbeneficiary=Loanbeneficiary.objects.filter(status="completed", reg_no=reg_no)
        usr=User.objects.filter(username=reg_no)
        usr.delete()
        complete_loanbeneficiary.delete()
    return redirect("/university/view-complete")

@permit_uloanofficer
@login_required
def view_initial_import(request):
    fs = FileSystemStorage('universityloanoffice/files/initial')
    file_names=fs.listdir('')[1]
    count_new_initial_files=len( list( filter(lambda a: a.startswith("New_"), file_names) ) )
    files=filter( lambda a: not a.name.startswith(".") and a.is_file(), sorted(Path(fs.path('')).iterdir(), key=lambda f: f.stat().st_mtime) )
    files_with_time=[]
    for fl in files:
        tm=time.ctime( fl.stat().st_mtime )
        files_with_time.append(type('File', (object,), dict(file_obj=fl, time_sent=tm)) )
    templete_data={
    'initial_num': count_new_initial_files,
    'initial_files': files_with_time,
    }
    return render(request, 'import_initial.html', templete_data )

@permit_uloanofficer
@login_required
def show_initial_file(request, file_name):
    fs = FileSystemStorage('universityloanoffice/files/initial')
    file_path=fs.path('')+'/'+file_name
    data=excel_data(file_path)
    templete_data={
    'data':data,
    }
    return render(request, 'unifile.html', templete_data)

@permit_uloanofficer
@login_required
def import_initial_beneficiaries(request, file_name):
    fs = FileSystemStorage('universityloanoffice/files/initial')
    file_path=fs.path('')+'/'+file_name
    fl=pyexcel.iget_records(file_name=file_path)
    loanbeneficiary=None;
    for record in fl:
        if Student.objects.filter(reg_no=record['Registration Number']) and not Loanbeneficiary.objects.filter(reg_no=record['Registration Number']):
            loanbeneficiary=Loanbeneficiary(
                reg_no=record['Registration Number'],
                form_four_index_no=record['F4Index'],
                status=Student.objects.get(reg_no=record['Registration Number']).status,
                account_no=record['account number'],
                bank_name=record['Bank name'],
                tuition_fee=record['Tuition fee'],
                accomodation=record['Accommodation'],
                special_faculty=record['special faculty'],
                field=record['field'],
                project_and_research=record['project and reseach']
            )
            loanbeneficiary.save()
    if file_name.startswith("New_"):
        os.rename(file_path, fs.path('')+'/'+fs.get_available_name(file_name[4:]) )
    return redirect("/university/inital-import-status")

@csrf_exempt
def receive_barcode(request):
    if request.method != 'POST':
        print("This page accept only POST requests!...")
        return HttpResponse("Invalid request method!...")

    barcode_id=request.POST['barcode_id']
    current_time=request.POST['current_time']
    print("********************")
    print("Scanned barcode is:   "+barcode_id)
    print("Time to scan barcode is:  "+current_time)
    print("********************")
    return HttpResponse("Sent")

def ajax(request):
    fs = FileSystemStorage('universityloanoffice/files/signing')
    file_names=fs.listdir('')[1]
    notification=len( list( filter(lambda a: a.startswith("New_"), file_names) ) )
    return HttpResponse(notification)

@permit_uloanofficer
@login_required
def get_signing_status(request, reg_no):
    record=SigningSession.objects.get(student=Loanbeneficiary.objects.get(reg_no=reg_no))
    return HttpResponse(record.status)


def get_signing_progress(request):
    signed_num=SigningSession.objects.filter(status='signed').count()
    unsigned_num=SigningSession.objects.filter(status='unsigned').count()
    templete_data={
    'signed_num': signed_num,
    'unsigned_num': unsigned_num,
    }
    return HttpResponse(json.dumps(templete_data))

@permit_uloanofficer
@login_required
def generate_barcode(request):
    stds=SigningSession.objects.all().values_list('student')
    print(stds)
    for i, std in enumerate(stds):
        bc=barcode.get('code128', std[0])
        bc.save("/home/yezy/Desktop/.security/sss/barcode"+str(i))
    return HttpResponse("All barcodes generated!..")

def smtp_server(host, email, password, port):
    server = smtplib.SMTP(host)
    server.connect(host, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email, password)
    return server

def send_email(frm, to, subject, message):
    server=smtp_server('smtp.live.com', 'yezileliilomo@hotmail.com', '1234yezy', 587)
    msg = MIMEMultipart()
    msg['From'] = frm
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    for destination in to:
        msg['To']=destination
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

@permit_uloanofficer
@login_required
def send_massmail(request):
    send_email('yezileliilomo@hotmail.com', ['yezileliilomo@gmail.com',], "About Signing Boom", "Boom is ready!...")
    return HttpResponse("Sent successfully!...")

@permit_uloanofficer
@login_required
def email_configuration(request):
    with open("universityloanoffice/files/notifications/email", "r") as f:
        email_content=f.read()
        return render(request, "email_configuration.html", {'current_content': email_content} )

@permit_uloanofficer
@login_required
def configure_email(request):
    email_content=request.POST['email_content']
    with open("universityloanoffice/files/notifications/email", "w") as f:
        for line in email_content.splitlines():
            f.write("<span>" + line + "</span> <br>")
    return redirect("/university/email-configuration")

@permit_uloanofficer
@login_required
def web_notf_configuration(request):
    with open("universityloanoffice/files/notifications/web_notification", "r") as f:
        web_notification=f.read()
    return render(request, "web_notf_configuration.html", {'current_content': web_notification} )

@permit_uloanofficer
@login_required
def configure_web_notf(request):
    email_content=request.POST['web_notification']
    with open("universityloanoffice/files/notifications/web_notification", "w") as f:
        for line in email_content.splitlines():
            f.write("<span>" + line + "</span> <br>")
    return redirect("/university/web-notf-configuration")
