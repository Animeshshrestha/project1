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

from .models import UserEmail, CustomUser
from .forms import UserLoginForm, CustomUserForm, EmailForm
from .custom_auth import EmailBackend
from .serializers import EmailListSerializer

def logout_view(request):

	logout(request)
	return HttpResponse("You are logged out ")

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
        form = EmailForm(initial={'sender_email': request.user.email})
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            sender = CustomUser.objects.get(email=request.user.email)
            email = UserEmail(
                sender=sender,
                subject=form.cleaned_data.get('subject'),
                message_text=form.cleaned_data.get('message_text'),
            )
            email.save()
            for user_email in form.cleaned_data.get('receiver_list'):
                user = CustomUser.objects.get(email=user_email)
                print(user)
                email.receiver.add(user)
            email.save()
            messages.success(request,"Message Sent Sucessfully")
            return render(request, self.template_name, {'form':EmailForm(initial={'sender_email': request.user.email})})
            
        return render(request, self.template_name,{'form':form})		

class EmailList(View):

    def get(self, request):

        query_params = request.GET.get('type','inbox')
        if query_params == 'send':
            email_list = UserEmail.objects.filter(sender=request.user).order_by('-created_at')
        if query_params == 'inbox':
            email_list = UserEmail.objects.filter(receiver=request.user, is_archived=False).order_by('-created_at')
        if query_params == 'archived':
            email_list = UserEmail.objects.filter(receiver=request.user, is_archived=True).order_by('-created_at')
        serializer = EmailListSerializer(email_list, many=True)
        return JsonResponse(serializer.data, safe=False)