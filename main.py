import time
import logging
import sys
import threading
from config import REFRESH_INTERVAL, LOG_LEVEL, SYMBOL
from exchange import BinanceClient
from strategy import FixedSpreadStrategy
from risk import RiskManager
from order_manager import OrderManager

# Setup Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class BotEngine:
    # Start time for Realized PnL: 2025-11-20 11:00 ET (16:00 UTC)
    PNL_START_TIME = 1763654400000
    PNL_START_STR = "2025-11-20 11:00 ET"

    def __init__(self):
        self.running = False
        self.thread = None
        self.status = {
            "mid_price": 0.0,
            "position": 0.0,
            "balance": 0.0,
            "orders": [],
            "pnl": 0.0,
            "realized_pnl": 0.0,
            "pnl_start_str": self.PNL_START_STR,
            "leverage": 0,
            "active": False,
            "error": None
        }
        
        # Initialize Modules
        try:
            self.client = BinanceClient()
            self.strategy = FixedSpreadStrategy()
            self.risk = RiskManager()
            self.om = OrderManager()
            logger.info(f"Connected to Binance Testnet. Symbol: {SYMBOL}")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise e

    def start(self):
        if self.running:
            logger.warning("Bot is already running.")
            return
        
        # Check connection before starting
        try:
            account_data = self.client.fetch_account_data()
            if not account_data:
                logger.error("Failed to connect to exchange. Cannot start bot.")
                self.status["error"] = "Connection failed"
                return
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self.status["error"] = str(e)
            return
        
        # Reset error state
        self.status["error"] = None
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Bot started in background thread.")

    def stop(self):
        if not self.running:
            return
        
        logger.info("Stopping bot...")
        self.running = False
        
        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=5)
        
        # Cancel all open orders for safety
        try:
            self.client.cancel_all_orders()
            logger.info("All orders canceled.")
        except Exception as e:
            logger.error(f"Error canceling orders during stop: {e}")
        
        logger.info("Bot stopped.")

    def get_status(self):
        self.status["active"] = self.running
        return self.status

    def _run_loop(self):
        try:
            while self.running:
                try:
                    # 1. Fetch Data
                    market_data = self.client.fetch_market_data()
                    if not market_data or not market_data['mid_price']:
                        logger.warning("Market data unavailable, skipping tick.")
                        time.sleep(REFRESH_INTERVAL)
                        continue

                    account_data = self.client.fetch_account_data()
                    if not account_data:
                        logger.warning("Account data unavailable, skipping tick.")
                        time.sleep(REFRESH_INTERVAL)
                        continue

                    current_orders = self.client.fetch_open_orders()

                    # Fetch Realized PnL (less frequent? for now every tick is fine for MVP)
                    realized_pnl = self.client.fetch_realized_pnl(start_time=self.PNL_START_TIME)
                    
                    # Fetch current leverage
                    leverage = self.client.get_leverage() or 0

                    # Update Status
                    self.status.update({
                        "mid_price": market_data['mid_price'],
                        "position": account_data['position_amt'],
                        "balance": account_data['balance'],
                        "orders": current_orders,
                        # Simple PnL calc (unrealized)
                        "pnl": (market_data['mid_price'] - account_data['entry_price']) * account_data['position_amt'] if account_data['position_amt'] != 0 else 0.0,
                        "realized_pnl": realized_pnl,
                        "leverage": leverage
                    })

                    # 2. Strategy Calculation
                    target_orders = self.strategy.calculate_target_orders(market_data)

                    # 3. Risk Check
                    allowed_sides = self.risk.check_position_limits(account_data['position_amt'])
                    filtered_orders = [o for o in target_orders if o['side'] in allowed_sides]
                    
                    if len(filtered_orders) < len(target_orders):
                        logger.warning(f"Risk limit reached! Allowed sides: {allowed_sides}. Filtered orders.")

                    # 4. Order Management
                    to_cancel_ids, to_place_orders = self.om.sync_orders(current_orders, filtered_orders)

                    # 5. Execution
                    if to_cancel_ids:
                        self.client.cancel_orders(to_cancel_ids)
                    
                    if to_place_orders:
                        self.client.place_orders(to_place_orders)

                    # 6. Logging
                    logger.info(
                        f"Mid: {market_data['mid_price']:.2f} | "
                        f"Pos: {account_data['position_amt']} | "
                        f"Bal: {account_data['balance']:.2f} | "
                        f"Orders: {len(current_orders)} -> -{len(to_cancel_ids)} +{len(to_place_orders)}"
                    )

                except Exception as e:
                    logger.error(f"Error in main loop iteration: {e}")
                
                time.sleep(REFRESH_INTERVAL)
        except Exception as e:
            # Critical error - stop the bot
            logger.error(f"CRITICAL ERROR in bot loop: {e}")
            self.status["error"] = str(e)
            self.stop()
            self.status["active"] = False

# Global Instance for Server
bot_engine = None
try:
    bot_engine = BotEngine()
except Exception:
    pass # Allow server to start even if bot fails init (for debugging)

if __name__ == "__main__":
    # Standalone mode
    if bot_engine:
        try:
            bot_engine.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bot_engine.stop()
