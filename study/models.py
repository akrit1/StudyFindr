from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.urls import reverse
from icalendar import Calendar, Event
from .utils import EventCalendar
from django.utils.safestring import mark_safe
from picklefield.fields import PickledObjectField
import datetime

class Course(models.Model):
    name = models.TextField(max_length=100, default='Unnamed Course')
    course_code = models.TextField(max_length=10, default='CS-1110')
    start_time = models.TextField(max_length=50, default='2020-08-25 14:00:00')
    end_time = models.TextField(max_length=50, default='2020-08-25 15:15:00')
    weekdays = PickledObjectField(default=list)

class Meeting(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    who = models.CharField(max_length=200)
    where = models.TextField(max_length=100)
    when = models.TextField()
    why = models.TextField(max_length=800)
    subject = models.TextField(max_length=100, default="")

class Profile(models.Model):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "Create An Edit Profile Page"
    # *  Author: Codemy.com
    # *  Date: Jun 11, 2020
    # *  Code version: N/A
    # *  URL: https://www.youtube.com/watch?v=R6-pB5PAA6s
    # *  Software License: N/A
    # *  
    # *  Title: "Extraction of Tweets using Tweepy"
    # *  Author: GeeksForGeeks
    # *  Date: May 30, 2018
    # *  Code version: N/A
    # *  URL: https://www.geeksforgeeks.org/extraction-of-tweets-using-tweepy/
    # *  Software License: N/A
    # *
    # *  Title: "Making Queries"
    # *  Author: Django 
    # *  Date: Accessed November 16, 2020 
    # *  Code version: 3.1
    # *  URL: https://docs.djangoproject.com/en/3.1/topics/db/queries/
    # *  Software License: BSD-3
    # ***************************************************************************************/
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    biography = models.TextField(max_length=800, blank=True, default='Tell us about yourself!')
    importance_of_collaboration = models.IntegerField(default='2')
    openness_to_social_studying = models.CharField(max_length = 100, default="Make friends!")
    time_preference_for_studying = models.CharField(max_length = 20, default='Morning')
    personal_strengths = models.TextField(max_length=800, blank=True, default='What are you confident in?')
    personal_weaknesses = models.TextField(max_length=800, blank=True, default='What are you weak in?')
    type_of_learner = models.CharField(max_length=25, default='Visual')
    user_major = models.TextField(max_length=100, default="Undeclared")
    twitter_username = models.CharField(max_length=40, default="", blank=True)

    my_schedule_file = models.FileField(upload_to = 'uploads/', default="uploads/basic.ics")
    # to access the file, we need to go to uploads and then use the my_schedule_file.get_name()

    #pickledobjectfield allows storage of complex things (this will store an array of dicts)
    classes = PickledObjectField(default=list)

    class_name = PickledObjectField(default=list)

    def __str__(self):
        return self.user.username
        
    def read_calendar_info(self):
        if 'basic.ics' in self.my_schedule_file.name:
            return
        # try to read ics file, save to permanent storage (only needs to run when ics file is first uploaded)
        try:
            calendar_data = Calendar.from_ical(self.my_schedule_file.read())
        except: 
            return
        classes = []
        class_name = []
        for component in calendar_data.walk():
            info_dict = {}
            if component.name == "VEVENT":
                info_dict["summary"] = str(component.get('summary'))
                if str(component.get('summary')) not in class_name:
                    class_name.append(str(component.get('summary')))
                info_dict["description"] = str(component.get('description'))
                info_dict["location"] = str(component.get('location'))
                info_dict["starttime"] = str(component.get('dtstart').dt)
                info_dict["endtime"] = str(component.get('dtend').dt)
                info_dict["rules"] = component.get('rrule')
            classes.append(info_dict)

        #if the course does not exist in course list, add it --> this is for search by class page
        for course in classes:
            seen = False
            for already_added in Course.objects.all():
                if course.get('summary') and (course.get("summary").replace(' ', '-') == already_added.course_code):
                    seen = True
            if(course and not seen):
                Course.objects.create(course_code=course.get("summary").replace(' ', '-'), name=course.get("description"), start_time=course.get("starttime"), end_time=course.get("endtime"), weekdays=course.get('rules').get('BYDAY'))
        self.classes = classes
        self.class_name = [c.replace(' ', '-') for c in class_name]
        self.save()

    def create_calendar_html(self):
        d = datetime.date.today()
        cal = EventCalendar()
        html_calendar = cal.formatmonth(d.year, d.month, self.classes, withyear=True)
        html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')
        return mark_safe(html_calendar)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except:
        Profile.objects.create(user=instance)

class SearchPeople(models.Model):
    searchChoices = models.CharField(max_length = 100, default="major")
    
class SearchClasses(models.Model):
    searchChoices= models.TextField(max_length=100, blank=True, default='CS-3240')