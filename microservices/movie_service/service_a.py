import requests
import time
from fastapi import FastAPI

app = FastAPI()

MOVIES_DB = {
    1: {"title": "The devil wears Prada 2", "desc": "The movie reunites Miranda Priestly and a seasoned Andy Sachs to save a struggling Runway magazine in a digital-first world."},
    2: {"title": "Michael", "desc": "A musical biographical drama that chronicles the life of Michael Jackson, from his childhood stardom in the Jackson 5 to his peak as the King of Pop"},
    3: {"title": "Wuthering Heights", "desc": "An adaptation after the gothic novel with the same name, exploring an intense, destructive love between Catherine Earnshaw and Heathcliff."}
}

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
    movie = MOVIES_DB.get(movie_id, {"title": "Not found", "desc": "Not found"})

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