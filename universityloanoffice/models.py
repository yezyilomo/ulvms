from django.db import models
from django.contrib.auth.models import AbstractUser
from aris.models import Student as Aris_Student

class User(AbstractUser):
    ROLE_CHOICES=(
       ('superuser', 'superuser'),
       ('student', 'student'),
       ('universityloanofficer', 'universityloanofficer'),
       ('loanboardofficer', 'loanboardofficer')
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

class Student(models.Model):
    STATUS_CHOICES = (
        ('discontinued', 'discontinued'),
        ('continuous', 'continuous'),
        ('postponed', 'postponed'),
        ('completed', 'completed'),
    )
    reg_no=models.CharField(max_length=15, primary_key=True)
    form_four_index_no=models.CharField(max_length=18)
    status=models.CharField(max_length=12, choices=STATUS_CHOICES)
    account_no=models.CharField(max_length=25)
    bank_name=models.CharField(max_length=10)
    tuition_fee=models.FloatField()
    accomodation=models.FloatField()
    special_faculty=models.FloatField()
    field=models.FloatField()
    project_and_research=models.FloatField()

class SigningSession(models.Model):
    SIGNATURE_STATUS=(
        ('signed', 'signed'),
        ('unsigned', 'unsigned'),
    )
    student=models.ForeignKey(Student, on_delete=models.CASCADE, unique=True)
    signature_id=models.ForeignKey(Aris_Student, on_delete=models.CASCADE, unique=True)
    status=models.CharField(max_length=10, choices=SIGNATURE_STATUS)
