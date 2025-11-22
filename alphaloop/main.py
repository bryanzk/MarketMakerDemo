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
        
    def run_cycle(self):
        logger.info("Starting AlphaLoop Cycle")
        
        # 1. Run Simulation / Execution
        sim = MarketSimulator(self.strategy)
        stats = sim.run(steps=500)
        
        # 2. Data Ingestion & Analysis
        # Assuming sim.run returns trades in stats for now, or we need to modify sim
        # For this prototype, we'll pass the aggregate stats as a mock
        self.data.ingest_data({'price': 1000}, []) # Mock ingestion
        metrics = self.data.calculate_metrics()
        
        logger.info(f"Cycle Performance", extra={'extra_data': {'pnl': stats['realized_pnl'], 'metrics': metrics}})
        
        # 3. Quant Analysis & Proposal
        current_config = {'spread': self.strategy.spread}
        # Pass metrics to Quant instead of raw stats
        proposal = self.quant.analyze_and_propose(current_config, {**stats, **metrics})
        
        if not proposal:
            logger.info("No changes proposed. Cycle complete.")
            return
            
        # 3. Risk Validation
        approved = self.risk.validate_proposal(proposal)
        
        if approved:
            # 4. Deployment (Apply changes)
            logger.info(f"Applying new config", extra={'extra_data': {'proposal': proposal}})
            self.strategy.spread = proposal['spread']
            # In a real system, this would commit code or update a config file/DB
        else:
            logger.warning("Proposal rejected by Risk. Keeping current config.")
            
    def run_continuous(self, cycles=5):
        for i in range(cycles):
            logger.info(f"Iteration {i+1}")
            self.run_cycle()
            time.sleep(1)

if __name__ == "__main__":
    loop = AlphaLoop()
    loop.run_continuous(cycles=3)
