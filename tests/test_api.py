import unittest

import psycopg
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict, make_conninfo

import database
from main import app


TEST_DB = "tasks_test"


def prepare_test_database():
    """Point the app at a throwaway database so tests never touch real tasks."""
    info = conninfo_to_dict(database.database_url())
    admin = make_conninfo(**{**info, "dbname": "postgres"})
    with psycopg.connect(admin, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)
        ).fetchone()
        if not exists:
            connection.execute(f'CREATE DATABASE "{TEST_DB}"')
    return make_conninfo(**{**info, "dbname": TEST_DB})


class DatabaseApiTests(unittest.TestCase):
    def setUp(self):
        self.original_url = database.database_url()
        database.database_url = lambda url=prepare_test_database(): url
        with database.open_database() as connection:
            connection.execute("DROP TABLE IF EXISTS tasks")

    def tearDown(self):
        database.database_url = lambda url=self.original_url: url

    def test_startup_creates_table_and_three_seeds_without_duplicates(self):
        for _ in range(3):
            with TestClient(app) as client:
                response = client.get("/tasks")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 3)
                self.assertTrue(all(type(t["done"]) is bool for t in response.json()))

    def test_existing_database_without_table_is_initialized(self):
        with TestClient(app) as client:
            self.assertEqual(len(client.get("/tasks").json()), 3)

    def test_crud_survives_app_restart_and_empty_list_is_success(self):
        title = "Quote '); DROP TABLE tasks; --"
        with TestClient(app) as client:
            response = client.post("/tasks", json={"title": title})
            self.assertEqual(response.status_code, 201)
            task = response.json()
            self.assertEqual(task, {"id": 4, "title": title, "done": False})
            response = client.put("/tasks/4", json={"title": "Updated", "done": True})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"id": 4, "title": "Updated", "done": True})
        with TestClient(app) as client:
            self.assertEqual(client.get("/tasks/4").json()["done"], True)
            for task in client.get("/tasks").json():
                response = client.delete(f'/tasks/{task["id"]}')
                self.assertEqual(response.status_code, 204)
                self.assertEqual(response.content, b"")
            response = client.get("/tasks")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])
            for method in ("GET", "PUT", "DELETE"):
                kwargs = {"json": {"title": "Missing", "done": False}} if method == "PUT" else {}
                response = client.request(method, "/tasks/999", **kwargs)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {"error": "Task not found"})

    def test_invalid_bodies_and_path_validation(self):
        with TestClient(app) as client:
            for method, path, bodies in (
                ("POST", "/tasks", [{}, {"title": ""}, {"title": None}, {"title": []}]),
                ("PUT", "/tasks/1", [{}, {"title": "x"}, {"title": "", "done": False}, {"title": "x", "done": "invalid"}]),
            ):
                for body in bodies:
                    with self.subTest(method=method, body=body):
                        response = client.request(method, path, json=body)
                        self.assertEqual(response.status_code, 400)
                        self.assertIn("error", response.json())
                for content in (b"", b"{"):
                    response = client.request(method, path, content=content, headers={"Content-Type": "application/json"})
                    self.assertEqual(response.status_code, 400)
            self.assertEqual(client.get("/tasks/not-an-integer").status_code, 422)


if __name__ == "__main__":
    unittest.main()
