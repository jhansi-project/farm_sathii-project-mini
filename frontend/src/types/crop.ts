export interface CropRecommendationPayload {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
}

export interface TopPrediction {
  crop: string;
  probability: number;
}

export interface CropRecommendationResult {
  id?: string | null;
  recommended_crop: string;
  top_predictions: TopPrediction[];
  inputs: Record<string, number>;
  model_version: string;
  is_saved: boolean;
  created_at?: string | null;
}

export interface CropRecommendationHistoryItem {
  id: string;
  recommended_crop: string;
  top_predictions: TopPrediction[];
  inputs: Record<string, number>;
  model_version: string;
  created_at: string;
}
