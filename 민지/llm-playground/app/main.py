from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv; load_dotenv()
import os, httpx, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
OLLAMA_URL = f"http://{os.getenv('OLLAMA_HOST','ollama')}:{os.getenv('OLLAMA_PORT','11434')}/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

_tok = None
_model = None

def ensure_hf():
    global _tok, _model
    if _tok is None or _model is None:
        _tok = AutoTokenizer.from_pretrained(HF_MODEL_ID, use_fast=True)
        _model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_ID,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True,
        )

class ChatReq(BaseModel):
    prompt: str
    backend: str = "auto"   # "hf" | "ollama" | "auto"
    max_new_tokens: int = 256

@app.post("/chat")
async def chat(req: ChatReq):
    # 1) Ollama 시도
    if req.backend in ("ollama","auto"):
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                r = await client.post(OLLAMA_URL, json={
                    "model": OLLAMA_MODEL,
                    "prompt": req.prompt,
                    "stream": False
                })
                r.raise_for_status()
                return {"backend":"ollama", "text": r.json()["response"]}
        except Exception:
            if req.backend == "ollama":
                raise
    # 2) HF 로컬 추론
    ensure_hf()
    inputs = _tok(req.prompt, return_tensors="pt").to(_model.device)
    with torch.no_grad():
        out = _model.generate(**inputs, max_new_tokens=req.max_new_tokens)
    text = _tok.decode(out[0], skip_special_tokens=True)
    return {"backend":"hf", "text": text}
