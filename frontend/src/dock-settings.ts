// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

// ESM entry point for Home's settings component.
// Dock's DockSettingsAppHost lazy-loads this bundle and renders HomeSettings
// inside the Dock SPA at /dock/settings/app/home.
//
// This file is built as a separate Vite library entry: home-settings.esm.js

export { default as HomeSettings } from './pages/HomeSettings.vue'
