# CUDA 12.9 포함된 NGC PyTorch(25.xx) 이미지 사용
FROM nvcr.io/nvidia/pytorch:25.05-py3

# 비루트 사용자 (호스트 UID와 맞추면 볼륨 퍼미션 깔끔)
ARG USER=appuser
ARG UID=1008
RUN useradd -m -u ${UID} ${USER}

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /workspace

# 최소 시스템 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl nano ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ===== 프로젝트 복사 =====
# pyproject/lock 먼저 복사 → uv가 의존성 해석/캐시를 일찍 수행
COPY pyproject.toml uv.lock ./
# 소스 복사
COPY src ./src
COPY app ./app

# ===== 의존성 설치 (시스템 파이썬에 설치) =====
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir \
      "fastapi" "uvicorn[standard]" "httpx" "python-dotenv" \
      "transformers>=4.43" "huggingface_hub>=0.24" "safetensors" "tokenizers" "pydantic>=2" \
      "accelerate" "peft" "optimum"


# ===== 런타임 환경 =====
ENV HF_HOME=/data/hf \
    TRANSFORMERS_CACHE=/data/hf/transformers \
    OLLAMA_HOST=ollama \
    OLLAMA_PORT=11434 \
    HF_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    OLLAMA_MODEL=qwen2.5:1.5b

# 퍼미션 정리 후 비루트 전환
RUN mkdir -p /data/hf && chown -R ${USER}:${USER} /workspace /data
USER ${USER}

EXPOSE 12321
CMD ["bash","-lc","python -m uvicorn app.main:app --host 0.0.0.0 --port 12321"]
