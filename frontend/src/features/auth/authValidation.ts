/**
 * Frontend Validation Rules for FarmSathi Authentication & Registration
 *
 * Enforces field validation rules matching backend schema contracts:
 * - Full Name: Required, alphabetic names, Indian name support, initials, hyphens/apostrophes.
 *   Rejects numbers, arbitrary symbols, empty values.
 * - Email or Mobile Number: EITHER a valid email address OR a valid Indian mobile number (10 digits, +91).
 *   Rejects short digits ("26323", "123"), arbitrary alphabetic text ("abcdef"), symbols ("@@@"), invalid lengths.
 * - Password: Minimum 6 chars, rejects numeric-only passwords ("21332133"), rejects empty.
 */

export interface IdentifierValidationResult {
  error: string | null;
  type?: 'email' | 'phone';
  value?: string;
}

/**
 * Validates Farmer Full Name.
 *
 * Rules:
 * - Required.
 * - Leading/trailing whitespace trimmed.
 * - Length between 2 and 100 characters.
 * - Reject numbers (0-9).
 * - Reject arbitrary special characters / symbols.
 * - Accept normal alphabetic characters, spaces, initials with periods, apostrophes, and hyphens.
 * - Must contain at least 2 letters.
 * - Must start with a letter.
 * - Avoid overly restrictive validation that would reject legitimate Indian names.
 */
export function validateFullName(name: string): string | null {
  const trimmed = name.trim();
  if (!trimmed) {
    return 'Please enter a valid full name.';
  }

  if (trimmed.length < 2 || trimmed.length > 100) {
    return 'Please enter a valid full name.';
  }

  // Reject if it contains any numbers
  if (/\d/.test(trimmed)) {
    return 'Please enter a valid full name.';
  }

  // Allowed characters: Latin letters, accented letters, Devanagari/Indian scripts, spaces, '.', "'", '-'
  const allowedCharRegex = /^[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F\s.'-]+$/;
  if (!allowedCharRegex.test(trimmed)) {
    return 'Please enter a valid full name.';
  }

  // Must start with an alphabetic character
  if (!/^[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F]/.test(trimmed)) {
    return 'Please enter a valid full name.';
  }

  // Must contain at least 2 alphabetic letters
  const letters = trimmed.match(/[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F]/g);
  if (!letters || letters.length < 2) {
    return 'Please enter a valid full name.';
  }

  // Reject consecutive punctuation (e.g. '..', '--', '\'\'')
  if (/[.'-]{2,}/.test(trimmed)) {
    return 'Please enter a valid full name.';
  }

  return null;
}

/**
 * Validates Email or Indian Mobile Number.
 *
 * Rules:
 * - Required.
 * - If input contains '@', validates as email.
 *   - Must be properly formatted with local part, domain, and valid TLD (.com, .org, etc.).
 *   - Rejects "abc", "abc@", "@gmail.com", "abc@gmail".
 * - If input does not contain '@', validates as Indian mobile number.
 *   - 10 digits starting with 6, 7, 8, 9.
 *   - Supports optional +91, 91, or 0 country prefix with optional space/hyphen.
 *   - Rejects "26323", "123", "abcdef", "@@@", invalid-length numbers.
 */
export function validateEmailOrPhone(input: string): IdentifierValidationResult {
  const trimmed = input.trim();
  if (!trimmed) {
    return { error: 'Please enter a valid email address or mobile number.' };
  }

  if (trimmed.includes('@')) {
    // Email validation
    const emailRegex =
      /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;

    if (!emailRegex.test(trimmed)) {
      return { error: 'Please enter a valid email address or mobile number.' };
    }

    return { error: null, type: 'email', value: trimmed };
  }

  // Mobile number validation (Indian mobile format)
  // Allows optional prefix: +91, 91, 0 followed by 10 digits starting with 6-9
  const indianPhoneRegex = /^(?:\+91[-\s]?|91[-\s]|0)?[6-9]\d{9}$/;

  if (!indianPhoneRegex.test(trimmed)) {
    return { error: 'Please enter a valid email address or mobile number.' };
  }

  // Normalize phone formatting: remove spaces/hyphens while preserving country code
  const normalizedPhone = trimmed.replace(/[\s-]/g, '');
  return { error: null, type: 'phone', value: normalizedPhone };
}

/**
 * Validates Password.
 *
 * Rules:
 * - Required.
 * - Minimum 6 characters (matching backend policy min_length=6), maximum 128 characters.
 * - Must NOT be numeric-only (e.g. rejects "21332133", "123456").
 * - Does NOT silently modify the user's actual password.
 * - Does NOT display the password in error messages.
 */
export function validatePassword(password: string): string | null {
  if (!password || password.trim().length === 0) {
    return 'Password does not meet the required security requirements.';
  }

  if (password.length < 6 || password.length > 128) {
    return 'Password does not meet the required security requirements.';
  }

  // Reject passwords consisting only of numbers (e.g. "21332133")
  if (/^\d+$/.test(password)) {
    return 'Password does not meet the required security requirements.';
  }

  return null;
}
