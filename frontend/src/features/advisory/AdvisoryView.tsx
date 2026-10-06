import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AdvisoryInputView } from './AdvisoryInputView';
import { QueryResultView } from './QueryResultView';
import { advisoryService } from '../../services/advisoryService';
import { useAuthStore } from '../../stores/authStore';
import { useLanguageStore } from '../../stores/languageStore';
import { useLocationStore } from '../../stores/locationStore';
import type {
  AdvisoryConversationDetail,
  AdvisoryConversationSummary,
} from '../../types/advisory';

interface AdvisoryActionOptions {
  language?: string;
  imageBase64?: string;
  imageContentType?: string;
  imageFilename?: string;
  imagePreviewUrl?: string;
}

interface AdvisoryViewProps {
  initialQuery?: string;
  initialConversationId?: string;
  onNavigateToDiagnosis?: () => void;
  onOpenAuth?: () => void;
}

export const AdvisoryView: React.FC<AdvisoryViewProps> = ({
  initialQuery = '',
  initialConversationId,
  onNavigateToDiagnosis,
  onOpenAuth,
}) => {
  const { user } = useAuthStore();
  const locStore = useLocationStore();

  const getEffectiveLocation = () => {
    let lat = locStore.latitude;
    let lon = locStore.longitude;
    let name = locStore.locationName;
    if (!name || lat == null) {
      try {
        const raw = localStorage.getItem('farmsathi_active_location');
        if (raw) {
          const parsed = JSON.parse(raw);
          lat = lat ?? parsed.latitude;
          lon = lon ?? parsed.longitude;
          name = name ?? parsed.locationName;
        }
      } catch {
        // Ignore parse error
      }
    }
    return { lat, lon, name };
  };

  const isAuthenticated = Boolean(user);

  const [conversations, setConversations] = useState<AdvisoryConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] =
    useState<AdvisoryConversationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessageText, setLastMessageText] = useState<string | null>(null);
  const [lastOptions, setLastOptions] = useState<AdvisoryActionOptions | undefined>(undefined);

  const initialHandled = useRef(false);
  const initialConvHandled = useRef(false);

  // Fetch past conversations on mount or when user logs in
  const loadConversations = useCallback(async () => {
    if (!isAuthenticated) {
      setConversations([]);
      return;
    }
    try {
      const list = await advisoryService.getConversations();
      setConversations(list);
    } catch {
      // Non-fatal, conversation history will be empty
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Handle initial conversation ID from history/dashboard if passed
  useEffect(() => {
    if (initialConversationId && !initialConvHandled.current) {
      initialConvHandled.current = true;
      handleSelectConversation(initialConversationId);
    }
  }, [initialConversationId]);

  // Handle initial query from dashboard if passed
  useEffect(() => {
    if (initialQuery && initialQuery.trim() && !initialHandled.current) {
      initialHandled.current = true;
      handleCreateConversation(initialQuery.trim());
    }
  }, [initialQuery]);

  const handleCreateConversation = async (
    queryText: string,
    options?: AdvisoryActionOptions
  ) => {
    if (!isAuthenticated) {
      if (onOpenAuth) onOpenAuth();
      return;
    }

    setLoading(true);
    setError(null);
    setLastMessageText(queryText);
    setLastOptions(options);

    const { lat, lon, name } = getEffectiveLocation();

    try {
      const activeLang = options?.language || useLanguageStore.getState().currentLanguage || 'en';
      const conv = await advisoryService.createConversation({
        initial_message: queryText,
        language: activeLang,
        image_base64: options?.imageBase64,
        image_content_type: options?.imageContentType,
        image_filename: options?.imageFilename,
        latitude: lat ?? undefined,
        longitude: lon ?? undefined,
        location_name: name ?? undefined,
      });
      setActiveConversation(conv);
      loadConversations();
    } catch (err: any) {
      let msg = 'Failed to submit advisory question. Please check connection and try again.';
      if (err.response?.status === 401) {
        msg = 'Your session has expired or sign-in is required. Please sign in and try again.';
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        msg = 'Unable to connect to FarmSathi advisory services. Please check connection and try again.';
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          if (!detail.includes('Traceback') && !detail.includes('Exception')) {
            msg = detail;
          }
        } else if (detail.message && typeof detail.message === 'string') {
          msg = detail.message;
        }
      } else if (err.message && typeof err.message === 'string') {
        if (!err.message.includes('Network Error')) {
          msg = err.message;
        }
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (
    text: string,
    options?: AdvisoryActionOptions
  ) => {
    if (!activeConversation) return;

    setLoading(true);
    setError(null);
    setLastMessageText(text);
    setLastOptions(options);

    const { lat, lon, name } = getEffectiveLocation();

    // Optimistically show user question in UI
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversation.id,
      sender_role: 'user' as const,
      message_text: text,
      context_used: options?.imageFilename
        ? {
            attached_image: {
              filename: options.imageFilename,
              has_image: true,
              mime_type: options.imageContentType || 'image/jpeg',
              size_bytes: 0,
              width: 0,
              height: 0,
            },
          }
        : null,
      created_at: new Date().toISOString(),
    };

    setActiveConversation((prev) =>
      prev ? { ...prev, messages: [...prev.messages, tempUserMsg] } : prev
    );

    try {
      const activeLang = options?.language || useLanguageStore.getState().currentLanguage || activeConversation.language || 'en';
      const executionResult = await advisoryService.sendMessage(
        activeConversation.id,
        text,
        {
          language: activeLang,
          image_base64: options?.imageBase64,
          image_content_type: options?.imageContentType,
          image_filename: options?.imageFilename,
          latitude: lat ?? undefined,
          longitude: lon ?? undefined,
          location_name: name ?? undefined,
        }
      );

      // Replace optimistic messages with confirmed server response
      setActiveConversation((prev) => {
        if (!prev) return prev;
        const filtered = prev.messages.filter((m) => m.id !== tempUserMsg.id);
        return {
          ...prev,
          messages: [
            ...filtered,
            executionResult.user_message,
            executionResult.assistant_message,
          ],
        };
      });
      loadConversations();
    } catch (err: any) {
      let msg = 'Failed to send message. Please retry.';
      if (err.response?.data?.detail) {
        msg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.message || msg;
      } else if (err.message) {
        msg = err.message;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectConversation = async (conversationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const detail = await advisoryService.getConversation(conversationId);
      setActiveConversation(detail);
    } catch (err: any) {
      setError('Failed to load advisory conversation.');
    } finally {
      setLoading(false);
    }
  };

  const handleAskAnother = () => {
    setActiveConversation(null);
    setError(null);
    setLastMessageText(null);
    setLastOptions(undefined);
  };

  const handleRetry = () => {
    if (!lastMessageText) return;
    if (activeConversation) {
      handleSendMessage(lastMessageText, lastOptions);
    } else {
      handleCreateConversation(lastMessageText, lastOptions);
    }
  };

  if (activeConversation) {
    return (
      <QueryResultView
        conversation={activeConversation}
        loading={loading}
        error={error}
        onSendMessage={handleSendMessage}
        onAskAnother={handleAskAnother}
        onNavigateToDiagnosis={onNavigateToDiagnosis}
        onRetry={handleRetry}
      />
    );
  }

  return (
    <AdvisoryInputView
      initialQuery={initialQuery}
      onSubmitQuery={handleCreateConversation}
      recentConversations={conversations}
      onSelectConversation={handleSelectConversation}
      onNavigateToDiagnosis={onNavigateToDiagnosis}
      isAuthenticated={isAuthenticated}
      onOpenAuth={onOpenAuth}
      loading={loading}
      error={error}
      onRetry={handleRetry}
      onDismissError={() => setError(null)}
    />
  );
};
