# AWS Bedrock Agent Sample

AWS Bedrock를 사용한 AI 에이전트 샘플 코드입니다.

## 기능

- **Simple Agent Invocation**: 기본적인 텍스트 생성
- **Tool Use**: 에이전트가 정의된 도구를 사용하여 작업 수행
- **Agentic Loop**: 도구를 반복적으로 사용하는 에이전트 루프

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 1. AWS 자격증명 설정

```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### 2. 스크립트 실행

```bash
python bedrock_agent.py
```

## 코드 구조

### `invoke_bedrock_agent(prompt, model_id)`
기본적인 에이전트 호출 함수. 사용자의 프롬프트에 대해 응답을 반환합니다.

### `bedrock_agent_with_tools(prompt, tools)`
도구 정의와 함께 에이전트를 호출합니다. 에이전트가 제공된 도구를 사용할 수 있습니다.

### `run_agent_loop(initial_prompt, max_iterations)`
에이전트 루프를 실행하여 도구를 반복적으로 사용할 수 있도록 합니다.

## 샘플 도구

- `get_weather`: 특정 위치의 날씨 정보 조회
- `calculate_distance`: 두 위치 사이의 거리 계산

## 지원하는 모델

- `anthropic.claude-3-5-sonnet-20241022-v2:0` (기본)
- `anthropic.claude-3-opus-20250219-v1:0`
- `anthropic.claude-3-haiku-20250307-v1:0`

## 참고사항

- AWS 계정과 Bedrock 접근 권한이 필요합니다.
- 도구 실행 결과는 시뮬레이션된 데이터입니다. 실제 구현 시 실제 데이터를 반환하도록 수정하세요.
