import React, { useState, useRef, useEffect } from 'react';
import { diseaseService } from '../../services/diseaseService';
import { DiseaseDiagnosisResult } from '../../types/disease';
import { useTranslation } from '../../i18n/useTranslation';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';

export const DiseaseDetectionView: React.FC = () => {
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<DiseaseDiagnosisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Desktop Webcam Capture States
  const [cameraMode, setCameraMode] = useState<'idle' | 'streaming' | 'captured'>('idle');
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [capturedPreview, setCapturedPreview] = useState<string | null>(null);
  const [cameraError, setCameraError] = useState<{
    type: 'denied' | 'unavailable' | 'error';
    message: string;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Stop camera helper to ensure hardware release
  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // ignore error on stop
        }
      });
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  // Ensure webcam tracks stop when component unmounts
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const handleFile = (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      setError('Selected image exceeds 10 MB. Please choose a smaller photo.');
      return;
    }
    setError(null);
    setCameraError(null);
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      stopCamera();
      setCameraMode('idle');
      setCameraError(null);
      handleFile(file);
    }
  };

  const startCamera = async () => {
    setCameraError(null);
    setError(null);
    setCapturedFile(null);
    setCapturedPreview(null);

    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      setCameraError({
        type: 'unavailable',
        message: 'Camera is not supported in this browser. Please use Upload from Gallery instead.',
      });
      return;
    }

    try {
      stopCamera();
      setCameraMode('streaming');

      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: { ideal: 'environment' },
          },
          audio: false,
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
    } catch (err: any) {
      stopCamera();
      setCameraMode('idle');

      const errName = err.name || '';
      if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
        setCameraError({
          type: 'denied',
          message:
            'Camera access was denied. Please allow camera access in your browser settings or use Upload from Gallery instead.',
        });
      } else if (
        errName === 'NotFoundError' ||
        errName === 'DevicesNotFoundError' ||
        errName === 'OverconstrainedError'
      ) {
        setCameraError({
          type: 'unavailable',
          message:
            'No webcam was detected on this device. Please connect a camera or use Upload from Gallery instead.',
        });
      } else {
        setCameraError({
          type: 'error',
          message:
            err.message ||
            'Unable to access the camera. Please check your browser permissions or use Upload from Gallery.',
        });
      }
    }
  };

  const handleCapturePhoto = () => {
    const video = videoRef.current;
    if (!video) return;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, width, height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError('Failed to capture photo frame from webcam. Please try again.');
          return;
        }

        const file = new File([blob], `crop_foliage_${Date.now()}.jpg`, {
          type: 'image/jpeg',
          lastModified: Date.now(),
        });

        const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
        setCapturedFile(file);
        setCapturedPreview(dataUrl);
        setCameraMode('captured');
        stopCamera();
      },
      'image/jpeg',
      0.95
    );
  };

  const handleUseCapturedPhoto = () => {
    if (!capturedFile) return;
    const file = capturedFile;
    setCameraMode('idle');
    setCapturedFile(null);
    setCapturedPreview(null);
    stopCamera();
    handleFile(file);
    handleAnalyze(file);
  };

  const handleAnalyze = async (fileToAnalyze?: File) => {
    const targetFile = fileToAnalyze || selectedFile;
    if (!targetFile) {
      setError(t.disease.emptyUploadPrompt);
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const result = await diseaseService.diagnoseImage(targetFile);
      setDiagnosisResult(result);
    } catch (err: any) {
      let message = 'Failed to analyze crop image. Please check your connection and try again.';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        } else if (err.response.data.detail.message) {
          message = err.response.data.detail.message;
        }
      } else if (err.message) {
        message = err.message;
      }
      setError(message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setDiagnosisResult(null);
    setPreviewImage(null);
    setSelectedFile(null);
    setError(null);
    setCameraError(null);
    setCameraMode('idle');
    setCapturedFile(null);
    setCapturedPreview(null);
    stopCamera();
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const isHealthy = Boolean(diagnosisResult?.is_healthy);
  const confidencePercent =
    diagnosisResult?.confidence != null
      ? (diagnosisResult.confidence * 100).toFixed(1)
      : null;

  return (
    <div className="farmsathi-page-container-narrow">
      {/* Header */}
      <PageHeader
        icon="photo_camera"
        title={t.disease.title}
        subtitle={t.disease.subtitle}
      />

      {/* Hidden File Input for Gallery Selection */}
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {/* Error Banner */}
      {error && (
        <div
          style={{
            backgroundColor: 'var(--color-error-bg)',
            color: 'var(--color-error)',
            border: '1px solid var(--color-error-border)',
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            fontSize: 'var(--font-size-sm)',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
            error
          </span>
          <span style={{ flex: 1 }}>{error}</span>
          <button
            type="button"
            onClick={() => setError(null)}
            style={{ color: 'var(--color-error)', cursor: 'pointer', background: 'none', border: 'none' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
              close
            </span>
          </button>
        </div>
      )}

      {!diagnosisResult ? (
        /* Image Selection & Upload Area */
        <Card padding="lg" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {previewImage ? (
            /* Selected Photo Preview */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '100%',
                  maxHeight: '340px',
                  borderRadius: 'var(--radius-lg)',
                  overflow: 'hidden',
                  position: 'relative',
                  backgroundColor: 'var(--color-header-bg, #2f3e20)',
                  boxShadow: 'var(--shadow-sm)',
                }}
              >
                <img
                  src={previewImage}
                  alt="Crop foliage preview"
                  style={{
                    width: '100%',
                    height: '100%',
                    maxHeight: '340px',
                    objectFit: 'contain',
                    display: 'block',
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', width: '100%', flexWrap: 'wrap' }}>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleReset}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      refresh
                    </span>
                  }
                >
                  {t.disease.changePhoto}
                </Button>
                <Button
                  type="button"
                  size="md"
                  onClick={() => handleAnalyze()}
                  isLoading={analyzing}
                  style={{ flex: 1 }}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      search_check
                    </span>
                  }
                >
                  {analyzing ? t.disease.diagnosing : t.disease.diagnoseButton}
                </Button>
              </div>
            </div>
          ) : cameraMode === 'streaming' ? (
            /* Live Camera Preview */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', width: '100%' }}>
              <div
                style={{
                  width: '100%',
                  maxHeight: '380px',
                  borderRadius: 'var(--radius-lg)',
                  overflow: 'hidden',
                  position: 'relative',
                  backgroundColor: 'var(--color-header-bg, #2f3e20)',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <video
                  ref={(node) => {
                    videoRef.current = node;
                    if (node && mediaStreamRef.current && node.srcObject !== mediaStreamRef.current) {
                      node.srcObject = mediaStreamRef.current;
                      node.play().catch(() => {});
                    }
                  }}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    width: '100%',
                    height: '100%',
                    maxHeight: '380px',
                    objectFit: 'contain',
                    display: 'block',
                  }}
                />

                {/* Live Webcam Status Badge */}
                <div
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    left: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    backgroundColor: 'rgba(0, 0, 0, 0.65)',
                    padding: '0.3rem 0.65rem',
                    borderRadius: 'var(--radius-full)',
                    color: '#fff',
                    fontSize: '11px',
                    fontWeight: 600,
                    letterSpacing: '0.04em',
                  }}
                >
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#ef4444',
                      display: 'inline-block',
                    }}
                  />
                  <span>LIVE WEBCAM</span>
                </div>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  width: '100%',
                }}
              >
                <Button
                  type="button"
                  size="md"
                  onClick={handleCapturePhoto}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                      photo_camera
                    </span>
                  }
                >
                  Capture Photo
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    stopCamera();
                    setCameraMode('idle');
                  }}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      close
                    </span>
                  }
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    stopCamera();
                    setCameraMode('idle');
                    fileInputRef.current?.click();
                  }}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      upload_file
                    </span>
                  }
                >
                  {t.disease.uploadPhoto}
                </Button>
              </div>
            </div>
          ) : cameraMode === 'captured' ? (
            /* Captured Image Preview */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', width: '100%' }}>
              <div
                style={{
                  width: '100%',
                  maxHeight: '380px',
                  borderRadius: 'var(--radius-lg)',
                  overflow: 'hidden',
                  position: 'relative',
                  backgroundColor: 'var(--color-header-bg, #2f3e20)',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <img
                  src={capturedPreview || ''}
                  alt="Captured crop foliage"
                  style={{
                    width: '100%',
                    height: '100%',
                    maxHeight: '380px',
                    objectFit: 'contain',
                    display: 'block',
                  }}
                />

                <div
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    left: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    backgroundColor: 'rgba(0, 0, 0, 0.65)',
                    padding: '0.3rem 0.65rem',
                    borderRadius: 'var(--radius-full)',
                    color: '#fff',
                    fontSize: '11px',
                    fontWeight: 600,
                  }}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--color-active, #889063)' }}>
                    check_circle
                  </span>
                  <span>PHOTO CAPTURED</span>
                </div>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  width: '100%',
                }}
              >
                <Button
                  type="button"
                  size="md"
                  onClick={handleUseCapturedPhoto}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      check
                    </span>
                  }
                >
                  Use Photo
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={startCamera}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      replay
                    </span>
                  }
                >
                  Retake
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setCameraMode('idle');
                    setCapturedFile(null);
                    setCapturedPreview(null);
                    fileInputRef.current?.click();
                  }}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      upload_file
                    </span>
                  }
                >
                  {t.disease.uploadPhoto}
                </Button>
              </div>
            </div>
          ) : cameraError ? (
            /* Camera Permission / Availability Fallback Notice */
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                padding: '2.5rem 1.5rem',
                border: '2px dashed var(--color-border)',
                borderRadius: 'var(--radius-xl)',
                backgroundColor: 'var(--color-surface-container-low)',
                gap: '1rem',
              }}
            >
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-error-bg)',
                  color: 'var(--color-error)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '32px' }}>
                  videocam_off
                </span>
              </div>

              <div>
                <h3
                  style={{
                    fontSize: 'var(--font-size-base)',
                    fontWeight: 700,
                    color: 'var(--color-text-primary)',
                    margin: '0 0 0.25rem 0',
                  }}
                >
                  {cameraError.type === 'denied'
                    ? 'Camera Permission Needed'
                    : 'Camera Unavailable'}
                </h3>
                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    maxWidth: '420px',
                    margin: '0 auto',
                    lineHeight: 1.45,
                  }}
                >
                  {cameraError.message}
                </p>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  marginTop: '0.5rem',
                }}
              >
                {cameraError.type !== 'unavailable' && (
                  <Button
                    type="button"
                    onClick={startCamera}
                    leftIcon={
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                        refresh
                      </span>
                    }
                  >
                    Retry Camera
                  </Button>
                )}
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setCameraError(null);
                    fileInputRef.current?.click();
                  }}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      upload_file
                    </span>
                  }
                >
                  {t.disease.uploadPhoto}
                </Button>
              </div>
            </div>
          ) : (
            /* Upload Drop Area */
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                padding: '2.5rem 1.5rem',
                border: '2px dashed var(--color-border)',
                borderRadius: 'var(--radius-xl)',
                backgroundColor: 'var(--color-surface-container-low)',
                gap: '1rem',
              }}
            >
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-primary-light)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '32px' }}>
                  add_a_photo
                </span>
              </div>

              <div>
                <h3
                  style={{
                    fontSize: 'var(--font-size-base)',
                    fontWeight: 700,
                    color: 'var(--color-text-primary)',
                    margin: '0 0 0.25rem 0',
                  }}
                >
                  Capture or Upload Crop Foliage
                </h3>
                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    maxWidth: '380px',
                    margin: '0 auto',
                    lineHeight: 1.45,
                  }}
                >
                  Take a sharp, close-up photograph of the affected leaf in clear sunlight for high-precision diagnosis.
                </p>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  marginTop: '0.5rem',
                }}
              >
                <Button
                  type="button"
                  onClick={startCamera}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      photo_camera
                    </span>
                  }
                >
                  {t.disease.takePhoto}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  leftIcon={
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                      upload_file
                    </span>
                  }
                >
                  {t.disease.uploadPhoto}
                </Button>
              </div>
            </div>
          )}
        </Card>
      ) : diagnosisResult.is_suitable === false ? (
        /* Unsuitable Image Result Presentation */
        <Card
          padding="lg"
          style={{
            border: '2px dashed var(--color-warning-border, #f59e0b)',
            backgroundColor: 'var(--color-surface-container-low)',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '2.5rem 1.5rem',
              gap: '1.25rem',
            }}
          >
            <div
              style={{
                width: '68px',
                height: '68px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                color: '#d97706',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '36px' }}>
                image_not_supported
              </span>
            </div>

            <div>
              <h2
                style={{
                  fontFamily: 'var(--font-secondary)',
                  fontSize: 'var(--font-size-xl)',
                  fontWeight: 800,
                  margin: '0 0 0.5rem 0',
                  color: 'var(--color-text-primary)',
                }}
              >
                {t.disease.unsuitableTitle || 'Image not suitable for crop disease detection'}
              </h2>
              <p
                style={{
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--color-text-secondary)',
                  maxWidth: '460px',
                  margin: '0 auto',
                  lineHeight: 1.5,
                }}
              >
                {diagnosisResult.suitability_message ||
                  t.disease.unsuitablePrompt ||
                  'Please capture or upload a clear close-up photograph of an affected crop leaf.'}
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                flexWrap: 'wrap',
                justifyContent: 'center',
                marginTop: '0.5rem',
              }}
            >
              <Button
                type="button"
                size="md"
                onClick={() => {
                  handleReset();
                  startCamera();
                }}
                leftIcon={
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                    photo_camera
                  </span>
                }
              >
                {t.disease.retakePhoto || 'Retake Photo'}
              </Button>
              <Button
                type="button"
                variant="outline"
                size="md"
                onClick={() => {
                  handleReset();
                  fileInputRef.current?.click();
                }}
                leftIcon={
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                    upload_file
                  </span>
                }
              >
                {t.disease.uploadPhoto || 'Upload from Gallery'}
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        /* Diagnostic Result Presentation */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Card padding="lg" style={{ border: `2px solid ${isHealthy ? 'var(--color-success-border)' : 'var(--color-primary-subtle)'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span
                  className="material-symbols-outlined"
                  style={{
                    fontSize: '28px',
                    color: isHealthy ? 'var(--color-success)' : 'var(--color-error)',
                    fontVariationSettings: "'FILL' 1",
                  }}
                >
                  {isHealthy ? 'check_circle' : 'warning'}
                </span>
                <h2 style={{ fontFamily: 'var(--font-secondary)', fontSize: 'var(--font-size-xl)', fontWeight: 800, margin: 0 }}>
                  {diagnosisResult.display_name || (isHealthy ? t.disease.healthyFoliage : t.disease.diseaseDetected)}
                </h2>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Badge variant={isHealthy ? 'success' : 'warning'} size="md">
                  {isHealthy ? 'Healthy Foliage' : 'Pathogen Detected'}
                </Badge>
                {confidencePercent && (
                  <Badge variant="primary" size="md">
                    {confidencePercent}% {t.disease.confidenceLabel}
                  </Badge>
                )}
              </div>
            </div>

            {/* Uncertainty Notice for Low-Confidence Crop Leaf */}
            {diagnosisResult.uncertainty_notice && (
              <div
                style={{
                  backgroundColor: 'rgba(245, 158, 11, 0.12)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.75rem 1rem',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  marginBottom: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '18px', color: '#d97706' }}>
                  info
                </span>
                <span>{diagnosisResult.uncertainty_notice}</span>
              </div>
            )}

            {/* Crop Type Info */}
            {diagnosisResult.crop && (
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: '1.25rem' }}>
                <strong>{t.disease.cropDetected}:</strong>{' '}
                <span style={{ textTransform: 'capitalize', color: 'var(--color-text-primary)', fontWeight: 600 }}>
                  {diagnosisResult.crop}
                </span>
                {diagnosisResult.condition && (
                  <span style={{ marginLeft: '0.75rem', color: 'var(--color-text-tertiary)' }}>
                    • Condition: <strong style={{ color: 'var(--color-text-primary)' }}>{diagnosisResult.condition}</strong>
                  </span>
                )}
              </div>
            )}

            {/* Management Guidance & Cultural Practices */}
            {diagnosisResult.management_guidance?.cultural_practices && diagnosisResult.management_guidance.cultural_practices.length > 0 && (
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-low)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '1rem',
                  border: '1px solid var(--color-border-subtle)',
                  marginBottom: '1rem',
                }}
              >
                <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--color-primary)' }}>
                  {t.disease.culturalPractices || 'Cultural Practices & Management'}
                </h4>
                <ul style={{ paddingLeft: '1.25rem', margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                  {diagnosisResult.management_guidance.cultural_practices.map((practice, idx) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>{practice}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Prevention & Sanitation Actions */}
            {diagnosisResult.management_guidance?.prevention && diagnosisResult.management_guidance.prevention.length > 0 && (
              <div
                style={{
                  backgroundColor: 'var(--color-primary-light)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '1rem',
                  border: '1px solid var(--color-primary-subtle)',
                  marginBottom: '1.25rem',
                }}
              >
                <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--color-primary)' }}>
                  {t.disease.prevention || 'Prevention Steps'}
                </h4>
                <ul style={{ paddingLeft: '1.25rem', margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-text-primary)' }}>
                  {diagnosisResult.management_guidance.prevention.map((step, idx) => (
                    <li key={idx} style={{ marginBottom: '0.25rem' }}>{step}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimer */}
            <p style={{ fontSize: '11px', color: 'var(--color-text-muted)', margin: '0 0 1.25rem 0', lineHeight: 1.4 }}>
              ⚠️ {t.disease.disclaimer}
            </p>

            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              leftIcon={
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                  refresh
                </span>
              }
            >
              {t.disease.scanAnother}
            </Button>
          </Card>
        </div>
      )}
    </div>
  );
};
