from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import BaseMessage # foundational class for all msg types in langgraph
from langchain_core.messages import ToolMessage # pass data back to llm after it calls a tool
from langchain_core.messages import SystemMessage  # msg provides instruction to llm
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
import smtpblib, ssl, email 

load_dotenv()



class AgentState(TypedDict): 
    
    messages: Annotated[Sequence[BaseMessage], add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv('GOOGLE_API_KEY'))

## insert -- smtp settings
port = 465
smtp_server = "smtp.gmail.com"
sender_email = ""
receiver_email = ""
password = os.getenv('smtp_pass')
message = """\
Subject: Job application inquiry


    """

@tool 
def emailIt():
## 
    context = ssl.create_default_context()
    with smtpblib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

user_input = input("Enter your query: ")
while user_input !="exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter your query: ")
