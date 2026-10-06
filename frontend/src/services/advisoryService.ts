import { apiClient } from './api';
import type {
  AdvisoryConversationDetail,
  AdvisoryConversationSummary,
  AdvisoryExecutionResponse,
  CreateConversationParams,
  SendMessageOptions,
} from '../types/advisory';

export const advisoryService = {
  /**
   * Create a new advisory conversation, optionally asking an initial question (with optional image) immediately.
   */
  async createConversation(
    params: CreateConversationParams
  ): Promise<AdvisoryConversationDetail> {
    const res = await apiClient.post<{
      success: boolean;
      data: AdvisoryConversationDetail;
      message: string;
    }>('/advisory/conversations', params);
    return res.data.data;
  },

  /**
   * Send a question to an existing advisory conversation with optional language and image payload.
   */
  async sendMessage(
    conversationId: string,
    messageText: string,
    options?: SendMessageOptions
  ): Promise<AdvisoryExecutionResponse> {
    const payload = {
      message_text: messageText,
      ...(options || {}),
    };
    const res = await apiClient.post<{
      success: boolean;
      data: AdvisoryExecutionResponse;
      message: string;
    }>(`/advisory/conversations/${conversationId}/messages`, payload);
    return res.data.data;
  },

  /**
   * Fetch all advisory conversations for the authenticated farmer.
   */
  async getConversations(
    skip = 0,
    limit = 20
  ): Promise<AdvisoryConversationSummary[]> {
    const res = await apiClient.get<{
      success: boolean;
      data: AdvisoryConversationSummary[];
      message: string;
    }>('/advisory/conversations', {
      params: { skip, limit },
    });
    return res.data.data;
  },

  /**
   * Get full conversation detail and message history.
   */
  async getConversation(
    conversationId: string
  ): Promise<AdvisoryConversationDetail> {
    const res = await apiClient.get<{
      success: boolean;
      data: AdvisoryConversationDetail;
      message: string;
    }>(`/advisory/conversations/${conversationId}`);
    return res.data.data;
  },

  /**
   * Delete an advisory conversation.
   */
  async deleteConversation(conversationId: string): Promise<boolean> {
    const res = await apiClient.delete<{
      success: boolean;
      data: boolean;
      message: string;
    }>(`/advisory/conversations/${conversationId}`);
    return res.data.data;
  },
};
