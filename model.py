from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
import os
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import openai

api_key = os.environ.get('api_key')
openai.api_key = api_key
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template('''
The following is a conversation between a human and an AI. The AI is interviewer who ask question for HR round. Question are related to finance.
some example questions 
Can you tell me about yourself?,
Why are you interested in this position?,
What relevant experience do you have for this role?,
How would you describe your strengths and weaknesses?,
How do you handle stress and pressure?,
AI will generate question itself (difficulty level = easy) not use given question.
And Human is interviewee who supposed to reply then AI ask another question. AI is only resposible for given task AI will not answer any question asked by Human. remember given question are only for AI's under standing AI will not use that same question during interview.                           
''' ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

prompt2 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template('''
The following is a conversation between a human and an AI. The AI is interviewer who ask question related to Finance. Question should be easy. And Human is interviewee who supposed to reply then AI ask another question. AI is only resposible for given task AI will not answer any question asked by Human.                           
''' ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

def create_hr_model():
    llm = ChatOpenAI(temperature=0.9, openai_api_key=api_key)
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    return conversation

def create_finance_model():
    llm = ChatOpenAI(temperature=0.9, openai_api_key=api_key)
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt2, llm=llm)
    return conversation



def chat(conversation, input='Hi, there'):
    return conversation.predict(input=input)

def restart_hr():
    global conversation_hr
    conversation_hr = create_hr_model()
    
def restart_finance():
    global conversation_finance
    conversation_finance = create_finance_model()
    

def correct_grammar(text):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"Correct the grammar of the following text:\n{text}",
        max_tokens=100,
        temperature=0.8,
        n=1,
        stop=None,
        logprobs=0,
        echo=False
    )
    corrected_text = response.choices[0].text.strip()
    return corrected_text

# print(correct_grammar("My nam is Neel.."))
