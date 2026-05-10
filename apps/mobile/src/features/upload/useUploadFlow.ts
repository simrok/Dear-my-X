// 업로드 플로우 단계 머신.
//   idle           → 시작 전
//   picking        → 파일 선택 중 (DocumentPicker 모달)
//   uploading      → 서버에 업로드 중 (preview 호출)
//   choose-speaker → 발화자 선택 대기
//   ingesting      → ingest API 호출 중
//   done           → 완료
//   error          → 실패 (재시도 가능)
import { useCallback, useState } from 'react';

import { ApiError } from '@/services/api/client';
import {
  ingestKakao,
  uploadKakaoTxt,
} from '@/services/api/uploads';
import type { IngestResponse, KakaoPreviewResponse } from '@dear-my-x/shared';

export type UploadStep =
  | 'idle'
  | 'picking'
  | 'uploading'
  | 'choose-speaker'
  | 'ingesting'
  | 'done'
  | 'error';

interface State {
  step: UploadStep;
  preview: KakaoPreviewResponse | null;
  result: IngestResponse | null;
  error: string | null;
}

const initial: State = { step: 'idle', preview: null, result: null, error: null };

function toMessage(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  return e instanceof Error ? e.message : String(e);
}

export function useUploadFlow(personaId: string) {
  const [state, setState] = useState<State>(initial);

  const startPicking = useCallback(() => {
    setState({ ...initial, step: 'picking' });
  }, []);

  const cancelPicking = useCallback(() => {
    setState(initial);
  }, []);

  const upload = useCallback(
    async (file: { uri: string; name: string; mimeType?: string | null }) => {
      setState({ ...initial, step: 'uploading' });
      try {
        const preview = await uploadKakaoTxt(file, personaId);
        setState({ step: 'choose-speaker', preview, result: null, error: null });
      } catch (e) {
        setState({ ...initial, step: 'error', error: toMessage(e) });
      }
    },
    [personaId],
  );

  const ingest = useCallback(
    async (speaker: string) => {
      const upload = state.preview;
      if (!upload) return;
      setState((s) => ({ ...s, step: 'ingesting', error: null }));
      try {
        const result = await ingestKakao(upload.upload_id, speaker);
        setState((s) => ({
          ...s,
          step: result.status === 'failed' ? 'error' : 'done',
          result,
          error: result.status === 'failed' ? result.error ?? '임베딩 실패' : null,
        }));
      } catch (e) {
        setState((s) => ({ ...s, step: 'error', error: toMessage(e) }));
      }
    },
    [state.preview],
  );

  const reset = useCallback(() => setState(initial), []);

  return { ...state, startPicking, cancelPicking, upload, ingest, reset };
}
