"""Tests for activities API endpoints"""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        # Arrange - nothing needed, using fixture client

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Based on the predefined activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Music Band" in data
        assert "Math Club" in data
        assert "Science Club" in data

    def test_get_activities_structure(self, client):
        """Test that each activity has the correct structure"""
        # Arrange
        response = client.get("/activities")
        data = response.json()

        # Act - check one activity structure
        chess_club = data["Chess Club"]

        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity(self, client):
        """Test successful signup for an existing activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

        # Verify participant was added
        response_check = client.get("/activities")
        data = response_check.json()
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_email(self, client):
        """Test signup fails when student is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student already signed up"}

    def test_signup_nonexistent_activity(self, client):
        """Test signup fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}


class TestUnregisterActivity:
    """Test cases for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_valid_participant(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in Programming Class

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

        # Verify participant was removed
        response_check = client.get("/activities")
        data = response_check.json()
        assert email not in data[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister fails when student is not signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "notsigned@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student not signed up for this activity"}

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}


class TestIntegration:
    """Integration tests for complete signup/unregister workflows"""

    def test_signup_then_unregister_workflow(self, client):
        """Test complete signup and unregister flow"""
        # Arrange
        activity_name = "Gym Class"
        email = "integrationtest@example.com"

        # Act - Signup
        signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert signup
        assert signup_response.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in client.get("/activities").json()[activity_name]["participants"]

    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple different activities"""
        # Arrange
        activities_and_emails = [
            ("Basketball Team", "multi1@example.com"),
            ("Tennis Club", "multi2@example.com"),
        ]

        # Act & Assert
        for activity_name, email in activities_and_emails:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            assert response.status_code == 200
            assert email in client.get("/activities").json()[activity_name]["participants"]