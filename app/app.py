import os
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage,  ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from hero_db import HeroDB

def get_hero(hero_name: str):
    hero_db = HeroDB()
    return hero_db.heroes.get(hero_name)


@st.cache_resource(show_spinner=False)
def get_llm(key, model, temperature):
    llm = ChatOpenAI(api_key=key, model=model, temperature=temperature)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a DOTA 2 expert. You must answer to the user's questions using the available tool `get_hero` to retrieve the information regarding the hero. Always generate the hero names in lower case"),
            ("human", "User message: {user_message} \n\n Chat History: {chat_history}")

        ]
    )
    llm_with_tools = llm.bind_tools([get_hero])
    return prompt_template | llm_with_tools

st.set_page_config(page_title="Minimal Chat", page_icon="💬")

# --- Sidebar for config ---
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1", "gpt-5-mini", "gpt-5-nano"], index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
system_prompt = st.sidebar.text_area("System prompt", "You are a helpful assistant.")

# --- State ---
if "msgs" not in st.session_state:
    st.session_state.msgs = [SystemMessage(content=system_prompt)]

# If the sidebar prompt changes, replace the first system message
if st.session_state.msgs and isinstance(st.session_state.msgs[0], SystemMessage):
    if st.session_state.msgs[0].content != system_prompt:
        st.session_state.msgs[0] = SystemMessage(content=system_prompt)

llm = get_llm(api_key, model, temperature) if api_key else None

st.title("Conversational AI (one user message → one reply)")

# --- Render history (skip the system message) ---
for m in st.session_state.msgs[1:]:
    role = "user" if isinstance(m, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(m.content)

# --- Input box ---
if prompt := st.chat_input("Type your message…"):
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.msgs.append(HumanMessage(content=prompt))

    # Generate assistant reply (single-turn response based on running history)
    if not llm:
        reply = "⚠️ Please provide an OpenAI API key in the sidebar."
    else:
        try:
            ai = llm.invoke({'user_message': prompt,'chat_history':st.session_state.msgs})
            if ai.tool_calls:
                tool_response = get_hero(**ai.tool_calls[0]['args'])
                st.session_state.msgs.append(ToolMessage(content=tool_response, tool_call_id=ai.tool_calls[0]['id']))
                ai = llm.invoke({'user_message': prompt, 'chat_history': st.session_state.msgs})
                reply = ai.content
            else:
                reply = ai.content
        except Exception as e:
            reply = f"❌ Error: {e}"

    # Show assistant reply
    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.msgs.append(AIMessage(content=reply))

# --- Utilities ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Clear chat"):
        st.session_state.msgs = [SystemMessage(content=system_prompt)]
        st.rerun()
with col2:
    st.caption("Built with Streamlit + LangChain ChatOpenAI. No tools, no HTML—just message in, reply out.")