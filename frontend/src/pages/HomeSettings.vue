<!--
  SPDX-License-Identifier: AGPL-3.0-or-later
  Copyright (C) 2024-2026 Tonic

  Home settings component for Dock's unified settings hub.
  Loaded via ESM bundle at /dock/settings/app/home.
  Receives `section` prop from DockSettingsAppHost to show the active subsection.
-->
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { frappeRequest } from 'frappe-ui'
import HouseholdMemberAvatar from '@/components/HouseholdMemberAvatar.vue'
import HomeSettingsPanel from '@/components/HomeSettingsPanel.vue'
import { __ } from '@/composables/useTranslate'

const props = defineProps<{ section?: string }>()

interface Member {
  name: string
  display_name: string
  role: 'Owner' | 'Adult' | 'Child'
  user: string | null
  email: string | null
  avatar: string | null
  pending: boolean
}

const currentUser = (window as any).frappe?.session?.user || ''
const household = ref('')
const members = ref<Member[]>([])
const loading = ref(true)
const error = ref('')
const noHousehold = ref(false)

// Create household form
const newHouseholdName = ref('')
const creatingHousehold = ref(false)

// Invite form
const inviteEmail = ref('')
const inviteRole = ref<'Adult' | 'Child'>('Adult')
const inviting = ref(false)
const inviteMessage = ref('')

// Role change
const changingRole = ref<string | null>(null)

const currentMember = computed(() =>
  members.value.find(m => m.user === currentUser)
)

const isOwner = computed(() => currentMember.value?.role === 'Owner')

// Active section — default to 'household'
const activeSection = computed(() => props.section || 'household')

async function loadHousehold() {
  loading.value = true
  error.value = ''
  try {
    const households = await frappeRequest({
      url: '/api/method/home.api.permission.get_user_households',
    })
    const list = households || []
    if (!list.length) {
      noHousehold.value = true
      loading.value = false
      return
    }
    household.value = list[0]
    await loadMembers()
  } catch (e: any) {
    error.value = e.message || __('Failed to load household')
  } finally {
    loading.value = false
  }
}

async function loadMembers() {
  const res = await frappeRequest({
    url: '/api/method/home.api.household.get_members',
    params: { household: household.value },
  })
  members.value = res || []
}

async function inviteMember() {
  if (!inviteEmail.value.trim()) return
  inviting.value = true
  inviteMessage.value = ''
  try {
    const res = await frappeRequest({
      url: '/api/method/home.api.household.invite_member',
      params: {
        household: household.value,
        email: inviteEmail.value.trim(),
        role: inviteRole.value,
      },
    })
    const data = res
    inviteMessage.value = data.user_exists
      ? __('Member added successfully')
      : __('Invitation sent — they will appear once they register')
    inviteEmail.value = ''
    await loadMembers()
  } catch (e: any) {
    inviteMessage.value = e.message || __('Failed to invite member')
  } finally {
    inviting.value = false
  }
}

async function removeMember(memberName: string) {
  try {
    await frappeRequest({
      url: '/api/method/home.api.household.remove_member',
      params: { household: household.value, member_name: memberName },
    })
    await loadMembers()
  } catch (e: any) {
    alert(e.message || __('Failed to remove member'))
  }
}

async function changeRole(memberName: string, newRole: string) {
  try {
    await frappeRequest({
      url: '/api/method/home.api.household.change_member_role',
      params: { household: household.value, member_name: memberName, new_role: newRole },
    })
    changingRole.value = null
    await loadMembers()
  } catch (e: any) {
    alert(e.message || __('Failed to change role'))
  }
}

function roleBadgeClass(role: string): string {
  switch (role) {
    case 'Owner': return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
    case 'Adult': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    case 'Child': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    default: return 'bg-gray-100 text-gray-800'
  }
}

async function createHousehold() {
  creatingHousehold.value = true
  error.value = ''
  try {
    await frappeRequest({
      url: '/api/method/home.api.household.create_household',
      params: { household_name: newHouseholdName.value.trim() },
    })
    noHousehold.value = false
    newHouseholdName.value = ''
    await loadHousehold()
  } catch (e: any) {
    error.value = e.message || __('Failed to create household')
  } finally {
    creatingHousehold.value = false
  }
}

onMounted(loadHousehold)
</script>

<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="text-gray-500">
      {{ __('Loading…') }}
    </div>

    <!-- No household — create one -->
    <div
      v-else-if="noHousehold"
      class="text-center py-16"
    >
      <div class="text-6xl mb-4">🏠</div>
      <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-2">
        {{ __('Welcome to Home') }}
      </h2>
      <p class="text-body text-gray-500 dark:text-gray-400 mb-6">
        {{ __('Create your household to get started.') }}
      </p>
      <div class="max-w-sm mx-auto flex flex-col gap-3">
        <input
          v-model="newHouseholdName"
          type="text"
          :placeholder="__('My Home')"
          class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          @keyup.enter="createHousehold"
        />
        <Button
          variant="solid"
          :loading="creatingHousehold"
          @click="createHousehold"
        >
          {{ __('Create Household') }}
        </Button>
        <p v-if="error" class="text-sm text-red-600 dark:text-red-400">
          {{ error }}
        </p>
      </div>
    </div>

    <!-- Error (other) -->
    <div v-else-if="error" class="text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <template v-else>
      <!-- Household section: Members + Invite -->
      <template v-if="activeSection === 'household'">
        <!-- Members List -->
        <section class="mb-8">
          <h2 class="text-h3 text-gray-800 dark:text-gray-200 mb-4">
            {{ __('Members') }}
          </h2>

          <div class="space-y-3">
            <div
              v-for="member in members"
              :key="member.name"
              class="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <HouseholdMemberAvatar
                :display-name="member.display_name"
                :avatar="member.avatar"
                size="md"
              />

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {{ member.display_name }}
                  </span>
                  <span
                    v-if="member.pending"
                    class="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                  >
                    {{ __('Pending') }}
                  </span>
                  <span
                    v-if="member.user === currentUser"
                    class="text-xs text-gray-400"
                  >
                    {{ __('(you)') }}
                  </span>
                </div>
                <div class="text-caption text-gray-500 dark:text-gray-400">
                  {{ member.email || member.user || __('No account') }}
                </div>
              </div>

              <!-- Role badge / change -->
              <div class="flex items-center gap-2">
                <template v-if="isOwner && changingRole === member.name">
                  <select
                    :value="member.role"
                    @change="changeRole(member.name, ($event.target as HTMLSelectElement).value)"
                    class="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="Owner">Owner</option>
                    <option value="Adult">Adult</option>
                    <option value="Child">Child</option>
                  </select>
                  <button
                    @click="changingRole = null"
                    class="text-xs text-gray-400 hover:text-gray-600"
                  >
                    {{ __('Cancel') }}
                  </button>
                </template>
                <template v-else>
                  <span
                    :class="['text-xs px-2 py-0.5 rounded-full font-medium', roleBadgeClass(member.role)]"
                    @click="isOwner && member.user !== currentUser ? changingRole = member.name : null"
                    :style="isOwner && member.user !== currentUser ? 'cursor: pointer' : ''"
                  >
                    {{ member.role }}
                  </span>
                </template>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-1">
                <button
                  v-if="isOwner && member.user !== currentUser"
                  @click="removeMember(member.name)"
                  class="text-xs text-red-400 hover:text-red-600 px-2 py-1"
                  :title="__('Remove member')"
                >
                  {{ __('Remove') }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Invite Form (owner only) -->
        <section v-if="isOwner" class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 class="text-h4 text-gray-800 dark:text-gray-200 mb-3">
            {{ __('Invite Member') }}
          </h3>
          <div class="flex gap-3 items-end flex-wrap">
            <div class="flex-1 min-w-[200px]">
              <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
                {{ __('Email') }}
              </label>
              <input
                v-model="inviteEmail"
                type="email"
                :placeholder="__('person@example.com')"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                @keyup.enter="inviteMember"
              />
            </div>
            <div>
              <label class="text-caption text-gray-500 dark:text-gray-400 block mb-1">
                {{ __('Role') }}
              </label>
              <select
                v-model="inviteRole"
                class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="Adult">{{ __('Adult') }}</option>
                <option value="Child">{{ __('Child') }}</option>
              </select>
            </div>
            <Button @click="inviteMember" variant="solid" :loading="inviting">
              {{ __('Send Invite') }}
            </Button>
          </div>
          <p v-if="inviteMessage" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {{ inviteMessage }}
          </p>
        </section>
      </template>

      <!-- Alerts / Lifespans / Preferences — delegated to HomeSettingsPanel -->
      <HomeSettingsPanel
        v-if="isOwner && (activeSection === 'alerts' || activeSection === 'lifespans' || activeSection === 'preferences')"
        :household="household"
        :section="activeSection"
      />

      <!-- Non-owner message for settings sections -->
      <div
        v-if="!isOwner && activeSection !== 'household'"
        class="text-center py-12"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {{ __('Only the household owner can manage these settings.') }}
        </p>
      </div>
    </template>
  </div>
</template>
