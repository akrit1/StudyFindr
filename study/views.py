from django.shortcuts import render
from .forms import UserForm, ProfileForm, SearchPeopleForm, SearchClassesForm, MeetingForm
from django.http import HttpResponseRedirect, HttpResponse
from .models import Profile, User, SearchPeople, SearchClasses, Course, Meeting
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth import models
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
from collections import Counter
import sys

def update_profile(request):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "File Uploads"
    # *  Author: Django 
    # *  Date: Accessed November 16, 2020 
    # *  Code version: 3.1
    # *  URL: https://docs.djangoproject.com/en/3.1/topics/http/file-uploads/
    # *  Software License: BSD-3
    # ***************************************************************************************/
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile) # added request.FILES
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse(account_view, args=[request.user.username]))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'study/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def account_view(request, username):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "Extraction of Tweets using Tweepy"
    # *  Author: GeeksForGeeks
    # *  Date: May 30, 2018
    # *  Code version: N/A
    # *  URL: https://www.geeksforgeeks.org/extraction-of-tweets-using-tweepy/
    # *  Software License: N/A
    # ***************************************************************************************/
    username = username.lower()
    user = get_object_or_404(User, username=username)

    consumer_key="Iy1sTDD2qcC5ekypsd4nPrB6n"
    consumer_secret="9A1RIv1aYMKHss83lPRrWV8TSM6NCBS7E8vU0Yl5ec6RYk6PQs"
    access_token="1277681931581358080-AMcKTd0bQapqVA3Xc8Xg7zBPXTEJ4L"
    access_token_secret="PPbEcotacL9325c8qFGfgQKLcio4vSqxXtGPVg3PwxQV7"
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth)
    try:
        if user.profile.twitter_username[0] == '@':
            item = auth_api.user_timeline(screen_name=user.profile.twitter_username[1:], count=3)
        else:
            item = auth_api.user_timeline(screen_name=user.profile.twitter_username, count=3)
    except:
        item = []
    item = "BADBADBAD" if len(item) == 0 else item
    if item == "BADBADBAD":
        return render(request, 'study/account.html', {'user': user, 'tweet1': item, 'tweet2': item, 'tweet3': item })
    else:
        return render(request, 'study/account.html', {'user': user, 'tweet1': item[0], 'tweet2': item[1], 'tweet3': item[2] })

def course_view(request, code):
    def date_key(x):
        try:
            return int(x.when.split('-')[-1] + x.when.split('-')[0].split(' ')[-1] + x.when.split('-')[1])
        except:
            return int(x.when.split('-')[-1] + x.when.split('-')[0] + x.when.split('-')[1])
    
    c = get_object_or_404(Course, course_code=code.upper())
    m = sorted(Meeting.objects.all(), key=lambda x: date_key(x), reverse=True)
    return render(request, 'study/course.html', {'course': c, 'meetings': m})

@login_required
def redirect(request):
    return HttpResponseRedirect(reverse(account_view, args=[request.user.username]))
    
def search_people(request):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "Django shortcut functions."
    # *  Author: Django
    # *  Date: Accessed November 16, 2020 
    # *  Code version: 3.1 
    # *  URL: https://docs.djangoproject.com/en/3.1/topics/http/shortcuts/
    # *  Software License: BSD-3
    # ***************************************************************************************/
    if request.method == 'POST':
        search_form = SearchPeopleForm(request.POST, instance=request.user)
        if search_form.is_valid():
            search_form.save()
            my_choice = request.POST['searchChoices']
            return render(request, 'study/search_people_result.html', {'searchChoices': my_choice, 'data': models.User.objects.all()
            })

    else:
        search_form = SearchPeopleForm(instance=request.user)
    return render(request, 'study/search_people_form.html', {
        'search_form': search_form
    })

def search_classes(request):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "Django shortcut functions"
    # *  Author: Django
    # *  Date: Accessed November 16, 2020 
    # *  Code version: 3.1 
    # *  URL: https://docs.djangoproject.com/en/3.1/topics/http/shortcuts/
    # *  Software License: BSD-3
    # * 
    # *  REFERENCES
    # *  Title: "Making Queries"
    # *  Author: Django
    # *  Date: Accessed November 16, 2020 
    # *  Code version: 3.1 
    # *  URL: https://docs.djangoproject.com/en/3.1/topics/db/queries/
    # *  Software License: BSD-3
    # ***************************************************************************************/
    if request.method == 'POST':
        search_form = SearchClassesForm(request.POST, instance=request.user)
        if search_form.is_valid():
            search_form.save()
            my_choice = request.POST['searchChoices'].strip().upper()
            results = []
            for c in Course.objects.all():
                if my_choice in c.course_code.upper() or my_choice in c.name.upper():
                    results.append(c) 
            try:
                return render(request, 'study/search_classes_result.html', {'searchChoices': my_choice, 'data': models.User.objects.values(), 'results': sorted(results, key=lambda x: x.course_code)})
            except:
                return render(request, 'study/search_classes_result.html', {'searchChoices': my_choice, 'data': models.User.objects.values(), 'results': results })
    else:
        search_form = SearchClassesForm(instance=request.user)
    return render(request, 'study/search_classes_form.html', {
        'search_form': search_form
    })

def new_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/courses/'+form.cleaned_data['course'].course_code)
    else:
        try:
            form = MeetingForm(initial = {'course': Course.objects.filter(course_code=request.META.get('HTTP_REFERER').split('/')[-2])[0] })
        except:
            form = MeetingForm()
    return render(request, 'study/new_meeting.html', {'form': form})