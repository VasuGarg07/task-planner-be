"""
Seeds the task_planner database with realistic test data by driving the
real Flask API (not raw SQL), so state-machine transitions and the
@log_action middleware fire and populate the `logs` audit table.

Requires the Flask app to already be running on BASE_URL.

Usage:
    python scripts/seed_via_api.py
"""
import json
import random
from datetime import date, timedelta

import psycopg2
import requests

BASE_URL = "http://localhost:5000"

with open("config.json") as f:
    DB_CONFIG = json.load(f)


def reset_database():
    """Truncate all tables so the API seed starts from a clean slate."""
    conn = psycopg2.connect(
        host=DB_CONFIG.get("DB_HOST", "localhost"),
        port=5432,
        user="postgres",
        password=DB_CONFIG.get("DB_PASSWORD"),
        dbname="task_planner",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE logs, tasks, sprints, projects, users RESTART IDENTITY CASCADE;")
    cur.close()
    conn.close()
    print("Database truncated.")


USERS = [
    ("priya.nair", "priya.nair@zenlayer.dev", "PM"),
    ("daniel.osei", "daniel.osei@zenlayer.dev", "DEV"),
    ("sara.holm", "sara.holm@zenlayer.dev", "QA"),
    ("fatima.al-sayed", "fatima.alsayed@zenlayer.dev", "BA"),
    ("ines.fischer", "ines.fischer@zenlayer.dev", "DEV-OPS"),
]

PROJECTS = [
    # (name, description, sprint_count, task_count, target_status)
    ("Customer Portal Redesign",
     "Overhaul of the self-service customer portal, moving from legacy jQuery views to a component-based frontend.",
     2, 15, "IN PROGRESS"),
    ("Payment Gateway Migration",
     "Migrate checkout and subscription billing onto the new PCI-compliant gateway with retry and webhook handling.",
     4, 20, "DISCOVERY"),
]

PROJECT_TRANSITIONS_PATH = {
    "NOT STARTED": [],
    "DISCOVERY": ["DISCOVERY"],
    "IN PROGRESS": ["DISCOVERY", "IN PROGRESS"],
    "COMPLETED": ["DISCOVERY", "IN PROGRESS", "COMPLETED"],
}

TASK_POOL = [
    ("Fix login redirect loop on Safari", "Users on Safari get stuck bouncing between /login and /dashboard after SSO callback."),
    ("Add pagination to task list endpoint", "GET /tasks currently returns all rows unbounded; add limit/offset with sane defaults."),
    ("Write unit tests for sprint capacity service", "Cover edge cases where story points exceed max_capacity and where sprint has zero tasks."),
    ("Investigate slow query on projects dashboard", "Dashboard load time spikes above 2s when a project has 500+ tasks."),
    ("Add webhook retry logic for failed payment events", "Currently a single failed delivery is dropped silently; add exponential backoff."),
    ("Design empty-state UI for analytics dashboard", "No mockup yet for when a team has no data in the selected date range."),
    ("Migrate legacy billing table to new schema", "Old billing_records table lacks foreign keys and has duplicate rows to dedupe."),
    ("Set up staging environment for payment gateway", "Needed before QA can run end-to-end checkout tests against sandbox credentials."),
    ("Fix flaky end-to-end test for checkout flow", "Test fails intermittently on CI, passes locally; suspect race condition in test setup."),
    ("Add rate limiting to public API endpoints", "Currently no throttling, exposing the service to abuse from unauthenticated clients."),
    ("Refactor auth middleware to support API keys", "Product wants third-party integrations to authenticate via API key, not just session cookies."),
    ("Update push notification templates for iOS 18", "New OS version changed how rich notification payloads render."),
    ("Write runbook for on-call rotation", "No documented steps for common incidents like DB connection pool exhaustion."),
    ("Add index on tasks.sprint_id", "Sprint capacity queries are doing sequential scans on the tasks table."),
    ("Build CSV export for support ticket volume", "Support lead wants a weekly export they can open in Excel."),
    ("Patch XSS vulnerability in comment rendering", "User-submitted comment text is rendered without sanitization on the task detail page."),
    ("Add dark mode support to customer portal", "Design team delivered dark mode mockups for the account settings pages."),
    ("Reduce cold start time for notification worker", "Worker takes 8s to become ready after deploy, causing dropped jobs during rollout."),
    ("Write integration tests for webhook signature verification", "No test coverage for rejecting payloads with invalid signatures."),
    ("Clean up unused feature flags from last quarter", "Several flags are fully rolled out but still gating code paths, adding complexity."),
    ("Add retry queue for failed email sends", "Transactional emails silently fail when the provider returns a 5xx."),
    ("Improve error messages on signup form validation", "Users report confusion over generic \"invalid input\" messages."),
    ("Set up centralized logging for payment service", "Currently logs only go to stdout, making incident debugging painful."),
    ("Add database backup verification job", "Backups run nightly but nobody verifies they can actually be restored."),
    ("Optimize image upload pipeline for profile photos", "Large uploads are not resized server-side, bloating storage costs."),
    ("Draft API documentation for external partners", "Partner integrations team has been asking for OpenAPI spec for two sprints."),
    ("Add feature flag for new checkout UI rollout", "Need gradual rollout capability before full launch to all users."),
    ("Fix timezone bug in sprint burndown calculation", "Dates are compared without normalizing timezone, causing off-by-one errors."),
    ("Harden input validation on task creation endpoint", "Missing validation allows empty task names and negative story points."),
    ("Spike: evaluate message queue options for notifications", "Compare RabbitMQ vs SQS for the new notification worker architecture."),
    ("Add CI pipeline caching for faster builds", "Build times increased significantly after adding new test suites, slowing down PR feedback loops."),
    ("Fix duplicate charge bug in subscription renewal", "Some customers are billed twice when a subscription renews on a failed card retry."),
    ("Add health check endpoint for notification worker", "Kubernetes cannot currently tell if the worker pod is ready to receive jobs."),
    ("Write migration script for legacy user roles", "Old role names (admin, member) need mapping to the new RBAC role enum."),
    ("Add search functionality to task list view", "Users want to filter tasks by keyword without scrolling through pages."),
    ("Fix broken pagination links on mobile viewport", "Next/prev buttons overlap with content on screens under 400px wide."),
    ("Add Slack alert integration for failed deployments", "On-call currently only finds out about failed deploys by checking CI manually."),
    ("Optimize N+1 query on task list with assignee join", "Task list endpoint issues one query per task to fetch assignee details."),
    ("Add soft delete support for projects", "Deleting a project currently cascades and permanently removes all tasks and sprints."),
    ("Write load test for checkout endpoint", "Need to validate the payment gateway migration can handle peak Black Friday traffic."),
]

TASK_STATUS_WEIGHTS = [
    ("OPEN", []),
    ("IN PROGRESS", ["IN PROGRESS"]),
    ("DONE", ["IN PROGRESS", "DONE"]),
    ("ON HOLD", ["ON HOLD"]),
    ("VOID", ["VOID"]),
]
TASK_STATUS_PROBABILITY = [0.25, 0.2, 0.3, 0.15, 0.1]

STORY_POINTS = [1, 2, 3, 5, 8]


def headers_for(email):
    return {"X-User-Email": email, "Content-Type": "application/json"}


def post(path, email, payload):
    resp = requests.post(f"{BASE_URL}{path}", headers=headers_for(email), json=payload)
    if resp.status_code not in (200, 201):
        print(f"  ! POST {path} failed ({resp.status_code}): {resp.text.strip()}")
        return None
    return resp.json()


def patch(path, email, payload):
    resp = requests.patch(f"{BASE_URL}{path}", headers=headers_for(email), json=payload)
    if resp.status_code != 200:
        print(f"  ! PATCH {path} failed ({resp.status_code}): {resp.text.strip()}")
        return None
    return resp.json()


def seed_users():
    print("Creating users...")
    email_to_id = {}
    for username, email, role in USERS:
        result = post("/users", email, {"username": username, "email": email, "role": role})
        if result:
            email_to_id[email] = result["id"]
    print(f"  {len(email_to_id)} users created.")
    return email_to_id


def seed_projects_and_sprints(pm_email):
    print("Creating projects and sprints...")
    project_ids = []
    all_sprint_ids = {}  # project_id -> [sprint_id, ...]

    for name, description, sprint_count, task_count, target_status in PROJECTS:
        result = post("/projects", pm_email, {"name": name, "description": description})
        project_id = result["project_id"]
        project_ids.append(project_id)

        for step_status in PROJECT_TRANSITIONS_PATH[target_status]:
            patch(f"/projects/{project_id}/status", pm_email, {"status": step_status})

        sprint_ids = []
        today = date.today()
        for n in range(1, sprint_count + 1):
            offset_weeks = sprint_count - n + 1
            start = today - timedelta(weeks=2 * offset_weeks)
            end = start + timedelta(days=13)
            max_capacity = 20 + n * 5

            result = post("/sprints", pm_email, {
                "project_id": project_id,
                "name": f"Sprint {n}",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "max_capacity": max_capacity,
            })
            sprint_id = result["sprint_id"]
            sprint_ids.append(sprint_id)

            if end < today:
                patch(f"/sprints/{sprint_id}/status", pm_email, {"status": "ACTIVE"})
                patch(f"/sprints/{sprint_id}/status", pm_email, {"status": "COMPLETED"})
            elif start <= today <= end:
                patch(f"/sprints/{sprint_id}/status", pm_email, {"status": "ACTIVE"})
            # else: stays PLANNING

        all_sprint_ids[project_id] = sprint_ids

    print(f"  {len(project_ids)} projects, {sum(len(v) for v in all_sprint_ids.values())} sprints created.")
    return project_ids, all_sprint_ids


def seed_tasks(project_ids, all_sprint_ids, email_to_id, pm_email):
    print("Creating tasks...")
    dev_emails = [u[1] for u in USERS]
    total_created = 0

    for (name, description, sprint_count, task_count, _), project_id in zip(PROJECTS, project_ids):
        titles = random.sample(TASK_POOL, task_count)
        sprint_ids = all_sprint_ids[project_id]

        for title, desc in titles:
            reporter_email = random.choice(dev_emails)
            assignee_id = email_to_id[random.choice(dev_emails)]

            result = post("/tasks", reporter_email, {
                "project_id": project_id,
                "name": title,
                "description": desc,
                "assignee_id": assignee_id,
            })
            if result is None:
                continue
            task_id = result["task_id"]
            total_created += 1

            # Occasionally reassign, to generate a realistic reassignment log entry
            if random.random() < 0.2:
                new_assignee_id = email_to_id[random.choice(dev_emails)]
                patch(f"/tasks/{task_id}/assign", reporter_email, {"assignee_id": new_assignee_id})

            points = random.choice(STORY_POINTS)
            patch(f"/tasks/{task_id}/story-points", reporter_email, {"story_points": points})

            # Randomly assign into a sprint if capacity allows
            if sprint_ids and random.random() < 0.7:
                sprint_id = random.choice(sprint_ids)
                patch(f"/sprints/{sprint_id}/add-task", pm_email, {"task_id": task_id})

            # Walk the task through a realistic status path
            target_status, path = random.choices(TASK_STATUS_WEIGHTS, weights=TASK_STATUS_PROBABILITY)[0]
            for step_status in path:
                patch(f"/tasks/{task_id}/status", reporter_email, {"status": step_status})

    print(f"  {total_created} tasks created.")


def main():
    reset_database()
    email_to_id = seed_users()
    pm_email = USERS[0][1]
    project_ids, all_sprint_ids = seed_projects_and_sprints(pm_email)
    seed_tasks(project_ids, all_sprint_ids, email_to_id, pm_email)
    print("Done.")


if __name__ == "__main__":
    main()
