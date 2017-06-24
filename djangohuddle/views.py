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
from django import forms
from django.core.exceptions import ValidationError

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

            e1 = event.objects.filter(volunteer=fb_id,confirmed="y")[0]
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
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('start', flat=True)[0]
                speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B'))
                contextOut = "confirm_event"

        # Have they asked for the start time of the event?
        if request.get("result").get("action") == "details_time":
            try:
                eventstarttime = parameters.get("event-start-time")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('start', flat=True)[0]
                f = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('end', flat=True)[0]
                speech = "It starts at " + str(e.strftime('%I.%M %p')) + ", ending at " + str(f.strftime('%I.%M %p')) + ", on " + str(e.strftime('%A %d %B'))
                contextOut = "confirm_event"

        # Have they asked for the duration of the event?
        if request.get("result").get("action") == "details_duration":
            try:
                eventduration = parameters.get("event-duration")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('duration', flat=True)[0]
                speech = str(e) + " hours"
                contextOut = "confirm_event"

        # Have they asked for the location of the event?
        if request.get("result").get("action") == "details_location":
            try:
                eventlocation = parameters.get("event-location")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('address', flat=True)[0]
                f = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('postcode', flat=True)[0]
                speech = str(e) + ', ' + str(f)
                contextOut = "confirm_event"

        # Have they asked for a description of the event?
        if request.get("result").get("action") == "details_description":
            try:
                eventduration = parameters.get("event-description")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('details', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        # Have they asked for the name of the charity running the event?
        if request.get("result").get("action") == "details_charityname":
            try:
                eventduration = parameters.get("event-charity-name")
            except:
                pass
            else:
                e = event.objects.filter(volunteer=fb_id, confirmed="y").values_list('charity', flat=True)[0]
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
            if when == "night":
                when = "19:00:00"
            if when == "evening":
                when = "19:00:00"
            if when == "afternoon":
                when = "15:00:00"
            if when == "lunchtime":
                when = "13:00:00"
            if when == "midday":
                when = "12:00:00"
            if when == "morning":
                when = "09:00:00"
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
                closest_greater_qs = event.objects.filter(start__gte=datetime_object,confirmed="n").order_by('start')
                closest_less_qs = event.objects.filter(start__lt=datetime_object,confirmed="n").order_by('-start')

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

                try:
                    l2 = event.objects.filter(start__lt=datetime_object,confirmed="n").order_by('-start')[1]

                except event.DoesNotExist:
                    l2_card = ""
                except IndexError:
                    l2_card = ""

                else:
                    l2_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"
                    title = l2.name

                    l2_card = {
                      "type": 1,
                      "platform": "facebook",
                      "title": l2.name,
                      "subtitle": "Start: " + l2.start.strftime('%I:%M %p') + " on " + l2.start.strftime('%A %d %B') + ".\n End: "  + l2.end.strftime('%I:%M %p') + ".\n Address: " + l2.address + ", " + l2.postcode,
                      "imageUrl": str(l2.image),
                      "buttons": [
                        {
                          "text": "Details",
                          "postback": "Details " + str(l2.pk)
                        },
                        {
                          "text": "Confirm",
                          "postback": "Confirm " + str(l2.pk)
                        },
                      ]
                    }

                try:
                    l1 = event.objects.filter(start__lt=datetime_object,confirmed="n").order_by('-start')[0]

                except event.DoesNotExist:
                    l1_card = ""
                except IndexError:
                    l1_card = ""

                else:
                    l1_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"
                    title = l1.name

                    l1_card = {
                      "type": 1,
                      "platform": "facebook",
                      "title": l1.name,
                      "subtitle": "Start: " + l1.start.strftime('%I:%M %p') + " on " + l1.start.strftime('%A %d %B') + ".\n End: "  + l1.end.strftime('%I:%M %p') + ".\n Address: " + l1.address + ", " + l1.postcode,
                      "imageUrl": str(l1.image),
                      "buttons": [
                        {
                          "text": "Details",
                          "postback": "Details " + str(l1.pk)
                        },
                        {
                          "text": "Confirm",
                          "postback": "Confirm " + str(l1.pk)
                        },
                      ]
                    }

                try:
                    g1 = event.objects.filter(start__gte=datetime_object,confirmed="n").order_by('start')[0]

                except event.DoesNotExist:
                    g1_card = ""
                except IndexError:
                    g1_card = ""

                else:
                    g1_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"
                    title = g1.name

                    g1_card = {
                      "type": 1,
                      "platform": "facebook",
                      "title": g1.name,
                      "subtitle": "Start: " + g1.start.strftime('%I:%M %p') + " on " + g1.start.strftime('%A %d %B') + ".\n End: "  + g1.end.strftime('%I:%M %p') + ".\n Address: " + g1.address + ", " + g1.postcode,
                      "imageUrl": str(g1.image),
                      "buttons": [
                        {
                          "text": "Details",
                          "postback": "Details " + str(g1.pk)
                        },
                        {
                          "text": "Confirm",
                          "postback": "Confirm " + str(g1.pk)
                        },
                      ]
                    }

                try:
                    g2 = event.objects.filter(start__gte=datetime_object,confirmed="n").order_by('start')[1]

                except event.DoesNotExist:
                    g2_card = ""
                except IndexError:
                    g2_card = ""


                else:
                    g2_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"
                    title = g2.name

                    g2_card = {
                      "type": 1,
                      "platform": "facebook",
                      "title": g2.name,
                      "subtitle": "Start: " + g2.start.strftime('%I:%M %p') + " on " + g2.start.strftime('%A %d %B') + ".\n End: "  + g2.end.strftime('%I:%M %p') + ".\n Address: " + g2.address + ", " + g2.postcode,
                      "imageUrl": str(g2.image),
                      "buttons": [
                        {
                          "text": "Details",
                          "postback": "Details " + str(g2.pk)
                        },
                        {
                          "text": "Confirm",
                          "postback": "Confirm " + str(g2.pk)
                        },
                      ]
                    }

                try:
                    g3 = event.objects.filter(start__gte=datetime_object,confirmed="n").order_by('start')[2]

                except event.DoesNotExist:
                    g3_card = ""
                except IndexError:
                    g3_card = ""

                else:
                    g3_image = "http://funds.gfmcdn.com/1224153_1477933158.1268.jpg"
                    title = g3.name

                    g3_card = {
                      "type": 1,
                      "platform": "facebook",
                      "title": g3.name,
                      "subtitle": "Start: " + g3.start.strftime('%I:%M %p') + " on " + g3.start.strftime('%A %d %B') + ".\n End: "  + g3.end.strftime('%I:%M %p') + ".\n Address: " + g3.address + ", " + g3.postcode,
                      "imageUrl": str(g3.image),
                      "buttons": [
                        {
                          "text": "Details",
                          "postback": "Details " + str(g3.pk)
                        },
                        {
                          "text": "Confirm",
                          "postback": "Confirm " + str(g3.pk)
                        },
                      ]
                    }

                return {
                  "messages": [
                    l2_card, l1_card, g1_card, g2_card, g3_card,
                    ]
                }

        if request.get("result").get("action") == "details_button":
            originalRequest = request.get("originalRequest")
            originalData = originalRequest.get("data")
            postback = originalData.get("postback")
            payload = postback.get("payload")
            primary_key = payload[8:]
            e = event.objects.filter(pk=int(primary_key))[0]
            e.volunteer = fb_id
            e.save()
            speech = str(e.details) + " The event is at " + str(e.address) + ', ' + str(e.postcode) + ". You can ask any details you like just by typing"
            contextOut = "confirm_event"


        if request.get("result").get("action") == "confirm_button":
            originalRequest = request.get("originalRequest")
            originalData = originalRequest.get("data")
            postback = originalData.get("postback")
            payload = postback.get("payload")
            primary_key = payload[8:]
            e = event.objects.filter(pk=int(primary_key))[0]

            try:
                e2 = event.objects.filter(volunteer=fb_id,confirmed="y")[0]

            except IndexError:
                if e.confirmed != "y":
                    e.confirmed = "y"
                    e.save()
                    speech = "Yes! Great decision! You're in :)! Let me know if something changes and you suddenly can't make it, or feel free to keep asking for more details if you forget / want to know more."
                    contextOut = "locked_in"
                else:
                    speech = "Sorry mate! Someone must have snuck in on that opportunity when you weren't looking! Try another one..."
                    contextOut = "volunteer_timedate"

            else:
                speech = "Sorry, you're already confirmed on one event! We can only confirm people on one event at a time. If you've forgotten about this event, ask me for details!"
                contextOut = "volunteer_timedate"



        # if request.get("result").get("action") == "details_l2_button":
        #     try:
        #         eventdate = parameters.get("event-date")
        #     except:
        #         pass
        #     else:
        #         e = event.objects.filter(volunteer=fb_id).values_list('start', flat=True)[0]
        #         speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B')) + ". Let me know when you're able to confirm :)"
        #         contextOut = "confirm_event"



        # Have they asked for the date of the event?
        if request.get("result").get("action") == "details_date":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventdate = parameters.get("event-date")

            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('start', flat=True)[0]
                speech = "Your volunteering opportunity is on " + str(e.strftime('%A %d %B')) + ". Let me know when you're able to confirm :)"
                contextOut = "confirm_event"

        # Have they asked for the start time of the event?
        if request.get("result").get("action") == "details_starttime":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventstarttime = parameters.get("event-start-time")
            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('start', flat=True)[0]
                f = event.objects.filter(pk=primary_key).values_list('end', flat=True)[0]
                speech = "It starts at " + str(e.strftime('%I.%M %p')) + ", ending at " + str(f.strftime('%I.%M %p')) + ", on " + str(e.strftime('%A %d %B'))
                contextOut = "confirm_event"

        # Have they asked for the end time of the event?
        if request.get("result").get("action") == "details_endtime":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventendtime = parameters.get("event-end-time")
            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('end', flat=True)[0]
                speech = "It ends at " + str(e.strftime('%I.%M %p'))
                contextOut = "confirm_event"

        # Have they asked for the duration of the event?
        if request.get("result").get("action") == "details_duration":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventduration = parameters.get("event-duration")
            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('duration', flat=True)[0]
                speech = str(e) + " hours"
                contextOut = "confirm_event"

        # Have they asked for the location of the event?
        if request.get("result").get("action") == "details_location":
            try:
                eventlocation = parameters.get("event-location")
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")

            except:
                pass
            else:
                print(eventlocation)
                print(payload)
                primary_key = int(payload[8:])

                e = event.objects.filter(pk=primary_key).values_list('address', flat=True)[0]
                f = event.objects.filter(pk=primary_key).values_list('postcode', flat=True)[0]
                speech = str(e) + ', ' + str(f) + "... let me know if you can definitely make it :)"
                contextOut = "confirm_event"

        # Have they asked for a description of the event?
        if request.get("result").get("action") == "details_description":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventduration = parameters.get("event-description")
            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('details', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        # Have they asked for the name of the charity running the event?
        if request.get("result").get("action") == "details_charityname":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                eventduration = parameters.get("event-charity-name")
            except:
                pass
            else:
                primary_key = int(payload[8:])
                e = event.objects.filter(pk=primary_key).values_list('charity', flat=True)[0]
                speech = str(e)
                contextOut = "confirm_event"

        if request.get("result").get("action") == "event_confirmation":
            try:
                context = result.get("contexts")[0]
                parameters_2 = context.get("parameters")
                payload = parameters_2.get("details-button")
                confirmation = parameters.get("confirmation")
            except:
                pass
            else:
                primary_key = int(payload[8:])

                try:
                    e2 = event.objects.filter(volunteer=fb_id,confirmed="y")[0]

                except IndexError:
                    e1 = event.objects.filter(pk=primary_key)[0]
                    e1.volunteer = fb_id
                    e1.confirmed = 'y'
                    e1.save()
                    speech = "Yes! Great decision! You're in :)! Let me know if something changes and you suddenly can't make it, or feel free to keep asking for more details if you forget / want to know more."
                    contextOut = "locked_in"

                else:
                    speech = " already confirmed on one event! We can only confirm people on one event at a time. If you've forgotten about this event, ask me for details!"
                    contextOut = "volunteer_timedate"

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
