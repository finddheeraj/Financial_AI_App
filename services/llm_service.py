from openai import OpenAI
from config import Config

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=Config.GROK_API_KEY,
            base_url=Config.GROK_API_BASE,
        )
    return _client

def generate(prompt: str, max_tokens: int | None = None) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=Config.GROK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens or Config.MAX_NEW_TOKENS,
        temperature=Config.TEMPERATURE,
        top_p=Config.TOP_P,
    )
    return response.choices[0].message.content

def generate_stream(prompt: str, max_tokens: int | None = None):
    client = _get_client()
    response = client.chat.completions.create(
        model=Config.GROK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens or Config.MAX_NEW_TOKENS,
        temperature=Config.TEMPERATURE,
        top_p=Config.TOP_P,
        stream=True,
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

def chat_completion(messages, max_tokens=None, temperature=None, top_p=None, stop=None):
    client = _get_client()
    kwargs = dict(
        model=Config.GROK_MODEL,
        messages=messages,
        max_tokens=max_tokens or Config.MAX_NEW_TOKENS,
        temperature=temperature or Config.TEMPERATURE,
        top_p=top_p or Config.TOP_P,
    )
    if stop:
        kwargs["stop"] = stop

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""