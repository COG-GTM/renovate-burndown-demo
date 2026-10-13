def test_console_page_served():
    from fastapi.testclient import TestClient

    from app.main import app

    res = TestClient(app).get("/")
    assert res.status_code == 200
    assert "Orders console" in res.text
