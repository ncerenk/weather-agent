import streamlit as st
from agent import build_agent, TokenUsageCallbackHandler
from langchain_core.messages import HumanMessage, AIMessageChunk

st.set_page_config(page_title="Hava Durumu Agent")
st.title("Hava Durumu Agent")
st.write("Bir şehir yaz, agent gerçek hava durumu tool'unu çağırıp cevap versin.")

if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Örn: İstanbul hava durumu nasıl?"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        tool_status = st.empty()
        full_response = ""

        # Token callback
        token_tracker = TokenUsageCallbackHandler()

        for stream_type, chunk in st.session_state.agent.stream(
            {"messages": [HumanMessage(content=prompt)]},
            config={
                "callbacks": [token_tracker]
            },
            stream_mode=["messages", "values"],
        ):

            if stream_type == "messages":
                msg_chunk, metadata = chunk

                if isinstance(msg_chunk, AIMessageChunk) and msg_chunk.content:
                    full_response += msg_chunk.content
                    placeholder.markdown(full_response + "▌")

            elif stream_type == "values":
                last = chunk["messages"][-1]

                if getattr(last, "tool_calls", None):
                    tool_status.info(
                        f"🔧 Tool çağrılıyor: {last.tool_calls[0]['name']}"
                    )

        placeholder.markdown(full_response)
        tool_status.empty()

        if token_tracker.total_tokens > 0:
            st.info(
                f"📊 Token Kullanımı\n\n"
                f"Input Tokens: {token_tracker.input_tokens}\n\n"
                f"Output Tokens: {token_tracker.output_tokens}\n\n"
                f"Total Tokens: {token_tracker.total_tokens}"
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )