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


FB_PAGE_ACCESS_TOKEN = "EAAElJTd6foABAPkRNGlNHy6mxt277aJN8Yy4scRl4ViKYetPmlyZCPdbD3ZCcPt0uoANv61pZCeDDbdp20X7ukn8jZA6tX655ZBUAHDuMEg6luyGpXU3VcFaxK5ZC3DDCjhRptTZCDIIlqtW9ZBUE5WMPdPZBmvwirZCsPR1vvWoQgZAQZDZD"

# A little welcome page that calls an html file as a placeholder
def hello(request):
    hello = "Welcome to Huddle!"
    return render(request, 'hello.html', {'hello':hello})

# A little homepage that gives a list of things to view, either events, users, charities, or charity contacts
def home(request):
    hello = "Welcome to Huddle!"
    return render(request, 'home.html', {'home':hello})

# def form(request):
#     return render(request, 'form.html')

@csrf_exempt
def add_event(request):
    form = eventForm()
    return render(request, 'add_event.html', {'form': form})

    if request.method == "POST":
        form = eventForm(request.POST)
        if form.is_valid():
            # u1 = user(facebook_id="123456789")
            # u1.first_name = "Test"
            # u1.last_name = "Mackie"
            # u1.save()
            event = form.save(commit=True)
#            event.volunteer = ''
#            event.confirmed = 'n'
            return redirect('/home')

        else:
            return ("The form was not valid")
    else:
        return ("The request method does not equal POST")
        return render(request, 'add_event.html', {'form': form})


# Create the form class.
# class eventForm(ModelForm):
#     class Meta:
#         model = event
#         fields = ['name', 'details', 'address', 'city', 'postcode', 'start', 'end', 'duration', 'charity']
#         form = eventForm()
#         form.save()

# The list of events from the database
class eventList(ListView):
    model = event

# The list of users from the database
class userList(ListView):
    model = user

# The list of charities from the database
class charityList(ListView):
    model = charity

# The list of charity contacts from the database
class charitycontactList(ListView):
    model = charitycontact

# This is how a user signs up on the website
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

# This is the wrapper for sending the webhook to api.ai
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

#This is the creation of the webhook result based on which 'action' is sent by api.ai - ie where in the conversation you are
@csrf_exempt
def makeWebhookResult(request):
    result = request.get("result")
    parameters = result.get("parameters")
    originalRequest = request.get("originalRequest")
    data = originalRequest.get("data")
    sender = data.get("sender")
    fb_id = sender.get("id")
    user_profile = urllib.request.urlopen("https://graph.facebook.com/v2.6/" + fb_id + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + FB_PAGE_ACCESS_TOKEN).read().decode()
    user_profile = ast.literal_eval(user_profile)
    first_name = user_profile['first_name']
    last_name = user_profile['last_name']
    profile_pic = user_profile['profile_pic']
    locale = user_profile['locale']
    timezone = user_profile['timezone']
    gender = user_profile['gender']

    # Are they already confirmed on an event?
    try:
        e = event.objects.filter(volunteer=fb_id, confirmed="y")[0]
        f = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('start', flat=True)[0]
        dateandtime = str(f.strftime('%I:%M %p')) + " on " + str(f.strftime('%A %d %B'))
        speech = "Hi there again! You have a volunteering opportunity at " + dateandtime + " called " + str(e) + ". Want any more details?"
        contextOut = "confirm_event"

        # Have they asked to cancel the event?
        if request.get("result").get("action") == "event_cancel":
            e1 = event.objects.filter(volunteer=fb_id)[0]
            e1.confirmed = 'n'
            e1.volunteer = ''
            e1.save()
            speech = "Not a problem :) Thanks for letting me know! I've taken you off the event"
            contextOut = ""

        # Have they asked for the date of the event?
        if request.get("result").get("action") == "details_date":
            try:
                eventdate = parameters.get("event-date")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
                speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B'))
                contextOut = "confirm_event"

        # Have they asked for the start time of the event?
        if request.get("result").get("action") == "details_starttime":
            try:
                eventstarttime = parameters.get("event-start-time")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
                speech = "It starts at " + str(e.strftime('%I.%M %p'))
                contextOut = "confirm_event"

        # Have they asked for the end time of the event?
        if request.get("result").get("action") == "details_endtime":
            try:
                eventendtime = parameters.get("event-end-time")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('end', flat=True)[0]
                speech = "It ends at " + str(e.strftime('%I:%M %p'))
                contextOut = "confirm_event"

        # Have they asked for the duration of the event?
        if request.get("result").get("action") == "details_duration":
            try:
                eventduration = parameters.get("event-duration")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('duration', flat=True)[0]
                speech = str(e) + " hours"
                contextOut = "confirm_event"

        # Have they asked for the location of the event?
        if request.get("result").get("action") == "details_location":
            try:
                eventlocation = parameters.get("event-location")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('address', flat=True)[0]
                f = event.objects.filter(volunteer=fb_id).values_list('postcode', flat=True)[0]
                speech = str(e) + ', ' + str(f)
                contextOut = "confirm_event"

        # Have they asked for a description of the event?
        if request.get("result").get("action") == "details_description":
            try:
                eventduration = parameters.get("event-description")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('details', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        # Have they asked for the name of the charity running the event?
        if request.get("result").get("action") == "details_charityname":
            try:
                eventduration = parameters.get("event-charity-name")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('charity', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        sending_message = return_message(speech, contextOut)
        return sending_message


    # If they're not already confirmed on an event
    except IndexError:
    # Checks for greeting action
        if request.get("result").get("action") == "volunteer.new":
            # Test to see if someone is in our database
            try:
                u = user.objects.get(facebook_id=fb_id)
            # If they're not, then lets add them! And tell them they're a newbie
            except user.DoesNotExist:
                speech = "Why hello there " + first_name + "! This is the first time we've spoken, an absolute pleasure. I'm here to help you find volunteering opportunities, when can you volunteer?"
                u1 = user(facebook_id=fb_id)
                u1.first_name = first_name
                u1.last_name = last_name
                u1.save()
                contextOut = "volunteer_timedate"

            # If they are, let's welcome them warmly and ask them when they can volunteer
            else:
                speech = "Welcome back " + first_name + "! When can you volunteer?"
                contextOut = "volunteer_timedate"

        # Checks for the 'volunteer.assign' action - which will come with four parameters, the date, time, location and duration
        if request.get("result").get("action") == "volunteer.assign":
            # Get a bunch of information from the JSON
            day = parameters.get("date")
            when = parameters.get("time")
            dur = parameters.get("duration")
            location = parameters.get("location")
            available_time = str(day) + " " + str(when)
            datetime_object = datetime.strptime(available_time, '%Y-%m-%d %H:%M:%S')
            # This is to take their ideal start time and add a couple of hours each side to create a range!
            early_start = datetime_object + timedelta(hours=-72)
            print("early_start = " + str(early_start))
            late_start = datetime_object + timedelta(hours=72)
            print("late_start = " + str(late_start))
            print (datetime_object)

            # Go and check for an event based on user input
            try:
                closest_greater_qs = event.objects.filter(start__gte=datetime_object).order_by('start')

                closest_less_qs = event.objects.filter(start__lt=datetime_object).order_by('-start')

                #e = event.objects.filter(start__gte=early_start, start__lte=late_start).values_list('start', flat=True)
            # There is no event, let's apologise and ask them to start again
            except event.DoesNotExist:
                speech = "Sorry, there's no event at that day and time :(. Maybe suggest another day?"
                contextOut = "volunteer_timedate"

            except IndexError:
                speech = "Sorry, there's no event at that day and time :(. Maybe suggest another day?"
                contextOut = "volunteer_timedate"


            # There is an event! Let's tell them what the event is and confirm the date. Let's ask them what details they need to confirm

            else:
                # for line in e:
                #     naive = line.replace(tzinfo=None)
                #     line2 = naive - datetime_object
                #     print(line2)
                g1_name = closest_greater_qs.values_list('name')[0]
                g1_name = g1_name[0]

                g1_details = closest_greater_qs.values_list('details')[0]
                g1_details = g1_details[0]

                g1_start = closest_greater_qs.values_list('start')[0]
                g1_start = g1_start[0]

                g1_end = closest_greater_qs.values_list('end')[0]
                g1_end = g1_end[0]

                g1_location = closest_greater_qs.values_list('postcode')[0]
                g1_location = g1_location[0]

                g1_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"


                closest_greater_2 = closest_greater_qs[1]
                closest_greater_3 = closest_greater_qs[2]
                closest_less_1 = closest_less_qs[0]
                closest_less_2 = closest_less_qs[1]

#                print (closest_greater_1[0])



#                userevent=event.objects.get(start__gte=early_start, start__lte=late_start)
#                userevent.volunteer = fb_id#
#                userevent.save()
#                f = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
#                dateandtime = str(f.strftime('%I:%M %p')) + " on " + str(f.strftime('%A %d %B'))
#                speech = "Great! We have an opportunity at " + dateandtime + " called " + str(e) + ". I can give you any details you want (charity, location, time, date, opportunity etc), just ask!"
#                print("Response:")
#                print(speech)
#                contextOut = "confirm_event"
                return {
                  "messages": [
                    {
                      "type": 1,
                      "platform": "facebook",
                      "title": g1_name,
                      "subtitle": "Start: " + str(g1_start.strftime('%I:%M %p'), # + " on " + str(g1_start.strftime('%A %d %B')) + ". End: "  + str(g1_start.strftime('%I:%M %p') + ". Postcode: " + g1_location,
                      "imageUrl": g1_image,
                      "buttons": [
                        {
                          "text": "Confirm",
                          "postback": "I'd like to confirm"
                        },
                        {
                          "text": "Details",
                          "postback": "Could you give me more details?"
                        },
                      ]
                    },
                    {
                      "type": 1,
                      "platform": "facebook",
                      "title": 'Feed the Homeless',
                      "subtitle": 'Feed the Homeless',
                      "imageUrl": "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg",
                      "buttons": [
                        {
                          "text": "View Details",
                          "postback": "http://www.google.co.uk"
                        }
                        ],
                    },
                    {
                      "type": 1,
                      "platform": "facebook",
                      "title": 'Feed the Homeless',
                      "subtitle": 'Feed the Homeless',
                      "imageUrl": "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg",
                      "buttons": [
                        {
                          "text": "View Details",
                          "postback": "http://www.google.co.uk"
                        }
                        ],
                    },
                    {
                      "type": 1,
                      "platform": "facebook",
                      "title": 'Feed the Homeless',
                      "subtitle": 'Feed the Homeless',
                      "imageUrl": "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg",
                      "buttons": [
                        {
                          "text": "View Details",
                          "postback": "http://www.google.co.uk"
                        }
                        ],
                    },
                    {
                      "type": 1,
                      "platform": "facebook",
                      "title": 'Feed the Homeless',
                      "subtitle": 'Feed the Homeless',
                      "imageUrl": "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg",
                      "buttons": [
                        {
                          "text": "View Details",
                          "postback": "http://www.google.co.uk"
                        }
                        ],
                    },
                  ]
                }


        # Have they asked for the date of the event?
        if request.get("result").get("action") == "details_date":
            try:
                eventdate = parameters.get("event-date")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
                speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B')) + ". Let me know when you're able to confirm :)"
                contextOut = "confirm_event"

        # Have they asked for the start time of the event?
        if request.get("result").get("action") == "details_starttime":
            try:
                eventstarttime = parameters.get("event-start-time")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
                speech = "It starts at " + str(e.strftime('%I:%M %p'))
                contextOut = "confirm_event"

        # Have they asked for the end time of the event?
        if request.get("result").get("action") == "details_endtime":
            try:
                eventendtime = parameters.get("event-end-time")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('end', flat=True)[0]
                speech = "It ends at " + str(e.strftime('%I.%M %p'))
                contextOut = "confirm_event"

        # Have they asked for the duration of the event?
        if request.get("result").get("action") == "details_duration":
            try:
                eventduration = parameters.get("event-duration")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('duration', flat=True)[0]
                speech = str(e) + " hours"
                contextOut = "confirm_event"

        # Have they asked for the location of the event?
        if request.get("result").get("action") == "details_location":
            try:
                eventlocation = parameters.get("event-location")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('address', flat=True)[0]
                f = event.objects.filter(volunteer=fb_id).values_list('postcode', flat=True)[0]
                speech = str(e) + ', ' + str(f) + "... let me know if you can definitely make it :)"
                contextOut = "confirm_event"

        # Have they asked for a description of the event?
        if request.get("result").get("action") == "details_description":
            try:
                eventduration = parameters.get("event-description")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('details', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        # Have they asked for the name of the charity running the event?
        if request.get("result").get("action") == "details_charityname":
            try:
                eventduration = parameters.get("event-charity-name")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id).values_list('charity', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        if request.get("result").get("action") == "event_confirmation":
            try:
                confirmation = parameters.get("confirmation")
            except:
                pass
            else:
                e1 = event.objects.filter(volunteer=fb_id)[0]
                e1.confirmed = 'y'
                e1.save()
                speech = "Yes! Great decision! You're in :)! Let me know if something changes and you suddenly can't make it, or feel free to keep asking for more details if you forget / want to know more."
                contextOut = "locked_in"

        sending_message = return_message(speech, contextOut)
        return sending_message

def volunteer_today():

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    early_start = current_time
    late_start = datetime_object + timedelta(hours=24)
    print("late_start = " + str(late_start))

    events_today = event.objects.filter(start__gte=early_start, start__lte=late_start).values_list('volunteer',flat=True)
    if events_today:
        for volunteer in events_today:
            speech = "Your event is today! Just thought I'd check in and make sure you were still planning on coming along?"
            contextOut = ""
            sending_message = return_message(speech, contextOut)
            return sending_message
            res = sending_message
            res = json.dumps(res, indent=4)
            print(res)
            return HttpResponse(res)

# schedule.every(10).minutes.do(volunteer_today)
#
# while True:
#         schedule.run_pending()
#         time.sleep(1)

# This creates the json for the webhook callback
def return_message(speech, contextOut):
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        "contextOut": [{"name":contextOut, "lifespan":5, "parameters":{}}],
        "source": "apiai-onlinestore-shipping"
    }
