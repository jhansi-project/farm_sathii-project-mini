import { useState, useRef, useCallback, useEffect } from 'react';

export type VoiceState =
  | 'idle'
  | 'listening'
  | 'processing'
  | 'recognized'
  | 'permission_denied'
  | 'unsupported'
  | 'error';

export const LANGUAGE_SPEECH_LOCALES: Record<string, string> = {
  en: 'en-IN',
  te: 'te-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
  mr: 'mr-IN',
};

export interface UseSpeechRecognitionOptions {
  onTranscriptChange?: (text: string) => void;
  onFinalTranscript?: (text: string) => void;
}

export const useSpeechRecognition = (options: UseSpeechRecognitionOptions = {}) => {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [transcript, setTranscript] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const activeSessionIdRef = useRef<number>(0);
  const baseTextRef = useRef<string>('');
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Check browser support
  const isSupported =
    typeof window !== 'undefined' &&
    Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

  const cleanupInstance = (instance: any) => {
    if (!instance) return;
    try {
      instance.onstart = null;
      instance.onaudiostart = null;
      instance.onspeechstart = null;
      instance.onspeechend = null;
      instance.onresult = null;
      instance.onerror = null;
      instance.onend = null;
      instance.abort();
    } catch {
      // Ignore abort errors on stale instance
    }
  };

  const stopListening = useCallback(() => {
    activeSessionIdRef.current += 1;
    if (recognitionRef.current) {
      const instance = recognitionRef.current;
      recognitionRef.current = null;
      try {
        instance.onstart = null;
        instance.onaudiostart = null;
        instance.onspeechstart = null;
        instance.onspeechend = null;
        instance.onresult = null;
        instance.onerror = null;
        instance.onend = null;
        instance.stop();
      } catch {
        // Ignore stop error
      }
    }
    setVoiceState('idle');
  }, []);

  const startListening = useCallback(
    (langCode = 'en', baseText = '') => {
      setErrorMessage(null);

      if (!isSupported) {
        setVoiceState('unsupported');
        setErrorMessage(
          'Voice input is not supported in this browser. Please use Chrome, Edge, or enter text manually.'
        );
        return;
      }

      // Invalidate any previously running session and cleanup old instance
      activeSessionIdRef.current += 1;
      const sessionId = activeSessionIdRef.current;
      baseTextRef.current = baseText.trim();

      if (recognitionRef.current) {
        cleanupInstance(recognitionRef.current);
        recognitionRef.current = null;
      }

      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      try {
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;

        const locale = LANGUAGE_SPEECH_LOCALES[langCode.toLowerCase()] || 'en-IN';
        recognition.lang = locale;
        recognition.continuous = false; // Stop cleanly when farmer finishes speaking
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
          if (activeSessionIdRef.current !== sessionId) return;
          setVoiceState('listening');
          setErrorMessage(null);
        };

        recognition.onaudiostart = () => {
          if (activeSessionIdRef.current !== sessionId) return;
          setVoiceState('listening');
        };

        recognition.onspeechstart = () => {
          if (activeSessionIdRef.current !== sessionId) return;
          setVoiceState('listening');
        };

        recognition.onspeechend = () => {
          if (activeSessionIdRef.current !== sessionId) return;
          setVoiceState('processing');
        };

        recognition.onresult = (event: any) => {
          if (activeSessionIdRef.current !== sessionId) return;

          let sessionFinal = '';
          let sessionInterim = '';

          // Reconstruct entire session transcript from event.results to guarantee idempotence
          for (let i = 0; i < event.results.length; i++) {
            const item = event.results[i];
            if (item && item[0]) {
              const textChunk = (item[0].transcript || '').trim();
              if (item.isFinal) {
                sessionFinal += (sessionFinal ? ' ' : '') + textChunk;
              } else {
                sessionInterim += (sessionInterim ? ' ' : '') + textChunk;
              }
            }
          }

          const sessionSpeech = [sessionFinal, sessionInterim].filter(Boolean).join(' ').trim();
          const base = baseTextRef.current;
          const currentFullText = base ? `${base} ${sessionSpeech}`.trim() : sessionSpeech;

          if (currentFullText) {
            setTranscript(currentFullText);
            optionsRef.current.onTranscriptChange?.(currentFullText);
          }

          if (sessionFinal.trim()) {
            const finalFullText = base ? `${base} ${sessionFinal.trim()}`.trim() : sessionFinal.trim();
            setVoiceState('processing');
            optionsRef.current.onFinalTranscript?.(finalFullText);
          }
        };

        recognition.onerror = (event: any) => {
          if (activeSessionIdRef.current !== sessionId) return;
          if (event.error === 'aborted') {
            // Programmatically stopped or aborted - not an error
            return;
          }
          recognitionRef.current = null;
          const errType = event.error;

          if (errType === 'not-allowed' || errType === 'service-not-allowed') {
            setVoiceState('permission_denied');
            setErrorMessage(
              'Microphone access was denied. Please allow microphone permission in your browser settings to speak your question.'
            );
          } else if (errType === 'no-speech') {
            setVoiceState('error');
            setErrorMessage('No speech detected. Please tap the microphone and try speaking again.');
          } else if (errType === 'network') {
            setVoiceState('error');
            setErrorMessage(
              'Network connection error during speech recognition. Please retry or type your query.'
            );
          } else {
            setVoiceState('error');
            setErrorMessage(
              `Speech recognition encountered an issue (${errType}). Please try again or type.`
            );
          }
        };

        recognition.onend = () => {
          if (activeSessionIdRef.current !== sessionId) return;
          recognitionRef.current = null;
          setVoiceState('idle');
        };

        recognition.start();
      } catch (err: any) {
        activeSessionIdRef.current += 1;
        setVoiceState('error');
        setErrorMessage('Could not initialize speech recognition. Please type your question.');
        recognitionRef.current = null;
      }
    },
    [isSupported]
  );

  const resetState = useCallback(() => {
    stopListening();
    baseTextRef.current = '';
    setVoiceState('idle');
    setTranscript('');
    setErrorMessage(null);
  }, [stopListening]);

  // Clean up completely on unmount
  useEffect(() => {
    return () => {
      activeSessionIdRef.current += 1;
      if (recognitionRef.current) {
        cleanupInstance(recognitionRef.current);
        recognitionRef.current = null;
      }
    };
  }, []);

  return {
    voiceState,
    transcript,
    errorMessage,
    isSupported,
    startListening,
    stopListening,
    resetState,
    setVoiceState,
  };
};
