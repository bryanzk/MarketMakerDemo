from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import threading
import os

# Import the bot engine instance
from main import bot_engine

app = FastAPI()

# Setup Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class ConfigUpdate(BaseModel):
    spread: float
    quantity: float

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    if bot_engine:
        return bot_engine.get_status()
    return {"error": "Bot not initialized"}

@app.post("/api/control")
async def control_bot(action: str):
    if not bot_engine:
        return {"error": "Bot not initialized"}
    
    if action == "start":
        bot_engine.start()
        return {"status": "started"}
    elif action == "stop":
        bot_engine.stop()
        return {"status": "stopped"}
    return {"error": "Invalid action"}

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    if bot_engine:
        # Update strategy parameters dynamically
        bot_engine.strategy.spread = config.spread
        bot_engine.strategy.quantity = config.quantity
        return {"status": "updated", "config": config}
    return {"error": "Bot not initialized"}

@app.post("/api/leverage")
async def update_leverage(leverage: int):
    if not bot_engine:
        return {"error": "Bot not initialized"}
    
    # Validate leverage range (Binance allows 1-125x)
    if leverage < 1 or leverage > 125:
        return {"error": "Leverage must be between 1 and 125"}
    
    # Set leverage via exchange client
    success = bot_engine.client.set_leverage(leverage)
    if success:
        return {"status": "updated", "leverage": leverage}
    else:
        return {"error": "Failed to set leverage"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
