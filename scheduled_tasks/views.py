from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from events.models import user, charity, charitycontact, event
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from datetime import datetime, timedelta
from django.forms import ModelForm
from .forms import eventForm

import json
import urllib
import urllib.request
import os
import ast
import schedule
import time
import sys

from django.shortcuts import render

FB_PAGE_ACCESS_TOKEN = "EAAElJTd6foABAPkRNGlNHy6mxt277aJN8Yy4scRl4ViKYetPmlyZCPdbD3ZCcPt0uoANv61pZCeDDbdp20X7ukn8jZA6tX655ZBUAHDuMEg6luyGpXU3VcFaxK5ZC3DDCjhRptTZCDIIlqtW9ZBUE5WMPdPZBmvwirZCsPR1vvWoQgZAQZDZD"

def send_message():

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    early_start = current_time
    late_start = datetime_object + timedelta(hours=24)

    events_today = event.objects.filter(start__gte=early_start, start__lte=late_start).values_list('volunteer',flat=True)
    for volunteer in events_today:
        speech = "Your event is today! Just thought I'd check in and make sure you were still planning on coming along?"

        params = {
            "access_token": FB_PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": volunteer
            },
            "message": {
                "text": speech
            }
        })
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)


# # Create your views here.
# def volunteer_today():
#
#     current_time = time.strftime("%Y-%m-%d %H:%M:%S")
#     early_start = current_time
#     late_start = datetime_object + timedelta(hours=24)
#     print("late_start = " + str(late_start))
#
#     events_today = event.objects.filter(start__gte=early_start, start__lte=late_start).values_list('volunteer',flat=True)
#     if events_today:
#         for volunteer in events_today:
#             speech = "Your event is today! Just thought I'd check in and make sure you were still planning on coming along?"
#             contextOut = ""
#             sending_message = return_message(speech, contextOut)
#             return sending_message
#             res = sending_message
#             res = json.dumps(res, indent=4)
#             print(res)
#             return HttpResponse(res)

# def return_message(speech, contextOut):
#     return {
#         "speech": speech,
#         "displayText": speech,
#         #"data": {},
#         "contextOut": [{"name":contextOut, "lifespan":5, "parameters":{}}],
#         "source": "apiai-onlinestore-shipping"
#     }
