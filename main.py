from typing import Optional
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from mechanical import BoardGameScrapper
from database import engine
from database.models.board_game import BoardGameDetails

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/games", response_class=HTMLResponse)
async def games(request: Request):
    games = await engine.find(BoardGameDetails)
    return templates.TemplateResponse(
        "games.html", {"request": request, "games": games}
    )


@app.get("/find-game", response_class=HTMLResponse)
async def findGame(request: Request, game: Optional[str] = None):
    if game:
        board_scrapper = BoardGameScrapper(game)
        if links := board_scrapper.get_links():
            if game_info := board_scrapper.get_info(links.rebel):
                new_game = BoardGameDetails(bgg_details=game_info, shop_links=links)
                await engine.save(new_game)
                return templates.TemplateResponse(
                    "find_game.html", {"request": request, "ok": True}
                )
        return templates.TemplateResponse(
            "find_game.html", {"request": request, "fail": True}
        )

    return templates.TemplateResponse(
        "find_game.html", {"request": request, "status": "Ready"}
    )


if __name__ == "__main__":
    import asyncio
    import uvicorn

    loop = asyncio.get_event_loop()
    config = uvicorn.Config(app=app, port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
