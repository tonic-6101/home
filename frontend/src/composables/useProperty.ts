// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'

const propertyName = ref('')
const loading = ref(false)
const loaded = ref(false)

/**
 * Shared composable that resolves the household's single property.
 *
 * Community tier enforces one active property per household, so this
 * should always resolve deterministically. If multiple properties
 * exist (legacy data), picks the one with the most items to avoid
 * showing an empty page.
 */
export function useProperty() {
  async function load(): Promise<string> {
    if (loaded.value) return propertyName.value
    loading.value = true
    try {
      const res = await frappeRequest({
        url: '/api/method/home.api.property.list_properties',
        params: { include_archived: false },
      })
      const list = res || []
      if (list.length === 0) {
        propertyName.value = ''
      } else if (list.length === 1) {
        propertyName.value = list[0].name
      } else {
        // Multiple properties (legacy or Pro) — pick the one with
        // the most items so the user sees their data immediately.
        const best = list.reduce((a: any, b: any) =>
          (a.item_count || 0) >= (b.item_count || 0) ? a : b
        )
        propertyName.value = best.name
      }
    } catch {
      propertyName.value = ''
    } finally {
      loading.value = false
      loaded.value = true
    }
    return propertyName.value
  }

  function reset() {
    propertyName.value = ''
    loaded.value = false
  }

  return { propertyName, loading, loaded, load, reset }
}
