import os
import unittest
from unittest.mock import patch


os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

import server


class FakeCursor:
    def __init__(self, fetchall_result=None, fetchone_result=None):
        self.fetchall_result = fetchall_result or []
        self.fetchone_result = fetchone_result
        self.executed = []

    def execute(self, query, params=()):
        self.executed.append((query, params))

    def fetchall(self):
        return self.fetchall_result

    def fetchone(self):
        return self.fetchone_result

    def close(self):
        return None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        return None


class RouteTests(unittest.TestCase):
    def setUp(self):
        server.app.config["TESTING"] = True
        self.client = server.app.test_client()

    def test_home_route_renders(self):
        cursor = FakeCursor(fetchall_result=[(1, "Naruto", "Action", "Watching", 220)])
        with patch("server.connect", return_value=FakeConnection(cursor)):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Anime List", response.data)

    def test_details_route_renders(self):
        cursor = FakeCursor(fetchone_result=(1, "Death Note", "Thriller", "Completed", 37))
        with patch("server.connect", return_value=FakeConnection(cursor)):
            response = self.client.get("/details/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Death Note", response.data)

    def test_recommendations_route_renders(self):
        cursor = FakeCursor(fetchall_result=[(1, "Attack on Titan", "Action", "Completed", 89)])
        with patch("server.connect", return_value=FakeConnection(cursor)):
            response = self.client.get("/recommendations")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Recommended Anime", response.data)

    def test_add_route_redirects_after_post(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)
        with patch("server.connect", return_value=connection):
            response = self.client.post(
                "/add",
                data={
                    "title": "Fullmetal Alchemist: Brotherhood",
                    "genre": "Action",
                    "status": "Completed",
                    "total_episodes": "64",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(connection.committed)


if __name__ == "__main__":
    unittest.main()
