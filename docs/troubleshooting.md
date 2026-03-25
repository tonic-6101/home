# Troubleshooting

## Household creation fails for first-time users

**Symptom:** New users see a blank screen or "No household found" after logging in.

**Cause:** The user has no `Home Household Member` record. The onboarding flow should create one, but this can fail if the user navigates directly to `/home` before completing onboarding.

**Fix:** Call `home.api.onboarding.get_onboarding_status` to check state. If `has_household` is `false`, redirect to `/home/onboarding`. Alternatively, an Owner can invite the user via `home.api.household.invite_member`.

---

## Permission errors — "You do not have permission"

**Symptom:** User receives a 403 or permission error when accessing Home data.

**Possible causes:**

1. **User is not a household member.** Verify the user has a `Home Household Member` record linking them to the correct household.
2. **Role mismatch.** Child-role users cannot access financial endpoints (budget, insurance, equity, utility bills, returns, repair fund). This is by design — the API returns empty results, not errors, for financial endpoints. A 403 usually means the user lacks the `Home User` Frappe role entirely.
3. **Archived property.** Some actions are blocked on archived properties. Unarchive the property first.

**Diagnosis:**

```python
# In bench console:
frappe.get_all("Home Household Member", filters={"user": "user@example.com"})
```

---

## Archived properties blocking actions

**Symptom:** User cannot create items, rooms, or maintenance tasks for a property.

**Cause:** The property is archived. Archived properties are read-only — no new child records can be created.

**Fix:** An Owner must unarchive the property via `home.api.property.unarchive_property` before new records can be added.

---

## Child role seeing limited data

**Symptom:** A household member reports missing sections in the dashboard — no budget, no bills, no insurance.

**Cause:** This is expected behavior. Child-role members cannot view financial data. The API returns empty results for financial endpoints when the requesting user has the Child role.

**Verification:**

```python
# Check the user's household role:
frappe.get_value("Home Household Member",
    {"user": "user@example.com", "parent": "household-name"},
    "role")
```

To grant financial access, an Owner must change the member's role to Adult.

---

## Health score seems wrong

**Symptom:** Property health score is unexpectedly low.

**Cause:** The health score is calculated from 8 deduction factors. Each factor can deduct up to 10-20 points from a base of 100. Common culprits:

| Factor | Max Deduction | Common Trigger |
|--------|--------------|----------------|
| Overdue maintenance | -20 | Forgotten seasonal tasks |
| Expired warranties | -15 | Warranties past end date |
| Missing insurance | -15 | No active policy on property |
| Empty rooms | -10 | Rooms created but no items assigned |

**Diagnosis:** Call `home.api.health.get_health_score` with the property name. The response includes a `factors` array listing each active deduction with its description.

---

## Recall checks return no results

**Symptom:** `check_recall` always returns `{has_recall: false}`.

**Cause:** Recall matching depends on item metadata (brand, model, serial number). Items without these fields cannot be matched against recall databases.

**Fix:** Ensure items have at minimum a brand and model populated. Serial numbers improve matching accuracy.

---

## Utility bill trends show "insufficient data"

**Symptom:** `get_consumption_trends` returns an error or empty trends.

**Cause:** Trend calculation requires at least 2 months of utility bill data for the same utility type. The `months` parameter defaults to 12, but the endpoint needs at least 2 data points to compute percentage changes.

**Fix:** Enter utility bill data for at least 2 consecutive months. For meaningful trends, 6-12 months of data is recommended.

---

## OCR extraction returns low-confidence results

**Symptom:** `extract_from_image` returns results with low confidence scores or incorrect data.

**Cause:** OCR accuracy depends on image quality, lighting, and text clarity. Common issues:

- Blurry or low-resolution photos
- Glare on labels or packaging
- Handwritten text (not supported)
- Non-English text (limited support)

**Workaround:** Use a well-lit, focused photo of the item's label or packaging. Crop to show only the relevant text. If OCR fails, enter item details manually.

**Note:** This feature requires Jana to be installed. Without Jana, the endpoint returns a "Jana not installed" error.

---

## Guest portal token expired

**Symptom:** Guest link returns "Session expired" or "Invalid token".

**Cause:** Guest sessions have a configurable expiry (default set in Dock Settings). Once expired, the token is no longer valid.

**Fix:** The property owner must create a new guest session. Guest sessions can be managed via the property detail view or directly via `dock.api.guest.create_session`.

**Prevention:** Set a longer `expires_in_days` when creating the session, or configure the default expiry in Dock Settings.

---

## Home Settings not appearing in Dock Settings

**Symptom:** The Home section does not appear in Dock's unified settings panel.

**Cause:** The `home-settings.esm.js` bundle may not be built, or the `dock_settings_sections` hook is not being read.

**Fix:**

```bash
# Rebuild Home frontend assets:
cd apps/home/frontend
npm install
npm run build

# Clear cache:
bench --site your-site.localhost clear-cache
```

If the issue persists, verify that `dock_settings_sections` is declared in `home/hooks.py` and that Dock is installed.

---

## Single DocType sync issue after migrate

**Symptom:** `Home Settings` behaves like a regular DocType instead of a Single DocType after running `bench migrate`.

**Cause:** Known Frappe v16 issue where `issingle` flag may reset during migration.

**Fix:**

```python
# In bench console:
frappe.db.sql("UPDATE `tabDocType` SET issingle=1 WHERE name='Home Settings'")
frappe.db.commit()
```
