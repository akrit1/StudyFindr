from calendar import HTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
 
# /***************************************************************************************
# * Code adapted from:
# *  REFERENCES
# *  Title: Django and Python calendar
# *  Author: Pawel Grajewski
# *  Date: Oct 12, 2019
# *  Code version: N/A
# *  URL: https://medium.com/@unionproject88/django-and-python-calendar-e647a8eccff6
# *  Software License: N/A
# *
 
class EventCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events
 
    def formatday(self, weekday, events):
        """
        Return a day as a table cell.
        """
        events_html = "<ul style='list-style-type:none;'>"

        for event in events:
            if(event.get('rules')):
                int_day = []
                string_day = event.get('rules').get('BYDAY')
                if 'MO' in string_day:
                    int_day.append(0)
                if 'TU' in string_day:
                    int_day.append(1)
                if 'WE' in string_day:
                    int_day.append(2)
                if 'TH' in string_day:
                    int_day.append(3)
                if 'FR' in string_day:
                    int_day.append(4)
                if weekday in int_day:
                    events_html += "<li><a href='/courses/" + (event.get('summary').replace(' ', '-')) + "'>" + (event.get('summary').replace(' ', '-')) + "</a></li>"
        events_html += "</ul>"
        return '<td style="border: 1px solid" class="%s">%s</td>' % (self.cssclasses[weekday], events_html)
 
    def formatweek(self, theweek, events):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(wd, events) for wd in theweek)
        return '<tr>%s</tr>' % s
 
    def formatmonth(self, theyear, themonth, events, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table style="margin: 20px auto 50px auto" border="0" cellpadding="0" cellspacing="0" class="month">')
        a(self.formatweekday(0))
        a(self.formatweekday(1))
        a(self.formatweekday(2))
        a(self.formatweekday(3))
        a(self.formatweekday(4))
        a('\n')
        
        week = [0, 1, 2, 3, 4]
        # for week in self.monthdays2calendar(theyear, themonth):
            # print(week)
        a(self.formatweek(week, events))
        a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)