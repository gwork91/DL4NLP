import os
import time
import shutil
from os.path import join, dirname
import sys
import json
import re
import random
import requests
from flask import Flask, request
from flask import Flask, render_template
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import urllib2
import cookielib


app = Flask(__name__)
english_bot = ChatBot("English Bot")
english_bot.set_trainer(ChatterBotCorpusTrainer)
english_bot.train("chatterbot.corpus.english")

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])   
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":   # make sure this is a page subscription

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):     # someone sent us a message
                    received_message(messaging_event)

                elif messaging_event.get("delivery"):  # delivery confirmation
                    pass
                    # received_delivery_confirmation(messaging_event)

                elif messaging_event.get("optin"):     # optin confirmation
                    pass
                    # received_authentication(messaging_event)

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(messaging_event)

                else:    # uknown messaging_event
                    log("Webhook received unknown messaging_event: " + messaging_event)

    return "ok", 200


def received_message(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    
    # could receive text or attachment but not both
    if "text" in event["message"]:
        message_text = event["message"]["text"]

        # parse message_text and give appropriate response   
        if message_text == 'image':
            send_image_message(sender_id)

        elif message_text == 'receive guide':
            send_file_message(sender_id)
	    send_return(sender_id)
	
        elif message_text == 'hi':
            send_first_reply(sender_id)
	
	elif message_text == 'hey':
            send_first_reply(sender_id)
	
	elif message_text == 'return':
            send_first_reply(sender_id)
	
	elif message_text == 'hello':
            send_first_reply(sender_id)
	
        elif message_text == 'play audio':
	    send_text_message(sender_id, "Click to listen")
            send_audio_message(sender_id)
	    send_return(sender_id)
	
	elif message_text == 'book reading':
            send_quick_reply(sender_id)
	
	elif(re.match('(\d{2})[/.-](\d{2})[/.-](\d{4})$',message_text)):
	         if ((time.strftime("%d/%m/%Y"))==message_text):
                       send_image_message(sender_id)
	         send_quick_reply(sender_id)

        elif message_text == 'play video':
            send_text_message(sender_id, "Click to play")
            send_video_message(sender_id)
	    send_return(sender_id)
	
	elif message_text == 'bye':
            send_text_message(sender_id, "Bye, see you soon")
	
	elif message_text == 'share book':
            send_share_message(sender_id)
	    send_return(sender_id)
	
	elif message_text == 'chatterbot':
            send_text_message(sender_id, "Welcome, Welcome to chatterbot, shoot it..")

        elif message_text == 'read book':
            send_button_message(sender_id)

        elif message_text == 'buy book':
            send_generic_message(sender_id)

        else: # default case
            send_text_message(sender_id, str(english_bot.get_response(message_text)))
            
    elif "attachments" in event["message"]:
        message_attachments = event["message"]["attachments"]   
        send_text_message(sender_id, "Message with attachment received, we will contact you soon")


# Message event functions
def send_text_message(recipient_id, message_text):

    # encode('utf-8') included to log emojis to heroku logs
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text.encode('utf-8')))

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    call_send_api(message_data)

def send_return(recipient_id):
    
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "text":"Whenever you want, click return to start over, bye to exit",
            "quick_replies":[
              {
                "content_type":"text",
                "title":"return",
                "payload":"return"
              },
              {
                "content_type":"text",
                "title":"bye",
                "payload":"bye"
              },
            ]
          }
    })
    log("sending file to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)

def send_first_reply(recipient_id):
    
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "text":"Welcome to Bookworm, When is your birthday? or Choose from the options..",
            "quick_replies":[
              {
                "content_type":"text",
                "title":"chatterbot",
                "payload":"chatterbot"
              },
              {
                "content_type":"text",
                "title":"book reading",
                "payload":"book reading"
              },
            ]
          }
    })
    log("sending file to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)

def send_quick_reply(recipient_id):
    
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "text":"What is your query about? Choose from the options..",
            "quick_replies":[
              {
                "content_type":"text",
                "title":"share book",
                "payload":"share book"
              },
              {
                "content_type":"text",
                "title":"read book",
                "payload":"read book"
              },
	      {
                "content_type":"text",
                "title":"buy book",
                "payload":"buy book"
              },
	      {
                "content_type":"text",
                "title":"receive python guide",
                "payload":"receive python guide"
              },
	      {
                "content_type":"text",
                "title":"play audio",
                "payload":"play audio"
              },
              {
                "content_type":"text",
                "title":"play video",
                "payload":"play video"
              },
            ]
          }
    })
    log("sending file to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)
	
def send_generic_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Book",
                        "subtitle": "Hey, we love books..",
                        "item_url": "http://sumitopinions.blogspot.in/",               
                        "image_url": "http://www.freepressjournal.in/wp-content/uploads/2013/07/bookworm.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://sumitopinions.blogspot.in/",
                            "title": "Visit our blog"
                        }, {
                            "type": "postback",
                            "title": "Upload attachment",
                            "payload": "Payload for first bubble",
                        }],
                    }, {
                        "title": "Book",
                        "subtitle": "Hey, we love books..",
                        "item_url": "http://sumitopinions.blogspot.in/",               
                        "image_url": "http://www.freepressjournal.in/wp-content/uploads/2013/07/bookworm.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "http://sumitopinions.blogspot.in/",
                            "title": "Read our blog"
                        }, {
                            "type": "postback",
                            "title": "Upload attachment",
                            "payload": "Payload for first bubble",
                        }]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)
    

def send_image_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"image",
                "payload":{
                    "url":"http://www.happybirthday.quotesms.com/images/latest-happy-birthday-images.jpg"
                }
            }
        }
    })

    log("sending image to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_file_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"file",
                "payload":{
                    "url":"http://www3.canisius.edu/~yany/python/Python4DataAnalysis.pdf"
                }
            }
        }
    })

    log("sending file to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_audio_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"audio",
                "payload":{
                    "url":"http://planetofrock.com/samples/lballad.mp3"
                }
            }
        }
    })

    log("sending audio to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_video_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"video",
                "payload":{
                    "url":"https://www.w3schools.com/html/mov_bbb.mp4"
                }
            }
        }
    })

    log("sending video to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_button_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"Welcome to Bookworm",
                    "buttons":[
                    {
                        "type":"web_url",
                        "url":"http://sumitopinions.blogspot.in/",
                        "title":"Visit our website"
                    },
                    {
                        "type":"postback",
                        "title":"Upload attachment",
                        "payload":"Payload for send_button_message()"
                    }
                    ]
                }
            }
        }
    })

    log("sending button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_share_message(recipient_id):

    # Share button only works with Generic Template
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"generic",
                    "elements":[
                    {
                        "title":"Book",
                        "subtitle":"Hey, Share about Bookworm or start over",
                        "image_url":"http://www.freepressjournal.in/wp-content/uploads/2013/07/bookworm.png",
                        "buttons":[
                        {
                            "type":"element_share"
                        }
                        ]
                    }    
                    ]
                }
        
            }
        }
    })

    log("sending share button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def received_postback(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    payload = event["postback"]["payload"]

    log("received postback from {recipient} with payload {payload}".format(recipient=recipient_id, payload=payload))

    if payload == 'Get Started':
        # Get Started button was pressed
        send_text_message(sender_id, "Welcome to AXA")
    else:
        # Notify sender that postback was successful
        send_text_message(sender_id, "Please upload book if you want to share with the rest of the world....if not..")
	send_return(sender_id)

def call_send_api(message_data):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=message_data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


# @app.route('/', methods=['POST'])
# def set_greeting_text():
#     # Sets greeting text on welcome screen
#     message_data = json.dumps({
#         "setting_type":"greeting",
#         "greeting":{
#             "text":"Hi {{user_first_name}}, welcome to this bot."
#         }
#     })
#     params = {
#         "access_token": os.environ["PAGE_ACCESS_TOKEN"]
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=message_data)
#     if r.status_code != 200:
#         log("setting greeting text")
#         log(r.status_code)
#         log(r.text)

#     return "ok", 200

    
# @app.route('/', methods=['POST'])
# def set_get_started_button():
#     # Sets get started button on welcome screen
#     message_data = json.dumps({
#         "setting_type":"call_to_actions",
#         "thread_state":"new_thread",
#         "call_to_actions":[
#         {
#             "payload":"Get Started"
#         }
#         ]
#     })
#     params = {
#         "access_token": os.environ["PAGE_ACCESS_TOKEN"]
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=message_data)
#     if r.status_code != 200:
#         log("setting get started button")
#         log(r.status_code)
#         log(r.text)

#     return "ok", 200


if __name__ == '__main__':
    app.run(debug=True)
