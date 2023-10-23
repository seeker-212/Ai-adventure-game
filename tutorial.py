from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.llms import OpenAI
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain import LLMChain, PromptTemplate
import json

cloud_config= {
  'secure_connect_bundle': 'secure-connect-adventure-game.zip'
}

with open("adventure game-token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = "database"
OPENAI_API_KEY = "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"

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history,
)


template = """
"you are now the guide of a mystical journey in the whispering woods.
A traveler named John seeks the lost Gen of serenity.
You must navigate her through Challenges, Choices, and consequences,
dynamically adapting the tale based on the traveler's decisions.
Your goal is to create a branching narrative experience where each choices
leads to a new path, ultimately determining John's fate,

Here are some rules to follow:
1. start by asking the player to choose some kind of weapons that will be used later in the game
2.Have a few paths that leads to success
3.Have some Paths that leads to death. if the user dies generate a response that explains the death and ends in the text: 

Here is the chat history, use this to understand what to say next: (chat_history)
Human: (human_input)
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm =OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    Llm=llm,
    prompt="prompt",
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input="start the game")
    print(response.strip())

    if "The End" in response:
        break

    choice =input("Your reply: ")