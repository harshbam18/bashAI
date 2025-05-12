import os
import json
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import PromptTemplate

# load vector store
embedding = OllamaEmbeddings(model="llama2")
vectorstore = FAISS.load_local("embeddings", embedding, allow_dangerous_deserialization=True)

# initialize LLM
llm = ChatOllama(model="llama2")

# define prompts
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

code_only_prompt = PromptTemplate.from_template("""
You are a Linux Bash expert. Based on the context, return only the single-line shell command or script that solves the user's query.

DO NOT return explanations, comments, or output examples.
DO NOT use markdown formatting or any special characters like backticks.
DO NOT include anything other than the pure command.

The output must be copy-paste ready to run in a bash shell.

Context:
{context}

Question:
{question}

Command:
""")



def query_bash_ai(question, save_path="response.json"):
    # Retrieve docs
    docs = vectorstore.similarity_search(question, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    # generate explanation
    expl_prompt = explanation_prompt.format(context=context, question=question)
    explanation = llm.invoke(expl_prompt).content.strip()

    # generate code with explanation
    code_prompt = code_only_prompt.format(context=explanation, question=question)
    code = llm.invoke(code_prompt).content.strip()

    # save results
    result = {
        "question": question,
        "explanation": explanation,
        "code": code
    }

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return result
