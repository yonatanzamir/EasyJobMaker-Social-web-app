from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name="main"),
    path('jobs/', views.jobs, name="jobs"),
    path('checkout/<int:job_id>/', views.checkout, name="checkout"),
    path('jobBuilder/', views.jobBuilder, name="jobBuilder"),
    path('addJob/',views.addJob,name="addJob"),
    path('registerPage/', views.registerPage, name= "registerPage"),
    path('loginPage/', views.loginPage, name= "loginPage"),
    path('register/', views.makeRegister, name= "makeRegister"),
    path('jobdetails/<int:job_id>/', views.jobDetails, name='jobDetails'),
    path('login/', views.makelogin, name= "makelogin"),
    path('logout/', views.logoutUser, name= "logout") ,  
    path('takeJob/', views.takeJob, name= "takeJob"),
    path('myProfile/', views.myProfile, name = "myProfile"),
    path('search/', views.search, name = "search"),
    path('myJobs/', views.myJobs, name = "myJobs"),
    path('filtered_jobs_by_region/', views.filteredJobsByRegion, name = "filtered_jobs_by_region"),
    path('jobsToDo/', views.jobsToDo, name = "jobsToDo"),
    path('jobsApplications/', views.jobsApplications, name = "jobsApplications"),
    path('updateProfile/', views.updateProfile, name = "updateProfile"),
    path('finishJob/', views.finishJob, name = "finishJob"),
    path('submit_review/<int:job_id>/', views.submit_review, name="submit_review"),
    path('declineApplication/', views.declineApplication, name = "declineApplication"),
    path('acceptApplication/', views.acceptApplication, name = "acceptApplication"),
    path('applicationsStatus/', views.applicationsStatus, name = "applicationsStatus")
]
