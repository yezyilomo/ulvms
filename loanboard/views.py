import os
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from pathlib import Path
from django.http import HttpResponse
import pyexcel
from universityloanoffice.models import User
from loanboard.models import Beneficiary
from universityloanoffice.models import Student as Loanbeneficiary
from universityloanoffice.models import SigningSession
from aris.models import Student, College, Degree;

# Create your views here.

def filldata(request):
    fs = FileSystemStorage('loanboard/files')
    file_name=fs.path('')+'/'+'beneficiaries.xls'
    fl=pyexcel.iget_records(file_name=file_name)
    loanbeneficiary=None;
    for record in fl:
        if record['Registration Number'] != "" and not Beneficiary.objects.filter(reg_no=record['Registration Number']):
            loanbeneficiary=Beneficiary(
                reg_no=record['Registration Number'],
                first_name=record['First Name'],
                middle_name=record['Middle Name'],
                last_name=record['Last Name'],
                year_of_study=record['yos'],
                programe_name=record['Course'],
                status="unadmited",
                gender=record['gender'],
                form_four_index_no=record['F4Index'],
                account_no=record['account number'],
                bank_name=record['Bank name'],
                tuition_fee=record['Tuition fee'],
                accomodation=record['Accommodation'],
                special_faculty=record['special faculty'],
                field=record['field'],
                project_and_research=record['project and reseach']
            )
            loanbeneficiary.save()
    return HttpResponse("Filled successfully")

def paginate(data, page_num, request):
    paginator = Paginator(data, page_num)
    page = request.GET.get('page')
    paginateddata = paginator.get_page(page)
    return paginateddata

def permit_lbloanofficer(function):
    def wrap(request, *args, **kwargs):
        if request.user.role != "loanboardofficer":
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

@permit_lbloanofficer
@login_required
def profile(request):
    user_role=User.objects.get(id=request.session['_auth_user_id']).role
    if '_auth_user_id' in request.session and user_role=='loanboardofficer':
        fs = FileSystemStorage('loanboard/files')
        files=fs.listdir('')[1]
        notification=0
        for file in files:
            if file.startswith('New_'):
                notification+=1

        completed=Beneficiary.objects.filter(status="completed").count()
        continuous=Beneficiary.objects.filter(status="continuous").count()
        discontinued=Beneficiary.objects.filter(status="discontinued").count()
        postponed=Beneficiary.objects.filter(status="postponed").count()
        templete_data={
        'notification': notification,
        'continuous': continuous,
        'discontinued': discontinued,
        'postponed': postponed,
        'completed': completed,
        }
        return render(request, 'loanboard.html', templete_data)
    else:
        raise Http404('Page does not exist')

def logoutuser(request):
    logout(request)
    return redirect('/')

@permit_lbloanofficer
@login_required
def notifications(request):
    if '_auth_user_id' in request.session:
        fs = FileSystemStorage('loanboard/files')
        files=sorted(Path(fs.path('')).iterdir(), key=lambda f: f.stat().st_mtime)
        notification=0
        for fl in files:
            if fl.name.startswith('New_'):
                os.rename(fl, fs.path('')+'/'+fs.get_available_name(fl.name[4:]) )

        files=filter( lambda a: not a.name.startswith(".") and a.is_file(), sorted(Path(fs.path('')).iterdir(), key=lambda f: f.stat().st_mtime) )
        files = paginate(list(files), 13, request)
        return render(request, 'lbnotifications.html', {'notification': notification, 'files': files})
    else:
        raise Http404('Page does not exist')

@permit_lbloanofficer
@login_required
def send_beneficiaries(request):
    req_data=Beneficiary.objects.filter(status="continuous")
    file_name='loanboard/files/exported/emptyfile.xls'
    sheet = pyexcel.get_sheet(file_name=file_name, name_columns_by_row=0)
    sheet.row += ['First Name', 'Middle Name', 'Last Name', 'Registration Number', 'Form 4 Index Number', 'Account Number', 'Bank Name', 'Amount']
    for stdnt in req_data:
        sheet.row += [
            stdnt.first_name,
            stdnt.middle_name,
            stdnt.last_name,
            stdnt.reg_no,
            stdnt.form_four_index_no,
            stdnt.account_no,
            stdnt.bank_name,
            stdnt.accomodation,
        ]
    fs = FileSystemStorage('universityloanoffice/files/signing')
    sheet.save_as( fs.path('')+'/'+fs.get_available_name("New_Sheet_.xls") )
    return render(request, 'fl_sending_response.html')

@permit_lbloanofficer
@login_required
def showfile(request, file_name):
    fs = FileSystemStorage('loanboard/files')
    file_path=fs.path('')+'/'+file_name
    fl=pyexcel.get_book_dict(file_name=file_path)
    data=None
    for sheet in fl:
        if isinstance(fl[sheet], list):
               data=fl[sheet]
    return render(request, 'lbfile.html', {'data':data, 'filename': file_name})

@permit_lbloanofficer
@login_required
def view_beneficiaries(request):
    beneficiaries=Beneficiary.objects.all()
    beneficiaries = paginate(beneficiaries, 13, request)
    return render(request, 'beneficiaries.html', {'beneficiaries': beneficiaries})

@permit_lbloanofficer
@login_required
def new_beneficiaries(request):
    beneficiaries=Beneficiary.objects.filter(status="unadmited")
    beneficiaries = paginate(beneficiaries, 13, request)
    return render(request, 'to_be_admited_beneficiaries.html', {'beneficiaries': beneficiaries})

@permit_lbloanofficer
@login_required
def import_beneficiaries(request):
    beneficiaries=Beneficiary.objects.all()
    loanbeneficiary=None
    unadmited_beneficiaries=[]
    for record in beneficiaries:
        if Student.objects.filter(reg_no=record.reg_no):
            if Loanbeneficiary.objects.filter(reg_no=record.reg_no):
                continue
            loanbeneficiary=Loanbeneficiary(
                reg_no=record.reg_no,
                form_four_index_no=record.form_four_index_no,
                status=Student.objects.get(reg_no=record.reg_no).status,
                account_no=record.account_no,
                bank_name=record.bank_name,
                tuition_fee=record.tuition_fee,
                accomodation=record.accomodation,
                special_faculty=record.special_faculty,
                field=record.field,
                project_and_research=record.project_and_research
            )
            loanbeneficiary.save()
        else:
            unadmited_beneficiaries.append(record)
    return render(request, 'import_response.html', {'unadmited_beneficiaries': unadmited_beneficiaries})

@permit_lbloanofficer
@login_required
def view_changes(request, file_name):
    fn=file_name
    fs = FileSystemStorage('loanboard/files')
    file_name=fs.path('')+'/'+file_name
    fl=pyexcel.iget_records(file_name=file_name)

    list_to_be_updated=[]
    loanbeneficiary=Beneficiary.objects.all()
    for std in fl:
        try:
            if std['Status'] != Beneficiary.objects.get(form_four_index_no=std['Form 4 Index Number']).status:
                list_to_be_updated.append( ( Beneficiary.objects.get(reg_no=std['Registration Number']), std['Status'] ) )
        except Exception as e:
            continue;

    list_to_be_updated=paginate(list_to_be_updated, 13, request)

    return render(request, 'updates.html', {'beneficiaries': list_to_be_updated, 'file_name': fn})

@permit_lbloanofficer
@login_required
def update_status(request, file_name, reg_no):
    fn=file_name
    fs = FileSystemStorage('loanboard/files')
    file_name=fs.path('')+'/'+file_name
    fl=pyexcel.iget_records(file_name=file_name)

    loanbeneficiary=Beneficiary.objects.all()
    if reg_no=="all":
        for std in fl:
            bf=Beneficiary.objects.get(form_four_index_no=std['Form 4 Index Number'])
            if std['Status'] != bf.status:
                bf.status=std['Status']
                bf.save()
    templete_data={
      'beneficiaries': loanbeneficiary,
    }
    return redirect('/loanboard/view-changes/'+fn)

@permit_lbloanofficer
@login_required
def active_beneficiaries(request):
    beneficiaries=Beneficiary.objects.filter(status="continuous")
    beneficiaries = paginate(beneficiaries, 13, request)
    return render(request, 'active_beneficiaries.html', {'beneficiaries': beneficiaries})
