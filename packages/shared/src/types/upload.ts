export type UploadStatus =
  | 'pending'
  | 'parsing'
  | 'embedding'
  | 'completed'
  | 'failed';

export interface ConversationUpload {
  id: string;
  user_id: string;
  persona_id: string;
  file_url: string;
  original_filename: string;
  status: UploadStatus;
  created_at: string;
}

export interface KakaoPreviewResponse {
  upload_id: string;
  status: UploadStatus;
  speakers: string[];
  detected_format: 'pc' | 'mobile' | 'unknown';
  message_count: number;
  skipped_lines: number;
}

export interface IngestRequest {
  speaker: string;
}

export interface IngestResponse {
  upload_id: string;
  status: UploadStatus;
  speaker: string;
  chunks_created: number;
  masked_counts: Record<string, number>;
  error?: string | null;
}

export interface UploadStatusResponse {
  upload_id: string;
  status: UploadStatus;
  persona_id: string;
  original_filename: string;
  created_at: string;
}
