import streamlit as st
from agent import build_agent
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
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        tool_status = st.empty()
        full_response = ""

        usage_totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

        for stream_type, chunk in st.session_state.agent.stream(
            {"messages": [HumanMessage(content=prompt)]},
            stream_mode=["messages", "values"],
        ):
            if stream_type == "messages":
                msg_chunk, metadata = chunk

                usage = getattr(msg_chunk, "usage_metadata", None)
                if usage:
                    usage_totals["input_tokens"] += usage.get("input_tokens", 0)
                    usage_totals["output_tokens"] += usage.get("output_tokens", 0)
                    usage_totals["total_tokens"] += usage.get("total_tokens", 0)

                if isinstance(msg_chunk, AIMessageChunk) and msg_chunk.content:
                    full_response += msg_chunk.content
                    placeholder.markdown(full_response + "▌")

            elif stream_type == "values":
                last = chunk["messages"][-1]

                if getattr(last, "tool_calls", None):
                    tool_status.info(
                        f"Tool çağrılıyor: {last.tool_calls[0]['name']}"
                    )

        placeholder.markdown(full_response)
        tool_status.empty()

        if usage_totals["total_tokens"] > 0:
            st.info(
                f"📊 Token Kullanımı\n\n"
                f"Input Tokens: {usage_totals['input_tokens']}\n\n"
                f"Output Tokens: {usage_totals['output_tokens']}\n\n"
                f"Total Tokens: {usage_totals['total_tokens']}"
            )

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )