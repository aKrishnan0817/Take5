
import pathlib
import textwrap
import google.generativeai as genai
from langchain.prompts import PromptTemplate,ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core import retry
from secret import GOOGLE_API_KEY
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferWindowMemory

#get API key



def get_activity():
    activity = genai.protos.FunctionDeclaration(
    name="activity",
    description=textwrap.dedent("""\
        Extract the activity and a description of the activity from the user's input.
        """),
    parameters = genai.protos.Schema(
    type = genai.protos.Type.OBJECT,
    properties = {
        'name':  genai.protos.Schema(type=genai.protos.Type.STRING),
        'description':  genai.protos.Schema(type=genai.protos.Type.STRING)
    },
    required=['name', 'description']
    )
    )
    return activity
def get_confirm():
    confirm = genai.protos.FunctionDeclaration(
        name="confirm",
        description=textwrap.dedent("""\
            Extract if the user is affirmitaive or not as yes, no, or unknown. 
            """),
        parameters = genai.protos.Schema(
        type = genai.protos.Type.OBJECT,
        properties = {
            #'name':  genai.protos.Schema(type=genai.protos.Type.STRING),
            'yes_or_no':  genai.protos.Schema(type=genai.protos.Type.STRING)
        },
        required=['yes_or_no']
    )
    )
    return confirm

genai.configure(api_key=GOOGLE_API_KEY)
activity_model = genai.GenerativeModel(
    model_name='models/gemini-1.5-pro-latest',
    tools = [get_activity()]) #The Chatbot that extracts the activity and a description

confirmation_model = genai.GenerativeModel(
    model_name='models/gemini-1.5-pro-latest',
    tools = [get_confirm()])



#def chat(user_input):
chat_gemini = ChatGoogleGenerativeAI(google_api_key = GOOGLE_API_KEY, model="gemini-pro",
                                      temperature =0.4)
prompts = PromptTemplate(input_variables=['history', 'input'], template="""The following is a friendly conversation between a human and an AI.
The AI is a mental health advisor that should be gentle, and reccomend self-care activities depending on the clients situation.
The AI should also give a description of the activity.
The AI should only reccomend one activity at a time.
The AI should try to prompt the user about what self-care the user enjoys, and what problems they may be facing.
\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:""")

conversation_chain = ConversationChain(llm=chat_gemini, memory=ConversationBufferWindowMemory(k=3), prompt = prompts)

#response = conversation_chain.invoke(user_input)

#conversation_chain.invoke(response["history"]).split("AI")[-1]


while True:
  activities = {}
  response = " "
  question = input("Ask a question: ")
  confirm = confirmation_model.generate_content(f"""
    {question}
    """,
    tool_config={'function_calling_config':'ANY'})
  for key, value in confirm.candidates[0].content.parts[0].function_call.args.items():
    print(key, value)
    if value == "yes":
      activity = activity_model.generate_content(f"""
      {response["history"].split("AI:")[-1]}
      """,
      tool_config={'function_calling_config':'ANY'})
      for keys,values in activity.candidates[0].content.parts[0].function_call.args.items():
        activities[keys] = values
  if question == "exit":
    break
  response = conversation_chain.invoke(question)
  print(response["response"])
  print(response["history"])
