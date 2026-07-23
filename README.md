# AWS Bedrock Agent Suite

AWS Bedrock를 사용한 다양한 AI 에이전트 구현 모음입니다. Claude 모델을 활용하여 여러 도메인에서 작동하는 에이전트를 제공합니다.

## 📦 포함된 에이전트

### 1. Basic Bedrock Agent (`bedrock_agent.py`)
- 기본적인 텍스트 생성
- 도구 사용 능력 (Tool Use)
- 에이전트 루프 (Agentic Loop)

### 2. Data Analysis Agent (`data_analysis_agent.py`)
- 데이터 요약 및 통계
- 데이터 필터링
- 상관관계 분석
- 데이터 집계 및 그룹화
- 통합 데이터 쿼리 실행

### 3. AWS Service Agent (`aws_service_agent.py`)
- S3 버킷 관리
- EC2 인스턴스 조회
- CloudWatch 메트릭 수집
- AWS 계정 정보 조회

### 4. Web Server Agent (`web_server_agent.py`)
- RESTful API 제공
- 여러 에이전트 관리
- 채팅 인터페이스
- 텍스트 분석
- 배치 처리

## 🚀 설치

### 1. 저장소 클론
```bash
git clone <repository-url>
cd cloudwatch-Coding-Agent-Insights
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 설정
```bash
cp .env.example .env
# .env 파일 수정
```

### 4. AWS 자격증명 설정
```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

## 📖 사용 방법

### Basic Agent 실행
```bash
python bedrock_agent.py
```

### Data Analysis Agent 실행
```bash
python data_analysis_agent.py
```

### AWS Service Agent 실행
```bash
python aws_service_agent.py
```

### Web Server 시작
```bash
python web_server_agent.py
```

웹 서버는 기본적으로 `http://localhost:5000`에서 실행됩니다.

### 예제 실행
```bash
python examples.py
```

## 🔧 API 엔드포인트

### Health & Info
- `GET /health` - 헬스 체크
- `GET /agents` - 에이전트 목록
- `GET /agents/<agent_id>` - 에이전트 정보

### Chat & Analysis
- `POST /chat` - 에이전트와 채팅
- `POST /chat/streaming` - 스트리밍 채팅
- `POST /analyze` - 텍스트 분석
- `POST /batch` - 배치 처리

### 요청 예제
```bash
# Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "assistant",
    "message": "What is machine learning?"
  }'

# Analyze
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is amazing!",
    "analysis_type": "sentiment"
  }'

# Batch
curl -X POST http://localhost:5000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "assistant",
    "messages": [
      "Hello",
      "How are you?",
      "What is AI?"
    ]
  }'
```

## 📊 Data Analysis 예제

```python
from data_analysis_agent import DataAnalysisAgent

agent = DataAnalysisAgent()
agent.load_sample_data()

# 데이터 요약
summary = agent.get_data_summary('sales')

# 데이터 필터링
filtered = agent.filter_data('sales', 'region', 'North')

# 데이터 집계
aggregated = agent.aggregate_data('sales', 'region', 'sum', 'sales')

# 쿼리 실행
result = agent.run_analysis("What is the total sales by region?")
```

## ☁️ AWS Service 예제

```python
from aws_service_agent import AWSServiceAgent

agent = AWSServiceAgent()

# S3 버킷 목록
buckets = agent.list_s3_buckets()

# EC2 인스턴스 목록
instances = agent.list_ec2_instances()

# 쿼리 실행
result = agent.run_query("Tell me about my AWS resources")
```

## 🧪 테스트 실행

```bash
python -m pytest test_agents.py -v
# 또는
python test_agents.py
```

## 📝 구성 파일

### config.py
전역 설정을 관리합니다:
- AWS 지역
- Bedrock 모델 ID
- 에이전트 설정
- 웹 서버 설정

### .env 파일
환경 변수를 설정합니다. `.env.example`을 참고하세요.

## 🛠️ 지원 모델

- `claude-opus`: 가장 고급 모델 (Claude 3 Opus)
- `claude-sonnet`: 균형잡힌 모델 (Claude 3.5 Sonnet) - **기본**
- `claude-haiku`: 빠르고 가벼운 모델 (Claude 3 Haiku)

## 📚 주요 기능

### Tool Use
에이전트가 정의된 도구를 사용하여 작업을 수행합니다.

```python
tools = agent.define_tools()
result = agent.run_analysis(query)  # 에이전트가 자동으로 필요한 도구를 사용
```

### Agentic Loop
도구를 반복적으로 사용하여 복잡한 작업을 완성합니다.

```python
result = agent.run_agent_loop(initial_prompt, max_iterations=5)
```

### Streaming
대용량 응답을 스트리밍으로 받습니다.

```bash
curl http://localhost:5000/chat/streaming \
  -d '{"message": "Write a long story"}' \
  -H "Content-Type: application/json"
```

## ⚙️ 고급 설정

### 모델 변경
```python
agent = DataAnalysisAgent()
agent.bedrock_client.converse(
    modelId="anthropic.claude-3-opus-20250219-v1:0",
    ...
)
```

### 최대 반복 횟수 설정
```python
result = agent.run_analysis(query, max_iterations=10)
```

### 도구 맞춤화
tools 리스트를 수정하여 커스텀 도구를 추가할 수 있습니다.

## 🔒 보안 사항

- API 키 환경 변수로 관리
- CORS 설정 가능
- 입력 검증 구현
- 에러 처리 포함

## 📋 필수 권한

AWS IAM에서 다음 권한이 필요합니다:
- `bedrock:InvokeModel` - Bedrock API 호출
- `s3:ListAllMyBuckets` - S3 버킷 조회
- `ec2:DescribeInstances` - EC2 인스턴스 조회
- `cloudwatch:GetMetricStatistics` - CloudWatch 메트릭 조회
- `sts:GetCallerIdentity` - AWS 계정 정보 조회

## 🤝 기여

개선 사항이나 버그 리포트는 이슈를 통해 알려주세요.

## 📄 라이선스

MIT License

## 📞 지원

문제가 발생하면:
1. 로그 파일 확인
2. AWS 자격증명 확인
3. Bedrock 모델 접근 권한 확인

## 🔗 참고 자료

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude Models Guide](https://docs.anthropic.com/)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
