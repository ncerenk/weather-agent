from typing import Literal

from pydantic import BaseModel


class Route(BaseModel):
    next: Literal["weather", "general"]


def build_router(llm):
    router_llm = llm.with_structured_output(Route)

    def route(user_message: str) -> str:
        prompt = f"""
Sen bir Router Agent'sın.

Görevin kullanıcı mesajını doğru uzmana yönlendirmek.

SADECE aşağıdaki iki kelimeden birini döndür:

weather
general

Kurallar:

- Hava durumu
- Sıcaklık
- Yağmur
- Kar
- Rüzgar
- Nem
- Şehirlerin hava durumu
- Şemsiye gerekip gerekmediği
- Mont giyilip giyilmeyeceği

ile ilgiliyse

weather

döndür.

Diğer tüm mesajlar için

general

döndür.

Kullanıcı mesajı:

{user_message}
"""

        result = router_llm.invoke(prompt)

        return result.next

    return route