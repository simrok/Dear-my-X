# Dear my X — MVP 개발 명세서 (1차 PRD)

## 1. 앱 개요

**Dear my X**는 사용자가 과거 대화 기록을 업로드하고, 이를 기반으로 생성된 AI 페르소나와 채팅할 수 있는 감정형 AI 채팅 앱이다.

단, 앱은 실제 인물 복제를 목적으로 하지 않고, **과거 대화 스타일과 관계 맥락을 참고한 가상 페르소나**를 제공한다.

---

## 2. 핵심 컨셉

```text
과거의 대화에서 말투와 기억을 추출해,
사용자가 만든 가상 AI 페르소나와 대화하는 앱
```

---

## 3. MVP 핵심 기능

### 필수 기능

1. 회원가입 / 로그인
2. AI 페르소나 생성
3. 상대방 프로필 설정
4. 카카오톡 txt 대화 업로드
5. 대화 기록 파싱
6. 개인정보 마스킹
7. 말투 분석
8. 벡터DB 저장
9. AI 채팅
10. 채팅방 목록
11. 채팅방 상세
12. 실제 인물 아님 고지

---

## 4. 주요 화면

### 1. 온보딩 화면

목적: 앱의 성격과 주의사항 안내.

```text
Dear my X는 실제 인물을 복제하지 않습니다.
업로드한 대화 기록을 기반으로 가상 AI 페르소나를 생성합니다.
타인의 개인정보가 포함된 자료를 업로드할 경우 필요한 권리를 보유해야 합니다.
```

### 2. 로그인 화면

```text
이메일 로그인
구글 로그인
애플 로그인
```

MVP에서는 이메일 로그인만 먼저 구현.

### 3. 홈 화면

상단 로고 / 본문은 페르소나 카드 목록 / 하단 "새 X 만들기" 버튼.

페르소나 카드: 프로필 이미지, 이름, 관계 유형, 마지막 대화, 마지막 대화 시간.

### 4. AI 페르소나 생성 화면

입력 항목: 이름, 관계 유형(전 연인/친구/가족/기타), 성격 키워드, 말투 스타일, 프로필 이미지, 주의할 주제.

체크박스 고지:
```text
이 AI는 실제 인물이 아니라 가상 페르소나임을 이해했습니다.
업로드하는 대화 기록에 대한 사용 권한이 있음을 확인합니다.
```

### 5. 대화 업로드 화면

처리 흐름:
```text
txt 업로드
→ 발화자 자동 추출
→ 사용자에게 대상 발화자 선택
→ 상대방 메시지 추출
→ 개인정보 제거
→ 대화 chunk 분리
→ embedding 생성
→ pgvector 저장
```

### 6. 채팅 화면

카카오톡 + 아이돌 버블 느낌. 상단 프로필 고정, 중앙 메시지 리스트, 하단 입력창 고정. 내 메시지는 오른쪽, AI 메시지는 왼쪽, 짧은 말풍선 중심.

---

## 5. AI 응답 규칙

```text
너는 사용자가 만든 가상 AI 페르소나다.
실제 인물을 완전히 복제하거나 사칭하지 않는다.

응답 규칙:
- 모바일 채팅처럼 짧게 답한다.
- 너무 설명하지 않는다.
- 감정에 먼저 반응한다.
- 과거 대화 기록에서 확인 가능한 내용만 기억처럼 말한다.
- 모르는 사실은 지어내지 않는다.
- 사용자가 현실 인물이라고 착각하지 않도록 필요 시 부드럽게 경계한다.
- 자해, 집착, 의존적 대화가 감지되면 안전한 방향으로 유도한다.
```

---

## 6. RAG 구조

```text
사용자 메시지
→ 최근 채팅 20개 조회
→ 벡터DB에서 관련 과거 대화 5~10개 검색
→ 페르소나 정보 조회
→ Claude API 호출
→ 응답 저장
→ 앱에 반환
```

---

## 7. 추천 기술 스택 (MVP)

```text
Frontend: React Native + Expo (TypeScript)
Backend: FastAPI
Database: PostgreSQL + pgvector
Auth: Supabase Auth
Storage: Supabase Storage
AI: Claude API
Embedding: OpenAI text-embedding-3-small
```

---

## 8. DB 테이블 초안

```sql
users(id, email, created_at)
personas(id, user_id, name, relation_type, personality, speaking_style, profile_image_url, safety_notes, created_at)
chat_rooms(id, user_id, persona_id, created_at, updated_at)
messages(id, chat_room_id, sender_type, content, created_at)
conversation_uploads(id, user_id, persona_id, file_url, original_filename, status, created_at)
memory_chunks(id, user_id, persona_id, content, speaker, embedding, source, created_at)
```
