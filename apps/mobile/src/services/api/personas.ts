// 페르소나 API 클라이언트 (controller 와 1:1 대응).
import type { Persona, PersonaCreateInput } from '@dear-my-x/shared';

import { request } from './client';

// 업데이트는 동의 필드를 보내지 않는다.
export type PersonaUpdateInput = Partial<
  Omit<PersonaCreateInput, 'consent_virtual_persona' | 'consent_data_rights'>
>;

export const PersonasApi = {
  list: () => request<Persona[]>('/personas'),
  get: (id: string) => request<Persona>(`/personas/${id}`),
  create: (body: PersonaCreateInput) => request<Persona>('/personas', { method: 'POST', body }),
  update: (id: string, body: PersonaUpdateInput) =>
    request<Persona>(`/personas/${id}`, { method: 'PATCH', body }),
  delete: (id: string) => request<null>(`/personas/${id}`, { method: 'DELETE' }),
};
