import unittest
from app import app, varastot, store


class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        store.clear()

    def tearDown(self):
        store.clear()

    def test_index_empty(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Varastot", response.data)
        self.assertIn(b"Ei varastoja", response.data)

    def test_new_varasto_get(self):
        response = self.client.get("/varasto/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Luo uusi varasto", response.data)

    def test_create_varasto(self):
        response = self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testivarasto", response.data)
        self.assertEqual(len(varastot), 1)

    def test_view_varasto(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        response = self.client.get("/varasto/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Testivarasto", response.data)

    def test_view_nonexistent_varasto(self):
        response = self.client.get("/varasto/999", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Varastot", response.data)

    def test_edit_varasto_get(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        response = self.client.get("/varasto/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Muokkaa", response.data)

    def test_edit_varasto_post(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        response = self.client.post("/varasto/1/edit", data={
            "nimi": "Uusi nimi",
            "tilavuus": "200"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Uusi nimi", response.data)
        self.assertEqual(varastot[1]["varasto"].tilavuus, 200)

    def test_edit_nonexistent_varasto(self):
        response = self.client.get("/varasto/999/edit", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Varastot", response.data)

    def test_add_to_varasto(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        response = self.client.post("/varasto/1/add", data={
            "maara": "20"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(varastot[1]["varasto"].saldo, 30)

    def test_add_to_nonexistent_varasto(self):
        response = self.client.post(
            "/varasto/999/add",
            data={"maara": "20"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_from_varasto(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "50"
        })
        response = self.client.post("/varasto/1/remove", data={
            "maara": "20"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(varastot[1]["varasto"].saldo, 30)

    def test_remove_from_nonexistent_varasto(self):
        response = self.client.post(
            "/varasto/999/remove",
            data={"maara": "20"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_varasto(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        self.assertEqual(len(varastot), 1)
        response = self.client.post(
            "/varasto/1/delete",
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(varastot), 0)

    def test_delete_nonexistent_varasto(self):
        response = self.client.post(
            "/varasto/999/delete",
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_create_multiple_varastot(self):
        self.client.post("/varasto/new", data={
            "nimi": "Varasto 1",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        self.client.post("/varasto/new", data={
            "nimi": "Varasto 2",
            "tilavuus": "200",
            "alku_saldo": "20"
        })
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Varasto 1", response.data)
        self.assertIn(b"Varasto 2", response.data)
        self.assertEqual(len(varastot), 2)

    def test_create_varasto_with_invalid_input(self):
        response = self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "invalid",
            "alku_saldo": "invalid"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(varastot), 1)
        self.assertEqual(varastot[1]["varasto"].tilavuus, 0.0)

    def test_add_with_invalid_input(self):
        self.client.post("/varasto/new", data={
            "nimi": "Testivarasto",
            "tilavuus": "100",
            "alku_saldo": "10"
        })
        response = self.client.post("/varasto/1/add", data={
            "maara": "invalid"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(varastot[1]["varasto"].saldo, 10)
