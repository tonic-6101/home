// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

declare global {
  interface Window {
    __messages: Record<string, string>
    lang: string
    __: (text: string, replace?: unknown[] | Record<string, unknown>) => string
  }
}

export function __(text: string, replace?: unknown[] | Record<string, unknown>): string {
  const messages: Record<string, string> = window.__messages || {}
  let translated = messages[text] || text

  if (replace) {
    if (Array.isArray(replace)) {
      for (let i = 0; i < replace.length; i++) {
        translated = translated.replace(new RegExp(`\\{${i}\\}`, 'g'), String(replace[i]))
      }
    } else {
      for (const [key, value] of Object.entries(replace)) {
        translated = translated.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value))
      }
    }
  }

  return translated
}

export function getLang(): string {
  return window.lang || 'en'
}
