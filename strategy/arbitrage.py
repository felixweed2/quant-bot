#!/usr/bin/env python3
"""
Arbitrage Strategy
Detects and calculates cross-exchange arbitrage opportunities
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ArbitrageStrategy:
    """Detects and calculates arbitrage opportunities"""
    
    def __init__(self, config: Dict):
        """Initialize arbitrage strategy
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_profit_margin = config['trading']['min_profit_margin']
    
    def detect(self, pair: str, prices: Dict[str, float]) -> Optional[Dict]:
        """Detect arbitrage opportunity for a trading pair
        
        Args:
            pair: Trading pair (e.g., 'BTC/USDT')
            prices: Dictionary of prices from different exchanges
                    Format: {exchange: {'ask': price, 'bid': price}}
        
        Returns:
            Arbitrage opportunity dict or None if no opportunity found
        """
        if not prices or len(prices) < 2:
            return None
        
        try:
            best_buy = None
            best_sell = None
            best_buy_exchange = None
            best_sell_exchange = None
            
            # Find cheapest ask (buy price) and highest bid (sell price)
            for exchange, price_data in prices.items():
                if 'ask' not in price_data or 'bid' not in price_data:
                    continue
                
                ask_price = price_data['ask']
                bid_price = price_data['bid']
                
                if best_buy is None or ask_price < best_buy:
                    best_buy = ask_price
                    best_buy_exchange = exchange
                
                if best_sell is None or bid_price > best_sell:
                    best_sell = bid_price
                    best_sell_exchange = exchange
            
            if not best_buy or not best_sell or best_buy_exchange == best_sell_exchange:
                return None
            
            # Calculate profit
            profit_margin = (best_sell - best_buy) / best_buy
            
            if profit_margin < self.min_profit_margin:
                return None
            
            # Calculate amount to trade (based on capital allocation)
            position_size = self.config['risk']['max_position_size_usd']
            amount = position_size / best_buy
            
            # Account for trading fees
            buy_fee = self.config['exchanges'].get(best_buy_exchange, {}).get('fee_pct', 0.001)
            sell_fee = self.config['exchanges'].get(best_sell_exchange, {}).get('fee_pct', 0.001)
            
            net_profit = (best_sell - best_buy) * amount - (best_buy * amount * buy_fee) - (best_sell * amount * sell_fee)
            net_profit_margin = net_profit / position_size
            
            return {
                'pair': pair,
                'buy_exchange': best_buy_exchange,
                'buy_price': best_buy,
                'sell_exchange': best_sell_exchange,
                'sell_price': best_sell,
                'amount': amount,
                'profit_margin': profit_margin,
                'net_profit': net_profit,
                'net_profit_margin': net_profit_margin,
                'profit': net_profit,
                'timestamp': None
            }
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage: {e}")
            return None
    
    def calculate_roi(self, profit: float, investment: float) -> float:
        """Calculate return on investment
        
        Args:
            profit: Profit amount
            investment: Initial investment
            
        Returns:
            ROI as percentage
        """
        if investment <= 0:
            return 0.0
        return (profit / investment) * 100
