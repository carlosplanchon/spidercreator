#!/usr/bin/env python3

from langchain.chat_models import init_chat_model

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
