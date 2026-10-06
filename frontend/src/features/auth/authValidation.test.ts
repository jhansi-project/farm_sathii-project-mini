import assert from 'node:assert/strict';
import {
  validateFullName,
  validateEmailOrPhone,
  validatePassword,
} from './authValidation.ts';

console.log('--- Testing FarmSathi Signup Form Validation ---');

// ==========================================
// 1. FULL NAME TEST CASES
// ==========================================
console.log('Testing Full Name Validation...');

// Valid cases from prompt
assert.equal(validateFullName('Jhansi'), null, 'Valid name: Jhansi');
assert.equal(validateFullName('Jhansi Reddy'), null, 'Valid name: Jhansi Reddy');
assert.equal(validateFullName('A. Kumar'), null, 'Valid name with initial: A. Kumar');
assert.equal(validateFullName("O'Connor"), null, "Valid apostrophe name: O'Connor");
assert.equal(validateFullName('Mary-Jane'), null, 'Valid hyphen name: Mary-Jane');
assert.equal(validateFullName('K. V. Raman'), null, 'Valid multiple initials: K. V. Raman');
assert.equal(validateFullName('Balwinder Singh'), null, 'Valid name: Balwinder Singh');
assert.equal(validateFullName('   Ramesh Patel   '), null, 'Valid name with leading/trailing spaces');

// Invalid cases from prompt
assert.notEqual(validateFullName(''), null, 'Reject empty name');
assert.notEqual(validateFullName('   '), null, 'Reject whitespace-only name');
assert.notEqual(validateFullName('12345'), null, 'Reject numeric name: 12345');
assert.notEqual(validateFullName('Jhansi123'), null, 'Reject alphanumeric name: Jhansi123');
assert.notEqual(validateFullName('@@@'), null, 'Reject symbol name: @@@');
assert.notEqual(validateFullName('123@@'), null, 'Reject number and symbol: 123@@');
assert.notEqual(validateFullName('.'), null, 'Reject single period');
assert.notEqual(validateFullName('..'), null, 'Reject dots');
assert.notEqual(validateFullName('-'), null, 'Reject single hyphen');
assert.notEqual(validateFullName('A'), null, 'Reject single character name');
assert.notEqual(validateFullName('nsdkjf123'), null, 'Reject nsdkjf123');

console.log('✓ Full Name validation passed all cases.');

// ==========================================
// 2. EMAIL VALIDATION TEST CASES
// ==========================================
console.log('Testing Email Validation...');

// Valid email cases
const validEmail1 = validateEmailOrPhone('farmer@example.com');
assert.equal(validEmail1.error, null);
assert.equal(validEmail1.type, 'email');
assert.equal(validEmail1.value, 'farmer@example.com');

const validEmail2 = validateEmailOrPhone('jhansi.reddy@farmsathi.in');
assert.equal(validEmail2.error, null);
assert.equal(validEmail2.type, 'email');

const validEmail3 = validateEmailOrPhone('user+farm1@sub.domain.co');
assert.equal(validEmail3.error, null);
assert.equal(validEmail3.type, 'email');

// Invalid email cases from prompt
assert.notEqual(validateEmailOrPhone('abc').error, null, 'Reject non-email abc');
assert.notEqual(validateEmailOrPhone('abc@').error, null, 'Reject incomplete abc@');
assert.notEqual(validateEmailOrPhone('@gmail.com').error, null, 'Reject @gmail.com');
assert.notEqual(validateEmailOrPhone('abc@gmail').error, null, 'Reject abc@gmail without TLD');
assert.notEqual(validateEmailOrPhone('abc@gmail.').error, null, 'Reject trailing dot abc@gmail.');

console.log('✓ Email validation passed all cases.');

// ==========================================
// 3. MOBILE VALIDATION TEST CASES
// ==========================================
console.log('Testing Mobile Validation...');

// Valid mobile cases from prompt
const validMobile1 = validateEmailOrPhone('9876543210');
assert.equal(validMobile1.error, null);
assert.equal(validMobile1.type, 'phone');
assert.equal(validMobile1.value, '9876543210');

const validMobile2 = validateEmailOrPhone('+919876543210');
assert.equal(validMobile2.error, null);
assert.equal(validMobile2.type, 'phone');
assert.equal(validMobile2.value, '+919876543210');

const validMobile3 = validateEmailOrPhone('+91 9876543210');
assert.equal(validMobile3.error, null);
assert.equal(validMobile3.type, 'phone');
assert.equal(validMobile3.value, '+919876543210');

const validMobile4 = validateEmailOrPhone('09876543210');
assert.equal(validMobile4.error, null);
assert.equal(validMobile4.type, 'phone');

const validMobile5 = validateEmailOrPhone('7012345678');
assert.equal(validMobile5.error, null);
assert.equal(validMobile5.type, 'phone');

// Invalid mobile cases from prompt
assert.notEqual(validateEmailOrPhone('26323').error, null, 'Reject 26323');
assert.notEqual(validateEmailOrPhone('123').error, null, 'Reject 123');
assert.notEqual(validateEmailOrPhone('abcdef').error, null, 'Reject abcdef');
assert.notEqual(validateEmailOrPhone('@@@').error, null, 'Reject @@@');
assert.notEqual(validateEmailOrPhone('1234567890').error, null, 'Reject invalid starting digit (1)');
assert.notEqual(validateEmailOrPhone('5876543210').error, null, 'Reject invalid starting digit (5)');
assert.notEqual(validateEmailOrPhone('987654321').error, null, 'Reject 9 digits');
assert.notEqual(validateEmailOrPhone('9876543210123').error, null, 'Reject 13 digits without prefix');
assert.notEqual(validateEmailOrPhone('').error, null, 'Reject empty');
assert.notEqual(validateEmailOrPhone('   ').error, null, 'Reject whitespace');

console.log('✓ Mobile validation passed all cases.');

// ==========================================
// 4. PASSWORD VALIDATION TEST CASES
// ==========================================
console.log('Testing Password Validation...');

// Valid passwords matching backend policy
assert.equal(validatePassword('SecurePassword123!'), null, 'Valid: SecurePassword123!');
assert.equal(validatePassword('Password123!'), null, 'Valid: Password123!');
assert.equal(validatePassword('CorrectPassword'), null, 'Valid: CorrectPassword');
assert.equal(validatePassword('FarmerSecret@456'), null, 'Valid: FarmerSecret@456');
assert.equal(validatePassword('farmer123'), null, 'Valid: farmer123');
assert.equal(validatePassword('Pass#1'), null, 'Valid min length 6: Pass#1');

// Invalid passwords from prompt
assert.notEqual(validatePassword(''), null, 'Reject empty password');
assert.notEqual(validatePassword('   '), null, 'Reject whitespace password');
assert.notEqual(validatePassword('12345'), null, 'Reject too short password');
assert.notEqual(validatePassword('abc'), null, 'Reject too short password');
assert.notEqual(validatePassword('21332133'), null, 'Reject numeric-only password: 21332133');
assert.notEqual(validatePassword('123456'), null, 'Reject numeric-only password: 123456');
assert.notEqual(validatePassword('9876543210'), null, 'Reject numeric-only password: 9876543210');

console.log('✓ Password validation passed all cases.');

console.log('All frontend signup validation tests passed successfully!');
