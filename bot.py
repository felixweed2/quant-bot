#!/usr/bin/env python3
"""
Quant Bot - Self-Replicating Cryptocurrency Arbitrage Trading Bot
Main bot engine that runs the trading strategy
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
import traceback

from exchanges.exchange_manager import ExchangeManager
from strategy.arbitrage import ArbitrageStrategy
from strategy.risk_manager import RiskManager
from strategy.order_manager import OrderManager
from monitoring.performance import PerformanceMonitor
from monitoring.replicator import BotReplicator
from monitoring.self_destruct import SelfDestructMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class QuantBot:
    """Main bot engine for arbitrage trading"""
    
    def __init__(self, config_path: str = 'config/config.yaml', mode: str = 'paper'):
        """Initialize the bot with configuration
        
        Args:
            config_path: Path to configuration file
            mode: 'paper' for simulation, 'live' for real trading
        """
        self.config_path = config_path
        self.mode = mode
        self.running = False
        self.config = self._load_config()
        
        logger.info(f"Initializing QuantBot in {mode} mode")
        
        # Initialize components
        self.exchange_manager = ExchangeManager(self.config)
        self.arbitrage_strategy = ArbitrageStrategy(self.config)
        self.risk_manager = RiskManager(self.config)
        self.order_manager = OrderManager(self.exchange_manager, self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        self.replicator = BotReplicator(self.config)
        self.self_destruct_monitor = SelfDestructMonitor(self.config)
        
        logger.info("QuantBot initialized successfully")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration: {e}")
            sys.exit(1)
    
    def _check_arbitrage_opportunities(self) -> List[Dict]:
        """Detect arbitrage opportunities across exchanges
        
        Returns:
            List of arbitrage opportunities found
        """
        opportunities = []
        
        try:
            trading_pairs = self.config['trading']['trading_pairs']
            
            for pair in trading_pairs:
                # Fetch prices from multiple exchanges
                prices = self.exchange_manager.get_prices(pair)
                
                if not prices:
                    continue
                
                # Detect arbitrage opportunities
                arb_opp = self.arbitrage_strategy.detect(pair, prices)
                
                if arb_opp and arb_opp['profit_margin'] > self.config['trading']['min_profit_margin']:
                    opportunities.append(arb_opp)
                    logger.info(f"Arbitrage opportunity found: {pair} - Profit: {arb_opp['profit_margin']*100:.2f}%")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error checking arbitrage opportunities: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def _execute_trade(self, opportunity: Dict) -> bool:
        """Execute an arbitrage trade
        
        Args:
            opportunity: Arbitrage opportunity to trade
            
        Returns:
            True if trade executed successfully
        """
        try:
            # Check risk limits
            if not self.risk_manager.check_position_size(opportunity['amount']):
                logger.warning(f"Trade size exceeds risk limits: {opportunity['amount']}")
                return False
            
            if not self.risk_manager.check_exposure():
                logger.warning("Portfolio exposure exceeds maximum")
                return False
            
            if self.mode == 'paper':
                # Simulate trade
                logger.info(f"[PAPER] Simulated trade: BUY {opportunity['pair']} at {opportunity['buy_exchange']}")
                logger.info(f"[PAPER] Simulated trade: SELL {opportunity['pair']} at {opportunity['sell_exchange']}")
                self.performance_monitor.record_trade(opportunity, is_simulated=True)
                return True
            
            else:  # Live trading
                # Place actual orders
                buy_order = self.order_manager.place_order(
                    exchange=opportunity['buy_exchange'],
                    pair=opportunity['pair'],
                    side='buy',
                    amount=opportunity['amount'],
                    price=opportunity['buy_price']
                )
                
                if not buy_order:
                    logger.error(f"Failed to place buy order for {opportunity['pair']}")
                    return False
                
                # Wait for buy order to fill
                time.sleep(2)
                
                # Place sell order
                sell_order = self.order_manager.place_order(
                    exchange=opportunity['sell_exchange'],
                    pair=opportunity['pair'],
                    side='sell',
                    amount=opportunity['amount'],
                    price=opportunity['sell_price']
                )
                
                if not sell_order:
                    logger.error(f"Failed to place sell order for {opportunity['pair']}")
                    return False
                
                logger.info(f"Arbitrage trade executed: {opportunity['pair']} - Profit: {opportunity['profit']:.2f} USDT")
                self.performance_monitor.record_trade(opportunity, is_simulated=False)
                return True
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _check_daily_pnl(self):
        """Check daily P&L and update performance metrics"""
        try:
            daily_pnl = self.performance_monitor.get_daily_pnl()
            daily_return_pct = self.performance_monitor.get_daily_return_pct()
            
            logger.info(f"Daily P&L: {daily_pnl:.2f} USDT ({daily_return_pct*100:.2f}%)")
            
            # Check for replication trigger
            if self.performance_monitor.should_replicate():
                logger.warning("Replication trigger met! Bot is profitable enough to replicate.")
                if self.replicator.spawn_bot(self.config):
                    logger.info("New bot instance spawned successfully")
            
            # Check for self-destruct trigger
            if self.self_destruct_monitor.should_destruct():
                logger.error("SELF-DESTRUCT TRIGGER MET! Shutting down bot...")
                self.shutdown()
                
        except Exception as e:
            logger.error(f"Error checking daily P&L: {e}")
            logger.error(traceback.format_exc())
    
    def run(self):
        """Main trading loop"""
        logger.info(f"Starting QuantBot in {self.mode} mode")
        self.running = True
        last_pnl_check = datetime.now()
        price_check_interval = self.config['scheduler']['price_check_interval']
        pnl_check_interval = self.config['scheduler']['pnl_check_interval']
        
        try:
            while self.running:
                # Check for arbitrage opportunities
                opportunities = self._check_arbitrage_opportunities()
                
                # Execute profitable trades
                for opportunity in opportunities:
                    if opportunity['profit_margin'] > self.config['trading']['min_profit_margin']:
                        self._execute_trade(opportunity)
                
                # Check P&L periodically
                if (datetime.now() - last_pnl_check).total_seconds() > pnl_check_interval:
                    self._check_daily_pnl()
                    last_pnl_check = datetime.now()
                
                # Sleep before next price check
                time.sleep(price_check_interval)
                
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.error(traceback.format_exc())
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the bot"""
        logger.info("Shutting down QuantBot...")
        self.running = False
        
        # Close all open positions
        try:
            self.order_manager.close_all_positions()
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
        
        # Generate final report
        try:
            final_report = self.performance_monitor.generate_report()
            logger.info(f"Final Report: {final_report}")
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
        
        logger.info("QuantBot shutdown complete")
        sys.exit(0)


def main():
    """Entry point for the bot"""
    parser = argparse.ArgumentParser(description='QuantBot - Arbitrage Trading Bot')
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper',
                        help='Trading mode: paper (simulation) or live (real trading)')
    parser.add_argument('--config', default='config/config.yaml',
                        help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and run bot
    bot = QuantBot(config_path=args.config, mode=args.mode)
    bot.run()


if __name__ == '__main__':
    main()
