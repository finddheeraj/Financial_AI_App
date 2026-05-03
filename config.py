import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    MODEL_PATH = os.environ.get(
        "MODEL_PATH",
        r"C:\Users\chauradh\OneDrive - Barclays Bank PLC\Desktop\.netAIApp\LLMModels\llama-3-8b-gguf\Llama-3.1-8B.gguf",
    )
    MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "1536"))
    TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
    TOP_P = float(os.environ.get("TOP_P", "0.9"))
    N_CTX = int(os.environ.get("N_CTX", "4096"))
    N_GPU_LAYERS = int(os.environ.get("N_GPU_LAYERS", "0"))
    AGENT_MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERATIONS", "5"))
    AGENT_STEP_TOKENS = int(os.environ.get("AGENT_STEP_TOKENS", "300"))

    USE_GROK_API = os.environ.get("USE_GROK_API", "false").lower() in ("true", "1", "yes")
    GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
    GROK_API_BASE = os.environ.get("GROK_API_BASE", "https://api.x.ai/v1")
    GROK_MODEL = os.environ.get("GROK_MODEL", "grok-3-mini")
