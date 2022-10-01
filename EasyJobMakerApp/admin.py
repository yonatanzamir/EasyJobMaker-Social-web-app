from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Service_Provider)
admin.site.register(Job)
admin.site.register(Job_Address)
admin.site.register(Job_Location)
admin.site.register(ReviewRating)
admin.site.register(Job_Application)