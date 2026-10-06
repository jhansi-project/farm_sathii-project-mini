import React, { useState, useRef, useEffect } from 'react';
import type { AdvisoryConversationDetail } from '../../types/advisory';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { useTranslation } from '../../i18n/useTranslation';
import { useLanguageStore } from '../../stores/languageStore';
import type { ImageAttachment } from './AdvisoryInputView';

interface QueryResultViewProps {
  conversation: AdvisoryConversationDetail;
  loading: boolean;
  error: string | null;
  onSendMessage: (
    text: string,
    options?: {
      language?: string;
      imageBase64?: string;
      imageContentType?: string;
      imageFilename?: string;
      imagePreviewUrl?: string;
    }
  ) => void;
  onAskAnother: () => void;
  onNavigateToDiagnosis?: () => void;
  onRetry?: () => void;
}

function renderFormattedMessage(text: string): React.ReactNode {
  if (!text) return null;

  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];

  const parseInline = (inlineText: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    const regex = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(inlineText)) !== null) {
      if (match.index > lastIndex) {
        parts.push(inlineText.substring(lastIndex, match.index));
      }
      if (match[2] !== undefined) {
        parts.push(
          <strong key={match.index} style={{ fontWeight: 700, color: 'inherit' }}>
            {match[2]}
          </strong>
        );
      } else if (match[3] !== undefined) {
        parts.push(
          <em key={match.index} style={{ fontStyle: 'italic' }}>
            {match[3]}
          </em>
        );
      } else if (match[4] !== undefined) {
        parts.push(
          <code
            key={match.index}
            style={{
              backgroundColor: 'var(--color-surface-container)',
              padding: '0.1rem 0.3rem',
              borderRadius: '3px',
              fontSize: '90%',
            }}
          >
            {match[4]}
          </code>
        );
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < inlineText.length) {
      parts.push(inlineText.substring(lastIndex));
    }

    return parts.length > 0 ? parts : [inlineText];
  };

  let currentList: { type: 'ul' | 'ol'; items: React.ReactNode[] } | null = null;

  const flushList = (key: number) => {
    if (!currentList) return null;
    const list = currentList;
    currentList = null;
    if (list.type === 'ol') {
      return (
        <ol key={`list-${key}`} style={{ margin: '0.35rem 0', paddingLeft: '1.35rem' }}>
          {list.items.map((it, idx) => (
            <li key={idx} style={{ marginBottom: '0.2rem' }}>
              {it}
            </li>
          ))}
        </ol>
      );
    }
    return (
      <ul key={`list-${key}`} style={{ margin: '0.35rem 0', paddingLeft: '1.25rem' }}>
        {list.items.map((it, idx) => (
          <li key={idx} style={{ marginBottom: '0.2rem' }}>
            {it}
          </li>
        ))}
      </ul>
    );
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed) {
      if (currentList) {
        elements.push(flushList(index));
      }
      elements.push(<div key={`space-${index}`} style={{ height: '0.4rem' }} />);
      return;
    }

    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numberedMatch) {
      if (!currentList || currentList.type !== 'ol') {
        if (currentList) elements.push(flushList(index));
        currentList = { type: 'ol', items: [] };
      }
      currentList.items.push(parseInline(numberedMatch[2]));
      return;
    }

    const bulletMatch = trimmed.match(/^[-*•]\s+(.*)$/);
    if (bulletMatch) {
      if (!currentList || currentList.type !== 'ul') {
        if (currentList) elements.push(flushList(index));
        currentList = { type: 'ul', items: [] };
      }
      currentList.items.push(parseInline(bulletMatch[1]));
      return;
    }

    if (currentList) {
      elements.push(flushList(index));
    }

    elements.push(
      <p key={`p-${index}`} style={{ margin: '0 0 0.35rem 0', lineHeight: 1.6 }}>
        {parseInline(trimmed)}
      </p>
    );
  });

  if (currentList) {
    elements.push(flushList(lines.length));
  }

  return elements;
}

export const QueryResultView: React.FC<QueryResultViewProps> = ({
  conversation,
  loading,
  error,
  onSendMessage,
  onAskAnother,
  onNavigateToDiagnosis,
  onRetry,
}) => {
  const { t } = useTranslation();
  const [followUpText, setFollowUpText] = useState('');
  const [attachedImage, setAttachedImage] = useState<ImageAttachment | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { currentLanguage } = useLanguageStore();
  const effectiveLang = currentLanguage || conversation.language || 'en';

  // Speech Recognition hook for follow-up questions
  const {
    voiceState,
    errorMessage: voiceError,
    startListening,
    stopListening,
    resetState: resetVoice,
  } = useSpeechRecognition({
    onTranscriptChange: (text) => {
      setFollowUpText(text);
    },
    onFinalTranscript: (text) => {
      setFollowUpText(text);
    },
  });

  // Stop active voice recognition if language is changed
  useEffect(() => {
    if (voiceState === 'listening' || voiceState === 'processing') {
      stopListening();
    }
  }, [currentLanguage, stopListening]);

  const handleToggleVoice = () => {
    if (voiceState === 'listening' || voiceState === 'processing') {
      stopListening();
    } else {
      startListening(effectiveLang, followUpText);
    }
  };

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImageError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const MAX_BYTES = 10 * 1024 * 1024;
    if (file.size > MAX_BYTES) {
      setImageError('Image exceeds the maximum allowed size of 10 MB.');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    const allowedExts = ['jpg', 'jpeg', 'png', 'webp'];
    if (!allowedTypes.includes(file.type) && (!ext || !allowedExts.includes(ext))) {
      setImageError('Unsupported image format. Allowed: JPEG, PNG, WebP.');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = (loadEvt) => {
      const result = loadEvt.target?.result as string;
      setAttachedImage({
        file,
        base64: result,
        contentType: file.type || 'image/jpeg',
        filename: file.name,
        previewUrl: URL.createObjectURL(file),
        sizeKb: Math.round(file.size / 1024),
      });
    };
    reader.onerror = () => {
      setImageError('Failed to read image file.');
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    if (attachedImage?.previewUrl) {
      URL.revokeObjectURL(attachedImage.previewUrl);
    }
    setAttachedImage(null);
    setImageError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation.messages, loading]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (followUpText.trim() && !loading) {
      stopListening();
      const activeLang = useLanguageStore.getState().currentLanguage || conversation.language || 'en';
      onSendMessage(followUpText.trim(), {
        language: activeLang,
        imageBase64: attachedImage?.base64,
        imageContentType: attachedImage?.contentType,
        imageFilename: attachedImage?.filename,
        imagePreviewUrl: attachedImage?.previewUrl,
      });
      setFollowUpText('');
      handleRemoveImage();
    }
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-background)',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Advisory Conversation Toolbar */}
      <div
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 20,
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border-subtle)',
          minHeight: '56px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.75rem 1.25rem',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            type="button"
            onClick={onAskAnother}
            title={t.common.back || 'Back'}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-primary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--color-surface-container-low)',
              transition: 'background-color var(--transition-fast)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-surface-container-low)';
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>arrow_back</span>
          </button>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <h1
              style={{
                fontSize: 'var(--font-size-base)',
                fontWeight: 700,
                color: 'var(--color-text-primary)',
                margin: 0,
                maxWidth: '280px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                letterSpacing: '-0.01em',
              }}
            >
              {conversation.title && conversation.title !== 'ask_advisor' && conversation.title !== 'Agricultural Advisory Session'
                ? conversation.title
                : (t.ask.title || 'FarmSathi Advisor')}
            </h1>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              {new Date(conversation.created_at).toLocaleDateString()} • {conversation.messages.length} {t.common.queries || 'messages'}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onAskAnother}
          style={{
            padding: '0.4rem 0.85rem',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-primary-light)',
            color: 'var(--color-primary)',
            fontSize: 'var(--font-size-xs)',
            fontWeight: 700,
            border: '1px solid var(--color-primary-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            cursor: 'pointer',
            transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-primary)';
            e.currentTarget.style.color = 'var(--color-text-inverse, #E5D7C4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
            e.currentTarget.style.color = 'var(--color-primary)';
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
            add
          </span>
          <span>{t.common.ask_new_question || 'New Session'}</span>
        </button>
      </div>

      {/* Messages Stream Container */}
      <main
        style={{
          flex: 1,
          padding: '1rem 1rem 7rem 1rem',
          maxWidth: '768px',
          margin: '0 auto',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        {conversation.messages.length === 0 && !loading && (
          <div
            style={{
              textAlign: 'center',
              padding: '3rem 1rem',
              color: 'var(--color-on-surface-variant)',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--color-primary)' }}>
              forum
            </span>
            <p style={{ marginTop: '0.5rem', fontSize: 'var(--font-size-base)' }}>
              Ask your first agricultural question below.
            </p>
          </div>
        )}

        {conversation.messages.map((msg, index) => {
          const isUser = msg.sender_role === 'user';
          const contextUsed = msg.context_used;
          const providerStatus = contextUsed?.provider_status;
          const disclaimers = contextUsed?.disclaimers || [];
          const structuredData = contextUsed?.data;

          if (isUser) {
            return (
              <div
                key={msg.id || index}
                style={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  width: '100%',
                }}
              >
                <div
                  style={{
                    backgroundColor: 'var(--color-primary)',
                    color: 'var(--color-text-inverse)',
                    borderRadius: 'var(--radius-lg)',
                    borderBottomRightRadius: '4px',
                    padding: '0.85rem 1.15rem',
                    maxWidth: '85%',
                    boxShadow: 'var(--shadow-sm)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.25rem' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: '14px', opacity: 0.85 }}>
                      person
                    </span>
                    <span style={{ fontSize: '11px', fontWeight: 600, opacity: 0.85 }}>
                      Farmer Query
                    </span>
                  </div>
                  {contextUsed?.attached_image && (
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        backgroundColor: 'rgba(255, 255, 255, 0.2)',
                        borderRadius: 'var(--radius-full)',
                        padding: '0.2rem 0.5rem',
                        marginBottom: '0.4rem',
                        fontSize: '11px',
                      }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>
                        image
                      </span>
                      <span>Photo: {contextUsed.attached_image.filename}</span>
                    </div>
                  )}
                  <p
                    style={{
                      margin: 0,
                      fontSize: 'var(--font-size-sm)',
                      lineHeight: 1.5,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {msg.message_text}
                  </p>
                </div>
              </div>
            );
          }

          // Assistant Response Card
          return (
            <div
              key={msg.id || index}
              style={{
                display: 'flex',
                justifyContent: 'flex-start',
                width: '100%',
              }}
            >
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-lowest)',
                  border: '1px solid var(--color-outline-variant)',
                  borderRadius: 'var(--radius-lg)',
                  borderBottomLeftRadius: '4px',
                  padding: '1.25rem',
                  maxWidth: '92%',
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.85rem',
                  boxShadow: 'var(--shadow-sm)',
                }}
              >
                {/* Assistant Header & Status Badge */}
                {(() => {
                  const prevUserMsg = conversation.messages.slice(0, index).reverse().find(m => m.sender_role === 'user');
                  const userQ = (prevUserMsg?.message_text || '').toLowerCase();
                  const assistantText = (msg.message_text || '').toLowerCase();

                  const isWeatherQuery = /\b(rain|raining|rainfall|weather|temperature|temp|forecast|cloud|sunny|humid|humidity|storm|precipitation|wind|వర్షం|వాతావరణం|ఎండ|ఉష్ణోగ్రత|తేమ|గాలి|मौसम|बारिश|तापमान|वर्षा|हवा)\b/.test(userQ);
                  const isSprayOrIrrigation = /\b(spray|irrigate|irrigation|water|spraying|పిచికారీ|తడి|సిరింపు|सिंचाई|छिड़काव)\b/.test(userQ);

                  const isCropRelevant = !isWeatherQuery && (
                    /\b(crop|crops|grow|plant|sow|yield|harvest|seed|variety|fertilizer|soil|పంట|వరి|విత్తనం|ఎరువు|యూరియా|ఫసల్|बीज|खाद|मिट्टी)\b/.test(userQ)
                    || Boolean(structuredData?.crop_recommendation?.recommended_crop && assistantText.includes(structuredData.crop_recommendation.recommended_crop.toLowerCase()))
                  );

                  const isDiseaseRelevant = !isWeatherQuery && (
                    /\b(disease|pest|fungus|blight|spot|rot|rust|leaf|bug|yellow|curl|wilting|insect|pesticide|పురుగు|తెగులు|రోగం|ఆకు|రోగ|कीड़ा|झुलसा)\b/.test(userQ)
                    || Boolean(structuredData?.disease_diagnosis?.predicted_condition && assistantText.includes(structuredData.disease_diagnosis.predicted_condition.toLowerCase()))
                  );

                  const isGrounded = Boolean(
                    (structuredData?.disease_diagnosis?.predicted_condition && structuredData.disease_diagnosis.is_suitable !== false && isDiseaseRelevant) ||
                    (structuredData?.crop_recommendation?.recommended_crop && isCropRelevant) ||
                    (structuredData?.weather?.temperature_celsius != null && (isWeatherQuery || isSprayOrIrrigation))
                  );

                  return (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div
                          style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: 'var(--radius-full)',
                            backgroundColor: 'var(--color-primary)',
                            color: 'var(--color-text-inverse, #E5D7C4)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                            psychology
                          </span>
                        </div>
                        <div>
                          <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-primary)' }}>
                            FarmSathi Advisor
                          </span>
                        </div>
                      </div>

                      {providerStatus === 'success' && isGrounded && (
                        <span
                          style={{
                            backgroundColor: 'rgba(46, 125, 50, 0.15)',
                            color: 'var(--color-primary)',
                            fontSize: '11px',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontWeight: 600,
                          }}
                        >
                          Verified Advice
                        </span>
                      )}
                      {providerStatus === 'success' && !isGrounded && (
                        <span
                          style={{
                            backgroundColor: 'rgba(33, 150, 243, 0.12)',
                            color: 'var(--color-info, #1565C0)',
                            fontSize: '11px',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontWeight: 600,
                          }}
                        >
                          Agronomic Guidance
                        </span>
                      )}
                      {providerStatus === 'insufficient_context' && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-warning-bg, #CFBB99)',
                            color: 'var(--color-warning, #4C3D19)',
                            fontSize: '11px',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontWeight: 600,
                          }}
                        >
                          More Details Needed
                        </span>
                      )}
                    </div>
                  );
                })()}

                {/* Ground-truth Context Chips (only shown if real data was provided) */}
                {(() => {
                  if (!structuredData) return null;

                  const prevUserMsg = conversation.messages.slice(0, index).reverse().find(m => m.sender_role === 'user');
                  const userQ = (prevUserMsg?.message_text || '').toLowerCase();
                  const assistantText = (msg.message_text || '').toLowerCase();

                  const isWeatherQuery = /\b(rain|raining|rainfall|weather|temperature|temp|forecast|cloud|sunny|humid|humidity|storm|precipitation|wind|వర్షం|వాతావరణం|ఎండ|ఉష్ణోగ్రత|తేమ|గాలి|मौसम|बारिश|तापमान|वर्षा|हवा)\b/.test(userQ);

                  const isCropRelevant = !isWeatherQuery && (
                    /\b(crop|grow|plant|sow|yield|harvest|seed|variety|fertilizer|soil|పంట|వరి|విత్తనం|ఎరువు|యూరియా|ఫసల్|बीज|खाद|मिट्टी)\b/.test(userQ)
                    || (structuredData.crop_recommendation?.recommended_crop && assistantText.includes(structuredData.crop_recommendation.recommended_crop.toLowerCase()))
                  );

                  const isDiseaseRelevant = !isWeatherQuery && (
                    /\b(disease|pest|fungus|blight|spot|rot|rust|leaf|bug|yellow|curl|wilting|insect|pesticide|పురుగు|తెగులు|రోగం|ఆకు|రోగ|कीड़ा|झुलसा)\b/.test(userQ)
                    || (structuredData.disease_diagnosis?.predicted_condition && assistantText.includes(structuredData.disease_diagnosis.predicted_condition.toLowerCase()))
                  );

                  return (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {structuredData.weather && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-surface-container-low)',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '11px',
                            color: 'var(--color-on-surface)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-primary)' }}>
                            partly_cloudy_day
                          </span>
                          {structuredData.weather.location_name ? `${structuredData.weather.location_name}: ` : ''}
                          {structuredData.weather.condition_text || structuredData.weather.condition || 'Weather'}
                          {structuredData.weather.temperature_celsius != null ? ` (${structuredData.weather.temperature_celsius}°C)` : ''}
                        </span>
                      )}
                      {structuredData.farmer_profile?.soil_type && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-surface-container-low)',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '11px',
                            color: 'var(--color-on-surface)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-primary)' }}>
                            landscape
                          </span>
                          Soil: {structuredData.farmer_profile.soil_type}
                        </span>
                      )}
                      {structuredData.farmer_profile?.district && !structuredData.weather?.location_name && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-surface-container-low)',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '11px',
                            color: 'var(--color-on-surface)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-primary)' }}>
                            location_on
                          </span>
                          {structuredData.farmer_profile.district}, {structuredData.farmer_profile.state || ''}
                        </span>
                      )}
                      {structuredData.crop_recommendation?.recommended_crop && isCropRelevant && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-surface-container-low)',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '11px',
                            color: 'var(--color-on-surface)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-primary)' }}>
                            agriculture
                          </span>
                          Crop Rec: {structuredData.crop_recommendation.recommended_crop}
                        </span>
                      )}
                      {structuredData.disease_diagnosis?.predicted_condition && isDiseaseRelevant && (
                        <span
                          style={{
                            backgroundColor: 'var(--color-surface-container-low)',
                            padding: '0.2rem 0.5rem',
                            borderRadius: 'var(--radius-full)',
                            fontSize: '11px',
                            color: 'var(--color-on-surface)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-error)' }}>
                            bug_report
                          </span>
                          Diag: {structuredData.disease_diagnosis.predicted_condition.replace(/___+/g, ' - ').replace(/__+/g, ' - ').replace(/_/g, ' ')}
                        </span>
                      )}
                    </div>
                  );
                })()}

                {/* Primary Advisory Response Body */}
                <div
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-on-surface)',
                    lineHeight: 1.6,
                  }}
                >
                  {renderFormattedMessage(msg.message_text)}
                </div>


                {/* Safety Disclaimers */}
                {disclaimers.length > 0 && (
                  <div
                    style={{
                      borderTop: '1px solid var(--color-outline-variant)',
                      paddingTop: '0.75rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.5rem',
                    }}
                  >
                    {disclaimers.map((disc, dIdx) => (
                      <div
                        key={dIdx}
                        style={{
                          fontSize: '11px',
                          color: 'var(--color-on-surface-variant)',
                          lineHeight: 1.4,
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '0.35rem',
                        }}
                      >
                        <span>{disc}</span>
                      </div>
                    ))}

                    {/* Quick navigation link if visual diagnosis is suggested */}
                    {disclaimers.some((d) => d.includes('Disease Detection')) && onNavigateToDiagnosis && (
                      <button
                        type="button"
                        onClick={onNavigateToDiagnosis}
                        style={{
                          alignSelf: 'flex-start',
                          marginTop: '0.25rem',
                          backgroundColor: 'rgba(46, 125, 50, 0.1)',
                          border: '1px solid var(--color-primary)',
                          color: 'var(--color-primary)',
                          borderRadius: 'var(--radius-full)',
                          padding: '0.35rem 0.75rem',
                          fontSize: '11px',
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                        }}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                          photo_camera
                        </span>
                        Open Disease Detection to Upload Leaf Photo
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Bubble */}
        {loading && (
          <div
            style={{
              backgroundColor: 'var(--color-surface-container-lowest)',
              border: '1px solid var(--color-outline-variant)',
              borderRadius: 'var(--radius-lg)',
              padding: '1rem',
              maxWidth: '360px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <div
              style={{
                width: '18px',
                height: '18px',
                border: '2px solid var(--color-primary)',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }}
            />
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-on-surface-variant)' }}>
              Consulting FarmSathi Advisory Engine...
            </span>
          </div>
        )}

        {/* Error State Banner */}
        {error && (
          <div
            style={{
              backgroundColor: 'var(--color-error-container)',
              color: 'var(--color-on-error-container)',
              borderRadius: 'var(--radius-md)',
              padding: '0.75rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: 'var(--font-size-xs)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                error
              </span>
              <span>{error}</span>
            </div>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                style={{
                  backgroundColor: 'var(--color-error)',
                  color: 'var(--color-text-inverse, #E5D7C4)',
                  border: 'none',
                  borderRadius: 'var(--radius-full)',
                  padding: '0.25rem 0.75rem',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Retry
              </button>
            )}
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        style={{ display: 'none' }}
        onChange={handleImageFileChange}
      />

      {/* Sticky Bottom Follow-Up Question Input */}
      <footer
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: 'var(--color-surface)',
          boxShadow: '0 -2px 8px rgba(0,0,0,0.06)',
          padding: '0.6rem 1rem',
          zIndex: 30,
        }}
      >
        <div style={{ maxWidth: '768px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {/* Attached Image Preview Pill */}
          {attachedImage && (
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: 'var(--color-surface-container-low)',
                border: '1px solid var(--color-primary)',
                borderRadius: 'var(--radius-full)',
                padding: '0.2rem 0.6rem 0.2rem 0.35rem',
                fontSize: 'var(--font-size-xs)',
                alignSelf: 'flex-start',
              }}
            >
              <img
                src={attachedImage.previewUrl}
                alt="Thumbnail"
                style={{ width: '22px', height: '22px', borderRadius: '50%', objectFit: 'cover' }}
              />
              <span style={{ fontWeight: 600, color: 'var(--color-on-surface)' }}>
                {attachedImage.filename} ({attachedImage.sizeKb} KB)
              </span>
              <button
                type="button"
                onClick={handleRemoveImage}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-error)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  padding: 0,
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                  close
                </span>
              </button>
            </div>
          )}

          {/* Voice Error Notice */}
          {voiceError && (
            <div style={{ fontSize: '11px', color: 'var(--color-error)', padding: '0 0.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>🎙️ {voiceError}</span>
              <button
                type="button"
                onClick={resetVoice}
                style={{ background: 'none', border: 'none', color: 'var(--color-error)', cursor: 'pointer', fontSize: '10px', fontWeight: 600 }}
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Image Error Notice */}
          {imageError && (
            <div style={{ fontSize: '11px', color: 'var(--color-error)', padding: '0 0.25rem' }}>
              📷 {imageError}
            </div>
          )}

          <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            {/* Image Attachment Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              title="Attach foliage image"
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: attachedImage ? 'rgba(46, 125, 50, 0.15)' : 'var(--color-surface-container)',
                color: 'var(--color-primary)',
                border: '1px solid var(--color-outline-variant)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                flexShrink: 0,
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                photo_camera
              </span>
            </button>

            {/* Question Text Input */}
            <input
              type="text"
              placeholder={
                voiceState === 'listening'
                  ? 'Listening... speak your question'
                  : 'Ask a follow-up question...'
              }
              value={followUpText}
              onChange={(e) => setFollowUpText(e.target.value)}
              disabled={loading}
              style={{
                flex: 1,
                backgroundColor: 'var(--color-surface-container-lowest)',
                border: voiceState === 'listening' ? '1.5px solid var(--color-primary)' : '1.5px solid var(--color-outline-variant)',
                borderRadius: 'var(--radius-full)',
                padding: '0.65rem 1.15rem',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-on-surface)',
                outline: 'none',
              }}
            />

            {/* Microphone Button */}
            <button
              type="button"
              onClick={handleToggleVoice}
              title={voiceState === 'listening' ? 'Stop listening' : 'Speak follow-up'}
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: voiceState === 'listening' ? 'var(--color-primary)' : 'var(--color-surface-container)',
                color: voiceState === 'listening' ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-primary)',
                border: '1px solid var(--color-outline-variant)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                flexShrink: 0,
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                {voiceState === 'listening' ? 'graphic_eq' : 'mic'}
              </span>
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!followUpText.trim() || loading}
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: followUpText.trim() && !loading ? 'var(--color-primary)' : 'var(--color-surface-container-high)',
                color: followUpText.trim() && !loading ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-outline)',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: followUpText.trim() && !loading ? 'pointer' : 'not-allowed',
                boxShadow: followUpText.trim() && !loading ? 'var(--shadow-sm)' : 'none',
                flexShrink: 0,
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                send
              </span>
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
};
