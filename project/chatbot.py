from flask_login import login_user, login_required, logout_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from .models import User
from . import db
from .secret import apiKey
from openai import OpenAI


chatbot = Blueprint('chatbot', __name__)



API_KEY = apiKey
client = OpenAI(api_key=API_KEY)


iprompt = []
assert1={"role": "system", "content": "You are an ai mental health assistant"}
assert2={"role": "assistant", "content": "You are to speak to the user and slowly get to know them then recmcomend a self-care activity"}
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



def prepare_message(uinput,inputType, functionCalling = tools,button= None):
  #enter the request with a microphone or type it if you wish
  if inputType == 2:
      uinput = ""


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
