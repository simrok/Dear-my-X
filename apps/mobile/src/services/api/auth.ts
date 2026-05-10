// 인증 관련 API (controller 와 1:1 대응).
import type { User } from '@dear-my-x/shared';

import { request } from './client';

export const AuthApi = {
  /** 현재 JWT 가 가리키는 사용자 (없으면 자동 생성). 401 가능. */
  me: () => request<User>('/auth/me'),
};
