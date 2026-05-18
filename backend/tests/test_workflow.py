import os
from pathlib import Path

os.environ["DATABASE_URL"] = f"sqlite:///{(Path(__file__).parent / 'test.db').as_posix()}"
os.environ["SEED_ON_STARTUP"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    return body["data"]["access_token"]


def test_student_submit_and_teacher_grade_workflow():
    with TestClient(app) as client:
        student_token = _login(client, "student1", "123456")
        teacher_token = _login(client, "teacher1", "123456")

        assignments = client.get(
            "/api/v1/assignments",
            params={"only_mine": True},
            headers={"Authorization": f"Bearer {student_token}"},
        ).json()["data"]
        target = next(item for item in assignments if item["title"] == "详细设计说明")

        submit_response = client.post(
            "/api/v1/submissions",
            json={"assignment_id": target["id"], "content": "提交详细设计说明正文"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert submit_response.status_code == 200
        submission = submit_response.json()["data"]
        assert submission["status"] == "submitted"

        grade_response = client.post(
            f"/api/v1/submissions/{submission['id']}/grade",
            json={"grade": 88.5, "feedback": "设计完整，表达清楚。"},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert grade_response.status_code == 200
        graded = grade_response.json()["data"]
        assert graded["status"] == "graded"
        assert graded["grade"] == 88.5
