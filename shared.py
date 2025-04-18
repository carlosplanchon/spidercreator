#!/usr/bin/env python3

from langchain.chat_models import init_chat_model

gpt4o_llm = init_chat_model(
    # model="gpt-4o",
    model="gpt-4.1",
    model_provider="openai"
)
gpt41_llm = init_chat_model(
    model="gpt-4.1",
    model_provider="openai"
)

o3_llm = init_chat_model(
    model="o3",
    model_provider="openai"
)
