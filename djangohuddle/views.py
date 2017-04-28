from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

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

        result = data.get("result")
        print(result)

        # req = HttpRequest.get_json(silent=True, force=True)
        # print("Request:")
        # print(json.dumps(req, indent=4))
        #
        # res = makeWebhookResult(req)
        #
        # res = json.dumps(res, indent=4)
        # print(res)
        # r = make_response(res)
        # r.headers['Content-Type'] = 'application/json'
        # return r

    else:
        print('Hello')

@csrf_exempt
def makeWebhookResult(req):
    if req.get("result").get("action") != "shipping.cost":
        return {}
    result = req.get("result")
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
