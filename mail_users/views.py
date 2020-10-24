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
from django.db.models import Q
from django.core import serializers

from .models import UserEmail, CustomUser
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
        form = EmailForm(initial={'sender_email': request.user.email})
        return render(request, self.template_name, {'form':form})

    def post(self, request):

        form = EmailForm(request.POST)
        print(request.POST)
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
                email.receiver.add(user)
            email.save()
            success_message = "Message Sent Sucesfully"
            return JsonResponse(success_message, safe=False)
            # messages.success(request,"Message Sent Sucessfully")
            # return render(request, self.template_name, {'form':EmailForm(initial={'sender_email': request.user.email})})
        return JsonResponse(form.errors.as_json(), safe=False, status=404)            
        # return render(request, self.template_name,{'form':form})		

class EmailList(View):

    def get(self, request):

        query_params = request.GET.get('type','Inbox')
        if query_params == 'Sent':
            email_list = UserEmail.objects.filter(sender=request.user).order_by('-created_at')
        if query_params == 'Inbox':
            email_list = UserEmail.objects.filter(receiver=request.user, is_archived=False).order_by('-created_at')
        if query_params == 'Archive':
            email_list = UserEmail.objects.filter(
                Q(receiver=request.user)|Q(sender=request.user),  is_archived=True).order_by('-created_at')
        context_dict = {
            'emails':email_list,
            'params':query_params
        }
        return render(request,'email_list.html',context_dict)
        # serializer = EmailListSerializer(email_list, many=True)
        # return JsonResponse(serializer.data, safe=False)

class EmailActions(View):

    def get(self, request, id):

        list_of_actions = ['Sent','archived','unarchived','Inbox','Archive','read','reply']
        action = request.GET.get('action','read')

        if action not in list_of_actions:
            action = 'read'
        try:
            user_email = UserEmail.objects.get(id = id)
        except:
            response = {"error_message":"Email not found"}
            return JsonResponse(response, safe=False, status=404)
        if action in ['read','Sent','Inbox','Archive']:
            user_email.is_read = True
            user_email.save()
            context_dict = {
                'email':user_email,
                'action':action
            }
            return render(request, 'email_inbox_single.html',context_dict)
        if action == 'reply':
            email_subject = user_email.subject.split('Re:')[-1]
            context_dict = {
                'email':user_email,
                'subject':email_subject
            }
            return render(request, 'email_compose_test.html',context_dict)

        elif action == 'archived':
            user_email.is_archived = True
        elif action == 'unarchived':
            user_email.is_archived = False
        user_email.save()
        response = {"success":True}
        return JsonResponse(response, safe=False)



