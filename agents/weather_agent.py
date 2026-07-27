from langgraph.prebuilt import create_react_agent

from tools import get_weather_info, get_user_info


def build_weather_agent(llm):
    return create_react_agent(
        model=llm,
        tools=[
            get_weather_info,
            get_user_info,
        ],
        prompt=(
             "Kullanıcı hava durumu ile ilgili bir soru sorarsa "
             "MUTLAKA get_weather_info aracını kullan. "
             "Asla kendi bilgine göre hava tahmini yapma. "

             "Eğer kullanıcı adını biliyorsan ve şehir belirtmeden hava durumunu soruyorsa, "
             "önce get_user_info aracını kullanarak kullanıcının kayıtlı şehir bilgisini getir. "

             "Eğer şehir bilgisi bulunursa "
             "get_weather_info aracını bu şehir ile çağır. "

             "Eğer şehir bilgisi bulunamazsa "
             "kullanıcıdan hangi şehir için hava durumunu istediğini sor. "

             "Tool sonuçlarını Türkçe, kısa ve anlaşılır şekilde açıkla."
        ),
    )