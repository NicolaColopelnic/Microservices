import sqlite3

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

SERVICE_A_URL = "http://127.0.0.1:5001"

# home page interface - the user chooses a movie title and is redirected to that movies page
@app.get("/", response_class=HTMLResponse)
async def home_page():
    response = requests.get(f"{SERVICE_A_URL}/movies")
    movie_list = response.json()
    buttons_html = ""
    for movie in movie_list:
        buttons_html += f'<a href="/movie/{movie["id"]}" class="btn">{movie["title"]}</a>'

    return f"""
    <html>
        <head>
            <title>Movies</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; text-align: center; padding: 50px; background-color: #f0f2f5; }}
                .container {{ background: white; padding: 40px; border-radius: 15px; display: inline-block; box-shadow: 0px 10px 25px rgba(0,0,0,0.1); max-width: 500px; }}
                h1 {{ color: #1c1e21; }}
                .btn {{ 
                    display: block; margin: 10px auto; padding: 15px; background: #1877f2; 
                    color: white; text-decoration: none; border-radius: 8px; font-weight: bold; 
                }}
                .btn:hover {{ background: #166fe5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Movies</h1>
                <p>Select a title to see details:</p>
                {buttons_html}
            </div>
        </body>
    </html>
    """

# routing and failure handling + movie page interface
@app.get("/movie/{movie_id}", response_class=HTMLResponse)
async def route_to_movie_service(movie_id: int):
    try:
        response = requests.get(f"{SERVICE_A_URL}/movie/{movie_id}")
        # the gateway doesnt look up the movies itself - it asks service a
        data = response.json()

        title = data.get("title")
        desc = data.get("description")
        recs = data.get("recommendations", [])

        recommendation_list = "".join([f"<li>Movie ID: {r}</li>" for r in recs])

        return f"""
        <html>
            <head>
                <title>{title}</title>
                <style>
                    body {{ font-family: sans-serif; background: #f4f4f9; padding: 40px; text-align: center; }}
                    .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: inline-block; max-width: 600px; text-align: left; }}
                    h1 {{ color: #333; }}
                    li {{ background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px; border-left: 5px solid #1877f2; list-style: none; }}
                    .back-btn {{ display: inline-block; margin-top: 20px; text-decoration: none; color: #1877f2; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>{title}</h1>
                    <p>{desc}</p>
                    <hr>
                    <h3>Recommended movies:</h3>
                    <ul>{recommendation_list}</ul>
                    <a href="/" class="back-btn">← Back to the movie list</a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=502, detail="Movie service offline")