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


## insert -- smtp settings
port = 465
smtp_server = "smtp.gmail.com"
sender_email = ""
receiver_email = ""
password = os.getenv('smtp_pass')
message = """\
Subject: Job application inquiry
Dear Hiring Team,

I’m writing to express interest in a Software Engineer role at your esteemed company. With experience in software development, API testing, and software deployment, I’m eager to contribute to your team.

I’m proficient in Python, C++, JavaScript, and frameworks like Django and Nodejs, with additional experience in containerization tools such as Docker.

I’ve attached my resume and would appreciate the opportunity to discuss how my skills align with your needs.

Thank you for your consideration

Best Regards,



    """

@tool 
def emailIt():
## 
    context = ssl.create_default_context()
    with smtpblib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv('GOOGLE_API_KEY'))
tools = [emailIt]

def agent(state: AgentState) -> AgentState:
    systtem_prompt = SystemMessage(content=f"""
    * insert suitable system prompt *
    """)

# modify stategraph later
graph = StateGraph(AgentState)
graph.add_node("agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

graph.add_edge("tools", "agent")

app = graph.compile()

user_input = input("Enter your query: ")
while user_input !="exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter your query: ")
