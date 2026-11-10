/* =====================================================
   MyStat — Main JavaScript
   ===================================================== */

(function () {
  'use strict';

  // --------------------------------------------------
  //  i18n — Translation dictionary
  // --------------------------------------------------
  const translations = {
    ru: {
      page_title: 'MyStat - Авторизация',
      lang_label: 'Русский',
      login_title: 'Логин',
      email_placeholder: 'E-mail или Логин*',
      password_placeholder: 'Пароль*',
      forgot_password: 'Забыли пароль?',
      submit_button: 'Логин',
      google_play_alt: 'Get it on Google Play',
      app_store_alt: 'Download on the App Store',
    },
    en: {
      page_title: 'MyStat - Login',
      lang_label: 'English',
      login_title: 'Login',
      email_placeholder: 'E-mail or Login*',
      password_placeholder: 'Password*',
      forgot_password: 'Forgot password?',
      submit_button: 'Login',
      google_play_alt: 'Get it on Google Play',
      app_store_alt: 'Download on the App Store',
    },
  };

  // Current language (default: Russian)
  let currentLang = 'ru';

  /**
   * Apply translations for the given language code.
   * Updates text content, placeholders, alt attributes, and the page title.
   */
  function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;

    const dict = translations[lang];

    // Update page title
    document.title = dict.page_title;

    // Update elements with data-i18n (text content)
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      if (dict[key] !== undefined) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update alt attributes
    document.querySelectorAll('[data-i18n-alt]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-alt');
      if (dict[key] !== undefined) {
        el.setAttribute('alt', dict[key]);
      }
    });

    // Persist preference in localStorage
    try {
      localStorage.setItem('mystat_lang', lang);
    } catch (_) {
      // localStorage may be unavailable
    }
  }

  /**
   * Toggle between Russian and English.
   */
  function toggleLanguage() {
    var next = currentLang === 'ru' ? 'en' : 'ru';
    setLanguage(next);
  }

  // --------------------------------------------------
  //  Password visibility toggle
  // --------------------------------------------------
  function initPasswordToggle() {
    var toggle = document.querySelector('.password-toggle');
    if (!toggle) return;

    var input = toggle.closest('.relative').querySelector('input[type="password"], input[type="text"]');
    if (!input) return;

    toggle.addEventListener('click', function () {
      if (input.type === 'password') {
        input.type = 'text';
      } else {
        input.type = 'password';
      }
    });
  }

  // --------------------------------------------------
  //  Language toggle button
  // --------------------------------------------------
  function initLanguageToggle() {
    var btn = document.querySelector('.lang-toggle');
    if (!btn) return;

    btn.addEventListener('click', toggleLanguage);
  }

  // --------------------------------------------------
  //  Initialization — run on DOM ready
  // --------------------------------------------------
  function init() {
    // Restore saved language preference, if any
    try {
      var saved = localStorage.getItem('mystat_lang');
      if (saved && translations[saved]) {
        setLanguage(saved);
      }
    } catch (_) {
      // localStorage may be unavailable
    }

    initPasswordToggle();
    initLanguageToggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
