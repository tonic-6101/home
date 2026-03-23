// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { createApp, type App as VueApp } from 'vue'
import {
  FrappeUI,
  setConfig,
  frappeRequest,
  Button,
  Input,
  Badge,
} from 'frappe-ui'

import router from './router'
import App from './App.vue'
import { TranslatePlugin } from './plugins/translate'
import { getLang } from './composables/useTranslate'
import './index.css'

const app: VueApp = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(FrappeUI, { socketio: false })
app.use(TranslatePlugin)

document.documentElement.lang = getLang()

app.component('Button', Button)
app.component('Input', Input)
app.component('Badge', Badge)

app.config.errorHandler = (err, _instance, info) => {
  console.error(`[Home] Unhandled error (${info}):`, err)
}

app.mount('#app')
