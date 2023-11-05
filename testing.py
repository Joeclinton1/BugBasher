from secret_key import OPENAI_API_KEY
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.docstore.document import Document
# import
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import time 
import subprocess
import sys

# Setting up the LLM

api_key = OPENAI_API_KEY

llm = ChatOpenAI(temperature=0.4, model_name="gpt-3.5-turbo", openai_api_key=api_key)

test_template = f"""
hello
"""

test_prompt = PromptTemplate(
    input_variables = [],
    template = test_template 
) 

test_chain = LLMChain(llm=llm, prompt=test_prompt, verbose=True)

# code_test = """
# a = 2 + 2
# print(a)
# """

# code_result = run_code('example_test_cases.py')

command = 'python example_test_cases.py' # Example: command = 'python trial.py'
process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)

print(process)

# Making an embedded Chroma document
# Probably need a persistent version later 

# Some test documents 
# test_doc = Document(
#     page_content="test query title",
#     metadata={}
# )

# test_doc2 = Document(
#     page_content="this document is about techno",
#     metadata={}
# )

# test_doc3 = Document(
#     page_content="this document is about farm animals",
#     metadata={}
# )

# test_doc4 = Document(
#     page_content="this document is about tech",
#     metadata={}
# )

# test_docs = [test_doc, test_doc2, test_doc3, test_doc4]

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# db = Chroma.from_documents(test_docs, embedding_function, persist_directory="./chroma_db")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

start = time.time() 
query = "looking for info about techno"
docs = db.similarity_search(query)
end = time.time()

print(docs[0].page_content, f'retrieved in {end-start} secs')

# print(test_chain.run({}))



