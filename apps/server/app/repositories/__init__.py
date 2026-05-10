"""Repository 레이어 — DB 접근만 담당.

규칙:
    - 비즈니스 규칙 X (그건 service 가 한다)
    - 트랜잭션 commit 은 service 가 결정 (또는 라우트 단위)
    - 리포지토리는 항상 `AsyncSession` 을 인자로 받거나, __init__ 에 주입받는다.
"""
