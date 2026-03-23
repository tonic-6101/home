// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { frappeRequest } from 'frappe-ui'

interface UseHouseholdRoleReturn {
  role: Ref<string | null>
  household: Ref<string | null>
  isOwner: ComputedRef<boolean>
  isAdultOrAbove: ComputedRef<boolean>
  isChild: ComputedRef<boolean>
  loaded: Ref<boolean>
  load: () => Promise<void>
}

const role = ref<string | null>(null)
const household = ref<string | null>(null)
const loaded = ref(false)

export function useHouseholdRole(): UseHouseholdRoleReturn {
  async function load() {
    if (loaded.value) return
    try {
      const res = await frappeRequest({
        url: '/api/method/home.api.permission.get_my_role',
      })
      const data = res || {}
      role.value = data.role || null
      household.value = data.household || null
    } catch {
      role.value = null
      household.value = null
    } finally {
      loaded.value = true
    }
  }

  const isOwner = computed(() => role.value === 'Owner')
  const isAdultOrAbove = computed(() => role.value === 'Owner' || role.value === 'Adult')
  const isChild = computed(() => role.value === 'Child')

  return { role, household, isOwner, isAdultOrAbove, isChild, loaded, load }
}
