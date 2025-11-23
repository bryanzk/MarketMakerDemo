import sys
import time
from alphaloop.market.simulation import MarketSimulator
from alphaloop.strategies.strategy import FixedSpreadStrategy
from alphaloop.agents.quant import QuantAgent
from alphaloop.agents.risk import RiskAgent
from alphaloop.agents.data import DataAgent
from alphaloop.core.logger import setup_logger

logger = setup_logger("AlphaLoop")

class AlphaLoop:
    def __init__(self):
        self.strategy = FixedSpreadStrategy()
        self.quant = QuantAgent()
        self.risk = RiskAgent()
        self.data = DataAgent()
        self.alert = None
        self.current_stage = "Idle"
        self.active_orders = []
        
    def get_status(self):
        return {
            "active": True, # Mock active state
            "mid_price": 2000.0, # Mock
            "position": 0.5, # Mock
            "pnl": 150.0, # Mock
            "position": 0.5, # Mock
            "pnl": 150.0, # Mock
            "alert": self.alert,
            "orders": self.active_orders
        }
        
    def run_cycle(self):
        logger.info("Starting AlphaLoop Cycle")
        self.current_stage = "Market Simulation"
        
        # 1. Run Simulation / Execution
        sim = MarketSimulator(self.strategy)
        sim = MarketSimulator(self.strategy)
        stats = sim.run(steps=500)
        # Capture latest orders from strategy for display
        # In a real engine, this would be the open orders from the exchange
        # For mock, we'll recalculate based on current market data
        mock_market = sim.generate_market_data()
        self.active_orders = self.strategy.calculate_target_orders(mock_market)
        # Add mock IDs
        for i, o in enumerate(self.active_orders):
            o['id'] = f"ord_{int(time.time())}_{i}"
            o['amount'] = o['quantity'] # Frontend expects 'amount'
        
        # 2. Data Ingestion & Analysis
        self.current_stage = "Data Analysis"
        # Assuming sim.run returns trades in stats for now, or we need to modify sim
        # For this prototype, we'll pass the aggregate stats as a mock
        self.data.ingest_data({'price': 1000}, []) # Mock ingestion
        metrics = self.data.calculate_metrics()
        
        logger.info(f"Cycle Performance", extra={'extra_data': {'pnl': stats['realized_pnl'], 'metrics': metrics}})
        
        # 3. Quant Analysis & Proposal
        self.current_stage = "Quant Strategy"
        current_config = {'spread': self.strategy.spread}
        # Pass metrics to Quant instead of raw stats
        proposal = self.quant.analyze_and_propose(current_config, {**stats, **metrics})
        
        if not proposal:
            logger.info("No changes proposed. Cycle complete.")
            return
            
        # 3. Risk Validation
        self.current_stage = "Risk Check"
        approved, reason = self.risk.validate_proposal(proposal)
        
        if approved:
            # 4. Deployment (Apply changes)
            self.current_stage = "Execution"
            logger.info(f"Applying new config", extra={'extra_data': {'proposal': proposal}})
            self.strategy.spread = proposal['spread']
            self.alert = None # Clear alert on success
        else:
            logger.warning(f"Proposal rejected: {reason}")
            self.alert = {
                "type": "warning",
                "message": f"Risk Rejection: {reason}",
                "suggestion": "Check your strategy settings or market volatility."
            }
            
    def run_continuous(self, cycles=5):
        for i in range(cycles):
            logger.info(f"Iteration {i+1}")
            self.run_cycle()
            self.current_stage = "Idle"
            time.sleep(1)

if __name__ == "__main__":
    loop = AlphaLoop()
    loop.run_continuous(cycles=3)
