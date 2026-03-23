// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import type { App } from 'vue'
import { __ } from '@/composables/useTranslate'

export const TranslatePlugin = {
  install(app: App) {
    app.config.globalProperties.__ = __
    window.__ = __
  }
}
