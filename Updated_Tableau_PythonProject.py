# -*- coding: utf-8 -*-
"""
Edited on Wed Dec 29 2021
Last push on Thur Dec 30 2021
@author: Jealyn & Phil
"""
# Using the packages that are needed for the slack api.
import os
from flask import Flask, request, make_response
from slack_bolt import App
from slack_sdk import WebClient 
from slackeventsapi import SlackEventAdapter
from slack.errors import SlackApiError
from dotenv import load_dotenv
import requests
import json
import tableauserverclient as TSC
import pandas as pd


# Adding the environmental variables required to get slack to talk to Python
slack_token = os.environ.get('SLACK_BOT_TOKEN1')

# Creating requirements to built Bolt for slack using the slack app credentials
# given to us. These belong to a test app that will be transfered to the actual
# bot.
bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN1"),
               signing_secret=os.environ.get("SLACK_SIGNING_SECRET1"))

# Intializing the app with the signing secret created before.
# Flask allows us to work with HTML coding without having to strictly code for
# it.
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET1'], "/slack/events", app)


# # Creating an event that will allow Slack Bot to respond to message. Currently,
# # it is set to send a message to only Jealyn,  but you can change the if "<>"
# # statement to reflect yours.
@slack_events_adapter.on("message")
def message_sent(event_data):
    message = event_data["event"]
    channel = message["channel"]
    user = message["user"]

    if "<@U02ELQK362U>" in message.get("text"):
        slack_web_client.chat_postMessage(
                    channel= channel,
                    text= "Hi there <@" + user + ">!")
        return make_response("", 200)

# Now creating the script that will respond to the slash command. This command
# will print out the full utilization image as of now, but will be changed soon. 
@app.route('/utilizationtest', methods=['POST'])
def my_first_slash_command():
    channel_id = "C02RR87GNLQ"
    info = request.form
    user = info['user_id']
    channel = info['channel_id'] #here, we are requesting information from the 
    # channel, which will allow us to post based on the ID the bot was installed
    # in.

    
    # Adding all the access requirements for our tableau online
    try:
        load_dotenv()
        tess_token=os.getenv('ACCESS_TOKEN')
        tess_secret=os.getenv('TOKEN_SECRET')
        tess_domain=os.getenv('SITE_ID')
        tess_server=os.getenv('TABLEAU_SERV')
        tess_view=os.getenv('TABLEAU_VIEW')
        tess_path=os.getenv('TABLEAU_PATH')

    # Adding in a print statement to make sure everything is running smoothly.
        print("Talking to Tableau right now...\n")
    
    # Creating an authorization token and server to then be able to sign-in.
        tess_auth=TSC.PersonalAccessTokenAuth(tess_token,tess_secret,tess_domain)
        tess_serv = TSC.Server(tess_server, use_server_version=True)
        
    # Now, signing into tableau online and obtaining the view ID we will be 
    # getting infromation from.
        individual_image_options = TSC.ImageRequestOptions(imageresolution = 
             TSC.ImageRequestOptions.Resolution.High, maxage=1)
        individual_image_options.vf('SlackID', user)
        with tess_serv.auth.sign_in(tess_auth):
            utilization = tess_serv.views.get_by_id(tess_view)
            tess_serv.views.populate_image(utilization,individual_image_options) 
            with open('./utilization_{}.png'.format(user), 'wb') as v:
                v.write(utilization.image)
                
    # Adding another print statement to see where things could go wrong   
        print("Auth tokens, saving image, image options...\n")    

    # Now, we need to upload the image, so we're getting the file using the
    # .file_upload API from slack and adding the image to slack-util-channel.
        image = slack_web_client.files_upload(
            channels='#slack-util-bot',
            file= './utilization_{}.png'.format(user),
            title='utilization_image',
            filetype='png'
            )
        print("Uploading Image to Slack...\n") # Print statment to see where
        # the code is going
        
    # In order to upload this image, we need to create a url.
        url_private= image["file"]["url_private"]
        print("Making the URL for slack...\n") # Print statement shows if the
        # URL is running
        
    # The image can only be uploaded using blocks. It has header sections and 
    # the direct link to the online version.
        blocksjson=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Here is the utilization report!" 
                    }
                },
                {
                     "type": "context",
                     "elements": [
                        {
                          "type": "mrkdwn",
                          "text": "Link to <https://prod-useast-b.online.tableau.com/#/site/tessellationhq/views/ProjectReportingSLACK/BillableUtilizationforSlack|Full Report>"
                        }
                      ]
                }
            ]
    # In order to upload with blocks and have this still be private, we will be 
    # using attachements to complete it. Note: the use of "attachments" is a 
    # work around and may be deprecated in the future.
        attachmentsjson=[{
                    'title': ' ',
                    'text': ' ',
                    'image_url': url_private,
                    'alt_text': 'utilization'
                    }]
        
        print("Adding attachment onto a slack message...\n") # Seeing where the 
        # code is.
        
        
    # Since we now have attachments, we need to send them through a message
    # using the "blocks." However, need to do this through json because 
    # python doesn't have that option.
        msg =   slack_web_client.chat_postMessage(
                channel="C02RR87GNLQ",
                text = 'step 1',
                blocks=json.dumps(blocksjson),
                attachments = json.dumps(attachmentsjson))

    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")
    return make_response("", 200) # making sure we load the response onto slack.
        

# Initializing a Web API client using the tokens once again.
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN1'])

# Making the app runable! Using the ngrok http 8080.
if __name__ == "__main__":
   app.run(port=8080)
