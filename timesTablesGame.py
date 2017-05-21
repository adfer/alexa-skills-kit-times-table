import math
import random

SKILL_NAME = "Times tables games"


def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest, etc).
    The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID
    to prevent someone else from configuring a skill that sends requests
    to this function.
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


def on_session_started(session_started_request, session):
    """Called when the session starts."""
    print("on_session_started requestId=" +
          session_started_request['requestId'] + ", sessionId=" +
          session['sessionId'])


def init_game():
    """If we wanted to initialize the session to have some attributes we could add those here."""
    intro = ("Let's play {}. ".format(SKILL_NAME))
    should_end_session = False

    spoken_question = "How may questions would you like?"

    speech_output = intro + spoken_question
    attributes = {"speech_output": speech_output,
                  "reprompt_text": spoken_question,
                  "initializing": True
                  }

    return build_response(attributes, build_speechlet_response(
        SKILL_NAME, speech_output, spoken_question, should_end_session))


def on_launch(launch_request, session):
    """Called when the user launches the skill without specifying what they want."""
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return init_game()


def on_intent(intent_request, session):
    """Called when the user specifies an intent for this skill."""
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AnswerIntent":
        return handle_answer_request(intent, session)
    elif intent_name == "AnswerOnlyIntent":
        return handle_answer_request(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return handle_answer_request(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return handle_answer_request(intent, session)
    elif intent_name == "AMAZON.StartOverIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.RepeatIntent":
        return handle_repeat_request(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return handle_get_help_request(intent, session)
    elif intent_name == "AMAZON.StopIntent":
        return handle_finish_session_request(intent, session)
    elif intent_name == "AMAZON.CancelIntent":
        return handle_finish_session_request(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def get_welcome_response(session):
    """If we wanted to initialize the session to have some attributes we could add those here."""
    number_of_questions = int(session['attributes']['number_of_questions'])
    intro = ("I will ask you {} questions. ".format(number_of_questions))
    should_end_session = False
    starting_index = 0

    first_argument = int(math.floor(random.random() * 10))
    second_argument = int(math.floor(random.random() * 10))
    spoken_question = "{} multiply by {}".format(first_argument, second_argument)
    correct_answer = first_argument * second_argument

    speech_output = intro + spoken_question
    attributes = {"speech_output": speech_output,
                  "reprompt_text": spoken_question,
                  "current_questions_index": starting_index,
                  "score": 0,
                  "correct_answers": correct_answer,
                  "number_of_questions": number_of_questions
                  }

    return build_response(attributes, build_speechlet_response(
        SKILL_NAME, speech_output, spoken_question, should_end_session))


def handle_answer_request(intent, session):
    should_end_session = False
    answer = int(intent['slots'].get('Answer', {}).get('value'))
    print(("User's answer is {}".format(answer)))

    if 'initializing' in session['attributes']:
        session['attributes']['number_of_questions'] = answer
        return get_welcome_response(session)

    number_of_questions = int(session['attributes']['number_of_questions'])

    print(("Correct answer is {}".format(session['attributes']['correct_answers'])))
    user_gave_up = intent['name']

    if not answer and user_gave_up == "DontKnowIntent":
        # If the user provided answer isn't a number > 0 and < ANSWER_COUNT,
        # return an error message to the user. Remember to guide the user
        # into providing correct values.
        reprompt_text = session['attributes']['speech_output']
        speech_output = "Your answer must be a known element " + reprompt_text
        return build_response(
            session['attributes'],
            build_speechlet_response(
                SKILL_NAME, speech_output, reprompt_text, should_end_session
            ))
    else:
        current_score = session['attributes']['score']
        current_questions_index = session['attributes']['current_questions_index']
        correct_answers = int(session['attributes']['correct_answers'])

        print("Is answer correct: {}.".format(answer == correct_answers))

        speech_output_analysis = None
        if answer == correct_answers:
            current_score += 1
            speech_output_analysis = "correct. "
        else:
            if user_gave_up != "DontKnowIntent":
                speech_output_analysis = "wrong. "
            speech_output_analysis = (speech_output_analysis +
                                      "The correct answer is {}".format(
                                          correct_answers))

        # if current_questions_index is 4, we've reached 5 questions
        # (zero-indexed) and can exit the game session
        if current_questions_index == number_of_questions - 1:
            speech_output = "" if intent['name'] == "DontKnowIntent" else "That answer is "
            speech_output = (speech_output + speech_output_analysis +
                             "You got {} out of {} correct. ".format(current_score, number_of_questions) +
                             "Thank you for playing {} with Alexa!".format(SKILL_NAME))
            reprompt_text = None
            should_end_session = True
            return build_response(
                session['attributes'],
                build_speechlet_response(
                    SKILL_NAME, speech_output, reprompt_text, should_end_session
                ))
        else:
            current_questions_index += 1
            first_argument = int(math.floor(random.random() * 10))
            second_argument = int(math.floor(random.random() * 10))
            spoken_question = "{} multiply by {}".format(first_argument, second_argument)
            correct_answer = first_argument * second_argument
            reprompt_text = spoken_question

            speech_output = "" if user_gave_up == "DontKnowIntent" else "That answer is "
            speech_output = (speech_output + speech_output_analysis +
                             "Your score is " +
                             str(current_score) + '. ' + reprompt_text)
            attributes = {"speech_output": speech_output,
                          "reprompt_text": reprompt_text,
                          "current_questions_index": current_questions_index,
                          "score": current_score,
                          "correct_answers": correct_answer,
                          "number_of_questions": number_of_questions
                          }

            return build_response(attributes,
                                  build_speechlet_response(SKILL_NAME, speech_output, reprompt_text,
                                                           should_end_session))


def handle_repeat_request(intent, session):
    """
    Repeat the previous speech_output and reprompt_text from the session['attributes'].
    If available, else start a new game session.
    """
    if 'attributes' not in session or 'speech_output' not in session['attributes']:
        return get_welcome_response()
    else:
        attributes = session['attributes']
        speech_output = attributes['speech_output']
        reprompt_text = attributes['reprompt_text']
        should_end_session = False
        return build_response(
            attributes,
            build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)
        )


def handle_get_help_request(intent, session):
    attributes = {}
    speech_output = ("You can begin a game by saying start a new game, or, "
                     "you can say exit... What can I help you with?")
    reprompt_text = "What can I help you with?"
    should_end_session = False
    return build_response(
        attributes,
        build_speechlet_response(SKILL_NAME, speech_output, reprompt_text, should_end_session)
    )


def handle_finish_session_request(intent, session):
    """End the session with a message if the user wants to quit the game."""
    attributes = session['attributes']
    reprompt_text = None
    speech_output = "Thanks for playing {}!".format(SKILL_NAME)
    should_end_session = True
    return build_response(
        attributes,
        build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)
    )


# --------------- Helpers that build all of the responses -----------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_speechlet_response_without_card(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speechlet_response
    }
