"""team206 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from study.views import update_profile, account_view, redirect, search_people, search_classes, course_view, new_meeting
from allauth.account.views import LoginView, SignupView

urlpatterns = [
    path('edit_profile/', update_profile, name='edit_profile'),
    path('search_people/', search_people, name="search_people"),
    path('search_classes/', search_classes, name="search_classes"),
    path('new_meeting/', new_meeting, name='new_meeting'),
    path('', redirect),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/login/', LoginView.as_view(), name="login"),
    path('accounts/signup/', SignupView.as_view(), name="signup"),
    path('courses/<str:code>/', course_view, name='courses'),
    path('<str:username>/', account_view, name='account')
]
