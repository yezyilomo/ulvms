from django.contrib import admin

from .models import User, Student, SigningSession
from loanboard.models import Beneficiary
from aris.models import College, Degree, Student as St

# Register your models here.
admin.site.register(User)
admin.site.register(Student)
admin.site.register(SigningSession)
admin.site.register(Beneficiary)
admin.site.register(College)
admin.site.register(Degree)
admin.site.register(St)
