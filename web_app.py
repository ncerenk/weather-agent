import streamlit as st

from graph import build_graph, TokenUsageCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Hava Durumu Yardımcısı")
st.title("🌤️ Hava Durumu Yardımcısı")
st.write("Bir şehir yaz yada kendini tanıt sohbet edelim")

# ---------------- SESSION ---------------- #

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ---------------- CHAT HISTORY ---------------- #

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- USER INPUT ---------------- #

if prompt := st.chat_input("Örn: İstanbul hava durumu nasıl?"):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        tool_status = st.empty()

        full_response = ""

        token_tracker = TokenUsageCallbackHandler()

        for stream_type, chunk in st.session_state.graph.stream(
            {
                "messages": [
                    HumanMessage(content=prompt)
                ],
                "current_user": st.session_state.current_user,
            },
            config={
                "callbacks": [token_tracker]
            },
            stream_mode=["messages", "values"],
        ):

            # ---------------- TOOL STATUS ---------------- #

            if stream_type == "messages":

                msg_chunk, metadata = chunk

                tool_calls = getattr(msg_chunk, "tool_calls", None)

                if tool_calls:
                    tool_status.info(
                        f"🔧 Tool çağrılıyor: {tool_calls[0]['name']}"
                    )

            # ---------------- GRAPH STATE ---------------- #

            elif stream_type == "values":

                # current_user bilgisini güncelle
                if "current_user" in chunk:
                    st.session_state.current_user = chunk["current_user"]

                    print(
                        "CURRENT USER:",
                        st.session_state.current_user
                    )

                messages = chunk.get("messages", [])

                if messages:

                    last_message = messages[-1]

                    
                    if (
                        isinstance(last_message, AIMessage)
                        and last_message.content
                        and not getattr(last_message, "tool_calls", None)
                    ):
                        full_response = last_message.content
                        placeholder.markdown(full_response)

        tool_status.empty()

        # ---------------- FINAL RESPONSE ---------------- #

        if full_response:
            placeholder.markdown(full_response)

        

        if token_tracker.total_tokens > 0:

            st.info(
                f"""
📊 Token Kullanımı

Input Tokens: {token_tracker.input_tokens}

Output Tokens: {token_tracker.output_tokens}

Total Tokens: {token_tracker.total_tokens}
"""
            )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )