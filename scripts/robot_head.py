from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv
import os
from dummy_speak import DummySpeak

############################# setup llm ###################################
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

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

    If you think it will help you may choose to move your head and body to emphasize 
    your point. 

    Below or instructions on your input and output options. 
"""

speak_action = DummySpeak()
# speak_action2 = DummySpeak()
# speak_action3 = DummySpeak()

actions = []
actions.append(speak_action)
# actions.append(speak_action2)
# actions.append(speak_action3)

class RobotState(TypedDict):
    # captured observations
    audio: str
    vision: str

    # action to be perormed
    action: str

    # action performed
    response: str

############################# create nodes ###################################
def sense(state: RobotState):
    print("[SENSE] running")
    audio_result = input("audio: ") # "ok"
    vision_result = input("vision: ") # "I see a person at a desk using their phone and computer." "individual is working at desk"
    
    return {
        "audio": audio_result,
        "vision": vision_result
    }


def think(state: RobotState):
    print("[THINK] running")

    # build action options string
    list_actions = []
    for action in actions:
        list_actions.append(f"- {action.name}:{action.type}\n")
    actions_string = "".join(list_actions)

    prompt = f"""

    {life_goal}

    User said: {state['audio']}
    What you observed: {state['vision']}
    
    Decide what to do next.
    Choose ONE action option:
    {actions_string}
    - none
    
    Respond in format: [action]: [text]
    Where [action] is one of the options and [text] should contain
    no special characters so that it can be easily read out load.

    Example: speak: Try not to get distracted.
    Example: none
    """

    result = llm.invoke(prompt).content

    print("[THINK] prompt:", prompt)
    print("[THINK] raw LLM output:", result)
    return {"action": result}


def act(state: RobotState):
    print("[ACT] running")
    action = state["action"]
    
    for action_option in actions:
        if action.startswith(action_option.name + ":"):
            response = action.replace(action_option.name + ":", "")
            print(f"[ACT] {action_option.tag}{response}")
            return {"action": response}

    print("[ACT] No valid action detected")
    return {"response": "Idle"}



############################# build graph ###################################
graph = StateGraph(RobotState)

graph.add_node("sense", sense)
graph.add_node("think", think)
graph.add_node("act", act)

graph.set_entry_point("sense")

graph.add_edge("sense", "think")
graph.add_edge("think", "act")
graph.add_edge("act", "sense")

app = graph.compile()

state = {
    "audio": "",
    "vision": "",
    "action": "",
    "response": "",
}

result = app.invoke(state)