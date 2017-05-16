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

import json
import urllib
import os


def hello(request):
    hello = "Welcome to Huddle!"
    return render(request, 'hello.html', {'hello':hello})

def home(request):
    hello = "Welcome to Huddle!"
    return render(request, 'home.html', {'home':hello})

class eventList(ListView):
    model = event

class userList(ListView):
    model = user

class charityList(ListView):
    model = charity

class charitycontactList(ListView):
    model = charitycontact

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@csrf_exempt
def webhook(request):

    if request.method == "POST":
        req = request.body
        data = json.loads(req)
        print(data)
        res = makeWebhookResult(data)
        res = json.dumps(res, indent=4)
        print(res)
        return HttpResponse(res)

    else:
        print('Hello')

@csrf_exempt
def makeWebhookResult(request):

    result = request.get("result")
    parameters = result.get("parameters")
    originalRequest = request.get("originalRequest")
    data = originalRequest.get("data")
    sender = data.get("sender")
    fb_id = sender.get("id")

    # Checks for greeting action
    if request.get("result").get("action") == "volunteer.new":

        try:
            u = user.objects.get(facebook_id=fb_id)

        except user.DoesNotExist:
            speech = "You dont yet exist in my database"
            u1 = user(facebook_id=fb_id)
            u1.save()
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                # "contextOut": [],
                "source": "apiai-onlinestore-shipping"
            }

        else:
            speech = "Welcome back " + str(fb_id) + "! When can you volunteer?"
            contextOut = "volunteer_timedate"
            sending_message = return_message(speech, contextOut)
            return sending_message
            # return {
            #     "speech": speech,
            #     "displayText": speech,
            #     #"data": {},
            #     "contextOut": [{"name":contextOut, "lifespan":5, "parameters":{}}],
            #     "source": "apiai-onlinestore-shipping"
            # }

    if request.get("result").get("action") == "volunteer.assign":

        # Get a bunch of information from the JSON
        day = parameters.get("date")
        when = parameters.get("time")
        dur = parameters.get("duration")
        location = parameters.get("location")

#        date = datetime.strptime()
        available_time = str(day) + " " + str(when)
        datetime_object = datetime.strptime(available_time, '%Y-%m-%d %H:%M:%S')
        early_start = datetime_object + timedelta(hours=-2)
        print("early_start = " + str(early_start))
        late_start = datetime_object + timedelta(hours=2)
        print("late_start = " + str(late_start))
        print (datetime_object)


        # Go and check for an event based on user input
        try:
#            e = event.objects.filter(start=day).order_by("name").values_list('name')
            e = event.objects.filter(start__gte=early_start, start__lte=late_start)[0]

        except event.DoesNotExist:
            speech = "Sorry, there's no event at that day and time :(. Maybe suggest another day?"
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"volunteer_timedate", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

        except IndexError:
            speech = "Sorry, there's no event at that day and time :(. Maybe suggest another day?"
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"volunteer_timedate", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

        else:
            print(e)
            speech = "Great! We have an opportunity on " + day + " called " + str(e) + ". I can give you any details you want (charity, location, time, date, opportunity etc), just ask!"

            print("Response:")
            print(speech)

            userevent=event.objects.get(start__gte=early_start, start__lte=late_start)
            userevent.volunteer = fb_id
            userevent.save()

            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_date":
        get_message_details(request)

        try:
            eventdate = parameters.get("event-date")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
            speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B'))
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_starttime":
        get_message_details(request)

        try:
            eventstarttime = parameters.get("event-start-time")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
            speech = "It starts at " + str(e.strftime('%I.%M %p'))
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_endtime":
        get_message_details(request)

        try:
            eventendtime = parameters.get("event-end-time")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('end', flat=True)[0]
            speech = "It ends at " + str(e.strftime('%I.%M %p'))
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_duration":

        get_message_details(request)

        try:
            eventduration = parameters.get("event-duration")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('duration', flat=True)[0]
            speech = str(e) + " hours"
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_location":
        get_message_details(request)

        try:
            eventlocation = parameters.get("event-location")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('address', flat=True)[0]
            f = event.objects.filter(volunteer=fb_id).values_list('postcode', flat=True)[0]
            speech = str(e) + ', ' + str(f)
            print (speech)
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_description":
        get_message_details(request)

        try:
            eventduration = parameters.get("event-description")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('details', flat=True)[0]
            speech = str(e)
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

    if request.get("result").get("action") == "details_charityname":
        get_message_details(request)

        try:
            eventduration = parameters.get("event-charity-name")

        except:
            pass

        else:
            e = event.objects.filter(volunteer=fb_id).values_list('charity', flat=True)[0]
            speech = str(e)
            return {
                "speech": speech,
                "displayText": speech,
                #"data": {},
                "contextOut": [{"name":"confirm_event", "lifespan":5, "parameters":{}}],
                "source": "apiai-onlinestore-shipping"
            }

def return_message(speech, contextOut):
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        "contextOut": [{"name":contextOut, "lifespan":5, "parameters":{}}],
        "source": "apiai-onlinestore-shipping"
    }
