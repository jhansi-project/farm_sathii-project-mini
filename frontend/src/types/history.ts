import { CropRecommendationHistoryItem } from './crop';
import { DiseaseHistoryItem } from './disease';
import { AdvisoryConversationSummary } from './advisory';

export interface HistoryCounts {
  crop_recommendations: number;
  disease_diagnoses: number;
  advisory_conversations: number;
  total: number;
}

export interface UnifiedHistoryItem {
  id: string;
  module_type: 'crop' | 'disease' | 'advisory';
  title: string;
  subtitle?: string | null;
  status?: string | null;
  created_at: string;
  metadata?: Record<string, any> | null;
}

export interface UserHistorySummary {
  counts: HistoryCounts;
  recent_activities: UnifiedHistoryItem[];
}

export interface PaginatedCropHistory {
  items: CropRecommendationHistoryItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface PaginatedDiseaseHistory {
  items: DiseaseHistoryItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface PaginatedAdvisoryHistory {
  items: AdvisoryConversationSummary[];
  total: number;
  skip: number;
  limit: number;
}
