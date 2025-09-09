import requests

BASE_URL = "http://localhost:8080"

def test_create_task():
    resp = requests.post(f"{BASE_URL}/api/tasks", json={"content": "pytest task"})
    assert resp.status_code == 201

def test_get_tasks():
    resp = requests.get(f"{BASE_URL}/api/tasks")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
