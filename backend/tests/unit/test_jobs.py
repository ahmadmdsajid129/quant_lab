import pytest
from app.db.models import Job


def test_jobs_and_telemetry_lifecycle(client, db_session):
    # 1. Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "ops_engineer@quantlab.io", "password": "Password123!", "full_name": "DevOps Engineer"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed a test job in db
    test_job = Job(
        job_type="BACKTEST_GRID_SEARCH",
        status="RUNNING",
        progress=45.0,
    )
    db_session.add(test_job)
    db_session.commit()
    db_session.refresh(test_job)

    # 3. List jobs endpoint
    res_list = client.get("/api/v1/jobs", headers=headers)
    assert res_list.status_code == 200
    jobs = res_list.json()
    assert len(jobs) >= 1
    assert any(j["id"] == test_job.id for j in jobs)

    # 4. Cancel job endpoint
    res_cancel = client.post(f"/api/v1/jobs/{test_job.id}/cancel", headers=headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"

    # 5. Telemetry endpoint
    res_telem = client.get("/api/v1/jobs/telemetry", headers=headers)
    assert res_telem.status_code == 200
    telem = res_telem.json()
    assert telem["system_status"] in ["HEALTHY", "DEGRADED"]
    assert telem["database_status"] == "CONNECTED"
    assert telem["memory_usage_mb"] > 0.0
    assert telem["active_worker_threads"] > 0
