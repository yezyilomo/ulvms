from django.db import models

class Beneficiary(models.Model):
    STATUS_CHOICES = (
        ('discontinued', 'discontinued'),
        ('continuous', 'continuous'),
        ('postpone', 'postpone'),
        ('complete', 'complete'),
    )
    GENDER_CHOICES=(
       ('M', 'Male'),
       ('F', 'Female'),
    )

    reg_no=models.CharField(max_length=15, primary_key=True)
    form_four_index_no=models.CharField(max_length=18)
    first_name=models.CharField(max_length=30)
    middle_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    year_of_study=models.SmallIntegerField()
    gender=models.CharField(max_length=1, choices=GENDER_CHOICES)
    programe_name=models.CharField(max_length=100)
    status=models.CharField(max_length=12, choices=STATUS_CHOICES)
    account_no=models.CharField(max_length=25)
    bank_name=models.CharField(max_length=10)
    tuition_fee=models.FloatField()
    accomodation=models.FloatField()
    special_faculty=models.FloatField()
    field=models.FloatField()
    project_and_research=models.FloatField()
