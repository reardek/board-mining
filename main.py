from typing import Optional
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from mechanical import find_link_3trolle, find_link_gry_bez_pradu, find_link_rebel
 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('base.html', {"request": request})

@app.get("/games", response_class=HTMLResponse)
async def games(request: Request):
    return templates.TemplateResponse('games.html', {"request": request})

@app.get("/find-game", response_class=HTMLResponse)
async def findGame(request: Request, game: Optional[str] = None):
    links = []
    if game:
        if link := find_link_rebel(game):
            links.append(link)
        if link := find_link_3trolle(game):
            links.append(link)
        if link := find_link_gry_bez_pradu(game):
            links.append(link)
    
    return templates.TemplateResponse('find_game.html', {"request": request, "links": links})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, log_level="info", reload=True)
