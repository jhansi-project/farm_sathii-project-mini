export type AdvisoryProviderStatus =
  | 'success'
  | 'provider_unavailable'
  | 'provider_error'
  | 'provider_timeout'
  | 'safety_filtered'
  | 'insufficient_context';

export interface AttachedImageMetadata {
  has_image: boolean;
  filename: string;
  mime_type: string;
  size_bytes: number;
  width: number;
  height: number;
}

export interface AdvisoryMessage {
  id: string;
  conversation_id: string;
  sender_role: 'user' | 'assistant';
  message_text: string;
  audio_path?: string | null;
  context_used?: {
    summary?: {
      has_profile?: boolean;
      has_crop_recommendation?: boolean;
      has_disease_diagnosis?: boolean;
      has_weather?: boolean;
      has_attached_image?: boolean;
      language?: string;
      history_turns?: number;
    };
    data?: {
      farmer_profile?: Record<string, any> | null;
      crop_recommendation?: Record<string, any> | null;
      disease_diagnosis?: Record<string, any> | null;
      weather?: Record<string, any> | null;
      attached_image?: AttachedImageMetadata | null;
    };
    attached_image?: AttachedImageMetadata | null;
    language?: string;
    disclaimers?: string[];
    provider_name?: string;
    provider_status?: string;
  } | null;
  created_at: string;
}

export interface AdvisoryConversationSummary {
  id: string;
  title: string;
  language: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface AdvisoryConversationDetail {
  id: string;
  user_id: string;
  title: string;
  language: string;
  created_at: string;
  updated_at: string;
  messages: AdvisoryMessage[];
}

export interface AdvisoryExecutionResponse {
  conversation_id: string;
  user_message: AdvisoryMessage;
  assistant_message: AdvisoryMessage;
  provider_status: AdvisoryProviderStatus;
  safety_disclaimers: string[];
  context_summary?: Record<string, any>;
  provider_name: string;
}

export interface CreateConversationParams {
  title?: string;
  initial_message?: string;
  language?: string;
  image_base64?: string;
  image_content_type?: string;
  image_filename?: string;
  image_path?: string;
  latitude?: number;
  longitude?: number;
  location_name?: string;
}

export interface SendMessageOptions {
  language?: string;
  image_base64?: string;
  image_content_type?: string;
  image_filename?: string;
  image_path?: string;
  latitude?: number;
  longitude?: number;
  location_name?: string;
}
