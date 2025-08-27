from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from tools import tools_mapping


def get_llm_agent(model, **kwargs):
    llm = ChatOpenAI(model=model, streaming=True, **kwargs)
    with open('prompts/agent_prompt.md') as file:
        base_prompt = file.read()

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", base_prompt),
            ("human", "User message: {user_message} \n\n Chat History: {chat_history}")

        ]
    )
    llm_with_tools = llm.bind_tools(list(tools_mapping.values()))
    return prompt_template | llm_with_tools