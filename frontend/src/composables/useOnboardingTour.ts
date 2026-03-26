// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2024-2026 Tonic

import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import Shepherd from 'shepherd.js'
import 'shepherd.js/dist/css/shepherd.css'
import { __ } from './useTranslate'

const tourActive = ref(false)
const tourDismissedThisSession = ref(false)
let tourInstance: Shepherd.Tour | null = null

function progressHtml(current: number, total: number): string {
  const pct = Math.round((current / total) * 100)
  return `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <span style="font-size:12px;color:#6b7280;">${__('Step')} ${current} ${__('of')} ${total}</span>
      <div style="flex:1;height:4px;background:#e5e7eb;border-radius:2px;overflow:hidden;">
        <div style="width:${pct}%;height:100%;background:#f59e0b;border-radius:2px;transition:width 0.3s;"></div>
      </div>
    </div>
  `
}

function buildOwnerSteps(): Shepherd.Step.StepOptions[] {
  const total = 6 // progress steps (excluding welcome & done modals)
  return [
    // Step 1 — Welcome (modal)
    {
      id: 'welcome',
      text: `
        <div style="text-align:center;padding:8px 0;">
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${__('Welcome to Home')}</h2>
          <p style="color:#6b7280;">${__("Let's set up your first property in a few steps.")}<br>${__('You can skip this at any time and come back later.')}</p>
        </div>
      `,
      buttons: [
        {
          text: __('Skip tour'),
          action: function (this: Shepherd.Tour) {
            completeTour()
            this.complete()
          },
          classes: 'shepherd-button-secondary',
        },
        {
          text: __("Let's go") + ' →',
          action: function (this: Shepherd.Tour) { this.next() },
          classes: 'shepherd-button-primary',
        },
      ],
      modalOverlayOpeningPadding: 0,
    },
    // Step 2 — Add property
    {
      id: 'add-property',
      text: progressHtml(1, total) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Start here')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('Add your property — address, type, and when you moved in.')}</p>
      `,
      attachTo: { element: '[data-tour="add-property"]', on: 'bottom' },
      buttons: [
        { text: __('Skip'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 3 — Add rooms
    {
      id: 'add-rooms',
      text: progressHtml(2, total) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Add your rooms')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('Define the rooms in your property — kitchen, bathroom, bedroom, garage. Rooms help organise appliances and tasks.')}</p>
      `,
      attachTo: { element: '[data-tour="add-room"]', on: 'bottom' },
      buttons: [
        { text: '← ' + __('Back'), action: function (this: Shepherd.Tour) { this.back() }, classes: 'shepherd-button-secondary' },
        { text: __('Skip'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 4 — Register item
    {
      id: 'add-item',
      text: progressHtml(3, total) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Register your items')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('Add the appliances and possessions in your home — boiler, washing machine, fridge, furniture.')}<br>${__('Tap the camera icon to scan the barcode or rating plate and auto-fill the details.')}</p>
      `,
      attachTo: { element: '[data-tour="add-item"]', on: 'bottom' },
      buttons: [
        { text: '← ' + __('Back'), action: function (this: Shepherd.Tour) { this.back() }, classes: 'shepherd-button-secondary' },
        { text: __('Skip'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 5 — Set maintenance reminder
    {
      id: 'create-task',
      text: progressHtml(4, total) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Set your first reminder')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('Create your first task — boiler service, gutter cleaning, smoke alarm check. Manage tasks in Orga.')}</p>
      `,
      attachTo: { element: '[data-tour="create-task"]', on: 'bottom' },
      buttons: [
        { text: '← ' + __('Back'), action: function (this: Shepherd.Tour) { this.back() }, classes: 'shepherd-button-secondary' },
        { text: __('Skip'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 6 — Tour the dashboard
    {
      id: 'dashboard',
      text: progressHtml(5, total) + `
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Your property dashboard')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('This is your at-a-glance view — item count, upcoming tasks, health score, and cost forecast.')}</p>
      `,
      attachTo: { element: '[data-tour="dashboard"]', on: 'bottom' },
      buttons: [
        { text: '← ' + __('Back'), action: function (this: Shepherd.Tour) { this.back() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 7 — Done (modal)
    {
      id: 'done',
      text: `
        <div style="text-align:center;padding:8px 0;">
          ${progressHtml(6, total)}
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${__("You're all set")} &#10003;</h2>
          <p style="color:#6b7280;">${__('Home will remind you when warranties are expiring and keep everything about your property in one place.')}</p>
          <p style="color:#9ca3af;font-size:13px;margin-top:8px;">${__('You can restart this tour anytime from Settings.')}</p>
        </div>
      `,
      buttons: [
        {
          text: __('Go to dashboard') + ' →',
          action: function (this: Shepherd.Tour) {
            completeTour()
            this.complete()
          },
          classes: 'shepherd-button-primary',
        },
      ],
    },
  ]
}

function buildMemberSteps(ownerName: string): Shepherd.Step.StepOptions[] {
  return [
    // Step 1 — Welcome
    {
      id: 'welcome',
      text: `
        <div style="text-align:center;padding:8px 0;">
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${__('Welcome to Home')}</h2>
          <p style="color:#6b7280;">${ownerName} ${__('has added you to their household. Here\'s what you can see.')}</p>
        </div>
      `,
      buttons: [
        { text: __('Skip'), action: function (this: Shepherd.Tour) { completeTour(); this.complete() }, classes: 'shepherd-button-secondary' },
        { text: __('Show me') + ' →', action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 2 — What you can see
    {
      id: 'property-card',
      text: `
        ${progressHtml(1, 2)}
        <h3 style="font-size:16px;font-weight:600;margin-bottom:4px;">${__('Your household property')}</h3>
        <p style="color:#6b7280;font-size:14px;">${__('You can view the property details, items, task history, and emergency contacts.')}</p>
      `,
      attachTo: { element: '[data-tour="dashboard"]', on: 'bottom' },
      buttons: [
        { text: '← ' + __('Back'), action: function (this: Shepherd.Tour) { this.back() }, classes: 'shepherd-button-secondary' },
        { text: '→ ' + __('Next'), action: function (this: Shepherd.Tour) { this.next() }, classes: 'shepherd-button-primary' },
      ],
    },
    // Step 3 — Done
    {
      id: 'done',
      text: `
        <div style="text-align:center;padding:8px 0;">
          ${progressHtml(2, 2)}
          <h2 style="font-size:20px;font-weight:600;margin-bottom:8px;">${__("That's it!")}</h2>
          <p style="color:#6b7280;">${__('If you have any questions, ask the household owner.')}</p>
        </div>
      `,
      buttons: [
        {
          text: __('Got it'),
          action: function (this: Shepherd.Tour) {
            completeTour()
            this.complete()
          },
          classes: 'shepherd-button-primary',
        },
      ],
    },
  ]
}

let _household: string | null = null

async function completeTour() {
  if (!_household) return
  try {
    await frappeRequest({
      url: '/api/method/home.api.onboarding.complete_onboarding',
      params: { household: _household },
    })
  } catch {
    // silent — best effort
  }
}

function createTour(steps: Shepherd.Step.StepOptions[]): Shepherd.Tour {
  const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: { enabled: false },
      scrollTo: { behavior: 'smooth', block: 'center' },
      modalOverlayOpeningPadding: 8,
      modalOverlayOpeningRadius: 8,
      // When anchor not found, show as floating modal
      floatingUIOptions: {
        middleware: [],
      },
    },
    keyboardNavigation: true,
  })

  steps.forEach(step => tour.addStep(step))

  // Arrow key navigation: → / Enter advances, ← / Backspace goes back
  function onKeydown(e: KeyboardEvent) {
    if (!tour.isActive()) return
    if (e.key === 'ArrowRight' || e.key === 'Enter') {
      e.preventDefault()
      tour.next()
    } else if (e.key === 'ArrowLeft' || e.key === 'Backspace') {
      e.preventDefault()
      tour.back()
    }
  }

  tour.on('start', () => {
    document.addEventListener('keydown', onKeydown)
  })

  tour.on('cancel', () => {
    tourActive.value = false
    tourDismissedThisSession.value = true
    document.removeEventListener('keydown', onKeydown)
  })

  tour.on('complete', () => {
    tourActive.value = false
    tourDismissedThisSession.value = true
    document.removeEventListener('keydown', onKeydown)
  })

  return tour
}

export function useOnboardingTour() {
  async function initTour() {
    if (tourDismissedThisSession.value || tourActive.value) return

    try {
      // Get household
      const roleRes = await frappeRequest({
        url: '/api/method/home.api.permission.get_my_role',
      })
      const household = roleRes?.household
      if (!household) return
      _household = household

      // Check onboarding status
      const res = await frappeRequest({
        url: '/api/method/home.api.onboarding.get_onboarding_status',
        params: { household },
      })
      const data = res
      if (!data || data.tour_completed) return

      // Determine variant
      const variant = data.variant
      if (variant === 'owner_setup' && !data.household_has_properties) {
        tourInstance = createTour(buildOwnerSteps())
      } else if (variant === 'invited_member' || (variant === 'owner_setup' && data.household_has_properties)) {
        // Owner with existing properties sees member-style welcome
        const ownerName = data.owner_display_name || ''
        tourInstance = createTour(buildMemberSteps(ownerName))
      } else {
        return
      }

      // Delay slightly to let DOM render
      setTimeout(() => {
        if (tourInstance && !tourDismissedThisSession.value) {
          tourActive.value = true
          tourInstance.start()
        }
      }, 800)
    } catch {
      // silent — don't break app if tour fails
    }
  }

  async function restartTour() {
    if (!_household) {
      try {
        const roleRes = await frappeRequest({
          url: '/api/method/home.api.permission.get_my_role',
        })
        _household = roleRes?.household || null
      } catch {
        return
      }
    }
    if (!_household) return

    try {
      await frappeRequest({
        url: '/api/method/home.api.onboarding.reset_tour',
        params: {},
      })
      tourDismissedThisSession.value = false
      await initTour()
    } catch {
      // silent
    }
  }

  return { tourActive, initTour, restartTour }
}
