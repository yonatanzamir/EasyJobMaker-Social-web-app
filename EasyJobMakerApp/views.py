from contextvars import Context
from email.mime import image
from http.client import HTTPResponse
from itertools import count
from multiprocessing import Event, context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import datetime
from django.contrib import messages
import json
import os
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib import messages
import csv
from .forms import CreateUserForm, ReviewForm
from django.template import context,loader



# Render the main page of the application, showing also the best reviews that was written by customers to service providers
def main(request):
    reviews=[]
    best_review=ReviewRating.objects.order_by('-rating')
    for i in range (ReviewRating.objects.count()):
        reviews.append(best_review[i])
    if request.user.is_authenticated:  
        try: 
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
        except Service_Provider.DoesNotExist:
            is_service_provider = False
      
    else:
        is_service_provider = False    
    context = {"is_service_provider":is_service_provider,"reviews":reviews}
    return render(request, "EasyJobMakerApp/main.html", context)

# Returns all the jobs that available for the logged in user
def jobs(request):
    jobs = Job.objects.all()
    if request.user.is_authenticated:
        try:
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
            applied_jobs = Job_Application.objects.filter(service_provider = service_provider)
            applied_jobs = applied_jobs.values_list('job', flat=True)
            jobs = jobs.exclude(id__in = applied_jobs)
        except Service_Provider.DoesNotExist:
            is_service_provider = False

    else:
        is_service_provider = False
        
    context = {'jobs': jobs, 'is_service_provider': is_service_provider}
    return render(request, "EasyJobMakerApp/jobs.html", context)

# Returns the jobs that the current service provider got a permission to do (jobs in progress and completed jobs)
def jobsToDo(request):
    service_provider=Service_Provider.objects.get(user = request.user)
    my_jobs=Job.objects.filter(service_provider=service_provider)
    return render(request, "EasyJobMakerApp/jobsToDo.html", {'jobs': my_jobs,"is_service_provider":True, 'isBreak': False})

# Returns the jobs that the current customer posted in the app
def myJobs(request):
    customer=Customer.objects.get(user = request.user)
    my_jobs=Job.objects.filter(customer=customer)
    if request.user.is_authenticated:  
        try: 
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
        except Service_Provider.DoesNotExist:
            is_service_provider = False
    else:
        is_service_provider = False    
    
    return render(request, "EasyJobMakerApp/myJobs.html", {'jobs': my_jobs,"is_service_provider":is_service_provider})

# Returns all the applications of service providers to jobs that was posted by the logged in user (applications that are pending for the customer's response)
def jobsApplications(request):
    customer=Customer.objects.get(user = request.user)
    my_jobs=Job.objects.filter(customer=customer)
    my_jobs_applications = Job_Application.objects.filter(job__in = my_jobs, application_status = Job_Application.Application_status.Pending)

    try: 
        service_provider = Service_Provider.objects.get(user = request.user)
        is_service_provider = True
    except Service_Provider.DoesNotExist:
        is_service_provider = False

    return render(request, "EasyJobMakerApp/jobsApplications.html", {"my_jobs":my_jobs, "my_jobs_applications":my_jobs_applications,"is_service_provider":is_service_provider})


# Returns all the applications that the current service provider made (accepted, rejected and pending aplications)
def applicationsStatus(request):
    service_provider = Service_Provider.objects.get(user = request.user)
    my_applications = Job_Application.objects.filter(service_provider = service_provider)

    return render(request, "EasyJobMakerApp/applicationsStatus.html", {"my_applications":my_applications,"is_service_provider":True})
    
# Updates a job application as rejected in the database (it runs when a user declines a service provider)
def declineApplication(request):
    data = json.loads(request.body)
    application_id = data['Application_Id']
    application = get_object_or_404(Job_Application, id=application_id)
    application.application_status = Job_Application.Application_status.Rejected
    application.save()
    return render(request, "EasyJobMakerApp/jobsApplications.html")

# Updates a job application as accepted in the database (it runs when a user accepts a service provider)
def acceptApplication(request):
    data = json.loads(request.body)
    application_id = data['Application_Id']
    application = get_object_or_404(Job_Application, id=application_id)
    application.application_status = Job_Application.Application_status.Accepted
    application.save()
    job_taken = application.job
    job_taken.in_progress = True
    job_taken.service_provider = application.service_provider
    job_taken.save()
    return render(request, 'EasyJobMakerApp/jobsApplications.html')

# Returns details of a job for a checkout page (when user intends to apply for this job)
def checkout(request,job_id):
    job = get_object_or_404(Job, id=job_id)
    jobAddress=get_object_or_404(Job_Address,job=job)
    return render(request, "EasyJobMakerApp/checkout.html", {'job': job,'jobAddress':jobAddress})

# Returns details of a job for a jobDetails page (when user wants to view this job)
def jobDetails(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    jobAddress=get_object_or_404(Job_Address,job=job)
    return render(request, 'EasyJobMakerApp/jobDetails.html', {'job': job,'jobAddress':jobAddress})


# Returns all possible locations for jobs (this function runs when a user selects the 'Add a Job' option in the app)
def jobBuilder(request):
    jobsLocations = Job_Location.objects.all()
    if request.user.is_authenticated:    
        try: 
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
        except Service_Provider.DoesNotExist:
            is_service_provider = False
    else:
            is_service_provider = False    


    context = {'jobsLocations': jobsLocations,"is_service_provider":is_service_provider}
    return render(request, "EasyJobMakerApp/jobBuilder.html", context)


# This function process all the data of the new job that a user added to the app and it updates the database accordingly.
def addJob(request):
    transaction_id = datetime.datetime.now().timestamp()
    userData = json.loads(request.POST.get('userFormData'))['userData']
    jobDetails =  json.loads(request.POST.get('jobDetails'))['jobDetails']
    shipping =  json.loads(request.POST.get('shippingInfo'))['shipping']
    
    if request.user.is_authenticated:    
   
        customer = Customer.objects.get(user=request.user)
        contact_name = userData['name']
        contact_phone = userData['phone']
        job_title = jobDetails['jobTitle']
        job_description = jobDetails['jobDescription']
        payment_for_job = jobDetails['jobPayment']
        job_image = request.FILES.get('image')
        job_address = shipping['address']
        job_city = shipping['city']
        job_state = shipping['state']
        job_zipcode = shipping['zipcode']
        new_job = Job.objects.create(customer = customer, contact_name = contact_name, contact_phone = contact_phone,job_title = job_title, job_description = job_description, transaction_id = transaction_id
        ,payment_for_job = payment_for_job, image = job_image)

        Job_Address.objects.create(customer = customer, job = new_job, address = job_address, city = job_city, state =  job_state, zipcode = job_zipcode)
    context={}
  
    return render(request, "EasyJobMakerApp/jobBuilder.html", context)

# Returns registration form of the app
def registerPage(request):
    form = CreateUserForm()
    context = {'form': form}
    return render(request, "EasyJobMakerApp/register.html", context)

# Returns the login page of the app
def loginPage(request):
    context = {}
    return render(request, "EasyJobMakerApp/login.html", context)

# Performs authentication for the person requesting to login to the app (checks the given username and password)
def makelogin(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect("jobs")
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'EasyJobMakerApp/login.html', context)

# Logs out the current user
def logoutUser(request):
	logout(request)
	return redirect('loginPage')

# Creates new account for the person that signed up to the app
def makeRegister(request):
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                user_name = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user_name)

                full_name = form.cleaned_data.get('first_name') + ' ' + form.cleaned_data.get('last_name')
                email = form.cleaned_data.get('email')
                new_customer = Customer(user = user, full_name = full_name, email = email)
                new_customer.save()
                if request.POST.get('service_provider') == 'on':
                    new_service_provider = Service_Provider(user = user, full_name = full_name, email = email, customer = new_customer)
                    new_service_provider.save()
                return redirect('loginPage')

        context = {'form': form}
        return render(request, 'EasyJobMakerApp/register.html', context)

# Processes the job application of the user and updates the database
def takeJob(request):
    new_application = Job_Application()
    data = json.loads(request.body)
    job_id = data['Job_Id']
    job = get_object_or_404(Job, id=job_id)
    new_application.job = job

    service_provider = Service_Provider.objects.get(user = request.user)
    new_application.service_provider = service_provider
    

    new_application.save()
    return render(request, 'EasyJobMakerApp/jobs.html')


# Returns the current user details in order to show his profile page (including his reviews and rating if he's a service provider)
def myProfile(request):
    current_user = Customer.objects.get(user = request.user)
    try: 
        rate = 0
        service_provider = Service_Provider.objects.get(user = request.user)
        is_service_provider = True
        rate = service_provider.reviews_sum/service_provider.reviews_counter if service_provider.reviews_counter > 0 else 0
        my_reviews=ReviewRating.objects.filter(service_provider=service_provider)
    except Service_Provider.DoesNotExist:
        is_service_provider = False
        my_reviews = None
    return render(request, 'EasyJobMakerApp/myProfile.html', {'customer': current_user, 'is_service_provider': is_service_provider, 'reviews': my_reviews, 'rate': rate})

# Filters and returns the jobs that are compatible with the user's search
def search(request):
    query = request.GET.get('query', '')
    if query:
        jobs = Job.objects.filter(Q(job_title__icontains=query))
    else :
        jobs=Job.objects.all()
    if request.user.is_authenticated:
        try:
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
        except Service_Provider.DoesNotExist:
            is_service_provider = False

    else:
        is_service_provider = False        
    context = {'jobs': jobs, 'is_service_provider': is_service_provider}

    return render(request, 'EasyJobMakerApp/jobs.html', context)

# Filters and returns the jobs located in the region that the user chose
def filteredJobsByRegion(request):
    if request.user.is_authenticated:
        try:
            service_provider = Service_Provider.objects.get(user = request.user)
            is_service_provider = True
        except Service_Provider.DoesNotExist:
            is_service_provider = False

    else:
        is_service_provider = False 


    region = json.loads(request.POST.get('Region'))['region']
    if region != "All Regions":       
        jobLocation=Job_Location.objects.filter(region=region)
        temp_cities=list(jobLocation.values_list("city"))
        cities =[]
        for city in temp_cities:
            cities.append(str(city)[2:-3])
        job_addr=Job_Address.objects.filter(city__in=cities)
        jobs_str =[]
        for job in job_addr.values_list("job"):
            jobs_str.append(str(job)[1:-2])

        jobs=Job.objects.filter(id__in=jobs_str)
    
    else:
        jobs=Job.objects.all()
    
    if is_service_provider:
        applied_jobs = Job_Application.objects.filter(service_provider = service_provider)
        applied_jobs = applied_jobs.values_list('job', flat=True)
        jobs = jobs.exclude(id__in = applied_jobs)

    context = {'jobs': jobs, 'is_service_provider': is_service_provider}
    template = loader.get_template('EasyJobMakerApp/jobs.html')
    html = template.render(context)
    
    return HttpResponse(html)
    
# Updates the user's account when he asks to change his picture or to toggle the option to be a service provider
def updateProfile(request):
    userChoiceServiceProvider = json.loads(request.POST.get('ServiceProvider'))['isServiceProvider']
    customer = Customer.objects.get(user=request.user)
    profile_image = request.FILES.get('image')
    if profile_image:
        customer.image=profile_image
        customer.save()

    try: 
        service_provider = Service_Provider.objects.get(user = request.user)
        is_service_provider = True
    except Service_Provider.DoesNotExist:
        is_service_provider = False
    
    if is_service_provider:
        if  userChoiceServiceProvider==False:
            Job.objects.filter(service_provider=service_provider,in_progress=True).update(in_progress=False)
            service_provider.delete()
    else:
        if  userChoiceServiceProvider==True:
            new_service_provider = Service_Provider(user = request.user, full_name = customer.full_name, email = customer.email, customer = customer)
            new_service_provider.save()
    context = {}
    return render(request, "EasyJobMakerApp/myProfile.html", context)

# Updates a job's status to 'completed' in the database    
def finishJob(request):
    data = json.loads(request.body)
    job_id = data['Job_Id']
    job = get_object_or_404(Job, id=job_id)
    job.in_progress = False
    job.complete = True
    job.save()
    return render(request, 'EasyJobMakerApp/jobs.html')

# Processes the review & rating that a user sent (save it in the database and updates the service provider's rate accordingly)
def submit_review(request, job_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviewing_customer=Customer.objects.get(user = request.user)
            review = ReviewRating.objects.get(customer__id=reviewing_customer.id, job__id=job_id)
            old_rating = review.rating
            form = ReviewForm(request.POST, instance=review)
            form.save()
            new_rating = review.rating
            cur_service_provider = review.service_provider
            cur_service_provider.reviews_sum = cur_service_provider.reviews_sum - old_rating + new_rating
            cur_service_provider.save() 
            # messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                job_reviewed = Job.objects.get(id = job_id)
                data.job_id = job_reviewed.id
                data.service_provider_id = job_reviewed.service_provider.id
                data.customer_id = reviewing_customer.id
                data.save()
                cur_service_provider = data.service_provider
                cur_service_provider.reviews_counter += 1
                cur_service_provider.reviews_sum += data.rating 
                cur_service_provider.save() 
                # messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)