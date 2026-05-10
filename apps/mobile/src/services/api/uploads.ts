// Uploads API 클라이언트.
// multipart/form-data 는 fetch 직접 사용 (request 래퍼는 JSON 전용).
import type {
  IngestResponse,
  KakaoPreviewResponse,
  UploadStatusResponse,
} from '@dear-my-x/shared';

import { Config } from '@/constants/config';
import { getAccessToken } from '@/services/supabase/session';

import { ApiError, request } from './client';

interface KakaoFile {
  uri: string;
  name: string;
  /** 보통 'text/plain' */
  mimeType?: string | null;
}

function uploadsBaseUrl(): string {
  return `${Config.apiBaseUrl}/api/${Config.apiVersion}/uploads`;
}

/** POST /uploads/kakao (multipart) */
export async function uploadKakaoTxt(
  file: KakaoFile,
  personaId: string,
): Promise<KakaoPreviewResponse> {
  const form = new FormData();
  // RN 의 FormData 는 { uri, name, type } 형태를 받음
  // (Web 환경 호환을 위해 type 도 채움)
  form.append('file', {
    // @ts-expect-error: RN FormData 의 file shape
    uri: file.uri,
    name: file.name,
    type: file.mimeType ?? 'text/plain',
  });
  form.append('persona_id', personaId);

  const token = await getAccessToken();
  const res = await fetch(`${uploadsBaseUrl()}/kakao`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      // 'Content-Type' 은 명시하지 않음 — fetch 가 boundary 와 함께 자동 설정
    },
    body: form as unknown as BodyInit,
  });

  const text = await res.text();
  const parsed = text ? (JSON.parse(text) as unknown) : null;

  if (!res.ok) {
    const err = parsed as { error?: { code?: string; message?: string } } | null;
    throw new ApiError(
      res.status,
      err?.error?.code ?? 'unknown',
      err?.error?.message ?? res.statusText,
    );
  }
  return parsed as KakaoPreviewResponse;
}

/** POST /uploads/kakao/{id}/ingest (JSON) */
export function ingestKakao(uploadId: string, speaker: string): Promise<IngestResponse> {
  return request<IngestResponse>(`/uploads/kakao/${uploadId}/ingest`, {
    method: 'POST',
    body: { speaker },
  });
}

/** GET /uploads/kakao/{id} */
export function getKakaoUploadStatus(uploadId: string): Promise<UploadStatusResponse> {
  return request<UploadStatusResponse>(`/uploads/kakao/${uploadId}`);
}
