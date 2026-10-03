import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import database
from main import app


class DatabaseApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.original_path = database.DB_PATH
        database.DB_PATH = Path(self.folder.name) / "tasks.db"

    def tearDown(self):
        database.DB_PATH = self.original_path
        self.folder.cleanup()

    def test_startup_creates_file_table_and_three_seeds_without_duplicates(self):
        for _ in range(3):
            with TestClient(app) as client:
                self.assertTrue(database.DB_PATH.exists())
                response = client.get("/tasks")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 3)
                self.assertTrue(all(type(t["done"]) is bool for t in response.json()))

    def test_existing_file_without_table_is_initialized(self):
        sqlite3.connect(database.DB_PATH).close()
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
