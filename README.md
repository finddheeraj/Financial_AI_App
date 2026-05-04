Financial AI Agent App

A Flask-based agentic AI system that implements a ReAct-style reasoning loop with tool execution. This project demonstrates how to build a structured, extensible AI agent capable of multi-step reasoning, tool usage, and stateful conversations.

Live Application
https://financial-ai-app.onrender.com

This application is designed to move beyond traditional chatbot patterns. Instead of generating a single response, the system performs multiple reasoning steps before arriving at a final answer.

Agentic Loop (ReAct Pattern)

Following are the steps for Agentic loop

1. Construct prompt with context and memory
2. Call LLM
3. Parse structured output
4. If action is present, execute tool
5. Append observation to context
6. Repeat loop
7. Return final answer

Running Locally
1. git clone <repository-url>
2. cd financial-ai-agent
3. pip install -r requirements.txt
4. Create a .env file
5. Add your Grok API Key and following environmnet variables
   
   GROK_API_KEY= (paste your key)
   GROK_API_BASE=https://api.groq.com/openai/v1
   GROK_MODEL=llama-3.1-8b-instant
7. python app.py

Access the app at:

http://localhost:5000


