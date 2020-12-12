# StudyFindr
https://team206.herokuapp.com/  
Welcome to StudyFindr! This app helps University of Virginia students easily find friends and form meetings for studying purposes.
## Background
We recognized that it can be difficult for UVA students to form studying connections during a virtual semester that is unlike any other. This virtual study buddy finder app connects users according to their major, learning type, openness to social studying, how much they value collaboration, personal strengths, personal weaknesses, preferred time to study, and course schedule. 
## Major software
- This project incorporates a third-party Twitter API, Tweepy, as a feature of a user's Profile page. Twitter direct messages serve as the primary means for users to contact one another. 
- This project was built using the prescribed language (Python 3), framework (Django 3.1), build environment (Travis CI), source control management (GitHub), and cloud hosting (Heroku). 
- PostgreSQL was used as the database engine. 
## Usage
### Logging in and Site Navigation
Users can log in with either: (1) an email in the virginia.edu domain or (2) a Gmail account. After logging in, users can navigate the app using the navigation bar across the top. Click on the search glass to search for people and classes. Click on the hamburger menu button to reveal a dropdown menu to go to your Profile page, create a new study session, or sign out. 
### The Profile page
Users can edit their Profile with their username, first and last names, biography, major, learning type, openness to social studying, how much they value collaboration, personal strengths and weaknesses, and preferred time to study. 
#### Downloading the iCalendar file (.ics) from UVA SIS
1. Navigate to UVA SIS and login: https://www.virginia.edu/sis/
2. In SIS, expand the hamburger menu on the left side of the screen, and click on the 'My Schedule' option. 
3. You should see the My Schedule page. Click the 'Download Schedule' button and select the current term from the dropdown menu.   
4. From the Edit Profile page, users can upload their .ics file. After saving changes, their Profile page will be populated with the classes they are in. 
#### Specifying a Twitter account
While optional, specifying a Twitter account on your Profile page can be useful. Twitter serves as the primary form of communication between users of this app. When you specify a Twitter handle, other users will be able to see your handle on your Profile and get in touch with you via Twitter direct messages. This is how you can make study buddies. The Recent Tweets section of the Profile page displays the three most recent tweets from the specified Twitter account. 
### The Search People page
The Search People page can be accessed from the search glass button in the upper left corner. Select 'Find students' from the dropdown menu.  
The Search People page uses the fields that you filled out on your Profile page and compares them to the Profiles of other users of the app. Users can search for others with the same major, learning type, openness to social studying, collaboration level, study time preference, and classes.
### The Search Classes page
The Search Classes page can be accessed from the search glass button in the upper left corner. Select 'Find classes' from the dropdown menu.  
The Search Classes page works differently than the Search People page. The Search Classes page searches based on user-entered text rather than selecting an option from a dropdown menu. Users can search by course code department (e.g. 'CS'), course code number (e.g. '3240'), or course name (e.g. Advanced Software Development).
### The Create Study Session page
The Create Study Session page can be accessed from the hamburger menu button in the upper right corner. Select 'New study session' from the dropdown menu.  
Users can specify the course the meeting is for, the host, when the meeting is, what the meeting is about, and a link to the meeting. 
#### Changing the Link field
1. Click on the hyperlink next to the Link field that says 'this website'. 
2. Click the 'Create a free meeting' button and copy the meeting link.
3. Navigate back to the StudyFindr app. Paste the meeting link into the Link field. 
4. After saving changes, the class meeting page has now been updated with the meeting you created! After saving these changes to the Create Study Session page, any user can click on the 'Join study session' button to participate in a study session. 
# Authors
This app was developed by:
Akrit Sinha, Alexander Stiles, Isabel Ullman, Catherine Zhao