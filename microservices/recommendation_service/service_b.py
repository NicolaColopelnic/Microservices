import os
import random
import asyncio # handle waiting (sleeping) without freezing the service
from fastapi import FastAPI, HTTPException # framework to make the api

app = FastAPI()

CHAOS_MODE = os.environ.get("CHAOS_MODE", 'false').lower() == "true"
print(f"Service B starting. Chaos mode: {CHAOS_MODE} ---")

@app.get("/recommendations/{movie_id}") # {movie_id} is the placeholder
async def get_recommendations(movie_id: int): # async can handle many requests at once
    if CHAOS_MODE:
        if random.random() < 0.3: # 30% of time the service will not work and the service will be unavailable
            raise HTTPException(status_code=503, detail="Service unavailable")

        # if it works, it will work slower
        delay = random.uniform(3, 10)
        await asyncio.sleep(delay)

    # in case of success:
    return {
        "movie_id": movie_id,
        "recommendations": [101,102,103,104,105]
    }