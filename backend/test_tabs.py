"""
TabSense Backend — End-to-End API Test Suite
Run: python test_tabs.py
Requires: pip install requests
Backend must be running at http://127.0.0.1:8000
"""

import json
import sys
import requests

BASE_URL = "http://127.0.0.1:8000"

# ── Helpers ────────────────────────────────────────────────────────────────────

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"
SECTION = "\033[1;95m"
RESET = "\033[0m"

results = []


def section(title: str):
    print(f"\n{SECTION}{'─' * 60}{RESET}")
    print(f"{SECTION}  {title}{RESET}")
    print(f"{SECTION}{'─' * 60}{RESET}")


def check(label: str, response: requests.Response, expected_status: int):
    """Print result, record pass/fail."""
    ok = response.status_code == expected_status
    badge = PASS if ok else FAIL
    print(f"\n{badge} {label}")
    print(f"  Status : {response.status_code}  (expected {expected_status})")
    try:
        body = response.json()
        print(f"  Response: {json.dumps(body, indent=4, default=str)}")
    except Exception:
        print(f"  Response (raw): {response.text[:300]}")
    results.append((label, ok))
    return response


def summary():
    section("TEST SUMMARY")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for label, ok in results:
        badge = PASS if ok else FAIL
        print(f"  {badge} {label}")
    print(f"\n  {passed}/{total} tests passed.")
    if passed < total:
        sys.exit(1)


# ── Health Check ───────────────────────────────────────────────────────────────

section("0. Health Check")

r = requests.get(f"{BASE_URL}/health")
check("GET /health — backend is reachable", r, 200)

r = requests.get(f"{BASE_URL}/")
check("GET / — root route", r, 200)


# ── Settings ───────────────────────────────────────────────────────────────────

section("1. User Settings")

r = requests.get(f"{BASE_URL}/settings/")
check("GET /settings/ — fetch defaults", r, 200)

r = requests.patch(f"{BASE_URL}/settings/", json={
    "default_inactivity_threshold": 900,
    "notifications_enabled": True,
    "ai_summaries_enabled": True,
    "auto_close_enabled_globally": False,
})
check("PATCH /settings/ — update preferences", r, 200)


# ── Create Tabs ────────────────────────────────────────────────────────────────

section("2. POST /tabs/ — Create Tabs")

browser_tab_payload = {
    "type": "browser_tab",
    "title": "TabSense GitHub",
    "url": "https://github.com/tabsense/tabsense",
    "favicon_url": "https://github.com/favicon.ico",
    "inactivity_threshold": 60,   # 60 seconds — low so inactivity tests fire
    "auto_close_enabled": False,
}

r = check(
    "POST /tabs/ — create browser tab",
    requests.post(f"{BASE_URL}/tabs/", json=browser_tab_payload),
    201,
)
browser_tab_id = r.json().get("id")
print(f"{INFO} Created browser_tab id={browser_tab_id}")

desktop_app_payload = {
    "type": "desktop_app",
    "app_name": "Figma",
    "title": "Figma — TabSense UI Design",
    "inactivity_threshold": 60,
    "auto_close_enabled": True,   # This one WILL be auto-closed
}

r = check(
    "POST /tabs/ — create desktop app (auto-close enabled)",
    requests.post(f"{BASE_URL}/tabs/", json=desktop_app_payload),
    201,
)
desktop_app_id = r.json().get("id")
print(f"{INFO} Created desktop_app id={desktop_app_id}")


# ── Bad Input Validation ───────────────────────────────────────────────────────

section("3. Input Validation")

r = check(
    "POST /tabs/ — missing required 'type' field (expect 422)",
    requests.post(f"{BASE_URL}/tabs/", json={"title": "No type"}),
    422,
)

r = check(
    "POST /tabs/ — invalid type value (expect 422)",
    requests.post(f"{BASE_URL}/tabs/", json={"type": "fax_machine", "title": "Old tech"}),
    422,
)


# ── List & Get Tabs ────────────────────────────────────────────────────────────

section("4. GET /tabs/ — List and Retrieve")

r = check("GET /tabs/ — list all tabs", requests.get(f"{BASE_URL}/tabs/"), 200)

r = check(
    "GET /tabs/?status=active — filter by status",
    requests.get(f"{BASE_URL}/tabs/", params={"status": "active"}),
    200,
)

r = check(
    "GET /tabs/?search=figma — search by title/app_name",
    requests.get(f"{BASE_URL}/tabs/", params={"search": "figma"}),
    200,
)
assert any(t["id"] == desktop_app_id for t in r.json()), "Search should return Figma tab"

r = check(
    f"GET /tabs/{browser_tab_id} — get by ID",
    requests.get(f"{BASE_URL}/tabs/{browser_tab_id}"),
    200,
)

r = check(
    "GET /tabs/999999 — non-existent ID (expect 404)",
    requests.get(f"{BASE_URL}/tabs/999999"),
    404,
)


# ── Update Tab ─────────────────────────────────────────────────────────────────

section("5. PATCH /tabs/{id} — Update Tab")

r = check(
    f"PATCH /tabs/{browser_tab_id} — update title and threshold",
    requests.patch(f"{BASE_URL}/tabs/{browser_tab_id}", json={
        "title": "TabSense GitHub (Updated)",
        "inactivity_threshold": 120,
    }),
    200,
)
assert r.json()["title"] == "TabSense GitHub (Updated)", "Title should be updated"

r = check(
    f"PATCH /tabs/{browser_tab_id} — simulate activity ping (update last_active_at)",
    requests.patch(f"{BASE_URL}/tabs/{browser_tab_id}", json={
        "last_active_at": "2025-01-01T00:00:00Z",  # Old timestamp to trigger inactivity
    }),
    200,
)

r = check(
    f"PATCH /tabs/{desktop_app_id} — set old last_active_at on auto-close tab",
    requests.patch(f"{BASE_URL}/tabs/{desktop_app_id}", json={
        "last_active_at": "2025-01-01T00:00:00Z",
    }),
    200,
)


# ── AI Summaries ───────────────────────────────────────────────────────────────

section("6. POST /summaries/ — AI Summary Generation")

r = check(
    f"POST /summaries/ — generate summary for browser tab (id={browser_tab_id})",
    requests.post(f"{BASE_URL}/summaries/", json={"tab_id": browser_tab_id}),
    200,
)
summary_data = r.json()
assert "summary" in summary_data, "Response must contain 'summary'"
assert summary_data["tab_id"] == browser_tab_id

r = check(
    f"POST /summaries/ — generate summary for desktop app (id={desktop_app_id})",
    requests.post(f"{BASE_URL}/summaries/", json={"tab_id": desktop_app_id}),
    200,
)

r = check(
    "POST /summaries/ — non-existent tab_id (expect 404)",
    requests.post(f"{BASE_URL}/summaries/", json={"tab_id": 999999}),
    404,
)

r = check(
    "POST /summaries/batch — summarize all tabs without summaries",
    requests.post(f"{BASE_URL}/summaries/batch"),
    200,
)


# ── Inactivity ─────────────────────────────────────────────────────────────────

section("7. GET /inactivity/check — Detect Inactive Tabs")

r = check(
    "GET /inactivity/check — scan for inactive tabs",
    requests.get(f"{BASE_URL}/inactivity/check"),
    200,
)
inactive_tabs = r.json()
print(f"{INFO} Found {len(inactive_tabs)} inactive tab(s)")
for item in inactive_tabs:
    print(f"  tab_id={item['tab']['id']} | inactive_for={item['inactive_for_seconds']:.0f}s | will_auto_close={item['will_auto_close']}")

section("8. POST /inactivity/process — Mark Inactive + Auto-Close")

r = check(
    "POST /inactivity/process — process all inactive tabs",
    requests.post(f"{BASE_URL}/inactivity/process"),
    200,
)
processed = r.json()
print(f"{INFO} Processed {len(processed)} tab(s)")
for tab in processed:
    print(f"  tab_id={tab['id']} | new status={tab['status']}")


# ── Close Tabs ─────────────────────────────────────────────────────────────────

section("9. POST /tabs/{id}/close — Close Tabs")

# Create a fresh tab to close manually (so we don't depend on previous state)
r = requests.post(f"{BASE_URL}/tabs/", json={
    "type": "browser_tab",
    "title": "Tab to Close Manually",
    "url": "https://example.com",
})
close_tab_id = r.json().get("id")
print(f"{INFO} Created tab id={close_tab_id} for manual close test")

r = check(
    f"POST /tabs/{close_tab_id}/close — manual close",
    requests.post(f"{BASE_URL}/tabs/{close_tab_id}/close", params={"auto": False}),
    200,
)
assert r.json()["status"] == "manually_closed"

# Create another fresh tab for auto-close test
r = requests.post(f"{BASE_URL}/tabs/", json={
    "type": "browser_tab",
    "title": "Tab to Auto-Close",
    "url": "https://example.com/auto",
    "auto_close_enabled": True,
})
auto_close_tab_id = r.json().get("id")
print(f"{INFO} Created tab id={auto_close_tab_id} for auto close test")

r = check(
    f"POST /tabs/{auto_close_tab_id}/close?auto=true — auto close",
    requests.post(f"{BASE_URL}/tabs/{auto_close_tab_id}/close", params={"auto": True}),
    200,
)
assert r.json()["status"] == "auto_closed"

r = check(
    "POST /tabs/999999/close — non-existent tab (expect 404)",
    requests.post(f"{BASE_URL}/tabs/999999/close"),
    404,
)


# ── Events ─────────────────────────────────────────────────────────────────────

section("10. GET /events/ — Event Log")

r = check(
    f"GET /tabs/{browser_tab_id}/events — full event history for browser tab",
    requests.get(f"{BASE_URL}/tabs/{browser_tab_id}/events"),
    200,
)
events_list = r.json()
print(f"{INFO} {len(events_list)} event(s) found for tab_id={browser_tab_id}")
for ev in events_list:
    print(f"  event_id={ev['id']} | type={ev['type']} | timestamp={ev['timestamp']}")

r = check(
    "GET /events/ — list all events",
    requests.get(f"{BASE_URL}/events/"),
    200,
)

r = check(
    f"GET /events/?tab_id={browser_tab_id} — filter by tab_id",
    requests.get(f"{BASE_URL}/events/", params={"tab_id": browser_tab_id}),
    200,
)

r = check(
    "GET /events/?type=summary_generated — filter by event type",
    requests.get(f"{BASE_URL}/events/", params={"type": "summary_generated"}),
    200,
)

r = check(
    "POST /events/ — manually log a custom event",
    requests.post(f"{BASE_URL}/events/", json={
        "tab_id": browser_tab_id,
        "type": "activated",
        "details": '{"source": "manual_test"}',
    }),
    201,
)


# ── Delete Tab ─────────────────────────────────────────────────────────────────

section("11. DELETE /tabs/{id} — Remove Tab")

# Create a throwaway tab to delete
r = requests.post(f"{BASE_URL}/tabs/", json={
    "type": "browser_tab",
    "title": "Throwaway tab for delete test",
    "url": "https://delete-me.example.com",
})
delete_tab_id = r.json().get("id")
print(f"{INFO} Created throwaway tab id={delete_tab_id}")

r = check(
    f"DELETE /tabs/{delete_tab_id} — delete tab (expect 204)",
    requests.delete(f"{BASE_URL}/tabs/{delete_tab_id}"),
    204,
)

r = check(
    f"GET /tabs/{delete_tab_id} — verify deleted (expect 404)",
    requests.get(f"{BASE_URL}/tabs/{delete_tab_id}"),
    404,
)

r = check(
    "DELETE /tabs/999999 — non-existent tab (expect 404)",
    requests.delete(f"{BASE_URL}/tabs/999999"),
    404,
)


# ── Final Summary ──────────────────────────────────────────────────────────────

summary()
