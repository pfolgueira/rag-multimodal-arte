import React, { createContext, useContext, useState } from 'react';

import es from './es.json';
import en from './en.json';

const translations = { es, en };

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(() => {
    return localStorage.getItem('lang') || 'es';
  });

  const t = (key) => translations[lang][key] || key;

  const switchLang = (next) => {
    setLang(next);
    localStorage.setItem('lang', next);
  };

  return (
    <I18nContext.Provider value={{ lang, setLang: switchLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslation() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useTranslation must be used within I18nProvider');
  return ctx;
}
