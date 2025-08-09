from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from tools.tools import get_hero


def get_llm_agent(model, temperature):
    llm = ChatOpenAI(model=model, temperature=temperature, streaming=True)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a DOTA 2 expert. You must answer to the user's questions using the available tool `get_hero` to retrieve the information regarding the hero. Always generate the hero names in lower case"),
            ("human", "User message: {user_message} \n\n Chat History: {chat_history}")

        ]
    )
    llm_with_tools = llm.bind_tools([get_hero])
    return prompt_template | llm_with_tools