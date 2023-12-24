from random import randint

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user_ids = []

        self.account_number = randint(0, 1000000)

        resp = self.client.post(
            "/register",
            json={
                "email": f"random_user{self.account_number}@mail.com",
                "password": "password",
            },
        )
        if resp.status_code == 200:
            self.account_id = resp.json()["id_account"]
            resp = self.client.post(
                "/login",
                json={
                    "email": f"random_user{self.account_number}@mail.com",
                    "password": "password",
                },
            )
            if resp.status_code == 200:
                self.client.headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
            else:
                self.stop()
        else:
            self.stop()

    # @task
    # def on_stop(self):
    #     for uid in self.user_ids:
    #         with self.client.rename_request("/users/<user_id>"):
    #             self.client.delete(f"/users/{uid}")
    #     with self.client.rename_request("/accounts/<account_id>"):
    #         self.client.delete(f"/accounts/{self.account_id}")

    @task
    def create_user(self):
        if len(self.user_ids) > 0:
            username = int(self.user_ids[-1]) + 1
        else:
            username = 0
        resp = self.client.post("/users", json={"username": str(username)})
        if resp.status_code == 200:
            self.user_ids.append(resp.json()["id_user"])

    @task
    def exercises(self):
        self.client.get("/exercises")

    @task
    def filter_exercises(self):
        self.client.get("/exercises?complexity=hard")

    @task
    def sort_exercises(self):
        self.client.get("/exercises?order_by=title")

    @task
    def order_by_completion(self):
        if not self.user_ids:
            return
        u_id = self.user_ids[randint(0, len(self.user_ids) - 1)]
        with self.client.rename_request(
            "/exercises?order_by=completion&user_id=<user_id>"
        ):
            self.client.get(f"/exercises?order_by=completion&user_id={u_id}")

    @task
    def read_exercise(self):
        with self.client.rename_request("/exercises/<id>"):
            self.client.get(f"/exercises/{randint(1, 1000)}")

    @task
    def track_completion(self):
        if not self.user_ids:
            return
        ex_id = randint(1, 1000)
        u_id = self.user_ids[randint(0, len(self.user_ids) - 1)]
        with self.client.rename_request("/exercises/<id>/track_completion"):
            self.client.post(
                f"/exercises/{ex_id}/track_completion",
                json={"user_id": u_id, "completion": 20},
            )
