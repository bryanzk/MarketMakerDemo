from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import threading
import os
import time

# Import the bot engine class
from alphaloop.main import AlphaLoop

app = FastAPI()

# Setup Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Global Bot Instance
bot_engine = AlphaLoop()
bot_thread = None
is_running = False

class ConfigUpdate(BaseModel):
    spread: float
    quantity: float

class PairUpdate(BaseModel):
    symbol: str

def run_bot_loop():
    global is_running
    while is_running:
        bot_engine.run_cycle()
        time.sleep(1)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Clear any stale alerts on page load
    bot_engine.alert = None
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    status = bot_engine.get_status()
    status["active"] = is_running
    status["stage"] = bot_engine.current_stage
    return status


@app.post("/api/control")
async def control_bot(action: str):
    global is_running, bot_thread
    
    if action == "start":
        if not is_running:
            # Validate current config before starting
            current_spread = bot_engine.strategy.spread
            
            approved, reason = bot_engine.risk.validate_proposal({'spread': current_spread})
            
            if not approved:
                # Generate 3 suggestions
                min_spread = bot_engine.risk.risk_limits['MIN_SPREAD']
                max_spread = bot_engine.risk.risk_limits['MAX_SPREAD']
                
                suggestions = [
                    {
                        "label": "Conservative",
                        "spread": round(max_spread * 0.9, 4), # 90% of max allowed
                        "desc": "Safe choice"
                    },
                    {
                        "label": "Balanced",
                        "spread": round((min_spread + max_spread) / 2, 4), # Midpoint
                        "desc": "Middle ground"
                    },
                    {
                        "label": "Boundary",
                        "spread": round(max_spread * 0.99, 4) if current_spread > max_spread else round(min_spread * 1.01, 4),
                        "desc": "Limit edge"
                    }
                ]
                
                # Set alert so it shows up in status polling
                bot_engine.alert = {
                    "type": "warning",
                    "message": f"Risk Rejection: {reason}",
                    "suggestion": "Select a compliant setting below:",
                    "options": suggestions
                }
                
                # Return error with suggestions
                return {
                    "error": f"Risk Rejection: {reason}",
                    "suggestions": suggestions
                }
            
            is_running = True
            bot_thread = threading.Thread(target=run_bot_loop)
            bot_thread.daemon = True
            bot_thread.start()
            
        return {"status": "started"}
    elif action == "stop":
        is_running = False
        bot_engine.alert = None # Clear alerts on stop
        bot_engine.current_stage = "Idle"
        return {"status": "stopped"}
    return {"error": "Invalid action"}

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    # Convert spread from percentage (e.g., 0.005%) to decimal (0.00005)
    new_spread = config.spread / 100
    
    # 1. Validate with Risk Agent FIRST
    proposal = {'spread': new_spread}
    approved, reason = bot_engine.risk.validate_proposal(proposal)
    
    if not approved:
        return {"error": f"Risk Rejection: {reason}"}

    # 2. Apply if approved
    bot_engine.strategy.spread = new_spread
    bot_engine.strategy.quantity = config.quantity
    
    # Clear any existing alerts since we fixed it
    bot_engine.alert = None
    
    return {"status": "updated", "config": config}

@app.post("/api/leverage")
async def update_leverage(leverage: int):
    return {"status": "mock_updated", "leverage": leverage}

@app.post("/api/pair")
async def update_pair(pair: PairUpdate):
    success = bot_engine.set_symbol(pair.symbol)
    if success:
        return {"status": "updated", "symbol": pair.symbol}
    else:
        return {"status": "error", "message": f"Failed to update to symbol {pair.symbol}"}

@app.get("/api/suggestions")
async def get_suggestions():
    # Get metrics from DataAgent
    metrics = bot_engine.data.calculate_metrics()
    sharpe = metrics.get('sharpe_ratio', 0)
    
    # Get current config
    current_spread = bot_engine.strategy.spread * 100 # Convert back to percentage for display
    current_leverage = bot_engine.strategy.leverage # Assuming strategy has leverage
    
    # Risk-aware suggestions
    suggestion = {
        "spread": current_spread,
        "leverage": current_leverage,
        "condition": "Stable",
        "reason": "Current settings are stable."
    }

    # Check for high volatility
    volatility = metrics.get('volatility', 0)
    if volatility > 0.005: # Example threshold for high volatility
        suggestion["spread"] = round(current_spread * 1.2, 2) # Widen spread by 20%
        suggestion["leverage"] = max(1, current_leverage - 2) # Reduce leverage
        suggestion["condition"] = "High Volatility"
        suggestion["reason"] = "Market is volatile. Widening spread and reducing leverage to mitigate risk."
    
    # Check for low Sharpe Ratio
    if sharpe < 1.0 and volatility < 0.005: # Only suggest if not already adjusting for volatility
        suggestion["spread"] = round(current_spread * 1.1, 2) # Slightly widen spread
        suggestion["leverage"] = max(1, current_leverage - 1) # Slightly reduce leverage
        suggestion["condition"] = "Low Sharpe Ratio"
        suggestion["reason"] = "Performance is low. Adjusting spread and leverage to improve risk-adjusted returns."
    
    # Check for high PnL and low risk
    if sharpe > 2.0 and volatility < 0.002: # Example for good performance
        suggestion["spread"] = round(current_spread * 0.9, 2) # Tighten spread
        suggestion["leverage"] = current_leverage + 1 # Increase leverage
        suggestion["condition"] = "Excellent Performance"
        suggestion["reason"] = "Strong performance with low risk. Optimizing for higher returns."

    # Ensure spread is within reasonable bounds (e.g., 0.01% to 1%)
    suggestion["spread"] = max(0.01, min(1.0, suggestion["spread"]))
    # Ensure leverage is within reasonable bounds (e.g., 1 to 10)
    suggestion["leverage"] = max(1, min(10, suggestion["leverage"]))
        
    return suggestion

@app.get("/api/performance")
async def get_performance():
    # Get metrics from DataAgent
    metrics = bot_engine.data.calculate_metrics()
    # Add some mock trade counts since DataAgent tracks history
    total_trades = len(bot_engine.data.trade_history)
    
    return {
        "realized_pnl": sum(t['pnl'] for t in bot_engine.data.trade_history),
        "total_trades": total_trades,
        "metrics": metrics
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
