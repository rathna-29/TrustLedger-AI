"""API boot smoke tests: the three core pages stay up and serve content."""
import unittest

from application import create_app


class ApiBoot(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_healthz_is_ok(self):
        resp = self.client.get("/healthz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")

    def test_dashboard_renders(self):
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"TrustLedger", resp.data)

    def test_api_scenarios_return_payloads(self):
        resp = self.client.get("/api/scenarios")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.get_json()) >= 4)


if __name__ == "__main__":
    unittest.main()
