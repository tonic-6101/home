// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { ref, onMounted } from 'vue'

const THEME_KEY = 'dock-theme'

type Theme = 'light' | 'dark' | 'system'

const theme = ref<Theme>(
  (localStorage.getItem(THEME_KEY) as Theme) ?? 'system'
)

function apply(t: Theme) {
  const dark = t === 'dark' || (t === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', dark)
}

export function useTheme() {
  function setTheme(t: Theme) {
    theme.value = t
    localStorage.setItem(THEME_KEY, t)
    apply(t)
  }

  onMounted(() => apply(theme.value))

  return { theme, setTheme }
}
