export interface TopDiseasePrediction {
  raw_class: string;
  crop: string;
  condition: string;
  display_name: string;
  is_healthy: boolean;
  probability: number;
}

export interface ManagementGuidance {
  cultural_practices: string[];
  sanitation: string[];
  prevention: string[];
  disclaimer: string;
}

export interface DiseaseDiagnosisResult {
  id?: string | null;
  predicted_condition: string;
  crop: string;
  condition: string;
  display_name: string;
  is_healthy: boolean;
  confidence: number;
  is_confident: boolean;
  is_suitable?: boolean;
  suitability_message?: string | null;
  uncertainty_notice?: string | null;
  top_predictions: TopDiseasePrediction[];
  management_guidance: ManagementGuidance;
  original_image_path: string;
  image_url?: string | null;
  model_version: string;
  is_saved: boolean;
  created_at?: string | null;
}

export interface DiseaseHistoryItem {
  id: string;
  predicted_condition: string;
  crop: string;
  condition: string;
  display_name: string;
  is_healthy: boolean;
  confidence: number;
  is_confident: boolean;
  management_guidance?: Record<string, any> | null;
  original_image_path: string;
  image_url?: string | null;
  model_version: string;
  created_at: string;
}
