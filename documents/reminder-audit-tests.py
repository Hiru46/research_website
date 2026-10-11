"""
PP2 Audit Test Suite: Emotion & Progress-Aware Adaptive Study Reminder System.
Tests the 5 standard evaluation scenarios, 4 pipeline modules, and unified REST APIs.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.readiness_service import readiness_service
from app.services.memory_service import memory_service
from app.services.scheduler_service import scheduler_service
from app.services.recommendation_service import recommendation_service


class TestPP2AuditScenarios:
    """
    Direct evaluation of the 5 audit scenarios specified in the PP2 specification.
    """

    def test_scenario_1_high_readiness_review(self):
        """
        [Scenario 1: High Readiness Review]
        - Input: Emotion = 'Focused', Time = 'Morning', Priority = 75%
        - Expected: Readiness = 'High', Action = 'SEND_NOW', Activity = 'Active Recall'
        """
        # Step 1: Readiness
        readiness_res = readiness_service.predict(
            emotion="Focused",
            time_of_study="Morning (6 AM–12 PM)",
        )
        assert readiness_res["readiness"] == "High"
        assert readiness_res["confidence"] >= 0.85

        # Step 2: Scheduler Action with Priority = 75
        sched_res = scheduler_service.decide(
            readiness="High",
            priority=75,
            current_emotion="Focused",
        )
        assert sched_res["action"] == "SEND_NOW"

        # Step 3: Recommended Activity
        rec_res = recommendation_service.recommend(
            emotion="Focused",
            readiness="High",
            topic_familiarity="Familiar",
            topic_difficulty="Medium",
        )
        assert rec_res["recommended_activity"] == "Active Recall"

    def test_scenario_2_frustration_fatigue_protection(self):
        """
        [Scenario 2: Frustration / Fatigue Protection]
        - Input: Emotion = 'Frustrated', Time = 'Night', Priority = 80%
        - Expected: Readiness = 'Low', Action = 'DELAY_REMINDER' or 'SKIP_REMINDER', Activity = 'Take a Short Break'
        """
        # Step 1: Readiness
        readiness_res = readiness_service.predict(
            emotion="Frustrated",
            time_of_study="Night (After 9 PM)",
        )
        assert readiness_res["readiness"] == "Low"

        # Step 2: Scheduler Action with Priority = 80
        sched_res = scheduler_service.decide(
            readiness="Low",
            priority=80,
            current_emotion="Frustrated",
        )
        assert sched_res["action"] in ["DELAY_REMINDER", "SKIP_REMINDER"]

        # Step 3: Recommended Activity
        rec_res = recommendation_service.recommend(
            emotion="Frustrated",
            readiness="Low",
            topic_familiarity="Familiar",
            topic_difficulty="Hard",
        )
        assert rec_res["recommended_activity"] == "Take a Short Break"

    def test_scenario_3_unfamiliar_topic_support(self):
        """
        [Scenario 3: Unfamiliar Topic Support]
        - Input: Emotion = 'Confused', Time = 'Afternoon', Topic = 'Very unfamiliar'
        - Expected: Readiness = 'Medium' / 'Low', Activity = 'Guided Review'
        """
        # Step 1: Readiness
        readiness_res = readiness_service.predict(
            emotion="Confused",
            time_of_study="Afternoon (12 PM–5 PM)",
        )
        assert readiness_res["readiness"] in ["Medium", "Low"]

        # Step 2: Recommended Activity for Unfamiliar Topic with Confusion
        rec_res = recommendation_service.recommend(
            emotion="Confused",
            readiness=readiness_res["readiness"],
            topic_familiarity="Very unfamiliar",
            topic_difficulty="Medium",
        )
        assert rec_res["recommended_activity"] == "Guided Review"

    def test_scenario_4_fresh_topic_skip(self):
        """
        [Scenario 4: Fresh Topic Skip]
        - Input: Emotion = 'Focused', Retention = 95% (Priority = 5%)
        - Expected: Action = 'SKIP_REMINDER' (Topic does not need review yet)
        """
        readiness = "High"
        priority = 5  # 1.0 - 0.95 = 0.05 -> 5%
        
        sched_res = scheduler_service.decide(
            readiness=readiness,
            priority=priority,
            current_emotion="Focused",
        )
        assert sched_res["action"] == "SKIP_REMINDER"

    def test_scenario_5_sm2_spaced_interval_update(self):
        """
        [Scenario 5: SM-2 Spaced Interval Update]
        - Action: Submit quality rating = 5 on first review (reps = 1, interval = 1)
        - Expected: Interval advances from 1 day to 6 days, Ease Factor preserved / enhanced.
        """
        now = datetime.now(timezone.utc)
        
        # Initial review update (n=0 -> n=1, interval=1)
        first_review = memory_service.update_sm2(
            repetitions=0,
            ease_factor=2.5,
            interval_days=1,
            quality_rating=4,
            now=now,
        )
        assert first_review["new_repetitions"] == 1
        assert first_review["new_interval_days"] == 1
        
        # Second review update with quality rating 5 (n=1 -> n=2, interval=6)
        second_review = memory_service.update_sm2(
            repetitions=first_review["new_repetitions"],
            ease_factor=first_review["new_ease_factor"],
            interval_days=first_review["new_interval_days"],
            quality_rating=5,
            now=now + timedelta(days=1),
        )
        assert second_review["new_repetitions"] == 2
        assert second_review["new_interval_days"] == 6
        assert second_review["new_ease_factor"] >= 2.5


class TestUnifiedAPIEndpoints:
    """
    Tests REST API endpoints using FastAPI TestClient.
    """

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_generate_reminder_endpoint(self, client):
        payload = {
            "student_id": "S001",
            "topic_id": "DBMS_01",
            "emotion": "Focused",
            "time_of_study": "Morning (6 AM–12 PM)",
            "academic_year": "3rd Year",
            "daily_study_duration": "2–4 hours",
        }
        res = client.post("/api/reminder/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["student_id"] == "S001"
        assert data["topic_id"] == "DBMS_01"
        assert data["readiness"] == "High"
        assert data["action"] == "SEND_NOW"
        assert data["recommended_activity"] == "Active Recall"
        assert "timestamp" in data

    def test_respond_reminder_endpoint(self, client):
        payload = {
            "student_id": "S001",
            "topic_id": "DBMS_01",
            "reminder_id": "REM_9012",
            "user_response": "ACCEPTED",
        }
        res = client.post("/api/reminder/respond", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "logged"

    def test_study_review_endpoint(self, client):
        payload = {
            "student_id": "S001",
            "topic_id": "DBMS_01",
            "quality_rating": 4,
        }
        res = client.post("/api/study/review", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "updated"
        assert "new_interval_days" in data
        assert "new_ease_factor" in data
        assert "next_review_due" in data

    def test_mock_emotion_endpoint(self, client):
        payload = {"student_id": "S001"}
        res = client.post("/api/mock/emotion", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["emotion"] == "Focused"
        assert data["confidence"] > 0.8
        assert data["source"] == "simulated_camera_stream"
