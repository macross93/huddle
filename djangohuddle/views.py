from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from events.models import user, charity, charitycontact, event
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView

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

    # Checks for greeting action
    if request.get("result").get("action") == "volunteer.new":
        result = request.get("result")
        originalRequest = request.get("originalRequest")
        data = originalRequest.get("data")
        sender = data.get("sender")
        fb_id = sender.get("id")

        try:
            u = user.objects.get(facebook_id=fb_id)

        except user.DoesNotExist:
            speech = "You dont yet exist in my database"
            u1 = user(facebook_id=fb_id)
            u1.save()

        else:
            speech = "Youre in my database " + u

        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "apiai-onlinestore-shipping"
        }


    if request.get("result").get("action") == "shipping.cost":
        result = request.get("result")
        parameters = result.get("parameters")
        zone = parameters.get("shipping-zone")

        cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

        speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

        print("Response:")
        print(speech)

        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "apiai-onlinestore-shipping"
        }

    else:
        return{}
