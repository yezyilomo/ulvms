from django.db import models

class College(models.Model):
    college_name=models.CharField(max_length=100, primary_key=True)

class Degree(models.Model):
    programe_name=models.CharField(max_length=100, primary_key=True)
    tuition_fee=models.FloatField()
    college_name=models.ForeignKey(College, on_delete=models.CASCADE)

class Student(models.Model):
    STATUS_CHOICES = (
        ('discontinued', 'discontinued'),
        ('continuous', 'continuous'),
        ('postponed', 'postponed'),
        ('completed', 'completed'),
    )
    GENDER_CHOICES=(
       ('M', 'Male'),
       ('F', 'Female'),
    )
    reg_no=models.CharField(max_length=15, primary_key=True)
    form_four_index_no=models.CharField(max_length=18)
    signature=models.CharField(max_length=256)
    first_name=models.CharField(max_length=30)
    middle_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    status=models.CharField(max_length=12, choices=STATUS_CHOICES)
    year_of_study=models.SmallIntegerField()
    gender=models.CharField(max_length=1, choices=GENDER_CHOICES)
    programe_name=models.ForeignKey(Degree, on_delete=models.CASCADE)
    email=models.CharField(max_length=50, default="")
