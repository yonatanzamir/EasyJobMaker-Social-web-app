from distutils.command.upload import upload
from enum import Enum
from operator import truth
from pickle import TRUE
from django.db import models
from django.contrib.auth.models import User

# Table of all the users that signed up to the application
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)
    image = models.FileField(null = True, blank = True, upload_to = '')

    def __str__(self):
        return self.full_name
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = '../../static/images/avatar.png'
        return url    


# Table of all the active service providers in the app
class Service_Provider(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)
    reviews_counter = models.IntegerField(default=0)
    reviews_sum = models.FloatField(default=0)

    def __str__(self):
        return self.full_name

 
# Table of all the possible cities for jobs 
class Job_Location(models.Model):
    city = models.CharField(max_length=30, blank=True, null=True)
    region = models.CharField(max_length=30, null=True)
    def __str__(self):
        return self.city

 # Table of all the jobs that were posted in the app (including vacancies, jobs in progress and completed jobs)
class Job(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True)
    contact_name= models.CharField(max_length=200, null=True)
    contact_phone=models.CharField(max_length=10, null=True)
    job_description=models.CharField(max_length=1000, null=True)
    date_added = models.DateTimeField(auto_now_add=True,  blank = True)
    complete = models.BooleanField(default=False,  blank = True)
    in_progress = models.BooleanField(default=False,  blank = True)
    transaction_id = models.CharField(max_length=100, null=True)
    service_provider = models.ForeignKey(Service_Provider, on_delete=models.SET_NULL, null=True, blank=True)
    job_completion_time = models.DateTimeField(null=True, blank = True)
    payment_for_job = models.FloatField(null=True, blank = True)
    image = models.FileField(null = True, blank = True, upload_to = '')

    def __str__(self):
        return str(self.job_title)


    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = '../../static/images/defaulet_job.jpg'
        return url

# Table that contains additional details for each job, mainly location details
class Job_Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)



    def __str__(self):
        return self.address

# Table that contains all the applications made by service providers for jobs, including current status (pending, rejected, accepted)
class Job_Application(models.Model):
    class Application_status(Enum):
        Pending = 'PE'
        Accepted = 'AC'
        Rejected = 'RE'
    

    application_status = models.CharField(
    max_length=2,
    choices=[(tag, tag.value) for tag in Application_status],
    default=Application_status.Pending,
)

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    service_provider = models.ForeignKey(Service_Provider, on_delete=models.CASCADE)


# Table of all the reviews and ratings that customers gave service providers in the end of the job.
class ReviewRating(models.Model):
    service_provider = models.ForeignKey(Service_Provider, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.subject


# Create your models here.
