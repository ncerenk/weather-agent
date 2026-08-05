import os
import re

from typing import Optional, Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import SystemMessage

from agents.weather_agent import build_weather_agent
from agents.general_agent import build_general_agent
from agents.router_agent import build_router

from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# ---------------- STATE ---------------- #

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_user: Optional[str]


# ---------------- TOKEN CALLBACK ---------------- #

class TokenUsageCallbackHandler(BaseCallbackHandler):
    """
    LLM cevap üretimini tamamladıktan sonra UsageMetadata'dan
    token kullanımını okuyan callback.
    """

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def on_llm_end(self, response: LLMResult, **kwargs):
        for generations in response.generations:
            for generation in generations:

                message = getattr(generation, "message", None)

                if (
                    message
                    and hasattr(message, "usage_metadata")
                    and message.usage_metadata
                ):
                    usage = message.usage_metadata

                    self.input_tokens += usage.get("input_tokens", 0)
                    self.output_tokens += usage.get("output_tokens", 0)
                    self.total_tokens += usage.get("total_tokens", 0)


# ---------------- GRAPH ---------------- #

def build_graph():

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY bulunamadı.")

    llm = ChatOpenAI(
        model="anthropic/claude-haiku-4.5",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=0,
        streaming=True,
        stream_usage=True,
        max_tokens=4096,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Weather Multi Agent",
        },
    )

    weather_agent = build_weather_agent(llm)
    general_agent = build_general_agent(llm)
    router = build_router(llm)

    memory = MemorySaver()

    workflow = StateGraph(AgentState)

    # ---------------- GENERAL NODE ---------------- #

    def general_node(state: AgentState):

        current_user = state.get("current_user")

        # Kullanıcının son mesajını al
        user_message = state["messages"][-1].content

        # Kullanıcı kendisini açıkça tanıttıysa
        # aktif kullanıcı olarak belirle
        patterns = [
            r"\bben\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\b",
            r"\badım\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\b",
            r"\bismim\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                user_message,
                re.IGNORECASE
            )

            if match:

                current_user = match.group(1).capitalize()

                print(
                    "CURRENT USER SET:",
                    current_user
                )

                break

        
        messages = list(state["messages"])
       
        if current_user:

            messages.insert(
                0,
                SystemMessage(
                    content=(
                        f"Aktif kullanıcının adı: {current_user}. "
                        f"Kullanıcı kendisi hakkında yeni bir bilgi verirse "
                        f"save_user_info aracını çağırırken name alanında "
                        f"{current_user} adını kullan. "
                        f"Kullanıcıdan adını tekrar isteme."
                    )
                )
            )

        result = general_agent.invoke(
            {
                "messages": messages
            }
        )

        return {
            "messages": result["messages"],
            "current_user": current_user,
        }

    # ---------------- WEATHER NODE ---------------- #

    def weather_node(state: AgentState):

        current_user = state.get("current_user")

        messages = list(state["messages"])

        # Aktif kullanıcı varsa Weather Agent'a bildir
        if current_user:

            messages.insert(
                0,
                SystemMessage(
                    content=(
                        f"Aktif kullanıcının adı: {current_user}. "
                        f"Kullanıcı şehir belirtmeden hava durumunu sorarsa "
                        f"önce get_user_info aracını {current_user} adıyla çağır "
                        f"ve kayıtlı şehir bilgisini öğren. "
                        f"Daha sonra get_weather_info aracını kayıtlı şehir ile çağır."
                    )
                )
            )

        result = weather_agent.invoke(
            {
                "messages": messages
            }
        )

        return {
            "messages": result["messages"],
            "current_user": current_user,
        }

    # ---------------- NODES ---------------- #

    workflow.add_node(
        "general",
        general_node
    )

    workflow.add_node(
        "weather",
        weather_node
    )

    # ---------------- ROUTER ---------------- #

    def route(state: AgentState):

        user_message = state["messages"][-1].content

        decision = router(user_message)

        print(
            "ROUTER:",
            decision
        )

        return decision

    workflow.add_conditional_edges(
        START,
        route,
        {
            "general": "general",
            "weather": "weather",
        },
    )

    workflow.add_edge(
        "general",
        END
    )

    workflow.add_edge(
        "weather",
        END
    )

    return workflow.compile(
        checkpointer=memory
    )
    