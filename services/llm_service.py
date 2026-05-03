from config import Config


class GrokModel:
    def __init__(self):
        from openai import OpenAI

        self._client = OpenAI(
            api_key=Config.GROK_API_KEY,
            base_url=Config.GROK_API_BASE,
        )
        self._model = Config.GROK_MODEL

    def create_chat_completion(
        self,
        messages,
        max_tokens=None,
        temperature=None,
        top_p=None,
        stop=None,
        stream=False,
    ):
        kwargs = dict(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        if stop:
            kwargs["stop"] = stop

        if stream:
            return self._stream(kwargs)

        resp = self._client.chat.completions.create(**kwargs)
        return {
            "choices": [
                {"message": {"content": resp.choices[0].message.content}}
            ]
        }

    def _stream(self, kwargs):
        kwargs["stream"] = True
        for chunk in self._client.chat.completions.create(**kwargs):
            content = ""
            if chunk.choices and chunk.choices[0].delta:
                content = chunk.choices[0].delta.content or ""
            yield {"choices": [{"delta": {"content": content}}]}


_model = None


def get_model():
    global _model
    if _model is None:
        if Config.USE_GROK_API:
            _model = GrokModel()
        else:
            from llama_cpp import Llama

            _model = Llama(
                model_path=Config.MODEL_PATH,
                n_ctx=Config.N_CTX,
                n_gpu_layers=Config.N_GPU_LAYERS,
                verbose=False,
            )
    return _model


def generate(prompt: str, max_tokens: int | None = None) -> str:
    model = get_model()
    response = model.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens or Config.MAX_NEW_TOKENS,
        temperature=Config.TEMPERATURE,
        top_p=Config.TOP_P,
    )
    return response["choices"][0]["message"]["content"]


def generate_stream(prompt: str, max_tokens: int | None = None):
    model = get_model()
    stream = model.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens or Config.MAX_NEW_TOKENS,
        temperature=Config.TEMPERATURE,
        top_p=Config.TOP_P,
        stream=True,
    )
    for chunk in stream:
        delta = chunk["choices"][0].get("delta", {})
        token = delta.get("content", "")
        if token:
            yield token
