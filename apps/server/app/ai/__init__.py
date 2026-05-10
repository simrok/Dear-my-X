"""AI 전용 모듈.

이 패키지는 외부 AI/NLP 의존성(Claude, OpenAI, 정규식 기반 파서 등)을
캡슐화한다. 비즈니스 로직(`app.services.*`)은 여기 있는 인터페이스에만
의존하고, SDK 자체에는 의존하지 않는다.

구성:
    clients/    — 외부 모델 어댑터 (Claude, OpenAI Embedding)
    prompts/    — 프롬프트 템플릿
    rag/        — 검색기 / 랭커
    parsers/    — 카카오톡 등 입력 포맷 파서
    masking/    — 개인정보 마스킹
    chunkers/   — 대화 chunk 분리
"""
