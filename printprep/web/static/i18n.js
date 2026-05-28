"use strict";

// Minimal i18n for the PrintPrep web UI.
//
// - JSON files under /locales/<code>.json
// - t(key, params)  → interpolates {placeholder} from `params`
// - applyDom()      → walks `data-i18n`, `data-i18n-attr-*`, `data-i18n-placeholder`
// - setLang(code)   → fetches + applies + persists in localStorage
// - onChange(fn)    → callbacks fire AFTER each setLang() so dynamic render
//                     code (table headers, status text, etc.) can re-translate.

export const SUPPORTED = [
  { code: "en", name: "English", dir: "ltr" },
  { code: "zh", name: "中文", dir: "ltr" },
  { code: "hi", name: "हिन्दी", dir: "ltr" },
  { code: "es", name: "Español", dir: "ltr" },
  { code: "ar", name: "العربية", dir: "rtl" },
  { code: "bn", name: "বাংলা", dir: "ltr" },
  { code: "pt", name: "Português", dir: "ltr" },
  { code: "ru", name: "Русский", dir: "ltr" },
  { code: "ja", name: "日本語", dir: "ltr" },
  { code: "pa", name: "ਪੰਜਾਬੀ", dir: "ltr" },
  { code: "de", name: "Deutsch", dir: "ltr" },
  { code: "jv", name: "Basa Jawa", dir: "ltr" },
  { code: "ko", name: "한국어", dir: "ltr" },
  { code: "fr", name: "Français", dir: "ltr" },
  { code: "tr", name: "Türkçe", dir: "ltr" },
];

const STORAGE_KEY = "printprep.lang";
let current = "en";
let dict = {};
let fallback = {};
const subscribers = [];

function detect() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored && SUPPORTED.some((l) => l.code === stored)) return stored;
  const nav = (navigator.language || "en").toLowerCase();
  // Match "zh-cn" → "zh", "pt-br" → "pt".
  const base = nav.split("-")[0];
  if (SUPPORTED.some((l) => l.code === base)) return base;
  return "en";
}

async function fetchLocale(code) {
  const res = await fetch(`/locales/${code}.json`);
  if (!res.ok) throw new Error(`locale ${code} not found`);
  return res.json();
}

export function t(key, params) {
  let s = dict[key];
  if (s == null) s = fallback[key];
  if (s == null) return key;
  if (!params) return s;
  return s.replace(/\{(\w+)\}/g, (_, k) => (params[k] != null ? params[k] : `{${k}}`));
}

export function getLang() {
  return current;
}

export function applyDom(root) {
  root = root || document;
  root.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  root.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  root.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  root.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.title = t(el.dataset.i18nTitle);
  });
  // <title>
  if (dict.title) document.title = t("title");
}

export function onChange(fn) {
  subscribers.push(fn);
}

export async function setLang(code) {
  if (!SUPPORTED.some((l) => l.code === code)) code = "en";
  dict = await fetchLocale(code);
  current = code;
  localStorage.setItem(STORAGE_KEY, code);
  const meta = SUPPORTED.find((l) => l.code === code);
  document.documentElement.lang = code;
  document.documentElement.dir = (meta && meta.dir) || "ltr";
  applyDom();
  subscribers.forEach((fn) => {
    try { fn(code); } catch (e) { console.error(e); }
  });
}

export async function init() {
  // Always load English as the fallback so missing keys never show {placeholder}.
  fallback = await fetchLocale("en");
  await setLang(detect());
}
