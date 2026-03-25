# API Reference

All endpoints use the Frappe RPC convention:

```
POST /api/method/home.api.<module>.<function>
Content-Type: application/json
```

Authenticated via Frappe session cookie or token. Methods marked **(guest)** accept unauthenticated requests. Methods marked **(Adult+)** require Adult or Owner household role.

---

## Permission

### `get_user_households`

```
home.api.permission.get_user_households
```

**Returns:** `[{name, household_name, role, property_count}, ...]`

### `get_my_role`

```
home.api.permission.get_my_role
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `household` | string | Household name |

**Returns:** `{role}` — one of `Owner`, `Adult`, `Child`

### `has_app_permission`

```
home.api.permission.has_app_permission
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | string | Permission action to check |
| `household` | string | Household name |

**Returns:** `{allowed: bool}`

---

## Onboarding

### `get_onboarding_status`

```
home.api.onboarding.get_onboarding_status
```

**Returns:** `{has_household, has_property, has_room, has_item, completed}`

### `complete_onboarding`

```
home.api.onboarding.complete_onboarding
```

Marks the onboarding flow as completed for the current user.

**Returns:** `{success: true}`

---

## Household

### `create_household`

**(Adult+)**

```
home.api.household.create_household
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *(required)* | Household display name |

The creating user is automatically assigned the Owner role.

**Returns:** `{name, household_name, role}`

### `invite_member`

**(Owner only)**

```
home.api.household.invite_member
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `household` | string | *(required)* | Household name |
| `email` | string | *(required)* | User email |
| `role` | string | `"Adult"` | `Owner`, `Adult`, or `Child` |

**Returns:** `{member_name, email, role}`

---

## Property

### `get_dashboard`

```
home.api.property.get_dashboard
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

**Returns:** `{property, rooms, item_count, maintenance_due, warranty_expiring, health_score, equity, recent_activity}`

### `list_properties`

```
home.api.property.list_properties
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `household` | string | `None` | Filter by household |
| `include_archived` | bool | `False` | Include archived properties |

**Returns:** `[{name, property_name, address, type, status, room_count, item_count, health_score}, ...]`

### `get_property`

```
home.api.property.get_property
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Property name |

**Returns:** full property document with rooms, emergency contacts, and summary stats

### `create_property`

**(Adult+)**

```
home.api.property.create_property
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `household` | string | *(required)* | Household name |
| `property_name` | string | *(required)* | Display name |
| `address` | string | `None` | Property address |
| `type` | string | `"House"` | `House`, `Apartment`, `Unit`, `Other` |

**Returns:** property document

### `update_property`

**(Adult+)**

```
home.api.property.update_property
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Property name |
| `**fields` | any | Editable fields |

**Returns:** updated property document

### `archive_property`

**(Owner only)**

```
home.api.property.archive_property
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Property name |

Archived properties are excluded from listings and dashboards by default. Items and maintenance tasks remain intact but inactive.

**Returns:** `{archived: true}`

### `unarchive_property`

**(Owner only)**

```
home.api.property.unarchive_property
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Property name |

**Returns:** `{archived: false}`

### `update_emergency_info`

**(Adult+)**

```
home.api.property.update_emergency_info
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |
| `contacts` | list | `[{name, phone, relationship, notes}]` |

**Returns:** `{updated: true}`

---

## Room

### `get_rooms`

```
home.api.room.get_rooms
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

**Returns:** `[{name, room_name, room_type, floor, item_count}, ...]`

### `get_unassigned_counts`

```
home.api.room.get_unassigned_counts
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

**Returns:** `{items: int, maintenance: int}` — counts of records not assigned to any room

### `create_room`

**(Adult+)**

```
home.api.room.create_room
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | *(required)* | Property name |
| `room_name` | string | *(required)* | Display name |
| `room_type` | string | `None` | e.g. `Bedroom`, `Kitchen`, `Bathroom` |
| `floor` | int | `None` | Floor number |

**Returns:** room document

### `update_room`

**(Adult+)**

```
home.api.room.update_room
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Room name |
| `**fields` | any | Editable fields |

**Returns:** updated room document

---

## Item

### `get_items`

```
home.api.item.get_items
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `room` | string | `None` | Filter by room |
| `category` | string | `None` | Filter by category |
| `status` | string | `None` | `Active`, `Disposed`, `Returned` |
| `search` | string | `None` | Text search |
| `limit` | int | `20` | |
| `offset` | int | `0` | |

**Returns:** `{items: [...], total: int}`

### `get_item`

```
home.api.item.get_item
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Item name |

**Returns:** full item document with warranty, photos, recall status, and lifespan info

### `create_return_from_disposal`

**(Adult+)**

```
home.api.item.create_return_from_disposal
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `item` | string | Item name |
| `reason` | string | Return reason |
| `receipt_number` | string | Purchase receipt or order number |

Creates a `Home Purchase Return` linked to the item. **Returns:** return document

### `get_insurance_summary`

**(Adult+)**

```
home.api.item.get_insurance_summary
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `item` | string | Item name |

**Returns:** `{covered: bool, policy_name, coverage_amount, expiry_date}`

### `get_health`

```
home.api.item.get_health
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `item` | string | Item name |

**Returns:** `{score: int, factors: [{name, deduction, description}]}`

### `extract_from_image`

**(Adult+)**

```
home.api.item.extract_from_image
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `image` | string | File URL or base64 |

Requires Jana. Uses OCR to extract item details (brand, model, serial number) from a photo. **Returns:** `{brand, model, serial_number, category, confidence}`

### `lookup_barcode`

```
home.api.item.lookup_barcode
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `barcode` | string | UPC/EAN barcode |

**Returns:** `{found: bool, product_name, brand, category, image_url}`

### `check_recall`

```
home.api.item.check_recall
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `item` | string | Item name |

Checks item against known recalls. **Returns:** `{has_recall: bool, recalls: [{recall_name, description, severity, date}]}`

### `export_pdf`

```
home.api.item.export_pdf
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `items` | list | List of item names |

**Returns:** PDF file URL

### `export_csv`

```
home.api.item.export_csv
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `category` | string | `None` | Filter by category |

**Returns:** CSV file URL

---

## Maintenance

### `get_maintenance_list`

```
home.api.maintenance.get_maintenance_list
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `status` | string | `None` | `Pending`, `Overdue`, `Completed` |
| `limit` | int | `20` | |
| `offset` | int | `0` | |

**Returns:** `{tasks: [...], total: int}`

### `get_task`

```
home.api.maintenance.get_task
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Task name |

**Returns:** full maintenance task document

### `complete_task`

**(Adult+)**

```
home.api.maintenance.complete_task
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *(required)* | Task name |
| `notes` | string | `None` | Completion notes |
| `cost` | float | `None` | Cost incurred |

**Returns:** `{completed: true, next_due: date|null}`

---

## Warranty

### `get_warranties`

```
home.api.warranty.get_warranties
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `status` | string | `None` | `Active`, `Expiring`, `Expired` |
| `limit` | int | `20` | |
| `offset` | int | `0` | |

**Returns:** `{warranties: [...], total: int}`

### `get_warranty`

```
home.api.warranty.get_warranty
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Warranty name |

**Returns:** full warranty document with claims

### `get_property_warranties`

```
home.api.warranty.get_property_warranties
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

**Returns:** `[{name, item, warranty_type, provider, start_date, end_date, status}, ...]`

---

## Utility Bills

### `get_bills`

**(Adult+)**

```
home.api.utility.get_bills
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | *(required)* | Property name |
| `utility_type` | string | `None` | `Electric`, `Gas`, `Water`, `Internet`, etc. |
| `status` | string | `None` | `Paid`, `Unpaid`, `Overdue` |
| `limit` | int | `20` | |
| `offset` | int | `0` | |

**Returns:** `{bills: [...], total: int}`

### `mark_paid`

**(Adult+)**

```
home.api.utility.mark_paid
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *(required)* | Bill name |
| `paid_date` | string | today | ISO date |

**Returns:** `{paid: true}`

### `get_consumption_trends`

**(Adult+)**

```
home.api.utility.get_consumption_trends
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | *(required)* | Property name |
| `utility_type` | string | `None` | Filter by type |
| `months` | int | `12` | Number of months to include |

Requires at least 2 months of data to calculate trends. Returns monthly consumption and cost with percentage changes.

**Returns:** `{trends: [{month, consumption, cost, change_pct}], average_monthly_cost}`

---

## Budget

### `get_overview`

**(Adult+)**

```
home.api.budget.get_overview
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `household` | string | Household name |
| `period` | string | `monthly` or `yearly` |

**Returns:** `{budget_name, total_target, total_spent, remaining, lines: [{category, target, spent, remaining}]}`

### `suggest_targets`

**(Adult+)**

```
home.api.budget.suggest_targets
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `household` | string | Household name |

Analyzes past spending to suggest budget targets per category.

**Returns:** `[{category, suggested_target, based_on_months, average_spend}]`

---

## Insurance

### `get_policies`

**(Adult+)**

```
home.api.insurance.get_policies
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `status` | string | `None` | `Active`, `Expiring`, `Expired` |

**Returns:** `[{name, policy_number, provider, type, coverage_amount, premium, start_date, end_date, status}, ...]`

### `get_policy`

**(Adult+)**

```
home.api.insurance.get_policy
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Policy name |

**Returns:** full policy document with claims

---

## Equity

### `get_equity`

**(Adult+)**

```
home.api.equity.get_equity
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

**Returns:** `{current_value, purchase_price, mortgage_balance, equity, appreciation_pct, snapshots: [{date, value}]}`

### `update_value`

**(Owner only)**

```
home.api.equity.update_value
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | *(required)* | Property name |
| `value` | float | *(required)* | New estimated value |
| `source` | string | `"manual"` | Valuation source |

Creates a new `Home Equity Snapshot`. **Returns:** `{snapshot_name, value, date}`

---

## Health Score

### `get_health_score`

```
home.api.health.get_health_score
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | string | Property name |

Calculates a 0-100 health score for the property based on 8 deduction factors:

| Factor | Max Deduction | Trigger |
|--------|--------------|---------|
| Overdue maintenance | -20 | Any maintenance task past its due date |
| Expired warranties | -15 | Warranties that have lapsed without renewal |
| Missing insurance | -15 | No active insurance policy on the property |
| Overdue utility bills | -10 | Unpaid bills past their due date |
| No emergency contacts | -10 | Property has zero emergency contacts |
| Stale equity data | -10 | Last equity snapshot older than 12 months |
| Unresolved recalls | -10 | Items with active recall notices not dismissed |
| Empty rooms | -10 | Rooms with no items assigned |

**Returns:** `{score: int, factors: [{name, deduction, description}], grade}`

Grade mapping: 90-100 = Excellent, 70-89 = Good, 50-69 = Fair, 0-49 = Poor.

---

## Repair Fund

### `get_repair_fund`

**(Adult+)**

```
home.api.repair_fund.get_repair_fund
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `household` | string | Household name |

**Returns:** `{target, current_balance, monthly_contribution, months_to_target}`

---

## Returns

### `get_returns`

**(Adult+)**

```
home.api.returns.get_returns
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `property` | string | `None` | Filter by property |
| `status` | string | `None` | `Pending`, `Completed`, `Overdue` |
| `limit` | int | `20` | |
| `offset` | int | `0` | |

**Returns:** `{returns: [...], total: int}`

### `get_return`

**(Adult+)**

```
home.api.returns.get_return
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Return name |

**Returns:** full return document

---

## Recall

### `dismiss_recall`

**(Adult+)**

```
home.api.recall.dismiss_recall
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Recall name |

Marks a recall notice as reviewed/dismissed. **Returns:** `{dismissed: true}`

### `check_single_item`

```
home.api.recall.check_single_item
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `item` | string | Item name |

**Returns:** `{has_recall: bool, recalls: [...]}`

---

## Correspondence

### `get_templates`

```
home.api.correspondence.get_templates
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | `None` | Template category filter |

**Returns:** `[{name, title, category, description}, ...]`

### `render_draft`

**(Adult+)**

```
home.api.correspondence.render_draft
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `template` | string | Template name |
| `context` | dict | Variable substitutions |

Renders a letter template with the provided context. **Returns:** `{html, subject}`

### `export_pdf`

**(Adult+)**

```
home.api.correspondence.export_pdf
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `letter` | string | Generated letter name |

**Returns:** PDF file URL

---

## Guest Portal

### `get_property_guest` **(guest)**

```
home.api.frame.get_property_guest
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | Guest session token |

No authentication required. Validates the token via Dock's guest portal, then returns a read-only property summary.

**Returns:** `{property_name, address, type, rooms: [{name, type}], emergency_contacts: [{name, phone}], photo_url}`
