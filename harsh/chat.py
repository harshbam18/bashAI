import os
import json
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
import dotenv
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\Users\Harsh Sharma\Desktop\sujal-maheshwari2004 bashAI main sujal\DataPreperation\env")

# Load API key securely from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Load vector store using OpenAI embeddings
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=openai_api_key
)
vectorstore = FAISS.load_local("embeddings", embedding, allow_dangerous_deserialization=True)

# Initialize GPT-4o model
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=openai_api_key
)

# Prompt for explanation
explanation_prompt = PromptTemplate.from_template("""
You are a helpful assistant that explains Linux Bash scripting concepts in detail.
Using the provided context, answer the user's question in a clear and thorough way.
Give response shortly and concisely, use only text and no markdown.

Context:
{context}

Question:
{question}

Answer:
""")

# Prompt for code-only response
code_only_prompt = PromptTemplate.from_template("""
You are a Linux Bash expert. Based on the context, return only the single-line shell command or script that solves the user's query.

DO NOT return explanations, comments, or output examples.
DO NOT use markdown formatting or any special characters like backticks.
DO NOT include anything other than the pure command.
DO NOT include ''' or ' or " at the beginning or end of the command.
DO NOT include any other text or explanation.

The output must be copy-paste ready to run in a bash shell.

Context:
{context}

Question:
{question}

Command:
""")

# Main function to process a query
def query_bash_ai(question, save_path="response.json", k=5):
    # Search for relevant documents
    docs = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join(doc.page_content for doc in docs)

    if not context:
        return {
            "question": question,
            "explanation": "No relevant context found to generate an answer.",
            "code": ""
        }

    # Generate explanation
    expl_prompt = explanation_prompt.format(context=context, question=question)
    explanation = llm.invoke(expl_prompt).content.strip()

    # Generate bash command
    code_prompt = code_only_prompt.format(context=explanation, question=question)
    code = llm.invoke(code_prompt).content.strip()

    # Save result
    result = {
        "question": question,
        "explanation": explanation,
        "code": code
    }

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return result
