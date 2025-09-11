# llm-playground

LLM 실험을 위한 FastAPI 기반 디렉토리. Ollama 또는 Hugging Face Transformers를 백엔드로 사용하여 로컬에서 언어 모델을 실행하고 테스트 가능

## 주요 기능

- **듀얼 백엔드 지원**: Ollama와 Hugging Face Transformers를 선택적으로 또는 자동으로 사용하여 추론 수행
- **Docker 기반 환경**: `docker-compose`를 사용하여 GPU 가속을 포함한 전체 환경을 쉽게 구성하고 실행
- **간단한 API**: `/chat` 엔드포인트를 통해 모델과 상호작용 가능

## Prerequisites

1. **NVIDIA 드라이버 확인** (CUDA 12.x 이상 권장)
   ```shell
   nvidia-smi
   ```

2. **Docker 및 Docker Compose 확인**
   ```shell
   docker compose version
   ```
   * Windows 및 macOS에서는 Docker Desktop을 사용

3. **NVIDIA Container Toolkit 설치** (Linux)
   ```shell
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

## 프로젝트 실행

1. **(최초 1회)** Ollama 모델 다운로드
   `docker-compose.yml`에 정의된 `OLLAMA_MODEL` 다운로드
   ```shell
   docker compose run --rm ollama ollama pull qwen2.5:1.5b
   ```

2. **Docker Compose 실행**
   백그라운드에서 서비스를 빌드하고 실행
   ```shell
   docker compose up -d --build
   ```

3. **API 테스트**
   `curl`을 사용하여 `/chat` 엔드포인트에 요청
   - `backend` 필드를 `auto` (기본값), `ollama`, `hf` 중 하나로 설정 가능
   - `auto`로 설정 시 Ollama를 먼저 시도하고, 실패하면 Hugging Face 백엔드로 자동 전환

   ```shell
   curl -X POST http://localhost:12321/chat \
        -H "Content-Type: application/json" \
        -d '{"prompt": "대한민국의 수도는 어디인가요?", "backend": "auto"}'
   ```
   **응답 예시:**
   ```json
   {
     "backend": "ollama",
     "text": "대한민국의 수도는 서울입니다."
   }
   ```

## 서비스 종료

실행 중인 모든 컨테이너를 중지하고 네트워크를 제거
```shell
docker compose down
```

## 환경 변수 및 설정

주요 설정은 `docker-compose.yml`과 `Dockerfile.app`의 `environment` 섹션에서 관리

- `HF_MODEL_ID`: Hugging Face 백엔드에서 사용할 모델 ID (예: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`)
- `OLLAMA_MODEL`: Ollama 백엔드에서 사용할 모델 (예: `qwen2.5:1.5b`)
- `OLLAMA_HOST`/`OLLAMA_PORT`: Ollama 서비스의 호스트 및 포트

이 변수들을 수정하여 다른 모델을 테스트 가능

```