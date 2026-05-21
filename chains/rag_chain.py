from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

from utils.prompt_template import LEGAL_PROMPT

load_dotenv()


def create_rag_chain(google_api_key=None):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=google_api_key or os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    prompt = PromptTemplate(
        template=LEGAL_PROMPT,
        input_variables=["context", "question"]
    )

    return prompt | llm | StrOutputParser()