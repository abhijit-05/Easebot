import time
import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory

from utils import img_to_base64, vectorstore
from prompts import contextualize_q_system_prompt, qa_system_prompt
from new_citation import clean_chat_history, get_citations
source_md = "\n"+"""
**Sources:**\n""" + "\n"

def stream_data(data):
    for item in data.split(" "):
        yield item + ' '
        time.sleep(0.04)



st.set_page_config(
    page_title="EASE-Bot",
    layout="wide",
    initial_sidebar_state="expanded"
)

chat_message_history = MongoDBChatMessageHistory(
    session_id="test_session",
    connection_string="mongodb://localhost:27017",
    database_name="ChatbotDB",
    collection_name="Chat-History",
)

model = ChatOpenAI(
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="not-needed",
    base_url="http://192.168.4.31:1234/v1",
)

retriever = vectorstore.as_retriever(search_kwargs={'k':10})

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    model, retriever, contextualize_q_prompt
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


st.sidebar.title("EASE Bot")
if st.sidebar.button('Clear History'):
    st.session_state.chat_history.clear()
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state.chat_history.add_ai_message('How can I help you?')
    st.rerun()
    

st.title("EASE Bot")
st.session_state["chat_history"] = chat_message_history
if history := st.session_state.chat_history.messages:
    st.session_state["messages"] = []
    for message in history:
        if type(message) == HumanMessage:
            role = "user"
        elif type(message == AIMessage):
            role = "assistant"
        st.session_state.messages.append({"role": role, "content": message.content})
else:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state.chat_history.add_ai_message('How can I help you?')

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_history.add_user_message(prompt)
    st.chat_message("user").write(prompt)
    history = clean_chat_history(st.session_state["chat_history"].messages)
    response = rag_chain.invoke({"input": prompt, "chat_history": history})
    msg = response['answer']
    msg_with_citation = msg + get_citations(prompt)
    st.session_state.messages.append({"role": "assistant", "content": msg_with_citation})
    st.session_state.chat_history.add_ai_message(msg_with_citation)
    st.chat_message("assistant").write_stream(stream_data(msg_with_citation))