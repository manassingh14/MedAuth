import json, os, re
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv(override=True)
ROOT = Path(__file__).resolve().parent.parent


def load_yaml(name: str) -> dict:
    return yaml.safe_load((ROOT / "configs" / name).read_text(encoding="utf-8"))


MODELS = load_yaml("models.yaml")
RULES = load_yaml("rules.yaml")


def get_llm(agent: str) -> ChatGoogleGenerativeAI:
    cfg = MODELS[agent]
    return ChatGoogleGenerativeAI(
        model=cfg["model"],
        temperature=cfg.get("temperature", 0.0),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_retries=6,   # free tier rate-limits; retry with backoff
        timeout=60,
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    cfg = MODELS["embeddings"]
    return GoogleGenerativeAIEmbeddings(
        model="models/" + cfg["model"],
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


def parse_json(text: str) -> dict:
    """Parse LLM JSON output, tolerating markdown fences and stray prose."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


if __name__ == "__main__":
    print("LLM:", get_llm("decision_agent").invoke("Reply with the word OK").content)
    print("Embedding dims:", len(get_embeddings().embed_query("test")))