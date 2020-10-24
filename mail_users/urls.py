from django.urls import path

from .views import *

urlpatterns = [

    path('',UserSignUpView.as_view(), name='user-signup'),
    path('login/',UserLoginView.as_view(), name='user-login'),
    path('email/', EmailCreateView.as_view(), name='user-email'),
    path('email-list/', EmailList.as_view(), name='user-email-list'),
    path('logout/', logout_view, name='user-logout'),
    path('email/<int:id>', EmailActions.as_view(), name='email-actions'),

    path('test/<slug:slug>',test)
]