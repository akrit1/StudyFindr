from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.helpers import complete_social_login
from allauth.account.models import EmailAddress
from calendar import HTMLCalendar
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.safestring import SafeString
from icalendar import Calendar, Event
from picklefield.fields import PickledObjectField
from tweepy import OAuthHandler, API, Cursor
from unittest import mock
import datetime 
import icalendar
import json
import re
import urllib
from .models import Course, Meeting, Profile, SearchPeople, SearchClasses
from .utils import EventCalendar
from .views import update_profile, account_view, course_view, redirect, search_people, search_classes, new_meeting
from .forms import validate_name, UserForm, ProfileForm, SearchPeopleForm, SearchClassesForm, validate_date, validate_url, CourseModelChoiceField, MeetingForm


# Test Course model
class CourseTest(TestCase):
    """
    /***************************************************************************************
    *  REFERENCES
    *  Title: Basic Unit Testing in Django
    *  Author: GoDjango
    *  Date: Published 9 May 2019
    *  Code version: N/A
    *  URL: https://www.youtube.com/watch?v=DmRpNoQEx2o
    *  Software License: N/A
    *
    *  Title: Writing and Running Tests
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/topics/testing/overview/
    *  Software License: BSD-3   
    *  
    ***************************************************************************************/
    """

    # Test course fields: equivalence
    def test_course_fields_eq(self):
        course = Course()
        course.name = "Advanced Software Development"
        course.course_code = "CS-3240"
        course.start_time = "2020-08-25 14:00:00"
        course.end_time = "2020-08-25 15:15:00"
        course.weekdays = PickledObjectField(default=list)
        course.save()
        my_course = Course.objects.get(pk=course.id)
        self.assertEqual(my_course, course, "Fields of Course() and my_course do not match.")

    # Test course fields: edge (default values)
    def test_course_fields_edge(self):
        course = Course()
        course.save()
        self.assertEqual("Unnamed Course", course.name, "Doesn't match default value")
        self.assertEqual("CS-1110", course.course_code, "Doesn't match default value")
        self.assertEqual("2020-08-25 14:00:00", course.start_time, "Doesn't match default value")
        self.assertEqual("2020-08-25 15:15:00", course.end_time, "Doesn't match default value")
        self.assertEqual([], course.weekdays, "Doesn't match default value")
        

# Test Meeting model
class MeetingTest(TestCase):

    # Test meeting fields: equivalence
    def test_meeting_fields_eq(self):
        my_course = Course()       # Each Meeting has a Course
        my_course.save()
        meeting = Meeting()
        meeting.course = my_course
        meeting.who = "Me"
        meeting.where = "my_meeting_link.com"
        meeting.when = "2020-11-12 14:00:00"
        meeting.why = "To study for the upcoming exam"
        meeting.save()
        my_meeting = Meeting.objects.get(pk=meeting.id)
        self.assertEqual(my_meeting, meeting, "Fields of Meeting() and my_meeting do not match.")


# Test Profile model
class ProfileTest(TestCase):
    """
    /***************************************************************************************
    *  REFERENCES
    *  
    *  Title: Built-in Functions
    *  Author: Python 3.9.0 Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.9.0
    *  URL: https://docs.python.org/3/library/functions.html#isinstance
    *  Software License: PSF
    *  
    *  Title: Testing Tools
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/topics/testing/tools/
    *  Software License: BSD-3
    *  
    ***************************************************************************************/
    """

    def setUp(self):
        self.profile = Profile()

        # Set up fields of profile
        self.profile.user
        self.profile.biography = "my bio"
        self.profile.importance_of_collaboration = "8"
        self.profile.openness_to_social_studying = "I'm open to social studying"
        self.profile.time_preference_for_studying = "morning"
        self.profile.personal_strengths = "my strengths"
        self.profile.personal_weaknesses = "my weaknesses"
        self.profile.type_of_learner = "learn by doing"
        self.profile.user_major = "my major"
        self.profile.my_schedule_file = "uploads/2020_Fall.ics"
        self.profile.calendar_data = Calendar.from_ical(self.profile.my_schedule_file.read())
        self.profile.classes_test = PickledObjectField(default=list)

        # read_calendar_info() functionality repeated for testing purposes because read_calendar_info() doesn't return anything
        self.profile.classes_list = []
        for component in self.profile.calendar_data.walk():
            info_dict = {}
            if component.name == "VEVENT":
                info_dict["summary"] = str(component.get('summary'))
                info_dict["description"] = str(component.get('description'))
                info_dict["location"] = str(component.get('location'))
                info_dict["starttime"] = str(component.get('dtstart').dt)
                info_dict["endtime"] = str(component.get('dtend').dt)
                info_dict["rules"] = component.get('rrule')
            self.profile.classes_list.append(info_dict)
        self.profile.classes_test = self.profile.classes_list
        self.profile.stored = True
        self.profile.save()
    
    # Test profile fields: equivalence
    def test_profile_fields_eq(self):                  
        my_profile = Profile.objects.get(pk=self.profile.id)
        self.assertEqual(my_profile, self.profile, "Fields of Profile() and my_profile do not match.")
        
    # Test that calendar info was read in correctly 
    def test_read_calendar_info1(self):     
        self.profile.read_calendar_info()
        self.assertEqual(self.profile.classes_test, self.profile.classes_list, "Calendar info not read in correctly. Info read in was not same as stored info")

    # Test that "summary" (aka class number), "description" (aka class name), 
    # "location", "starttime", and "endtime" were parsed correctly from .ics file
    def test_read_calendar_info2(self):     
        # for each_class in self.profile.classes_list:
        #     print("--start of class info--")
        #     for info in each_class:
        #         print("-----", info+":", each_class[info])
        #     print("--end of class info--\n")
        self.assertEqual(self.profile.classes_list[1]["summary"], "CS 3330", "Class summary parsed from file does not match expected")
        self.assertEqual(self.profile.classes_list[1]["description"], "Computer Architecture", "Class description parsed from file does not match expected")
        self.assertEqual(self.profile.classes_list[1]["location"], "Web-Based Course", "Class location parsed from file does not match expected")
        self.assertEqual(self.profile.classes_list[1]["starttime"], "2020-08-25 17:00:00", "Class start time parsed from file does not match expected")
        self.assertEqual(self.profile.classes_list[1]["endtime"], "2020-08-25 18:15:00", "Class end time parsed from file does not match expected")

    # Test that "rules" was parsed correctly from .ics file
    def test_read_calendar_info3(self):     
        # print(type(self.profile.classes_list[1]["rules"]))
        if isinstance(self.profile.classes_list[1]["rules"], icalendar.prop.vRecur):
            same_type = True
        else:
            same_type = False
        self.assertTrue(same_type, "Type of rules parsed from calendar doesn't match expected")

    # Test that calendar was successfully parsed and returned as a SafeString for HTML
    def test_create_calendar_html1(self):   
        if isinstance(self.profile.create_calendar_html(), SafeString):
            same_type = True
        else:
            same_type = False
        self.assertTrue(same_type, "Didn't successfully get calendar info as SafeString")


# Test Profile model: edge cases (don't want to set up profile fields)
class ProfileTest2(TestCase):

    # Test that the default .ics file, 'uploads/basic.ics', is used if no .ics file is specified
    def test_default_schedule_file(self):   
        self.profile = Profile()
        self.assertEqual(self.profile.my_schedule_file, "uploads/basic.ics", "Default calendar uploads/basic.ics was not used")

    # Test that parsing the default file, which shouldn't have any classes, does not interpret anything as a class
    def test_read_calendar_info8(self):     
        self.profile = Profile()
        self.profile.read_calendar_info()
        # print("\n\n\n\n\n", self.profile.classes)
        self.assertEqual(self.profile.classes, [], "First class in default file, basic.ics, a file of empty classes, was not empty")


# Test SearchPeople and SearchClasses models
class SearchTest(TestCase):

    # Test search people fields
    def test_search_people1(self):          
        self.search_people = SearchPeople() 
        self.search_people.save()           # create an object
        self.search_people.searchChoices = "Search people by class"
        my_search_people = SearchPeople.objects.get(pk=self.search_people.id)
        self.assertEqual(my_search_people, self.search_people, "Field of SearchPeople() and my_search_people do not match.")

    # Test search classes fields
    def test_search_classes1(self):            
        self.search_classes = SearchClasses() 
        self.search_classes.save()
        self.search_classes.searchChoices = "Search by classes"
        my_search_classes = SearchClasses.objects.get(pk=self.search_classes.id)
        self.assertEqual(my_search_classes, self.search_classes, "Field of SearchClasses() and my_search_classes do not match.")


# Test EventCalendar util
class EventCalendarTest(TestCase):
    """
    /***************************************************************************************
    *  REFERENCES
    *  
    *  Title: Datetime — Basic Date and Time Types
    *  Author: Python 3.9.0 Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.9.0
    *  URL: https://docs.python.org/3/library/datetime.html
    *  Software License: PSF
    *  
    *  Title: Re — Regular Expression Operations
    *  Author: Python 3.9.0 Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.9.0
    *  URL: https://docs.python.org/3/library/datetime.html
    *  Software License: PSF
    *  
    ***************************************************************************************/
    """

    def setUp(self):
        self.profile = Profile()
        self.profile.my_schedule_file = "uploads/2020_Fall.ics"
        self.profile.read_calendar_info()
        self.profile.create_calendar_html()
        self.profile.d = datetime.date.today()
        # print(self.profile.d)             # today's date (e.g. 2020-11-04)
        # print(self.profile.d.day)         # today's day  (e.g. 4 for 4th of November)
        # print(self.profile.d.weekday())   # today's weekday (e.g. 2 for Wednesday because 11/4 is on Wed)
        self.cal = EventCalendar()
        self.profile.save()

    # Test that the classes on a day are formatted correctly in HTML
    def test_formatday(self):                   
        html_day = self.cal.formatday(self.profile.d.weekday(), self.profile.classes)
        # print("\n-----", html_day, "------\n")
        # print(self.cal.cssclasses[self.profile.d.weekday()]) # cssclasses[0] is 'mon', cssclasses[6] is 'sun'
        day_format = re.compile(r'(<td style="border: 1px solid" class="[a-z][a-z][a-z]">.*</ul></td>)')
        for match in day_format.finditer(html_day):
            day_format = match.group(1)
            # print(day_format)
        self.assertEqual(html_day, day_format, "Classes on today's day are not formatted correctly")

    # Test that classes for the week are formatted correctly in HTML
    def test_formatweek(self):                  
        html_week = self.cal.formatweek([0, 1, 2, 3, 4, 5, 6], self.profile.classes)
        # print("\n-----",html_week,"\n-----")
        week_format = re.compile(r'(<tr><td style="border: 1px solid" class="[a-z][a-z][a-z]">.*</ul></td></tr>)')
        for match in week_format.finditer(html_week):
            week_format = match.group(1)
            # print(week_format)
        self.assertEqual(html_week, week_format, "Classes on for this week are not formatted correctly")

    # Test that classes for the month (EDIT: changed this function to format the calendar as 1 week) are formattted correctly
    def test_formatmonth(self):                 
        html_month = self.cal.formatmonth(self.profile.d.year, self.profile.d.month, self.profile.classes)
        # print("\n-----",html_month,"\n-----")
        month_format = re.compile(r'(<table style="margin: 20px auto 50px auto" border="0" cellpadding="0" cellspacing="0" class="month"><th class="mon">Mon</th><th class="tue">Tue</th><th class="wed">Wed</th><th class="thu">Thu</th><th class="fri">Fri</th>\n<tr><td style="border: 1px solid" class="[a-z][a-z][a-z]">.*</ul></td></tr>\n</table>\n)')
        for match in month_format.finditer(html_month):
            month_format = match.group(1)
            # print(month_format)
        self.assertEqual(html_month, month_format, "Classes on for this month, in a week format, are not formatted correctly")


# Test views
@override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True)
class ViewsTests(TestCase):
    """
    /***************************************************************************************
    *  REFERENCES
    *  
    *  Title: Advanced Testing Topics
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/topics/testing/advanced/. 
    *  Software License: BSD-3
    *  
    *  Title: Customizing Authentication in Django
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/topics/auth/customizing/
    *  Software License: BSD-3
    *  
    *  Title: Django-Allauth
    *  Author: Raymond Penners
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 0.43.0
    *  URL: https://github.com/pennersr/django-allauth
    *  Software License: MIT
    *  
    *  Title: Django Testing Tutorial - Testing Views #3
    *  Author: The DumbFounds
    *  Date: Published 17 Dec. 2018
    *  Code version: N/A
    *  URL: https://www.youtube.com/watch?v=hA_VxnxCHbo
    *  Software License: N/A
    * 
    *  Title: How to Use Sessions
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/topics/http/sessions/
    *  Software License: BSD-3
    *  
    *  Title: Model Instance Reference
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/ref/models/instances/
    *  Software License: BSD-3
    *  
    *  Title: The Messages Framework
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/ref/contrib/messages/
    *  Software License: BSD-3
    *  
    ***************************************************************************************/
    """

    # Set up integration tests with Google user sign in
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/google/login/callback/')
        self.request.user = AnonymousUser()
        SessionMiddleware().process_request(self.request)
        MessageMiddleware().process_request(self.request)

        User = get_user_model()
        # print("\n-------", User, "\n") # prints <class 'django.contrib.auth.models.User'>
        user = User(username="my_username", email="test@test.com", password="my_password")
        # print("\n-------", user, "\n") # prints my_username

        account = SocialAccount(user=user, provider='google', uid='101')
        # print("\n-------", account) # prints my_username
        sociallogin = SocialLogin(user=user, account=account)
        # print("\n-------", sociallogin) # prints <allauth.socialaccount.models.SocialLogin object at 0x05581190>
        complete_social_login(self.request, sociallogin)


        self.profile = Profile()
        self.profile.my_schedule_file = "uploads/2020_Fall.ics"
        self.profile.twitter_username = "google"
        self.profile.full_clean()
        self.profile.save()

        self.searchpeople = SearchPeople()
        self.searchpeople.full_clean()
        self.searchpeople.save()

        self.searchclasses = SearchClasses()
        self.searchclasses.full_clean()
        self.searchclasses.save()

    # Test update profile GET
    def test_update_profile_view_get(self): 
        request = RequestFactory().get(reverse("edit_profile"))
        request.user = self.request.user
        response = update_profile(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated!")
        self.assertEqual(200, response.status_code, "Did not get correct response for update profile")

    # Test update profile POST
    def test_update_profile_view_post(self): 
        request = RequestFactory().post(reverse("edit_profile"))
        request.user = self.request.user
        response = update_profile(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated!")
        self.assertEqual(200, response.status_code, "Did not get correct response for update profile")

    # Test account view GET
    def test_account_view_get(self):
        # print(self.request.user.username) # my_username
        request = RequestFactory().post(reverse("account", args=[self.request.user.username]))
        request.user = self.request.user
        response = account_view(request, request.user.username)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated!")
        self.assertEqual(200, response.status_code, "Did not get correct response for account view")

    # Test account view Twitter API: equivalence
    def test_account_view_twitter_eq(self):
        request = RequestFactory().post(reverse("account", args=[self.request.user.username]))
        request.user = self.request.user
        response = account_view(request, request.user.username)
        request.user.profile = self.profile

        # Code from account_view()
        user = get_object_or_404(User, username=request.user.username)
        
        consumer_key="Iy1sTDD2qcC5ekypsd4nPrB6n"
        consumer_secret="9A1RIv1aYMKHss83lPRrWV8TSM6NCBS7E8vU0Yl5ec6RYk6PQs"
        access_token="1277681931581358080-AMcKTd0bQapqVA3Xc8Xg7zBPXTEJ4L"
        access_token_secret="PPbEcotacL9325c8qFGfgQKLcio4vSqxXtGPVg3PwxQV7"
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        auth_api = API(auth)
        try:
            item = auth_api.user_timeline(screen_name=request.user.profile.twitter_username, count=3)
        except:
            item = []
        item = "BADBADBAD" if len(item) == 0 else item
        # print(item) # 'item' is all tweets, and will be "BADBADBAD" if tweets not found
        # print(len(item[0])) # 3
        self.assertNotEqual("BADBADBAD", "item", "Tweets not found")
            
    # Test account view Twitter API: edge
    def test_account_view_twitter_edge(self):
        request = RequestFactory().post(reverse("account", args=[self.request.user.username]))
        request.user = self.request.user
        response = account_view(request, request.user.username)
        request.user.profile = self.profile
        request.user.profile.twitter_username = ""

        # Code from account_view
        user = get_object_or_404(User, username=request.user.username)
        
        consumer_key="Iy1sTDD2qcC5ekypsd4nPrB6n"
        consumer_secret="9A1RIv1aYMKHss83lPRrWV8TSM6NCBS7E8vU0Yl5ec6RYk6PQs"
        access_token="1277681931581358080-AMcKTd0bQapqVA3Xc8Xg7zBPXTEJ4L"
        access_token_secret="PPbEcotacL9325c8qFGfgQKLcio4vSqxXtGPVg3PwxQV7"
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        auth_api = API(auth)
        try:
            item = auth_api.user_timeline(screen_name=request.user.profile.twitter_username, count=3)
        except:
            item = []
        item = "BADBADBAD" if len(item) == 0 else item
        # print(item) # 'item' is all tweets, and will be "BADBADBAD" if tweets not found
        self.assertEqual("BADBADBAD", item, "Tweets not found")

    # Test course view GET
    def test_course_view_get(self):
        course = Course()
        course.name = "Advanced Software Development"
        course.course_code = "CS-3240"
        course.start_time = "2020-08-25 14:00:00"
        course.end_time = "2020-08-25 15:15:00"
        course.weekdays = PickledObjectField(default=list)
        course.save()

        request = RequestFactory().get(reverse("courses", args=["CS-3240"]))
        request.user = self.request.user
        response = course_view(request, "CS-3240")
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated!")
        self.assertEqual(200, response.status_code, "Did not get correct response for course view")

    # Test redirect GET
    def test_redirect_view_get(self):              
        request = RequestFactory().get(reverse("login"))
        request.user = self.request.user
        response = redirect(request)
        self.assertEqual(302, response.status_code, "Response was not redirected")

    # Test search people GET
    def test_search_people_view_get(self):
        request = RequestFactory().get(reverse("search_people"))
        request.user = self.request.user
        response = search_people(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated!")
        self.assertEqual(200, response.status_code, "Did not get correct response for search people")

    # Test search classes GET
    def test_search_classes_view_get(self):
        request = RequestFactory().get(reverse("search_classes"))
        request.user = self.request.user
        response = search_classes(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated")
        self.assertEqual(200, response.status_code, "Did not get correct response for search classes")

    # Test search classes POST
    def test_search_classes_view_post(self):
        request = RequestFactory().post(reverse("search_classes"))
        request.user = self.request.user
        response = search_classes(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated")
        self.assertEqual(200, response.status_code, "Did not get correct response for search classes")

    # Test new meeting GET
    def test_new_meeting_get(self):
        request = RequestFactory().get(reverse("new_meeting"))
        request.user = self.request.user
        response = new_meeting(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated")
        self.assertEqual(200, response.status_code, "Did not get correct response for new meeting")

    # Test new meeting POST
    def test_new_meeting_get(self):
        request = RequestFactory().post(reverse("new_meeting"))
        request.user = self.request.user
        response = new_meeting(request)
        self.assertTrue(self.request.user.is_authenticated, "User not authenticated")
        self.assertEqual(200, response.status_code, "Did not get correct response for new meeting")


# Test search people logic (in search_people_result.html)        
class SearchPeopleTests(TestCase):

    def setUp(self):
        #                0         1           2         3       4                      5                               6                            7
        # Format is: [username, first name, last name, major, collaboration level, openness to social studying, time preference for studying, type of learner]
        self.user1 = ["user1", "Johnny", "Appleseed", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        self.user2 = ["user2", "R", "BG", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        self.user3 = ["user3", "Catherine", "Z", "BME", 10, "Focus on school", "Afternoon", "Hands on practice"]
        self.user4 = ["user4", "Barry B.", "Benson", "BME", 9, "Make friends and focus on school", "Afternoon", "Hands on practice"]
        self.user5 = ["user5", "Hello", "Kitty", "CHEM", 9, "Make friends and focus on school", "Afternoon", "Hands on practice"]
        self.users = [self.user1, self.user2, self.user3, self.user4, self.user5]

    # Test search people logic: Major
    def test_search_people_logic1(self):
        current_user = ["user0", "Meta", "pod", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:             # commented parts are the HTML logic
            # {% if user.username != request.user.username and searchChoices == "major" and user.first_name != "" and user.profile.user_major == request.user.profile.user_major %}
            if user[0] != current_user[0] and user[1] != "" and user[3] == current_user[3]:
                search_results.append(user[0]) # append their username
        # print(search_results)
        self.assertEqual(['user1', 'user2'], search_results, "Users 1, 2 (same major as User 0) were not found")

    # Test search people logic: Study time preference
    def test_search_people_logic2(self):
        current_user = ["user0", "Meta", "pod", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:
            # {% elif user.username != request.user.username and searchChoices == "study time preference" and user.first_name != "" and user.profile.time_preference_for_studying == request.user.profile.time_preference_for_studying %}
            if user[0] != current_user[0] and user[1] != "" and user[6] == current_user[6]:
                search_results.append(user[0]) # append their username
        # print(search_results)
        self.assertEqual(['user1', 'user2'], search_results, "Users 1, 2 (same study time preference as User 0) were not found")

    # Test search people logic: Learning type
    def test_search_people_logic3(self):
        current_user = ["user0", "Meta", "pod", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:
            # {% elif user.username != request.user.username and searchChoices == "learning type" and user.first_name != "" and user.profile.type_of_learner == request.user.profile.type_of_learner %}
            if user[0] != current_user[0] and user[1] != "" and user[7] == current_user[7]:
                search_results.append(user[0]) # append their username
        # print(search_results)
        self.assertEqual(['user1', 'user2', 'user3', 'user4', 'user5'], search_results, "Users 1, 2, 3, 4, 5 (same type of learner as User 0) were not found")

    # Test search people logic: Collaboration level
    def test_search_people_logic4(self):
        current_user = ["user0", "Meta", "pod", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:
            # {% elif user.username != request.user.username and searchChoices == "collaboration level" and user.first_name != "" and user.profile.importance_of_collaboration == request.user.profile.importance_of_collaboration %}
            if user[0] != current_user[0] and user[1] != "" and user[4] == current_user[4]:
                search_results.append(user[0]) # append their username
        # print(search_results)
        self.assertEqual(['user1', 'user2', 'user3'], search_results, "Users 1, 2, 3 (same collaboration level as User 0) were not found")

    # Test search people logic: Openness to social studying
    def test_search_people_logic5(self):
        current_user = ["user0", "Meta", "pod", "CS", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:
            # {% elif user.username != request.user.username and searchChoices == "interest in making friends" and user.first_name != "" and user.profile.openness_to_social_studying == request.user.profile.openness_to_social_studying %}
            if user[0] != current_user[0] and user[1] != "" and user[5] == current_user[5]:
                search_results.append(user[0]) # append their username
        # print(search_results)
        self.assertEqual(['user1', 'user2', 'user3'], search_results, "Users 1, 2, 3 (same openness to social studying as User 0) were not found")

    # Test search people logic: Edge case (different major)
    def test_search_people_logic6(self):
        current_user = ["user0", "Meta", "pod", "PSYC", 10, "Focus on school", "Morning", "Hands on practice"]
        search_results = []
        for user in self.users:
            if user[0] != current_user[0] and user[1] != "" and user[3] == current_user[3]:
                search_results.append(user[0])
        # print(search_results)
        self.assertEqual([], search_results, "Did not match expected: should have had no users found with the major PSYC")

    # Test search people logic: Edge case (different study time preference)
    def test_search_people_logic7(self):
        current_user = ["user0", "Meta", "pod", "PSYC", 10, "Focus on school", "Evening", "Hands on practice"]
        search_results = []
        for user in self.users:
            if user[0] != current_user[0] and user[1] != "" and user[6] == current_user[6]:
                search_results.append(user[0])
        # print(search_results)
        self.assertEqual([], search_results, "Did not match expected: should have had no users found with the study time preference Evening")

    # Test search people logic: Edge case (different learning type)
    def test_search_people_logic7(self):
        current_user = ["user0", "Meta", "pod", "PSYC", 10, "Focus on school", "Evening", "Visual"]
        search_results = []
        for user in self.users:
            if user[0] != current_user[0] and user[1] != "" and user[7] == current_user[7]:
                search_results.append(user[0])
        # print(search_results)
        self.assertEqual([], search_results, "Did not match expected: should have had no users found with learning type Visual")

    # Test search people logic: Edge case (different collaboration level)
    def test_search_people_logic8(self):
        current_user = ["user0", "Meta", "pod", "PSYC", 1, "Focus on school", "Evening", "Visual"]
        search_results = []
        for user in self.users:
            if user[0] != current_user[0] and user[1] != "" and user[4] == current_user[4]:
                search_results.append(user[0])
        # print(search_results)
        self.assertEqual([], search_results, "Did not match expected: should have had no users found with collaboration level 1")

    # Test search people logic: Edge case (different opennes to social studying)
    def test_search_people_logic9(self):
        current_user = ["user0", "Meta", "pod", "PSYC", 1, "Make friends", "Evening", "Visual"]
        search_results = []
        for user in self.users:
            if user[0] != current_user[0] and user[1] != "" and user[5] == current_user[5]:
                search_results.append(user[0])
        # print(search_results)
        self.assertEqual([], search_results, "Did not match expected: should have had no users found with openness to social studying 'Make friends")


# Test forms
@override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True)
class FormsTests(TestCase):
    """
    /***************************************************************************************
    *  REFERENCES
    *  
    *  Title: How to Unit Test a Django Form
    *  Author: Adam Johnson
    *  Date: 15 Jun. 2020
    *  Code version: N/A
    *  URL: https://adamj.eu/tech/2020/06/15/how-to-unit-test-a-django-form/
    *  Software License: N/A
    *  
    *  Title: The Forms API
    *  Author: Django Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.1
    *  URL: https://docs.djangoproject.com/en/3.1/ref/forms/api/#binding-uploaded-files-to-a-form
    *  Software License: BSD-3
    *  
    *  Title: Urllib.Parse — Parse URLs into Components
    *  Author: Python 3.9.0 Documentation
    *  Date: Accessed 19 Nov. 2020
    *  Code version: 3.9.0
    *  URL: https://docs.python.org/3/library/urllib.parse.html
    *  Software License: PSF
    *  
    ***************************************************************************************/
    """

    # Set up integration tests with Google user sign in
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/google/login/callback/')
        self.request.user = AnonymousUser()
        SessionMiddleware().process_request(self.request)
        MessageMiddleware().process_request(self.request)

        User = get_user_model()
        user = User(username="my_username", email="test@test.com", password="my_password")

        account = SocialAccount(user=user, provider='google', uid='101')
        sociallogin = SocialLogin(user=user, account=account)
        complete_social_login(self.request, sociallogin)

        self.profile = Profile()
        self.profile.my_schedule_file = "uploads/2020_Fall.ics"
        self.profile.full_clean()
        self.profile.save()

        self.searchpeople = SearchPeople()
        self.searchpeople.full_clean()
        self.searchpeople.save()

        self.searchclasses = SearchClasses()
        self.searchclasses.full_clean()
        self.searchclasses.save()

    # Test validate_name: equivalence 
    def test_validate_name_eq(self):
        try:
            is_valid_bool = True
            # print("\n eq", is_valid_bool)
            validate_name('my_user')
        except:
            is_valid_bool = False
            # print("\n eq", is_valid_bool)
        self.assertTrue(is_valid_bool, "Does not match expected: name should be valid")
   
    # Test validate_name: exception thrown (username cannot be search or any of the keywords we define) 
    def test_validate_name_edge(self):
        try:
            is_valid_bool = True
            # print("\n edge", is_valid_bool)
            validate_name('search')
        except:
            is_valid_bool = False
            # print("\n edge", is_valid_bool)
        self.assertFalse(is_valid_bool, "Does not match expected: name should not be valid")

    # Test UserForm: equivalence
    def test_user_form_eq(self):
        user_form_data = {
            'username':'my_new_user',
            'first_name':'my_first_name',
            'last_name':'my_last_name'
            }
        user_output = UserForm(user_form_data)
        # print("\n", user_output, "\n")
        self.assertTrue(user_output.is_valid(), "Form was not valid")

    # Test UserForm: edge (username already exists)
    def test_user_form_edge1(self):
        user_form_data = {
            'username':'my_username',       # This username already exists
            'first_name':'my_first_name',
            'last_name':'my_last_name'
            }
        user_output = UserForm(user_form_data)
        self.assertFalse(user_output.is_valid(), "Form was considered valid even though username already exists in system")

    # Test UserForm: edge (missing a first name)
    def test_user_form_edge2(self):
        user_form_data = {
            'username':'my_new_user',
            'first_name':'',                # First name not specified
            'last_name':'my_last_name'
            }
        user_output = UserForm(user_form_data)
        self.assertFalse(user_output.is_valid(), "Form was considered valid even though no first name was specified")

    # Test ProfileForm: equivalence
    def test_profile_form_eq(self):
        profile_form_data = {
            'biography':'my_bio',
            'user_major':'my_major',
            'personal_strengths':'my_strengths',
            'personal_weaknesses':'my_weaknesses',
            'importance_of_collaboration':10,
            'openness_to_social_studying':'Make friends and focus on school!',
            'time_preference_for_studying':'Afternoon',
            'type_of_learner':'Visual',
            'twitter_username':'my_twitter_handle'
            }
        fi = open('uploads/2020_Fall.ics', 'rb')    # Using FileFields with forms requires binding file data to form as second arg
        file_data = {'my_schedule_file': SimpleUploadedFile('uploads/2020_Fall.ics', fi.read())}
        profile_output = ProfileForm(profile_form_data, file_data)
        # print("\n", profile_output, "\n")
        self.assertTrue(profile_output.is_valid(), "Form was not valid")

    # Test ProfileForm: edge (bio not specified)
    def test_profile_form_edge1(self):
        profile_form_data = {
            'biography':'',                         # bio not specified
            'user_major':'my_major',
            'personal_strengths':'my_strengths',
            'personal_weaknesses':'my_weaknesses',
            'importance_of_collaboration':10,
            'openness_to_social_studying':'Make friends and focus on school!',
            'time_preference_for_studying':'Afternoon',
            'type_of_learner':'Visual',
            'twitter_username':'my_twitter_handle'
            }
        fi = open('uploads/2020_Fall.ics', 'rb')
        file_data = {'my_schedule_file': SimpleUploadedFile('uploads/2020_Fall.ics', fi.read())}
        profile_output = ProfileForm(profile_form_data, file_data)
        self.assertFalse(profile_output.is_valid(), "Form was oonsidered valid even though a bio was not specified")

    # Test ProfileForm: edge (optional twitter handle not specified)
    def test_profile_form_edge2(self):
        profile_form_data = {
            'biography':'my_bio',
            'user_major':'my_major',
            'personal_strengths':'my_strengths',
            'personal_weaknesses':'my_weaknesses',
            'importance_of_collaboration':10,
            'openness_to_social_studying':'Make friends and focus on school!',
            'time_preference_for_studying':'Afternoon',
            'type_of_learner':'Visual',
            }
        fi = open('uploads/2020_Fall.ics', 'rb')
        file_data = {'my_schedule_file': SimpleUploadedFile('uploads/2020_Fall.ics', fi.read())}
        profile_output = ProfileForm(profile_form_data, file_data)
        self.assertTrue(profile_output.is_valid(), "Form was not valid, even though the twitter handle is optional")

    # Test SearchPeopleForm: Search for people by major
    def test_search_people_form_by_major(self):
        form_data = {
            'searchChoices':"major"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs) # {'data': 'searchChoices=major'}
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data) # major
        s = SearchPeople.objects.all()  # s is a QuerySet
        # print(s[0].searchChoices)       # s[0] is first item in QuerySet, default search choice is by major
        self.assertEqual(s[0].searchChoices, search_choices_data, "Did not search by major")

    # Test SearchPeopleForm: Search for people by learning type
    def test_search_people_form_by_learning_type(self):
        form_data = {
            'searchChoices':"learning type"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs) # {'data': 'searchChoices=learning+type'}
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("learning type", search_choices_data, "Did not search by learning type")

    # Test SearchPeopleForm: Search for people by interest in making friends
    def test_search_people_form_by_interest_in_making_friends(self):
        form_data = {
            'searchChoices':"interest in making friends"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs)
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("interest in making friends", search_choices_data, "Did not search by interest in making friends")

    # Test SearchPeopleForm: Search for people by collaboration level
    def test_search_people_form_by_collaboration_level(self):
        form_data = {
            'searchChoices':"collaboration level"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs)
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("collaboration level", search_choices_data, "Did not search by collaboration level")

    # Test SearchPeopleForm: Search for people by study time preference
    def test_search_people_form_by_study_time_preference(self):
        form_data = {
            'searchChoices':"study time preference"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs)
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("study time preference", search_choices_data, "Did not search by study time preference")

    # Test SearchPeopleForm: Search for people by classes
    def test_search_people_form_by_classes(self):
        form_data = {
            'searchChoices':"classes"
            }
        output = SearchPeopleForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_people(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs)
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("classes", search_choices_data, "Did not search by classes")

    # Test SearchClassesForm: Search with CS-3240
    def test_search_classes_form(self):
        form_data = {
            'searchChoices':"CS-3240"
            }
        output = SearchClassesForm(form_data)
        # print("\n", output, "\n")
        self.assertTrue(output.is_valid())
        request = RequestFactory().get('/search/{{urllib.parse.urlencode(output.cleaned_data)}}')
        request.user = self.request.user
        v = search_classes(request)
        v.request = request
        v.kwargs = {'data':urllib.parse.urlencode(output.cleaned_data)}
        # print(v.kwargs)
        if 'data' in v.kwargs:
            if 'searchChoices' in urllib.parse.parse_qs(v.kwargs['data']):
                search_choices_data = urllib.parse.parse_qs(v.kwargs['data'])['searchChoices'][0]
                # print(search_choices_data)
        self.assertEqual("CS-3240", search_choices_data, "Did not search by CS-3240")

    # Test MeetingForm
    def test_meeting_form(self):
        course = Course()
        course.name = "Advanced Software Development"
        course.course_code = "CS-3240"
        course.start_time = "2020-08-25 14:00:00"
        course.end_time = "2020-08-25 15:15:00"
        course.weekdays = PickledObjectField(default=list)
        course.save()

        meeting_form_data = {
            'course':course,
            'who':'Me',
            'when':'12:30 AM, 11-12-2020',
            'why':'To study for the upcoming exam',
            'where':'https://join.skype.com/rdbG7ClZH3QI',
            'subject': 'Exam prep'
            }
        meeting_output = MeetingForm(meeting_form_data)
        # print("\n", meeting_output, "\n")
        self.assertTrue(meeting_output.is_valid(), "Form was not valid")

