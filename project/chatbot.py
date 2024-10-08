from flask_login import login_user, login_required, logout_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from .models import User
from . import db
from .secret import apiKey
from .secret import GOOGLE_API_KEY
from openai import OpenAI
import requests

chatbot = Blueprint('chatbot', __name__)


API_KEY = apiKey
client = OpenAI(api_key=API_KEY)
gemini_key = GOOGLE_API_KEY

iprompt = []
assert1={"role": "user", "content": "You are an ai mental health assistant"}
assert2={"role": "model", "content": "You are to speak to the user and slowly get to know them then recommend a self-care activity"}
iprompt.append(assert1)
iprompt.append(assert2)

tools = [
      {
          "type": "function",
          "function": {
              "name": "stop",
              "description": "the user wants to stop having this conversation",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "location": {
                          "type": "string",
                          "description": "Example return",
                      },
                  },
              },
          }
      }
  ]

@chatbot.route("/chatbot")
def take5_chatbot():
    return render_template('chat.html',title="TAKE5 AI")

@chatbot.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg

    _,response,_ = prepare_message(input,iprompt)
    return response

# J's new route to get messages with history
@chatbot.route("/get_with_history", methods=["GET", "POST"])
def chat_with_history():
    data = request.get_json()
    print("data")

    message_history = data["message_history"]
    print(message_history)
    print("running get_gemini_chat_response")
    response = get_gemini_chat_response(message_history, system_prompt="You are an AI mental health assistant.")
    text = response["candidates"][0]["content"]["parts"][0]["text"]
    #`{"response":{"candidates":[{"content":{"parts":[{"text":"Hello! It's nice to hear from you. What's on your mind today? \\n"}],"role":"model"},"finishReason":"STOP","index":0,"safetyRatings":[{"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","probability":"NEGLIGIBLE"},{"category":"HARM_CATEGORY_HATE_SPEECH","probability":"NEGLIGIBLE"},{"category":"HARM_CATEGORY_HARASSMENT","probability":"NEGLIGIBLE"},{"category":"HARM_CATEGORY_DANGEROUS_CONTENT","probability":"NEGLIGIBLE"}]}],"usageMetadata":{"candidatesTokenCount":20,"promptTokenCount":14,"totalTokenCount":34}}}`
    return jsonify({"response": text})
    #_,response,_ = get_gemini_chat_response(message_history,iprompt)
    #_,response,_ = prepare_message_with_history(message_history,iprompt)
    #return response

def get_Chat_response(text):

    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)


# Prepare Gemini message with history
def get_gemini_chat_response(message_history, system_prompt):

    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=" + gemini_key  # Replace with Gemini's endpoint
    headers = {
        'Content-Type': 'application/json'#,
        #'Authorization': 'Bearer ' + gemini_key  # Use Bearer token if required
    }

    # Prepare the data payload with roles and content
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "model", "parts": [{"text": "Understood."}]},
            *[
                {"role": message["role"], "parts": [{"text": message["content"]}]}
                for message in message_history
            ]
        ]
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        gemini_output = response.json()  # Assuming structured JSON response
        # Extract the relevant text portion from the returned 'gemini_output'
        return gemini_output['choices'][0]['message']['content'] if 'choices' in gemini_output else gemini_output
    else:
        print(response.json())
        return "Gemini API Error"

# J's edit: A prepare_message function with a way to store the user's history
def prepare_message_with_history(messages, inputType, functionCalling = tools,button= None):
  for message in messages:
      iprompt.append(message)
  print("iprompt")
  print(iprompt)
  response=client.chat.completions.create(model="gpt-4o",messages=iprompt,tools=functionCalling, tool_choice="auto")

  text = response.choices[0].message.content

  try:
      functionCalled = response.choices[0].message.tool_calls[0].function.name
      print("Function called:", functionCalled)

      #response=client.chat.completions.create(model="gpt-4",messages=iprompt)
  except:
      functionCalled = None
      iprompt.append({"role" : "assistant" , "content" : text})
  print(text)
  return iprompt, text, functionCalled

def prepare_message(uinput,inputType, functionCalling = tools,button= None):
  #enter the request with a microphone or type it if you wish
  print("uinput")
  print(uinput)
  print("inputType")
  print(inputType)
  if inputType == 2:
      uinput = ""

  print("iprompt")
  print(iprompt)

  # J's edit: include the user text
  iprompt.append({"role":"user", "content": uinput})
  response=client.chat.completions.create(model="gpt-4o",messages=iprompt,tools=functionCalling, tool_choice="auto")

  text = response.choices[0].message.content

  try:
      functionCalled = response.choices[0].message.tool_calls[0].function.name
      print("Function called:", functionCalled)

      #response=client.chat.completions.create(model="gpt-4",messages=iprompt)
  except:
      functionCalled = None
      iprompt.append({"role" : "assistant" , "content" : text})
  print(text)
  return iprompt, text, functionCalled
