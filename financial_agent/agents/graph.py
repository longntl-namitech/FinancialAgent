from langgraph.graph import END, StateGraph, START

from financial_agent.agents.state import State
from financial_agent.agents import (
    memory_graph,
    planning_graph,
    supervisor_graph,
    file_control_graph,
    analyzer_graph,
    response_agent
)
from financial_agent.agents.memory.graph import update_memory

from financial_agent.core.logger import logger

graph = StateGraph(State)
graph.add_node("memory", memory_graph)
graph.add_node("planning", planning_graph)
graph.add_node("supervisor", supervisor_graph)
graph.add_node("file_controler", file_control_graph)
graph.add_node("analyzer", analyzer_graph)
graph.add_node("responser", response_agent)

graph.add_edge(START, "memory")
graph.add_edge("memory", "planning")
graph.add_edge("planning", "supervisor")
graph.add_edge("responser", END)

app = graph.compile()

logger.debug("Graph compiled successfully.")