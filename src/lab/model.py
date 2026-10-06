"""PROVIDED - do not edit. Builds the chat model from environment variables (see .env.example).

Two configurations are supported (the first that matches wins):

1. Azure OpenAI or an OpenAI-compatible gateway - set all three variables:
   AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_MODEL
   (optional: AZURE_OPENAI_API_VERSION, used only for real Azure endpoints).
2. Any LangChain provider - set LAB_MODEL="<provider>:<model>" (default "deepseek:deepseek-chat")
   and the key variable of that provider (for example DEEPSEEK_API_KEY).
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def make_model():
    """Return a chat model configured from the environment."""
    temperature = float(os.getenv("LAB_TEMPERATURE", "0"))
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_MODEL")
    extra_kwargs = {}
    max_tokens = int(os.getenv("LAB_MAX_TOKENS", "0"))
    if max_tokens > 0:
        extra_kwargs["max_tokens"] = max_tokens

    if endpoint and key and deployment:
        if "openai.azure.com" in endpoint or "cognitiveservices.azure.com" in endpoint:
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                azure_endpoint=endpoint, api_key=key, azure_deployment=deployment,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                temperature=temperature, timeout=120, **extra_kwargs,
            )
        import time
        from langchain_openai import ChatOpenAI

        class ResilientChatOpenAI(ChatOpenAI):
            """ChatOpenAI with automatic retry on OpenRouter in-flight rate limit (402/429)."""

            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                last_exc = None
                for attempt in range(8):
                    try:
                        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                    except Exception as e:
                        last_exc = e
                        err_str = str(e).lower()
                        if (
                            ("402" in err_str or "429" in err_str or "503" in err_str or "500" in err_str)
                            and (
                                "in-flight" in err_str
                                or "in_flight" in err_str
                                or "rate" in err_str
                                or "overloaded" in err_str
                                or "temporarily" in err_str
                                or "internal server error" in err_str
                                or "500" in err_str
                            )
                        ):
                            wait_s = min(15 * (attempt + 1), 60)
                            print(f"[API Retry {attempt+1}] {err_str[:60]}... waiting {wait_s}s", flush=True)
                            time.sleep(wait_s)
                            continue

                        raise
                if last_exc:
                    raise last_exc



        return ResilientChatOpenAI(base_url=endpoint, api_key=key, model=deployment, temperature=temperature, timeout=120, **extra_kwargs)
    return init_chat_model(os.getenv("LAB_MODEL", "deepseek:deepseek-chat"), temperature=temperature, **extra_kwargs)


