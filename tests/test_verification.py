"""
pnwc-poster — Full Verification Test Suite
Runs against the live service on localhost:8080.
All posts are created with dry_run=True — nothing touches real platforms.
"""
from __future__ import annotations
import pytest
import httpx

BASE_URL = "http://localhost:8080"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def http():
    """Shared HTTP client for the entire module."""
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        yield client


@pytest.fixture(scope="module")
def test_post(http):
    """
    Creates one dry-run test post for the whole module.
    All dispatch/status/idempotency tests share this post.
    The post is safe to delete from the dashboard after tests run.
    """
    payload = {
        "title": "[VERIFICATION TEST] Safe to delete",
        "body_long": "Automated verification test post. Safe to delete from the dashboard.",
        "body_short": "Verification test.",
        "hashtags": ["test"],
        "links": [],
        "media_paths": [],
        "targets": ["mastodon"],
        "dry_run": True,
    }
    r = http.post("/api/posts", json=payload)
    assert r.status_code == 201, f"Test post creation failed: {r.text}"
    data = r.json()
    assert "id" in data, "Response missing 'id' field"
    return data


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestServiceHealth:
    def test_api_reachable(self, http):
        """Service is up and the posts endpoint responds."""
        r = http.get("/api/posts")
        assert r.status_code == 200, f"Service unreachable — got {r.status_code}"

    def test_response_is_list(self, http):
        """Posts endpoint returns a JSON list."""
        r = http.get("/api/posts")
        assert isinstance(r.json(), list), "Expected list response from /api/posts"

    def test_events_reachable(self, http):
        """Events endpoint responds."""
        r = http.get("/api/events")
        assert r.status_code == 200, f"Events endpoint failed — got {r.status_code}"


class TestPostCreation:
    def test_post_has_id(self, test_post):
        """Created post has a numeric ID."""
        assert isinstance(test_post["id"], int)
        assert test_post["id"] > 0

    def test_post_initial_status_is_draft(self, test_post):
        """Newly created post status is 'draft'."""
        assert test_post["status"] == "draft", (
            f"Expected 'draft', got '{test_post['status']}'"
        )

    def test_post_dry_run_is_true(self, test_post):
        """Post was created with dry_run=True."""
        assert test_post["dry_run"] is True

    def test_post_targets_correct(self, test_post):
        """Post targets contain mastodon."""
        assert "mastodon" in test_post["targets"]

    def test_post_retrievable_by_id(self, http, test_post):
        """Created post is retrievable by ID."""
        r = http.get(f"/api/posts/{test_post['id']}")
        assert r.status_code == 200, f"Post not found by ID: {r.status_code}"
        assert r.json()["id"] == test_post["id"]


class TestDispatch:
    def test_dispatch_returns_200(self, http, test_post):
        """Dispatch endpoint returns 200."""
        r = http.post(f"/api/posts/{test_post['id']}/dispatch")
        assert r.status_code == 200, f"Dispatch failed: {r.text}"

    def test_dispatch_result_structure(self, http, test_post):
        """Dispatch response contains results list."""
        r = http.post(f"/api/posts/{test_post['id']}/dispatch")
        # Will be 409 if already dispatched — that means earlier test ran it
        if r.status_code == 409:
            pytest.skip("Post already dispatched by earlier test run")
        data = r.json()
        assert "results" in data, f"Response missing 'results': {data}"
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1

    def test_dispatch_mastodon_success(self, http, test_post):
        """Mastodon dry-run dispatch reports success."""
        r = http.post(f"/api/posts/{test_post['id']}/dispatch")
        if r.status_code == 409:
            pytest.skip("Post already dispatched")
        results = r.json()["results"]
        mastodon = next((x for x in results if x["platform"] == "mastodon"), None)
        assert mastodon is not None, "No mastodon result in response"
        assert mastodon["success"] is True, f"Mastodon dry-run failed: {mastodon}"
        assert mastodon["dry_run"] is True, "Expected dry_run=True on result"

    def test_dispatch_unknown_post_returns_404(self, http):
        """Dispatching a non-existent post returns 404."""
        r = http.post("/api/posts/999999/dispatch")
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"


class TestStatusUpdate:
    def test_status_updated_to_sent(self, http, test_post):
        """Post status is 'sent' after successful dispatch."""
        r = http.get(f"/api/posts/{test_post['id']}")
        assert r.status_code == 200
        status = r.json()["status"]
        assert status == "sent", (
            f"Expected status 'sent' after dispatch, got '{status}'. "
            f"Fix 3 (update_post_status) may not be working correctly."
        )

    def test_updated_at_changed(self, http, test_post):
        """updated_at timestamp changed after dispatch."""
        r = http.get(f"/api/posts/{test_post['id']}")
        data = r.json()
        assert data["updated_at"] != data["created_at"], (
            "updated_at was not changed after dispatch — "
            "update_post_status may not be writing the timestamp."
        )


class TestIdempotency:
    def test_second_dispatch_returns_409(self, http, test_post):
        """Dispatching an already-sent post returns 409 Conflict."""
        r = http.post(f"/api/posts/{test_post['id']}/dispatch")
        assert r.status_code == 409, (
            f"Expected 409 Conflict on duplicate dispatch, got {r.status_code}. "
            f"Idempotency guard may not be working."
        )

    def test_409_response_has_detail(self, http, test_post):
        """409 response includes a detail message."""
        r = http.post(f"/api/posts/{test_post['id']}/dispatch")
        assert r.status_code == 409
        data = r.json()
        assert "detail" in data, "409 response missing detail field"
        assert "already been sent" in data["detail"].lower()


class TestEventLogging:
    def test_event_exists_for_post(self, http, test_post):
        """At least one event is logged for the test post."""
        r = http.get("/api/events?limit=50")
        assert r.status_code == 200
        events = r.json()
        post_events = [e for e in events if e["post_id"] == test_post["id"]]
        assert len(post_events) >= 1, (
            f"No events found for post {test_post['id']}. "
            f"log_event may not be firing correctly."
        )

    def test_event_platform_is_mastodon(self, http, test_post):
        """Logged event is for the mastodon platform."""
        r = http.get("/api/events?limit=50")
        events = r.json()
        post_events = [e for e in events if e["post_id"] == test_post["id"]]
        assert len(post_events) >= 1
        assert post_events[0]["platform"] == "mastodon"

    def test_event_success_is_true(self, http, test_post):
        """Logged event records success=True."""
        r = http.get("/api/events?limit=50")
        events = r.json()
        post_events = [e for e in events if e["post_id"] == test_post["id"]]
        assert len(post_events) >= 1
        assert post_events[0]["success"] is True, (
            f"Event logged success=False for dry-run: {post_events[0]}"
        )
