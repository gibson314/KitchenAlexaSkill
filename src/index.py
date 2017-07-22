"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function


# =============== Data =================
#dishes_calories = {"Orange Chicken": 5000, "Broccoli Beef": 4000, "shit": 1000}
dishes_calories = {"Pineapple Chicken": 2549, "Potato Beef": 3786, "Onion Lamb": 2647, "Broccoli Pork": 1867}
food_calories = {"Broccoli": 205, "Pineapple": 452, "Onion": 44, "Potato": 163, "Tomato": 22, "Egg": 72, "Lamb": 1216, "Beef": 1506, "Chicken": 1083, "Pork": 1096}
category_food = {"vegetable": ["Broccoli", "Pineapple", "Onion", "Potato", "Tomato"], "meat": ["Egg", "Lamb", "Beef", "Chicken", "Pork"]}
# food_category = {"Brocoli": "vegetable", "Pineapple": "vegetable", "Onion": "vegetable", "Potato": "vegetable", "Tomato": "vegetable", "Egg": "meat", "Lamb": "meat", "Beef": "meat", "Chicken": "meat", "Pork": "meat"}
food_storage = {"Broccoli": 0.7, "Pineapple": 0.6, "Onion": 1, "Potato": 4, "Tomato": 1, "Egg": 2, "Lamb": 3, "Beef": 4, "Chicken": 0.3, "Pork": 0.8}

dishes_food = {"Pineapple Chicken":["Pineapple", "Chicken"] , "Potato Beef": ["Potato", "Beef"], "Onion Lamb": ["Onion", "Lamb"], "Brocoli Pork": ["Brocoli", "Pork"]}
food_unit = {"Broccoli": "bunch", "Pineapple": "fruit", "Onion": "medium", "Potato": "medium", "Tomato": "medium", "Egg": "large", "Lamb": "lb", "Beef": "lb", "Chicken": "lb", "Pork": "lb"}



# =============== State ================
exist_valid_dishes = True

global_state = 0

current_step = -1
prepare_cook_status = 0
current_recipe = "pasta"

ingredients = {
    "pasta": "1 pound spaghetti, 1 tablespoons of spaghetti sauce, 1 cup shredded mild Cheddar cheese",
    "lemon apple juice": "1/2 cup cool water 1 cucumber, halved 2 green apples, quartered 1 lemon, halved"
}

recipes = {
    "pasta": [
        "step one: Bring a large pot of lightly salted water to a boil. ",
        "step two: Mix in pasta and cook for 8 to 10 minutes or until al dente; drain. ",
        "step three: Mix together spaghetti and spaghetti sauce. ",
        "step four: Top with cheese. "],
    "lemon apple juice": [
        "step one: Pour water into a glass and place beneath the spigot of a juicer.",
        "step two: Process first the cucumber, waiting about 20 seconds between halves. ",
        "step three: Finally juice the lemon halves.",
        "step four: Stir juice vigorously to blend "]
}



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

# --------------- Helpers for recommendation system -------------------
def get_recommended_dish(calories_amount):
    calories_amount = int(calories_amount)
    remain_calories_amount = calories_amount
    food_list = []
    # Get meat
    meat_calories = [(food, food_calories[food]) for food in category_food["meat"]]
    meat_calories = sorted(meat_calories, key=lambda pair: pair[0], reverse=True)

    # Get vegetables
    vege_calories = [(food, food_calories[food]) for food in category_food["vegetable"]]
    vege_calories = sorted(vege_calories, key=lambda pair: pair[0])

    for pair in meat_calories:
        if pair[1] * min(1, food_storage[pair[0]]) <= remain_calories_amount:
            food_list.append((pair[0], 1))
            remain_calories_amount -= pair[1] * min(1, food_storage[pair[0]])
            if remain_calories_amount <= calories_amount / 2:
                break

    for pair in vege_calories:
        remain_calories_amount -= pair[1] * min(1, food_storage[pair[0]])
        if remain_calories_amount >= 0:
            food_list.append((pair[0], min(1, food_storage[pair[0]])))
            remain_calories_amount -= pair[1] * min(1, food_storage[pair[0]])


    # Get return
    return food_list, calories_amount - remain_calories_amount

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Kitchen Alexa Skills Kit. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

def create_required_calories_attributes(calories_amount):
    return {"calories_amount": int(calories_amount)}

def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# Get Dishes lower than particular amount of calories.
def get_dishes_from_session(intent, session):
    global global_state


    session_attributes = {}
    reprompt_text = None
    calories_amount = int(intent['slots']['Amount']['value'])
    print (calories_amount)
    dishes = []
    # Add calories amount to session.
    session_attributes = create_required_calories_attributes(calories_amount)
    
    for key in dishes_calories:
        if dishes_calories[key] <= int(calories_amount):
            print(key)
            print(dishes_calories[key])
            print(calories_amount)
            dishes.append(key)
    if len(dishes) > 0:
        EXIST_VALID_DISHES = True
        dishes_text = ""
        for dish in dishes:
            dishes_text += dish
            dishes_text += ","
        speech_output = "There are " + str(len(dishes)) + " dishes valid: " + dishes_text + "please select the dishes you want."
        should_end_session = True
        global_state = 1
    else:
        EXIST_VALID_DISHES = False
        speech_output = "There is no valid dish satisfies your requirement.  Do you want some recommendations about ingredients?"
        should_end_session = False
        global_state = 2


    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# Get recommended dishes from session
def get_recommended_dish_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None
    calories_amount = session['attributes']['calories_amount']
    # calories_amount = 3000

    food_list, total_calories = get_recommended_dish(calories_amount)

    if len(food_list) == 0:
        speech_output = "No Valid Dishes to be recommended!"
        should_end_session = True
    else:
        dish_text = ""
        for food_amount_pair in food_list:
            dish_text += food_amount_pair[0]
            dish_text += " " 
            dish_text += str(food_amount_pair[1])
            dish_text += " " 
            dish_text += food_unit[food_amount_pair[0]]
            dish_text += ", " 

        speech_output = "We have " + dish_text + ". Do you want to make a meal with those foods?"
        should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# Handle Yes response.
def handle_Yes_Response(intent, session):
    global global_state
    if global_state == 2:
        return get_recommended_dish_from_session(intent, session)

# Handle No response.
def handle_No_Response(intent, session):
    global global_state
    if global_state != 0:
        return handle_session_end_request()

# ================ Handler for chef ===================

def handle_repeat_indent(intent, session):
    speech_output = "there must be something wroing"
    reprompt_text = "you need to be right, man "
    should_end_session = False
    if current_recipe in recipes:
        steps = recipes[current_recipe]
        if (current_step< len(steps)):
            speech_output = steps[current_step]
    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def handle_go_to_step_intent(intent, session):
    global current_step
    step = int(intent['slots']['stepNumber']['value'])
    #speech_output = "!!!!!!!!!!!!!!!!!!!!!!!!!"
    #reprompt_text = "you need to be right, man "

    if current_recipe in recipes:
        steps = recipes[current_recipe]
        #print("current step: ", current_step, type(current_step) )
        #print("total step: ", len(steps), type(current_step))
        #print("aaaaaa")
        if step < len(steps):
            speech_output = "Now you came to step " + str(step) + steps[step]
            reprompt_text = "Now we are at step " + str(step) + steps[step]
            current_step = step
        else:
            speech_output = "This recipe only has " + str(len(steps)) + "steps."
            reprompt_text = "Now we are at step " + str(current_step) + steps[current_step]

    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, False))


def handle_prepare_intent(intent, session):
    global current_recipe
    global ingredients
    current_recipe = intent['slots']['RecipeName']['value']
    print("current recipe is", current_recipe)

    if current_recipe in recipes:
        speech_output = "To prepare " + current_recipe + " , we need " + ingredients[current_recipe] + " . Are you ready?"
        reprompt_text = "Take you time. You can tell me when you are well prepared for " + current_recipe
        should_end_session = False
        global current_step
        current_step = -1

    else:
        #TODO
        speech_output = "I can not find " + current_recipe + " in the cookbook. Please tell me another dish."
        reprompt_text = "I can not find " + current_recipe + " in the cookbook. Please tell me another dish. "
        should_end_session = False

    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def handle_next_step_intent(intent, session):
    speech_output = "there must be something wrong"
    reprompt_text = "you need to be right, man "
    should_end_session = False
    global current_step
    print("current step is %d", current_step)

    if current_recipe in recipes:
        steps = recipes[current_recipe]
        print("the length of step is ",len(steps))
        print("current step is ", current_step)
        current_step = current_step + 1
        if (current_step< len(steps)):
            speech_output = steps[current_step]
        else:
            speech_output = "We're all done. Enjoy!"
            should_end_session = True
    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def hanlde_which_step_intent(intent, session):
    should_end_session = False
    global current_step
    print("current step is %d", current_step)
    steps = recipes[current_recipe]
    if current_step == -1:
        speech_output = "We have not start yet. You can say next then we can start cooking " + current_recipe
        reprompt_text = speech_output
    elif (current_step < len(steps)):
        speech_output = "We are at" + steps[current_step]
        reprompt_text = speech_output
    else:
        speech_output = "We're all done. Enjoy!"
        should_end_session = True
    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def handle_cook_intent(intent, session):
    global current_recipe
    global recipes
    current_recipe = intent['slots']['RecipeName']['value']
    print("current recipe is", current_recipe)

    if current_recipe in recipes:
        speech_output = "To cook " + current_recipe + " , we need " + str(len(recipes[current_recipe])) + " steps. Would you like to follow me?"
        reprompt_text = "Come on, let's cook " + current_recipe
        should_end_session = False
        global current_step
        current_step = -1
        print("current step is", current_step)
    else:
        #TODO
        speech_output = "I can not find " + current_recipe + " in the cookbook. Please tell me another dish."
        reprompt_text = "I can not find " + current_recipe + " in the cookbook. Please tell me another dish. "
        should_end_session = False

    return build_response({}, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

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
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    # Calories Intent
    elif intent_name == "WhichDishesValidIntent":
        return get_dishes_from_session(intent, session)
    elif intent_name == "RecommendDishIntent":
        return get_recommended_dish_from_session(intent, session)
    elif intent_name == "YesResponseIntent":
        return handle_Yes_Response(intent, session)
    elif intent_name == "NoResponseIntent":
        return handle_No_Response(intent, session)

    elif intent_name == "PrepareIntent":
        return handle_prepare_intent(intent, session);
    elif intent_name == "CookIntent":
        return handle_cook_intent(intent, session);
    elif intent_name == "RepeatIntent":
        return handle_repeat_indent(intent,session)
    elif intent_name == "NextStepIntent":
        return handle_next_step_intent(intent, session);
    elif intent_name == "GoToStepIntent":
        return handle_go_to_step_intent(intent,session);
    elif intent_name == "WhichStepIntent":
        return hanlde_which_step_intent(intent, session);


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

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

