import os

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from rest_framework import viewsets, status

from .models import UserEmail
from .forms import UserLoginForm, CustomUserForm, EmailForm
from .custom_auth import EmailBackend
from .serializers import EmailListSerializer

def logout_view(request):

	logout(request)
	return HttpResponse("You are logged out ")


def test(request,slug):
    template_name = slug + '.html'
    return render(request, template_name)

class UserSignUpView(View):

    template_name = 'user_signup.html'

    def get(self, request):
        form = CustomUserForm(None)
        return render(request, self.template_name, {'form':form})

    def post(self,request):

        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('user-email')
        return render(request, self.template_name,{'form':form})

class UserLoginView(View, EmailBackend):

    template_name = 'user_login.html'

    def get(self, request):

        form = UserLoginForm(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):

        form = UserLoginForm(request.POST)
        print(request.POST)
        if form.is_valid():
            user_email = request.POST.get('email')
            password = request.POST.get('password')

            user = self.authenticate(request,email=user_email, password=password)

            if user is not None:

                login(request, user)
                return redirect('user-email')

            messages.error(request,"Invalid user/email combination")
            return render(request, self.template_name, {'form':form})	
        return render(request, self.template_name,{'form':form})		


class EmailCreateView(View):

    template_name = 'email_inbox.html'

    def get(self, request):
        form = EmailForm(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            print("oka")
        return render(request, self.template_name,{'form':form})		

class EmailList(View):

    def get(self, request):

        email_list = UserEmail.objects.filter(sender=request.user)
        serializer = EmailListSerializer(email_list, many=True)
        return JsonResponse(serializer.data, safe=False)