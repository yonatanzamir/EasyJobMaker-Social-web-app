
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from .models import *
from .models import ReviewRating
from django import forms


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		#full_name = forms.CharField(max_length=200)
		fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2']



class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']