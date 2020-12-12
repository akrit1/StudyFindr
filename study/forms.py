from django.contrib.auth.models import User
from django import forms
from .models import Profile, SearchPeople, SearchClasses, Meeting, Course
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.utils.safestring import mark_safe
from django.core.validators import URLValidator

def validate_name(value):
    if (value.lower() in ['search', 'search_people', 'search_classes', 'edit_profile', 'admin', 'accounts', 'login', 'signup', 'meeting', 'new_meeting']) or 'courses' in value.lower() or '/' in value.lower() or '.' in value.lower() or '#' in value.lower() or '%' in value.lower():
        raise ValidationError(
            _('This username is not allowed!'),
            params={'value': value},
        )

class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Usernames are not case-sensitive", max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}), validators=[validate_name])
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def clean_username(self):
        data = self.cleaned_data['username'].lower()
        return data

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class ProfileForm(forms.ModelForm):
    # /***************************************************************************************
    # *  REFERENCES
    # *  Title: "Create An Edit Profile Page"
    # *  Author: Codemy.com
    # *  Date: Jun 11, 2020
    # *  Code version: N/A
    # *  URL: https://www.youtube.com/watch?v=R6-pB5PAA6s
    # *  Software License: N/A
    # ***************************************************************************************/
    biography = forms.CharField(max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 5, 'class': 'form-control'}))
    user_major = forms.CharField(max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    personal_strengths = forms.CharField(max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    personal_weaknesses = forms.CharField(max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    importance_of_collaboration = forms.IntegerField(help_text="On a scale of 1 to 5, how important is a collaborative environment to you?", widget=forms.NumberInput(attrs={'type': 'range', 'step': '1', 'min' : '1', 'max' : '5'}), required =True) #, choices=CHOICES)
    openness_to_social_studying = forms.ChoiceField(label="Social/Academic Preference", choices=(("Focus on school!", "Focus on school"), ("Make friends!", "Make friends"), ("Make friends and focus on school!", "Make friends and focus on school")), required =True)
    time_preference_for_studying = forms.ChoiceField(choices=(('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening')), required=True)
    type_of_learner = forms.ChoiceField(choices=(('Visual', 'Visual'), ('Auditory', 'Auditory'), ('Hands on practice', 'Hands on practice')), required=True)
    
    my_schedule_file = forms.FileField(help_text=mark_safe('Upload an ICS file of your schedule -- available at <a href="https://sisuva.admin.virginia.edu/ihprd/signon.html" target="_blank">  UVA SIS </a> (select <i>Download Schedule</i> from the top-right corner of <i>My Schedule</i>)'), widget=forms.FileInput(attrs={'accept': '.ics', 'class': 'form-control'}))
    
    twitter_username = forms.CharField(help_text='Livestream your recent tweets on your profile page. Other students can view/contact your twitter account if enabled.', required=False, label="Twitter username (optional)", max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['biography', 'user_major', 'type_of_learner', 'openness_to_social_studying', 'importance_of_collaboration', 'personal_strengths', 'personal_weaknesses', 
        'time_preference_for_studying', 'my_schedule_file', 'twitter_username']

class SearchPeopleForm(forms.ModelForm): 
    searchChoices = forms.ChoiceField(choices=(("major", "major"), ("learning type", "learning type"), ("interest in making friends", "interest in making friends"), ("collaboration level", "collaboration level"), ("study time preference", "study time preference"), ("classes", "classes")), label="Find students with the same", widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model= SearchPeople
        fields = ['searchChoices']

class SearchClassesForm(forms.ModelForm):
    searchChoices= forms.CharField(max_length=100, help_text="Search for classes by name or department code (ex: CS-3240)", label="Find this class:", widget=forms.TextInput(attrs={'cols': 1, 'rows': 1, 'class': 'form-control'}))
    class Meta: 
        model= SearchClasses
        fields = ['searchChoices']

def validate_date(value):
    try:
        datetime.strptime(value, '%I:%M %p, %m-%d-%Y')
    except ValueError:
        raise ValidationError(
            _('This date is invalid!'),
            params={'value': value},
        )

def validate_url(value):
    try:
        temp = URLValidator()(value) if 'http' in value else URLValidator()('https://' + value)
    except:
        raise ValidationError(
            _('This link is invalid!'),
            params={'value': value},
        )

class CourseModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.course_code + ': ' + obj.name

class MeetingForm(forms.ModelForm):
    try:
        course = CourseModelChoiceField(queryset=Course.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    except:
        course = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    who = forms.CharField(label='Hosts', max_length=50, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    when = forms.CharField(initial=datetime.now().strftime("%I:%M %p, %m-%d-%Y"), widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}), validators=[validate_date])
    why = forms.CharField(initial='What will you discuss? How long will it take?', label='About', max_length=800, widget=forms.Textarea(attrs={'cols': 10, 'rows': 5, 'class': 'form-control'}))
    subject = forms.CharField(initial='What is this study session about?', label='Subject', max_length=100, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    where = forms.CharField(validators=[validate_url], help_text=mark_safe('For a free video-chat link, try visiting <a href="https://www.skype.com/en/free-conference-call/" target="_blank">this website<a/>.'), label='Link', max_length=50, widget=forms.Textarea(attrs={'cols': 10, 'rows': 1, 'class': 'form-control'}))
    class Meta:
        model = Meeting
        fields= ["course", "who", "when", "subject", "why", "where"]