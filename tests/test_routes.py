import os
import unittest
from unittest.mock import patch


os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

import server


class FakeCursor:
    def __init__(self, fetchall_results=None, fetchone_results=None, lastrowid=101, rowcount=1):
        self.fetchall_results = list(fetchall_results or [])
        self.fetchone_results = list(fetchone_results or [])
        self.lastrowid = lastrowid
        self.rowcount = rowcount
        self.executed = []

    def execute(self, query, params=()):
        self.executed.append((" ".join(query.split()), params))

    def fetchall(self):
        if self.fetchall_results:
            return self.fetchall_results.pop(0)
        return []

    def fetchone(self):
        if self.fetchone_results:
            return self.fetchone_results.pop(0)
        return None

    def close(self):
        return None


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.committed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def close(self):
        return None


class RouteTests(unittest.TestCase):
    def setUp(self):
        server.app.config["TESTING"] = True
        self.client = server.app.test_client()

    def make_connection(self, fetchall_results=None, fetchone_results=None, lastrowid=101, rowcount=1):
        return FakeConnection(FakeCursor(fetchall_results, fetchone_results, lastrowid, rowcount))

    def test_home_redirects_to_login_when_logged_out(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_signup_redirects_new_user_to_preferences(self):
        connection = self.make_connection(fetchone_results=[None], lastrowid=55)
        with patch("server.connect", return_value=connection):
            response = self.client.post(
                "/signup",
                data={
                    "username": "hinata",
                    "email": "hinata@example.com",
                    "password": "verysecure",
                    "confirm_password": "verysecure",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/preferences", response.location)
        self.assertTrue(connection.committed)

    def test_preferences_requires_selection(self):
        connection = self.make_connection(
            fetchone_results=[(7, "itadori", "itadori@example.com", None)],
            fetchall_results=[[]],
        )
        with patch("server.connect", return_value=connection):
            with self.client.session_transaction() as session_state:
                session_state["user_id"] = 7

            response = self.client.post("/preferences", data={}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Choose at least one genre", response.data)

    def test_preferences_save_and_redirect_home(self):
        connection = self.make_connection(
            fetchone_results=[
                (7, "itadori", "itadori@example.com", None),
                (7, "itadori", "itadori@example.com", "2026-08-22 09:00:00"),
            ],
            fetchall_results=[[], [], [], [], []],
        )
        with patch("server.connect", return_value=connection):
            with self.client.session_transaction() as session_state:
                session_state["user_id"] = 7

            response = self.client.post(
                "/preferences",
                data={"genres": ["Action", "Mystery"]},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.location)
        executed_queries = [query for query, _ in connection.cursor_instance.executed]
        self.assertTrue(any("DELETE FROM user_preferences" in query for query in executed_queries))
        self.assertTrue(any("INSERT INTO user_preferences" in query for query in executed_queries))

    def test_add_route_scopes_entry_to_logged_in_user(self):
        connection = self.make_connection(
            fetchone_results=[(9, "levi", "levi@example.com", "2026-08-22 09:00:00")],
        )
        with patch("server.connect", return_value=connection):
            with self.client.session_transaction() as session_state:
                session_state["user_id"] = 9

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
        insert_query = next(
            (item for item in connection.cursor_instance.executed if "INSERT INTO anime" in item[0]),
            None,
        )
        self.assertIsNotNone(insert_query)
        self.assertEqual(insert_query[1][-1], 9)

    def test_details_cannot_access_other_users_anime(self):
        connection = self.make_connection(
            fetchone_results=[
                (9, "levi", "levi@example.com", "2026-08-22 09:00:00"),
                None,
                (9, "levi", "levi@example.com", "2026-08-22 09:00:00"),
                None,
            ],
            fetchall_results=[[], [], [], []],
        )
        with patch("server.connect", return_value=connection):
            with self.client.session_transaction() as session_state:
                session_state["user_id"] = 9

            response = self.client.get("/details/400", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"couldn&#39;t find that anime", response.data)

    def test_delete_failure_does_not_report_success(self):
        connection = self.make_connection(
            fetchone_results=[(7, "sakura", "sakura@example.com", "2026-08-22 09:00:00")],
            rowcount=0,
        )
        with patch("server.connect", return_value=connection):
            with patch("server.get_current_user", return_value={"user_id": 7, "username": "sakura", "email": "sakura@example.com", "has_completed_preferences": True}):
                with patch("server.get_user_anime", return_value={"anime_id": 42, "title": "Naruto", "user_id": 7}):
                    response = self.client.post("/delete/42", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"could not be deleted", response.data)

    def test_recommendation_candidates_exclude_existing_history(self):
        with patch("server.get_user_preferences", return_value=["Action"]):
            with patch("server.fetch_all") as mock_fetch_all:
                mock_fetch_all.side_effect = [
                    [("Attack on Titan",), ("Demon Slayer",)],
                    [
                        (11, "Attack on Titan", "Action", "Completed", 89, "desc", "AOT", 2),
                        (12, "Vinland Saga", "Action", "Completed", 24, "desc", "VIN", 3),
                        (13, "Demon Slayer", "Action", "Watching", 55, "desc", "DS", 4),
                        (14, "86", "Action", "Completed", 23, "desc", "EIGHTY SIX", 5),
                    ],
                ]

                candidates = server.get_recommendation_candidates(9)

        titles = [item["title"] for item in candidates]
        self.assertEqual(titles, ["Vinland Saga", "86"])


if __name__ == "__main__":
    unittest.main()
