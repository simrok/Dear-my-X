// 페르소나 목록 / 단일 fetch 훅.
// MVP 단계라 react-query 등을 쓰지 않고 직접 useState 로 처리한다. 추후 교체 후보.
import { useCallback, useEffect, useState } from 'react';

import { ApiError } from '@/services/api/client';
import { PersonasApi } from '@/services/api/personas';
import type { Persona } from '@dear-my-x/shared';

interface ListState {
  data: Persona[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

function toMessage(e: unknown): string {
  if (e instanceof ApiError) return `${e.status} ${e.code}: ${e.message}`;
  return e instanceof Error ? e.message : String(e);
}

export function usePersonas(): ListState {
  const [data, setData] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const items = await PersonasApi.list();
      setData(items);
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { data, isLoading, error, refresh };
}

interface SingleState {
  data: Persona | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function usePersona(id: string | undefined): SingleState {
  const [data, setData] = useState<Persona | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const item = await PersonasApi.get(id);
      setData(item);
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { data, isLoading, error, refresh };
}
