import time

import streamlit as st
from agent.react_agent import ReactAgent
st.title("智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] =ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    response_messages = []
    with st.spinner("think..."):
        res_stream = st.session_state["agent"].excute_stream(prompt)

        def capture(generator,cache_list):
            for item in generator:
                cache_list.append(item)
                for char in item:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]}) 