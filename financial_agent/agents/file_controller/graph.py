from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from typing import Literal
from financial_agent.agents.state import State
from financial_agent.agents.file_controller.prompt import file_control_prompt
from financial_agent.agents.file_controller.tools import tools
from financial_agent.core.config import configs


model = ChatOpenAI(
    model=configs.llm_model_name,
    api_key=configs.openai_api_key,
    temperature=0.0,
    streaming=True
)

file_control_agent = create_react_agent(
    model,
    tools=tools,
    prompt=file_control_prompt,
    name="file_controler",
)

def file_control_graph(state: State) -> Command[Literal["supervisor"]]:
    result = file_control_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="file_controler")
            ]
        },
        goto="supervisor",
    )