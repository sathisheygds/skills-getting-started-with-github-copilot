"""
Backend tests for the FastAPI application.

Tests cover all endpoints using the AAA (Arrange-Act-Assert) pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Snapshot of the original activities for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to original state before each test.
    This ensures test isolation and prevents state leakage.
    """
    global activities
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirection(self, client):
        """
        Arrange: Client is ready.
        Act: Send GET request to /.
        Assert: Expect 307 redirect to /static/index.html.
        """
        # Arrange
        # (client fixture is already set up)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    """Tests for the activities endpoint."""

    def test_get_activities(self, client):
        """
        Arrange: Client is ready.
        Act: Send GET request to /activities.
        Assert: Expect 200 response with activities dictionary.
        """
        # Arrange
        # (client fixture is already set up)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9  # 9 activities in the original data


class TestSignup:
    """Tests for the signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Client ready, select an activity and email not yet signed up.
        Act: POST signup request.
        Assert: Expect 200 response and participant added to activity.
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_already_registered(self, client):
        """
        Arrange: Client ready, select existing participant.
        Act: POST signup request with already-registered email.
        Assert: Expect 400 response with error message.
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Client ready, choose non-existent activity.
        Act: POST signup request for non-existent activity.
        Assert: Expect 404 response.
        """
        # Arrange
        fake_activity = "Fake Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    """Tests for the unregister endpoint."""

    def test_unregister_success(self, client):
        """
        Arrange: Client ready, select existing participant.
        Act: POST unregister request.
        Assert: Expect 200 response and participant removed from activity.
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_not_signed_up(self, client):
        """
        Arrange: Client ready, select email not in activity.
        Act: POST unregister request with non-participant email.
        Assert: Expect 400 response with error message.
        """
        # Arrange
        activity_name = "Chess Club"
        non_participant_email = "nobody@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": non_participant_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Client ready, choose non-existent activity.
        Act: POST unregister request for non-existent activity.
        Assert: Expect 404 response.
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
