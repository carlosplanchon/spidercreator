#!/usr/bin/env python3

from langchain.chat_models import init_chat_model

from langchain_google_genai import ChatGoogleGenerativeAI

# OpenAI:
# https://platform.openai.com/docs/api-reference/introduction
gpt4o_llm = init_chat_model(
    model="gpt-4o",
    model_provider="openai"
)
gpt45_llm = init_chat_model(
    model="gpt-4.5-preview",
    model_provider="openai"
)
o1_llm = init_chat_model(
    model="o1",
    model_provider="openai"
)

# Google Gemini:
# https://ai.google.dev/gemini-api/docs/models#gemini-2.5-pro-preview-03-25
gemini_2_5_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",
    temperature=0,
    max_retries=5
)
