from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from financial_agent.agents.state import State
from financial_agent.agents.response.prompt import response_prompt

from financial_agent.core.config import configs
from financial_agent.core.logger import logger

response_agent = response_prompt | ChatOpenAI(model=configs.llm_model_name, temperature=0)
