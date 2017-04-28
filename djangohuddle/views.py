from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from events.models import User, Charity, CharityContact, Event

import json
import urllib
import os


def hello(request):
    return HttpResponse("Hello world")

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
            u = User.objects.get(facebook_id=fb_id)
        except User.DoesNotExist:
            speech = "You dont yet exist in my database"
        else:
            speech = "Youre in my database"

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
