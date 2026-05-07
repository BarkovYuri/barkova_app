from django.test import TestCase


class HealthEndpointsTests(TestCase):
    def test_livez_returns_ok(self):
        response = self.client.get("/api/livez/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_healthz_returns_ok_when_db_works(self):
        response = self.client.get("/api/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
