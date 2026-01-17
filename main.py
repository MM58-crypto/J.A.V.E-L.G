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
    #messages: List[HumanMessage]

## insert -- smtp settings
port = 465
smtp_server = "smtp.gmail.com"
sender_email = ""
password = os.getenv('smtp_pass')
message = """\
Subject: Job opportunity inquiry

Dear Hiring Team,

I’m writing to express interest in a Software Engineer role at your esteemed company. With experience in software development, API testing, and software deployment, I’m eager to contribute to your team.

I’m proficient in Python, C++, JavaScript, and frameworks like Django and Nodejs, with additional experience in containerization tools such as Docker.

I’ve attached my resume and would appreciate the opportunity to discuss how my skills align with your needs.

Thank you for your consideration

Best Regards,



    """
emails_file = open("new_emails.txt", "r")


#def emailBody(state: AgentState) -> AgentState:
#    # make llm generate the email body and subject for the role
#    llm_response = llm.invoke(state["messages"])
#    print(f"\nJAVE: {response.content}")
#    return state


@tool 
def emailIt(file):
## 
## insert for loop to loop through the emails in the emails list
    context = ssl.create_default_context()
    with smtpblib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        try:
            for email in emails_file:
                server.sendmail(sender_email, email, message)
        except:
            print("An error occurred while sending emails")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv('GOOGLE_API_KEY'))
tools = [emailIt]


def llm_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are a powerful and helpful AI Assistant and Agent. fulfill my requests to the best of your ability
    """)
    llm_response = llm.invoke([system_prompt] + state["messages"])
    return  {"messages": [response]}
  

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = message[-1]

    if not last_message.tool_calls:
        
        return "end"
    else:
        return "continue"


# modify stategraph later
graph = StateGraph(AgentState)
graph.add_node("agent", llm_call)

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
    app.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter your query: ")
