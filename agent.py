import os
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools import get_weather_info

load_dotenv()
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
                    
def build_agent():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY bulunamadı. .env dosyasını kontrol et.")

    model = ChatOpenAI(
        model="anthropic/claude-haiku-4.5",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=0,
        streaming=True,
        stream_usage=True,
        max_tokens=4096,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Weather Agent",
        },
    )

    agent = create_agent(
        model=model,
        tools=[get_weather_info],
        system_prompt=(
            "Sen bir hava durumu asistanısın. "
            "Kullanıcı bir şehir adı yazarsa veya hava durumunu sorarsa "
            "mutlaka get_weather_info tool'unu çağır. "
            "Asla kendi bilgine göre tahmin yürütme. "
            "Tool sonucunu Türkçe, kısa ve anlaşılır şekilde açıkla."
        ),
    )

    return agent