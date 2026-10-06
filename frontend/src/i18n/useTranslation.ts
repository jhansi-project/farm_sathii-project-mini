import { useLanguageStore } from '../stores/languageStore';
import { translations, TranslationDictionary, LanguageCode } from './translations';

export type TFunction = {
  (key: string, fallback?: string): string;
} & TranslationDictionary;

export const useTranslation = () => {
  const { currentLanguage, setLanguage } = useLanguageStore();

  const langCode: LanguageCode = (
    currentLanguage in translations ? currentLanguage : 'en'
  ) as LanguageCode;

  const dict: TranslationDictionary = translations[langCode] || translations.en;

  const tFn = (key: string, fallback?: string): string => {
    // 1. Try nested dot-path in dict
    const parts = key.split('.');
    let cur: any = dict;
    for (const p of parts) {
      if (cur && typeof cur === 'object' && p in cur) {
        cur = cur[p];
      } else {
        cur = undefined;
        break;
      }
    }
    if (typeof cur === 'string' && cur.trim()) return cur;

    // 2. Try common dictionary
    const common = (dict as any).common;
    if (common && typeof common === 'object' && key in common && typeof common[key] === 'string') {
      return common[key];
    }

    // 3. Search top-level sections in current language
    for (const section of Object.values(dict as Record<string, any>)) {
      const s = section as Record<string, any>;
      if (s && typeof s === 'object' && key in s && typeof s[key] === 'string') {
        return s[key];
      }
    }

    // 4. Try English dictionary if non-English and not found
    if (langCode !== 'en' && translations.en) {
      let enCur: any = translations.en;
      for (const p of parts) {
        if (enCur && typeof enCur === 'object' && p in enCur) {
          enCur = enCur[p];
        } else {
          enCur = undefined;
          break;
        }
      }
      if (typeof enCur === 'string' && enCur.trim()) return enCur;

      const enCommon = (translations.en as any).common;
      if (enCommon && typeof enCommon === 'object' && key in enCommon && typeof enCommon[key] === 'string') {
        return enCommon[key];
      }

      for (const section of Object.values(translations.en as Record<string, any>)) {
        const s = section as Record<string, any>;
        if (s && typeof s === 'object' && key in s && typeof s[key] === 'string') {
          return s[key];
        }
      }
    }

    // 5. If fallback provided, return it
    if (fallback !== undefined) return fallback;

    // 6. Safe formatting guardrail: Never return raw snake_case keys like voice_input to farmers
    const humanized = key
      .replace(/[._-]+/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase())
      .trim();

    return humanized || key;
  };

  const t = Object.assign(tFn, dict) as TFunction;

  return {
    t,
    currentLanguage: langCode,
    setLanguage,
  };
};

