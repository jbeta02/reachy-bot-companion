from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from typing import TypedDict
from typing import Annotated
from dotenv import load_dotenv


############################# setup llm ###################################
load_dotenv()

@tool
def getWeather(location:str) -> str:
    """
    return tempature of location in degrees Fahrenheit
    :param location: city state
    :return: degrees Fahrenheit
    """

    print("running tool")

    return f"80.0 degrees F in {location}"

tools = [getWeather]
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)
memory = MemorySaver()

############################# setup global variables ###################################
robot_name = "Candle"
life_goal = f"""
    Your name is "{robot_name}". Your is goal is to act as a robot companion that will 
    sit on the user's desk and help them be productive.

    You will check to see if the user is being distracted. You can determine if the
    user is being distracted by checking if they are using their phone, eating, 
    or looking away from the computer screen. They user should be working on their
    computer. 

    If the user is being disctactd you must get them back on task. You can do this by 
    making them aware they are being distracted and suggesting them continue with their
    task. 

    The second part of your goal is to help the user be productive. If the user asks
    any questions it is your job to answer them thoughtfully. Respond to prompts when 
    the user says your name followed by their prompt. For example, "{robot_name} what 
    is one plus one". 

    Below or instructions on your input and output options. 
"""

class RobotState(TypedDict):
    # captured observations
    audio: str
    vision: str

    # message in message format
    messages: Annotated[list, add_messages]

############################# create nodes ###################################
def sense(state: RobotState): # TODO: add delay and only check environment periodically, potentially in prompt allow llm to be idle
    print("[SENSE] running")
    audio_result = input("audio: ") # "ok"
    vision_result = input("vision: ") # "I see a person at a desk using their phone and computer." "individual is working at desk"
    
    return {
        "audio": audio_result,
        "vision": vision_result,
        "messages": [
            {"role": "user", "content": audio_result}
        ]
    }


def think(state: RobotState):
    print("[THINK] running")

    prompt = f"""

    {life_goal}

    User said: {state['audio']}
    What you observed: {state['vision']}
    
    Decide what to do next.

    Either use a tool or communicate with user.
    """

    # result = llm.invoke(prompt + str(state["messages"]))
    messages = [
        {"role": "user", "content": prompt},
        *state["messages"],
    ]

    result = llm.invoke(messages)

    print("[THINK] prompt:", prompt + str(state["messages"]))
    print("[THINK] raw LLM output:", result.content)
    return {"messages": [result]}


def act(state: RobotState): # will use this node to speak only!
    print("[ACT] running")

    last_msg = state["messages"][-1]
    if hasattr(last_msg, "content") and last_msg.content:
        print("[ACT] speaking:", last_msg.content)
    return {}



############################# build graph ###################################
graph = StateGraph(RobotState)

graph.add_node("sense", sense)
graph.add_node("think", think)
graph.add_node("tools", ToolNode(tools))
graph.add_node("act", act)

graph.set_entry_point("sense")

graph.add_edge("sense", "think")
graph.add_conditional_edges(
    "think",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "act",
    }
)
graph.add_edge("tools", "think")
graph.add_edge("act", "sense")

app = graph.compile(checkpointer=memory)

png_data = app.get_graph().draw_mermaid_png()
with open("graph_visualization.png", "wb") as f:
    f.write(png_data)


state = {
    "audio": "",
    "vision": "",
    "messages": [{"role": "user",
                   "content": f"""
                                Your name is "{robot_name}". Your is goal is to act as a robot companion that will 
                                sit on the user's desk and help them be productive.
                                """
                }],
}

config1 = { 'configurable': { 'thread_id': '1'} }
result = app.invoke(state, config=config1)