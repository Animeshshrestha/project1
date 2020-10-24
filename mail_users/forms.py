import select2.fields
import select2.models

from django import forms
from .models import UserEmail, CustomUser
from django.contrib.auth.forms import UserCreationForm



class CustomUserForm(UserCreationForm):

	class Meta:
		model = CustomUser
		fields = ['username','email','password1','password2']
	
	def clean_email(self):
		email = self.cleaned_data.get('email')
		if CustomUser.objects.filter(email=email).exists():
			raise forms.ValidationError('This email is already in use.')
		return email


class UserLoginForm(forms.Form):

	email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class EmailForm(forms.ModelForm):
	
	sender_email = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	receiver_list = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))

	class Meta:
		model = UserEmail
		fields = ['subject','message_text','receiver_list','sender_email']

	def clean_receiver_list(self):
		if self.cleaned_data.get('receiver_list') is None:
			raise forms.ValidationError('At least one recipient is required.')
		receiver = [email.strip() for email in self.cleaned_data.get('receiver_list').split(",") if email]
		print(receiver)
		for email in receiver:
			try:
				user = CustomUser.objects.get(email=email)
			except CustomUser.DoesNotExist:
				raise forms.ValidationError('User with email {0} does not exist.'.format(email))
		return receiver		


	