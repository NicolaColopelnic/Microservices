import requests
import time
from fastapi import FastAPI
import sqlite3

app = FastAPI()

TRENDING_MOVIES = [50,51,52,53]

class CircuitBreaker:
    def __init__(self):
        self.fails = 0
        self.is_open = False
        self.last_failure_time = 0
        self.threshold = 3
        self.recovery_timeout = 20

    def record_failure(self):
        self.fails += 1
        print(f"    Service B failed. Total failures: {self.fails}")

        if self.fails >= self.threshold:
            self.is_open = True
            self.last_failure_time = time.time()
            print("     Circuit breaker tripped - circuit is now open!")

    def attempt_request(self):
        if self.is_open:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                print("     Recovery timeout reached. Attempting to check Service B...")
                return True
            print(f"    Circuit is open. (Wait {int(20 - (time.time() - self.last_failure_time))}s more)")
            return False

        # circuit closed
        return True

    def record_success(self): # if service B responds correctly - reset everything
        if self.is_open:
            print("     Service B is healthy again, closing circuit...")
        self.is_open = False
        self.fails = 0

breaker = CircuitBreaker()

@app.get("/movie/{movie_id}")
async def get_movie(movie_id: int):
    movie = get_movie_from_db(movie_id)

    if breaker.attempt_request():
        try:
            response = requests.get(
                f"http://127.0.0.1:5002/recommendations/{movie_id}",
                timeout=1.5
            ) # if service B takes longer to respond than 1.5 time out - throw exception
            if response.status_code == 200: # success
                data = response.json()
                recommendations = data["recommendations"]
                breaker.record_success()
            else: # in case of failure - display trending movies
                breaker.record_failure()
                recommendations = TRENDING_MOVIES

        except (requests.exceptions.Timeout, requests.exceptions.RequestException):
            breaker.record_failure()
            recommendations = TRENDING_MOVIES

    else:
        recommendations = TRENDING_MOVIES

    return {
        "title": movie["title"],
        "description": movie["desc"],
        "recommendations": recommendations
    }

def get_movie_from_db(movie_id):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    conn.close()

    if movie:
        return {"title": movie[1], "desc": movie[2]}
    return {"title": "Not found", "desc": "Not found"}