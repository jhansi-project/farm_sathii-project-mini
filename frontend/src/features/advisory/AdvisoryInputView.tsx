import React, { useState, useRef, useEffect } from 'react';
import type { AdvisoryConversationSummary } from '../../types/advisory';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { useLanguageStore } from '../../stores/languageStore';
import { useTranslation } from '../../i18n/useTranslation';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

export interface ImageAttachment {
  file: File;
  base64: string;
  contentType: string;
  filename: string;
  previewUrl: string;
  sizeKb: number;
}

interface AdvisoryInputViewProps {
  initialQuery?: string;
  onSubmitQuery: (
    query: string,
    options?: {
      language?: string;
      imageBase64?: string;
      imageContentType?: string;
      imageFilename?: string;
      imagePreviewUrl?: string;
    }
  ) => void;
  recentConversations?: AdvisoryConversationSummary[];
  onSelectConversation?: (id: string) => void;
  onNavigateToDiagnosis?: () => void;
  isAuthenticated: boolean;
  onOpenAuth?: () => void;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onDismissError?: () => void;
}

export const AdvisoryInputView: React.FC<AdvisoryInputViewProps> = ({
  initialQuery = '',
  onSubmitQuery,
  recentConversations = [],
  onSelectConversation,
  onNavigateToDiagnosis,
  isAuthenticated,
  onOpenAuth,
  loading = false,
  error = null,
  onRetry,
  onDismissError,
}) => {
  const { t } = useTranslation();
  const { currentLanguage } = useLanguageStore();
  const [selectedLanguage, setSelectedLanguage] = useState<string>(currentLanguage || 'en');
  const [queryText, setQueryText] = useState(initialQuery);
  const [notice, setNotice] = useState<string | null>(null);
  const [attachedImage, setAttachedImage] = useState<ImageAttachment | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync selected language when store updates
  useEffect(() => {
    if (currentLanguage) {
      setSelectedLanguage(currentLanguage);
    }
  }, [currentLanguage]);

  // Speech Recognition hook
  const {
    voiceState,
    errorMessage: voiceError,
    startListening,
    stopListening,
    resetState: resetVoiceState,
  } = useSpeechRecognition({
    onTranscriptChange: (text) => {
      setQueryText(text);
    },
    onFinalTranscript: (text) => {
      setQueryText(text);
    },
  });

  // Stop active voice recognition if language is changed
  useEffect(() => {
    if (voiceState === 'listening' || voiceState === 'processing') {
      stopListening();
    }
  }, [selectedLanguage, stopListening]);

  const handleToggleVoice = () => {
    if (voiceState === 'listening' || voiceState === 'processing') {
      stopListening();
    } else {
      startListening(selectedLanguage, queryText);
    }
  };

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImageError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate size (10 MB)
    const MAX_BYTES = 10 * 1024 * 1024;
    if (file.size > MAX_BYTES) {
      setImageError('Image exceeds the maximum allowed size of 10 MB. Please choose a smaller photo.');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    // Validate format
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    const allowedExts = ['jpg', 'jpeg', 'png', 'webp'];
    if (!allowedTypes.includes(file.type) && (!ext || !allowedExts.includes(ext))) {
      setImageError('Unsupported image format. Please upload a JPEG, PNG, or WebP photo.');
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
      setImageError('Failed to read image file. Please try selecting again.');
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    if (!queryText.trim()) return;

    if (!isAuthenticated) {
      if (onOpenAuth) {
        onOpenAuth();
      }
      return;
    }

    stopListening();
    onSubmitQuery(queryText.trim(), {
      language: selectedLanguage,
      imageBase64: attachedImage?.base64,
      imageContentType: attachedImage?.contentType,
      imageFilename: attachedImage?.filename,
      imagePreviewUrl: attachedImage?.previewUrl,
    });
  };

  const sampleQuestions = [
    'Yesterday morning I applied fertilizer and today the leaves are curling. What should I do?',
    'My rice leaves have brown spots. What could be the reason?',
    'The weather has been very humid for the last few days. What should I watch for?',
    'Which crop did FarmSathi recommend for my soil?',
    'My wheat plant is turning yellow. What information should I check?',
  ];

  return (
    <div className="farmsathi-page-container-narrow">
      {/* Header */}
      <PageHeader
        icon="forum"
        title={t.ask.title || 'Ask FarmSathi'}
        subtitle={t.ask.subtitle || 'Ask any question about your crops, weather, pest protection, or fertilizers.'}
      />

      {/* Notice & Feedback Banners */}
      {notice && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--color-primary-light)',
            border: '1px solid var(--color-primary-subtle)',
            color: 'var(--color-primary)',
            fontSize: 'var(--font-size-sm)',
            textAlign: 'center',
            fontWeight: 500,
          }}
        >
          {notice}
        </div>
      )}

      {/* Voice Error Notice */}
      {voiceError && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--color-error-bg)',
            border: '1px solid var(--color-error-border)',
            color: 'var(--color-error)',
            fontSize: 'var(--font-size-xs)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
              mic_off
            </span>
            <span>{voiceError}</span>
          </div>
          <button
            type="button"
            onClick={resetVoiceState}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-error)',
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: '11px',
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Image Error Notice */}
      {imageError && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--color-error-bg)',
            border: '1px solid var(--color-error-border)',
            color: 'var(--color-error)',
            fontSize: 'var(--font-size-xs)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
              error
            </span>
            <span>{imageError}</span>
          </div>
          <button
            type="button"
            onClick={() => setImageError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-error)',
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: '11px',
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Advisory Request Error Banner */}
      {error && (
        <div
          style={{
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--color-error-bg)',
            border: '1px solid var(--color-error-border)',
            color: 'var(--color-error)',
            fontSize: 'var(--font-size-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1 }}>
            <span className="material-symbols-outlined" style={{ fontSize: '20px', flexShrink: 0 }}>
              error
            </span>
            <span style={{ lineHeight: 1.4 }}>{error}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
            {onRetry && (
              <Button size="sm" onClick={onRetry} isLoading={loading}>
                {t.ask.retry || t.common.tryAgain || 'Retry'}
              </Button>
            )}
            {onDismissError && (
              <button
                type="button"
                onClick={onDismissError}
                style={{ color: 'var(--color-error)', cursor: 'pointer' }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                  close
                </span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Unauthenticated Notice */}
      {!isAuthenticated && (
        <Card
          padding="sm"
          surface="subtle"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)' }}>
              lock
            </span>
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
              Sign in to save and personalize your advisory consultations.
            </span>
          </div>
          <Button size="sm" onClick={onOpenAuth}>
            {t.nav.login}
          </Button>
        </Card>
      )}

      {/* 3 Quick Action Cards */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
        {/* Voice Input Card */}
        <Card
          hoverable
          onClick={handleToggleVoice}
          padding="sm"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            gap: '0.35rem',
            backgroundColor:
              voiceState === 'listening' ? 'var(--color-primary-light)' : 'var(--color-surface)',
            border: `1.5px solid ${
              voiceState === 'listening' ? 'var(--color-primary)' : 'var(--color-border)'
            }`,
          }}
        >
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-full)',
              backgroundColor:
                voiceState === 'listening'
                  ? 'var(--color-primary)'
                  : 'var(--color-surface-container-low)',
              color: voiceState === 'listening' ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>
              {voiceState === 'listening' ? 'graphic_eq' : 'mic'}
            </span>
          </div>
          <span
            style={{
              fontSize: 'var(--font-size-xs)',
              fontWeight: 700,
              color:
                voiceState === 'listening' ? 'var(--color-primary)' : 'var(--color-text-primary)',
            }}
          >
            {voiceState === 'listening'
              ? t.common.listening || 'Listening...'
              : t.common.voice_input || 'Voice Input'}
          </span>
          <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
            {voiceState === 'listening'
              ? 'Tap to Stop'
              : t.common.speak_placeholder || 'Speak Question'}
          </span>
        </Card>

        {/* Add Image Card */}
        <Card
          hoverable
          onClick={() => fileInputRef.current?.click()}
          padding="sm"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            gap: '0.35rem',
            backgroundColor: attachedImage ? 'var(--color-primary-light)' : 'var(--color-surface)',
            border: `1.5px solid ${
              attachedImage ? 'var(--color-primary)' : 'var(--color-border)'
            }`,
          }}
        >
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: attachedImage
                ? 'var(--color-primary)'
                : 'var(--color-surface-container-low)',
              color: attachedImage ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>
              {attachedImage ? 'image' : 'add_photo_alternate'}
            </span>
          </div>
          <span
            style={{
              fontSize: 'var(--font-size-xs)',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
            }}
          >
            {attachedImage ? 'Image Attached' : t.common.camera_upload || 'Add Photo'}
          </span>
          <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
            {attachedImage ? `${attachedImage.sizeKb} KB` : t.common.foliage_context || 'Foliage Context'}
          </span>
        </Card>

        {/* Disease Scan Shortcut */}
        <Card
          hoverable
          onClick={() => {
            if (onNavigateToDiagnosis) {
              onNavigateToDiagnosis();
            } else {
              setNotice('📸 For leaf disease diagnosis, please switch to the Diagnosis tab.');
              setTimeout(() => setNotice(null), 4000);
            }
          }}
          padding="sm"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            gap: '0.35rem',
          }}
        >
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--color-surface-container-low)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>
              photo_camera
            </span>
          </div>
          <span
            style={{
              fontSize: 'var(--font-size-xs)',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
            }}
          >
            {t.common.disease_detection || 'Leaf Doctor'}
          </span>
          <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
            {t.common.crop_health || 'Crop Health'}
          </span>
        </Card>
      </section>

      {/* Hidden File Input for Image Upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        style={{ display: 'none' }}
        onChange={handleImageFileChange}
      />

      {/* Attached Image Preview Card */}
      {attachedImage && (
        <Card
          padding="sm"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            border: '1.5px solid var(--color-primary-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', overflow: 'hidden' }}>
            <img
              src={attachedImage.previewUrl}
              alt="Farmer crop context"
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--radius-md)',
                objectFit: 'cover',
                border: '1px solid var(--color-border)',
              }}
            />
            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              <div
                style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {attachedImage.filename}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                {attachedImage.sizeKb} KB • Photo attached for agricultural context
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={handleRemoveImage}
            title="Remove attached image"
            style={{
              backgroundColor: 'var(--color-error-bg)',
              border: 'none',
              color: 'var(--color-error)',
              borderRadius: 'var(--radius-full)',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
              close
            </span>
          </button>
        </Card>
      )}

      {/* Main Advisory Question Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <Card padding="md" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ position: 'relative' }}>
            <textarea
              rows={4}
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder={t.common.type_placeholder || t.ask.inputPlaceholder || 'Describe your agricultural question or crop symptom in detail...'}
              style={{
                width: '100%',
                backgroundColor: 'transparent',
                border: 'none',
                fontSize: 'var(--font-size-base)',
                color: 'var(--color-text-primary)',
                resize: 'none',
                outline: 'none',
                fontFamily: 'inherit',
                lineHeight: 1.5,
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderTop: '1px solid var(--color-border-subtle)',
              paddingTop: '0.65rem',
            }}
          >
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Language: {selectedLanguage.toUpperCase()}
            </span>
            <Button
              type="button"
              size="sm"
              variant="subtle"
              onClick={handleToggleVoice}
              leftIcon={
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                  {voiceState === 'listening' ? 'graphic_eq' : 'mic'}
                </span>
              }
            >
              {voiceState === 'listening' ? 'Stop' : 'Voice'}
            </Button>
          </div>
        </Card>

        {/* Common Suggestion Chips */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', fontWeight: 600 }}>
            Common farm questions:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQueryText(q)}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  color: 'var(--color-text-secondary)',
                  fontSize: 'var(--font-size-xs)',
                  padding: '0.45rem 0.8rem',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--color-border)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  lineHeight: 1.35,
                  transition: 'all var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
                  e.currentTarget.style.borderColor = 'var(--color-primary-subtle)';
                  e.currentTarget.style.color = 'var(--color-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface)';
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                }}
              >
                "{q}"
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          size="lg"
          fullWidth
          disabled={!queryText.trim() || loading}
          isLoading={loading}
          leftIcon={
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              send
            </span>
          }
        >
          {loading
            ? t.ask.consulting || 'Consulting FarmSathi Advisory Engine...'
            : attachedImage
            ? t.ask.submitWithPhoto || 'Submit Question & Image'
            : t.ask.submitQuestion || t.ask.title || 'Ask FarmSathi'}
        </Button>
      </form>

      {/* Past Advisory Consultations List */}
      {recentConversations.length > 0 && (
        <section style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <h3
            style={{
              fontSize: 'var(--font-size-sm)',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              margin: 0,
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--color-primary)' }}>
              history
            </span>
            Recent Consultations
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {recentConversations.slice(0, 5).map((conv) => (
              <Card
                key={conv.id}
                hoverable
                padding="sm"
                onClick={() => onSelectConversation?.(conv.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '85%' }}>
                  <div
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: 600,
                      color: 'var(--color-text-primary)',
                    }}
                  >
                    {conv.title}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    {new Date(conv.updated_at).toLocaleDateString()} • {conv.message_count} messages
                  </div>
                </div>
                <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '20px' }}>
                  chevron_right
                </span>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
