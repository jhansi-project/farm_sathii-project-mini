import React, { useState, useRef, useEffect } from 'react';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../stores/authStore';
import { authService } from '../../services/authService';
import {
  validateFullName,
  validateEmailOrPhone,
  validatePassword,
} from './authValidation';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Field interaction tracking to prevent premature error messages
  const [touched, setTouched] = useState<{
    fullName: boolean;
    emailOrPhone: boolean;
    password: boolean;
  }>({
    fullName: false,
    emailOrPhone: false,
    password: false,
  });
  const [hasSubmitted, setHasSubmitted] = useState(false);

  // Focus management refs for first invalid field
  const fullNameRef = useRef<HTMLInputElement>(null);
  const emailOrPhoneRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const { setAuth } = useAuthStore();

  // Reset errors and touch state whenever modal opens or closes
  useEffect(() => {
    if (isOpen) {
      setErrorMsg(null);
      setHasSubmitted(false);
      setTouched({ fullName: false, emailOrPhone: false, password: false });
    }
  }, [isOpen]);

  // Derived validation results
  const fullNameError = isRegisterMode ? validateFullName(fullName) : null;
  const identifierResult = validateEmailOrPhone(emailOrPhone);
  const passwordError = isRegisterMode
    ? validatePassword(password)
    : !password
    ? 'Please enter your password.'
    : null;

  // Inline error strings only displayed after meaningful interaction or submit attempt
  const displayedFullNameError =
    isRegisterMode && (touched.fullName || hasSubmitted)
      ? fullNameError || undefined
      : undefined;

  const displayedIdentifierError =
    (touched.emailOrPhone || hasSubmitted)
      ? identifierResult.error || undefined
      : undefined;

  const displayedPasswordError =
    (touched.password || hasSubmitted)
      ? passwordError || undefined
      : undefined;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    // Prevent duplicate submissions while an active request is in flight
    if (isLoading) return;

    if (isRegisterMode) {
      setHasSubmitted(true);
      setTouched({ fullName: true, emailOrPhone: true, password: true });

      // Check all fields before API submission
      if (fullNameError) {
        fullNameRef.current?.focus();
        return;
      }

      if (identifierResult.error) {
        emailOrPhoneRef.current?.focus();
        return;
      }

      if (passwordError) {
        passwordRef.current?.focus();
        return;
      }

      setIsLoading(true);

      try {
        const tokenData = await authService.register({
          full_name: fullName.trim(),
          email: identifierResult.type === 'email' ? identifierResult.value : undefined,
          phone: identifierResult.type === 'phone' ? identifierResult.value : undefined,
          password, // Never silently alter the user's intended password
        });
        setAuth(tokenData);
        onClose();
      } catch (err: any) {
        setErrorMsg(
          err.response?.data?.detail ||
            'Registration failed. Please check your details.'
        );
      } finally {
        setIsLoading(false);
      }
    } else {
      // Login mode validation
      setHasSubmitted(true);
      setTouched((prev) => ({ ...prev, emailOrPhone: true, password: true }));

      if (!emailOrPhone.trim()) {
        emailOrPhoneRef.current?.focus();
        return;
      }

      if (!password) {
        passwordRef.current?.focus();
        return;
      }

      setIsLoading(true);

      try {
        const tokenData = await authService.login({
          identifier: emailOrPhone.trim(),
          password,
        });
        setAuth(tokenData);
        onClose();
      } catch (err: any) {
        setErrorMsg(
          err.response?.data?.detail ||
            'Login failed. Please check your credentials.'
        );
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleToggleMode = () => {
    setIsRegisterMode((prev) => !prev);
    setErrorMsg(null);
    setHasSubmitted(false);
    setTouched({ fullName: false, emailOrPhone: false, password: false });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isRegisterMode ? 'Sign Up for FarmSathi' : 'Farmer Login'}
    >
      {/* Brand Icon Header */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '1.25rem' }}>
        <img
          src="/assets/farmsathi_logo.png"
          alt="FarmSathi"
          style={{
            height: '46px',
            width: 'auto',
            maxWidth: '180px',
            objectFit: 'contain',
            borderRadius: 'var(--radius-md)',
            marginBottom: '0.65rem',
            display: 'block',
            boxShadow: 'var(--shadow-sm)',
          }}
        />
        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', textAlign: 'center', margin: 0, lineHeight: 1.4 }}>
          {isRegisterMode
            ? 'Create your free farmer account to save crop records & advisories'
            : 'Access your personalized farm guidance and history'}
        </p>
      </div>

      {errorMsg && (
        <div
          role="alert"
          style={{
            backgroundColor: 'var(--color-error-bg)',
            color: 'var(--color-error)',
            border: '1px solid var(--color-error-border)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: 'var(--font-size-sm)',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '18px', flexShrink: 0 }}>
            error
          </span>
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {isRegisterMode && (
          <Input
            ref={fullNameRef}
            id="register-fullname"
            label="Full Name"
            placeholder="e.g. Ramesh Kumar"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            onBlur={() => setTouched((prev) => ({ ...prev, fullName: true }))}
            error={displayedFullNameError}
            required
            autoFocus
          />
        )}

        <Input
          ref={emailOrPhoneRef}
          id="auth-email-or-phone"
          label="Email or Mobile Number"
          placeholder="farmer@example.com or 9876543210"
          value={emailOrPhone}
          onChange={(e) => setEmailOrPhone(e.target.value)}
          onBlur={() => setTouched((prev) => ({ ...prev, emailOrPhone: true }))}
          error={displayedIdentifierError}
          required
        />

        <Input
          ref={passwordRef}
          id="auth-password"
          label="Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Enter your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouched((prev) => ({ ...prev, password: true }))}
          error={displayedPasswordError}
          required
          rightIcon={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-text-tertiary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                padding: '0',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                {showPassword ? 'visibility' : 'visibility_off'}
              </span>
            </button>
          }
        />

        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth
          isLoading={isLoading}
          disabled={isLoading}
          style={{ marginTop: '0.5rem' }}
        >
          {isRegisterMode ? 'Complete Registration' : 'Sign In'}
        </Button>

        <Button
          type="button"
          variant="ghost"
          size="sm"
          fullWidth
          onClick={handleToggleMode}
          style={{ color: 'var(--color-primary)', fontWeight: 600 }}
        >
          {isRegisterMode ? 'Already have an account? Sign In' : 'Need an account? Sign Up with Email'}
        </Button>
      </form>
    </Modal>
  );
};
