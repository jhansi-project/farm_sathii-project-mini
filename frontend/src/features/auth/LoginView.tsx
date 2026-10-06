import React, { useState, useRef } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { authService } from '../../services/authService';
import {
  validateFullName,
  validateEmailOrPhone,
  validatePassword,
} from './authValidation';

interface LoginViewProps {
  onSuccess: () => void;
  onBack?: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onSuccess, onBack }) => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [socialNotice, setSocialNotice] = useState<string | null>(null);

  // Field interaction tracking
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

  const fullNameRef = useRef<HTMLInputElement>(null);
  const emailOrPhoneRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const { setAuth } = useAuthStore();

  const fullNameError = isRegisterMode ? validateFullName(fullName) : null;
  const identifierResult = validateEmailOrPhone(emailOrPhone);
  const passwordError = isRegisterMode
    ? validatePassword(password)
    : !password
    ? 'Please enter your password.'
    : null;

  const displayedFullNameError =
    isRegisterMode && (touched.fullName || hasSubmitted)
      ? fullNameError || undefined
      : undefined;

  const displayedIdentifierError =
    touched.emailOrPhone || hasSubmitted
      ? identifierResult.error || undefined
      : undefined;

  const displayedPasswordError =
    touched.password || hasSubmitted
      ? passwordError || undefined
      : undefined;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSocialNotice(null);

    if (isLoading) return;

    if (isRegisterMode) {
      setHasSubmitted(true);
      setTouched({ fullName: true, emailOrPhone: true, password: true });

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
          password,
        });
        setAuth(tokenData);
        onSuccess();
      } catch (err: any) {
        setErrorMsg(
          err.response?.data?.detail ||
            'Registration failed. Please verify your details.'
        );
      } finally {
        setIsLoading(false);
      }
    } else {
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
        onSuccess();
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

  const handleGoogleClick = () => {
    setSocialNotice(
      'Google federated authentication is not currently configured on this local instance. Please sign in or register with your email or mobile number.'
    );
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-background)',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '1.5rem 1rem',
      }}
    >
      <main
        style={{
          width: '100%',
          maxWidth: '440px',
          display: 'flex',
          flexDirection: 'column',
          flex: 1,
        }}
      >
        {/* Navigation Back if present */}
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            style={{
              alignSelf: 'flex-start',
              padding: '0.5rem',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              borderRadius: 'var(--radius-full)',
            }}
          >
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
        )}

        {/* Branding Header */}
        <header
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '1.5rem 0',
          }}
        >
          <img
            src="/assets/farmsathi_logo.png"
            alt="FarmSathi"
            style={{
              height: '56px',
              width: 'auto',
              maxWidth: '220px',
              objectFit: 'contain',
              borderRadius: 'var(--radius-lg)',
              display: 'block',
              boxShadow: 'var(--shadow-sm)',
            }}
          />
        </header>

        {/* Welcome Section */}
        <section style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h2
            style={{
              fontSize: 'var(--font-size-xl)',
              fontWeight: 600,
              color: 'var(--color-on-surface)',
              marginBottom: '0.25rem',
            }}
          >
            {isRegisterMode ? 'Create Farmer Account' : 'Login or Sign Up'}
          </h2>
          <p
            style={{
              fontSize: 'var(--font-size-base)',
              color: 'var(--color-on-surface-variant)',
            }}
          >
            {isRegisterMode
              ? 'Join FarmSathi for tailored agricultural guidance.'
              : 'Use your email or phone to access your personalized farm guidance.'}
          </p>
        </section>

        {/* Alerts */}
        {errorMsg && (
          <div
            style={{
              backgroundColor: 'var(--color-error-container)',
              color: 'var(--color-on-error-container)',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 500,
              marginBottom: '1rem',
            }}
          >
            {errorMsg}
          </div>
        )}

        {socialNotice && (
          <div
            style={{
              backgroundColor: 'var(--color-surface-container-low)',
              color: 'var(--color-on-surface-variant)',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-xs)',
              marginBottom: '1rem',
              border: '1px solid var(--color-outline-variant)',
            }}
          >
            {socialNotice}
          </div>
        )}

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            flex: 1,
          }}
        >
          {isRegisterMode && (
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <label
                htmlFor="login-fullname"
                style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: 600,
                  color: 'var(--color-on-surface)',
                  marginBottom: '0.25rem',
                  marginLeft: '0.25rem',
                }}
              >
                Farmer Full Name
              </label>
              <div style={{ position: 'relative' }}>
                <span
                  style={{
                    position: 'absolute',
                    top: 0,
                    bottom: 0,
                    left: 0,
                    display: 'flex',
                    alignItems: 'center',
                    paddingLeft: '0.75rem',
                    pointerEvents: 'none',
                    color: 'var(--color-outline)',
                  }}
                >
                  <span className="material-symbols-outlined">person</span>
                </span>
                <input
                  ref={fullNameRef}
                  id="login-fullname"
                  type="text"
                  placeholder="e.g. Ramesh Kumar"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  onBlur={() => setTouched((prev) => ({ ...prev, fullName: true }))}
                  required
                  style={{
                    width: '100%',
                    height: '56px',
                    paddingLeft: '44px',
                    paddingRight: '0.75rem',
                    borderRadius: 'var(--radius-md)',
                    border: displayedFullNameError
                      ? '2px solid var(--color-error)'
                      : '2px solid var(--color-outline-variant)',
                    backgroundColor: 'var(--color-surface-container-lowest)',
                    color: 'var(--color-on-surface)',
                    fontSize: 'var(--font-size-base)',
                    outline: 'none',
                  }}
                />
              </div>
              {displayedFullNameError && (
                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-error)', marginTop: '0.25rem', marginLeft: '0.25rem' }}>
                  {displayedFullNameError}
                </span>
              )}
            </div>
          )}

          {/* Email / Identifier */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label
              htmlFor="login-identifier"
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 600,
                color: 'var(--color-on-surface)',
                marginBottom: '0.25rem',
                marginLeft: '0.25rem',
              }}
            >
              Email Address or Phone
            </label>
            <div style={{ position: 'relative' }}>
              <span
                style={{
                  position: 'absolute',
                  top: 0,
                  bottom: 0,
                  left: 0,
                  display: 'flex',
                  alignItems: 'center',
                  paddingLeft: '0.75rem',
                  pointerEvents: 'none',
                  color: 'var(--color-outline)',
                }}
              >
                <span className="material-symbols-outlined">mail</span>
              </span>
              <input
                ref={emailOrPhoneRef}
                id="login-identifier"
                type="text"
                placeholder="farmer@example.com or +919876543210"
                value={emailOrPhone}
                onChange={(e) => setEmailOrPhone(e.target.value)}
                onBlur={() => setTouched((prev) => ({ ...prev, emailOrPhone: true }))}
                required
                style={{
                  width: '100%',
                  height: '56px',
                  paddingLeft: '44px',
                  paddingRight: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  border: displayedIdentifierError
                    ? '2px solid var(--color-error)'
                    : '2px solid var(--color-outline-variant)',
                  backgroundColor: 'var(--color-surface-container-lowest)',
                  color: 'var(--color-on-surface)',
                  fontSize: 'var(--font-size-base)',
                  outline: 'none',
                }}
              />
            </div>
            {displayedIdentifierError && (
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-error)', marginTop: '0.25rem', marginLeft: '0.25rem' }}>
                {displayedIdentifierError}
              </span>
            )}
          </div>

          {/* Password */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label
              htmlFor="login-password"
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 600,
                color: 'var(--color-on-surface)',
                marginBottom: '0.25rem',
                marginLeft: '0.25rem',
              }}
            >
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <span
                style={{
                  position: 'absolute',
                  top: 0,
                  bottom: 0,
                  left: 0,
                  display: 'flex',
                  alignItems: 'center',
                  paddingLeft: '0.75rem',
                  pointerEvents: 'none',
                  color: 'var(--color-outline)',
                }}
              >
                <span className="material-symbols-outlined">lock</span>
              </span>
              <input
                ref={passwordRef}
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={() => setTouched((prev) => ({ ...prev, password: true }))}
                required
                style={{
                  width: '100%',
                  height: '56px',
                  paddingLeft: '44px',
                  paddingRight: '48px',
                  borderRadius: 'var(--radius-md)',
                  border: displayedPasswordError
                    ? '2px solid var(--color-error)'
                    : '2px solid var(--color-outline-variant)',
                  backgroundColor: 'var(--color-surface-container-lowest)',
                  color: 'var(--color-on-surface)',
                  fontSize: 'var(--font-size-base)',
                  outline: 'none',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label="Toggle password visibility"
                style={{
                  position: 'absolute',
                  top: 0,
                  bottom: 0,
                  right: 0,
                  display: 'flex',
                  alignItems: 'center',
                  paddingRight: '0.75rem',
                  color: 'var(--color-outline)',
                }}
              >
                <span className="material-symbols-outlined">
                  {showPassword ? 'visibility' : 'visibility_off'}
                </span>
              </button>
            </div>
            {displayedPasswordError && (
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-error)', marginTop: '0.25rem', marginLeft: '0.25rem' }}>
                {displayedPasswordError}
              </span>
            )}
            {!isRegisterMode && (
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <a
                  href="#forgot"
                  onClick={(e) => {
                    e.preventDefault();
                    setSocialNotice('Password reset flow: please contact your local agricultural extension officer or administrator.');
                  }}
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: 600,
                    color: 'var(--color-primary)',
                  }}
                >
                  Forgot Password?
                </a>
              </div>
            )}
          </div>

          {/* Primary Action Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                height: '56px',
                backgroundColor: 'var(--color-primary)',
                color: 'var(--color-text-inverse)',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-sm)',
                opacity: isLoading ? 0.7 : 1,
              }}
            >
              {isLoading
                ? 'Processing...'
                : isRegisterMode
                ? 'Complete Registration'
                : 'Login'}
            </button>

            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setErrorMsg(null);
                setSocialNotice(null);
                setHasSubmitted(false);
                setTouched({ fullName: false, emailOrPhone: false, password: false });
              }}
              style={{
                width: '100%',
                height: '56px',
                backgroundColor: 'var(--color-surface-container-lowest)',
                border: '2px solid var(--color-primary)',
                color: 'var(--color-primary)',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {isRegisterMode ? 'Already have an account? Login' : 'Sign Up with Email'}
            </button>
          </div>

          {/* Divider */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              margin: '1.25rem 0',
            }}
          >
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-outline-variant)' }} />
            <span
              style={{
                padding: '0 0.75rem',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 500,
                color: 'var(--color-outline)',
              }}
            >
              OR
            </span>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-outline-variant)' }} />
          </div>

          {/* Social Google Action */}
          <button
            type="button"
            onClick={handleGoogleClick}
            style={{
              width: '100%',
              height: '56px',
              backgroundColor: 'var(--color-surface-container-lowest)',
              border: '1px solid var(--color-outline-variant)',
              color: 'var(--color-on-surface)',
              borderRadius: 'var(--radius-full)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuCesu3IK9PyM9WsC7PQQsNQCPK4JR_DZc4vo86MryN-2YTCptOEMYH7owd9FbVBmirFa2TMUGKgHhayFfp7OSZFgqHo7qYaadUIZknK_zmZCN_7Y6PpmrU8gQ3AB4qbQzJK4RzcJUY7xPssXuzySDMth2oGB6O245lX7E3NBhbSLA_lzRNqTHHnJata3TM9GS1hZ4LxojOhM4Ke6JGvwSLW7_leFoBw5R4y0MubHf1ESV68LRRARf57"
              alt="Google G"
              style={{ width: '22px', height: '22px' }}
            />
            <span>Continue with Google</span>
          </button>
        </form>
      </main>
    </div>
  );
};
