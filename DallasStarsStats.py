"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib 
import httplib
import base64
import string
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

all_players_stats = {}
dallas_stars_players_stats = []



# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    '''global all_players_stats
    global dallas_stars_players_stats
    get_all_players_stats()
    get_dallas_stars_players_stats(all_players_stats)'''

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Dallas Stars Stats skill. " \
                    "Please tell me how I can help you. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me how I can help you."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))






# ----------------- Calls to Stats API -----------------

def retrieve_player_stats(requested_player_number):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://dynamodb.us-east-1.amazonaws.com")
    table = dynamodb.Table('PlayerStats')
    response = table.scan(
          FilterExpression=Attr('City').eq("Calgary") & Attr('JerseyNumber').eq(requested_player_number)
          )
    player_stats = response["Items"][0]
    print(player_stats)
    return player_stats
    
def get_all_players_stats():
    global all_players_stats

    host = "www.mysportsfeeds.com"
    url = "/api/feed/pull/nhl/current/cumulative_player_stats.json?&force=true"
    f=open("/authentication/account.txt","r")
    lines=f.readlines()
    username=lines[0]
    password=lines[1]
    f.close()
    # base64 encode the username and password
    auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    webservice = httplib.HTTPS(host)
    # write your headers
    webservice.putrequest("GET", url)
    webservice.putheader("Host", host)
    webservice.putheader("User-Agent", "Python http auth")
    webservice.putheader("Content-type", "text/html; charset=\"UTF-8\"")
    # write the Authorization header like: 'Basic base64encode(username + ':' + password)
    webservice.putheader("Authorization", "Basic %s" % auth)
    webservice.endheaders()
    statuscode, statusmessage, header = webservice.getreply()

    all_players_stats = json.loads(webservice.getfile().read())
    
def get_dallas_stars_players_stats(all_players_stats):
    global dallas_stars_players_stats
    for player in all_players_stats['cumulativeplayerstats']['playerstatsentry']:
        if player["team"]["City"] == "Washington":
            dallas_stars_players_stats.append(player)
            print("INSIDE LOOP 1")
            #print(player)

    
    
# ----------------- Speech Output Functions -----------------

def write_intro_player_stats(speech_output, player_stats):
    FirstName = player_stats["PlayerInfo"]["FirstName"]
    LastName = player_stats["PlayerInfo"]["LastName"]

    speech_output = speech_output + "Here are the stats for " + FirstName + ' ' + LastName + " this season. "
    return speech_output
    
def old_write_intro_player_stats(speech_output, player_stats):
    FirstName = player_stats["player"]["FirstName"]
    LastName = player_stats["player"]["LastName"]

    speech_output = speech_output + "Here are the stats for " + FirstName + ' ' + LastName + " this season. "
    return speech_output

def write_basic_player_stats(speech_output, player_stats):
    Goals = player_stats["Stats"]["Goals"]
    Assists = player_stats["Stats"]["Assists"]
    Points = player_stats["Stats"]["Points"]
    GamesPlayed = player_stats["Stats"]["GamesPlayed"]
    PlusMinus = player_stats["Stats"]["PlusMinus"]
    PenaltyMinutes = player_stats["Stats"]["PenaltyMinutes"]
    FirstName = player_stats["PlayerInfo"]["FirstName"]
    LastName = player_stats["PlayerInfo"]["LastName"]
    
    speech_output = (speech_output + FirstName + ' ' + LastName + " has " + GamesPlayed + " games played. " +
    "He has " + Goals + " goals, and " + Assists + " assists, for a total of " + Points + " points. " +
    "His plus minus is " + PlusMinus + ", and has " + PenaltyMinutes + " penalty minutes. " +
    "Is there anything else I can help you with?")

    return speech_output


def old_write_basic_player_stats(speech_output, player_stats):
    print(player_stats["stats"])
    Goals = player_stats["stats"]["stats"]["Goals"]["#text"]
    Assists = player_stats["stats"]["stats"]["Assists"]["#text"]
    Points = player_stats["stats"]["stats"]["Points"]["#text"]
    GamesPlayed = player_stats["stats"]["GamesPlayed"]["#text"]
    PlusMinus = player_stats["stats"]["stats"]["PlusMinus"]["#text"]
    PenaltyMinutes = player_stats["stats"]["stats"]["PenaltyMinutes"]["#text"]
    FirstName = player_stats["player"]["FirstName"]
    LastName = player_stats["player"]["LastName"]

    speech_output = (speech_output + FirstName + ' ' + LastName + " has " + GamesPlayed + " games played. " +
        "He has " + Goals + " goals, and " + Assists + " assists, for a total of " + Points + " points. " +
        "His plus minus is " + PlusMinus + ", and has " + PenaltyMinutes + " penalty minutes. " +
        "Is there anything else I can help you with?")

    return speech_output

def player_not_found_speech_output(speech_output, requested_player_number):
    speech_output = ("I'm sorry, but I could not find stats for a player with the number " + str(requested_player_number) + 
        ". Please try again.")
    return speech_output

# ----------------- Intent Functions -----------------

def close_out(intent, session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    card_title = intent['name']
    
    speech_output = "Thank you for using the Dallas Stars stats skill. Dun dun, Dallas! Dun dun, Stars!"
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_player_stats(intent, session):
    session_attributes = {}
    should_end_session = False
    card_title = intent['name']
    reprompt_text = None
    speech_output = ""
    found = 0
    requested_player_number = intent['slots']['Number']['value']
    player_stats = {}
    if "Detail" in intent['slots']:
        detail = intent['slots']['Detail']['value']
    else:
        detail = "basic"
    
    player_stats = retrieve_player_stats(requested_player_number)
    if player_stats != {} or player_stats != []:
        found = 1
    
    if found == 1:
        speech_output = write_intro_player_stats(speech_output, player_stats)
        if detail == "basic":
            speech_output = write_basic_player_stats(speech_output, player_stats)
    
    if found == 0:
        speech_output = player_not_found_speech_output(speech_output, requested_player_number)
    
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
    
    

def old_get_player_stats(intent, session):
    global all_players_stats
    global dallas_stars_players_stats
    get_all_players_stats()
    get_dallas_stars_players_stats(all_players_stats)
    session_attributes = {}
    should_end_session = False
    card_title = intent['name']
    reprompt_text = None
    speech_output = ""
    found = 0
    
    player_stats = {}
    if intent['slots']['Detail']['value']:
        detail = intent['slots']['Detail']['value']
    else:
        detail = "basic"
    
    requested_player_number = intent['slots']['Number']['value']

    for player in dallas_stars_players_stats:
        print("INSIDE LOOP 2")
        print(player["player"])
        if "JerseyNumber" in player["player"]:
            if player["player"]["JerseyNumber"] == requested_player_number:
                player_stats = player
                print("WE FOUND EM")
                found = 1
                #print(player_stats)
                break
    
    
    if found == 1:
        speech_output = write_intro_player_stats(speech_output, player_stats)
        if detail == "basic":
            speech_output = write_basic_player_stats(speech_output, player_stats)
    
    if found == 0:
        speech_output = player_not_found_speech_output(speech_output, requested_player_number)
    
    #speech_output = "Thank you for using the City Invest skill. If you would like to learn more about personal wealth management opportunities with City, please visit www dot online dot city dot com. Goodbye."
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
    

# --------------------- Events -----------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    

    
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """



    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    
    
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhatsPlayerStats":
        return get_player_stats(intent, session)
    elif intent_name == "WhatsPlayerSimpleStats":
        return get_player_stats(intent, session)    
    elif intent_name == "CloseOut":
        return close_out(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    print(event['request']['type'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
