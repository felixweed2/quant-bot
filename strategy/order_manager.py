#!/usr/bin/env python3
"""
Order Manager
Handles order placement, tracking, and execution
"""

import logging
import time
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages order placement and tracking"""
    
    def __init__(self, exchange_manager, config: Dict):
        """Initialize order manager
        
        Args:
            exchange_manager: Exchange manager instance
            config: Configuration dictionary
        """
        self.exchange_manager = exchange_manager
        self.config = config
        self.orders = {}  # Track all orders
        self.order_counter = 0
    
    def place_order(self, exchange: str, pair: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """Place an order on exchange
        
        Args:
            exchange: Exchange name (e.g., 'binance')
            pair: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Price per unit
            
        Returns:
            Order details or None if failed
        """
        try:
            order_id = f"ORD_{self.order_counter}_{datetime.now().timestamp()}"
            self.order_counter += 1
            
            order = {
                'id': order_id,
                'exchange': exchange,
                'pair': pair,
                'side': side,
                'amount': amount,
                'price': price,
                'status': 'pending',
                'timestamp': datetime.now(),
                'fills': []
            }
            
            # Place order via exchange manager
            result = self.exchange_manager.place_order(
                exchange=exchange,
                pair=pair,
                side=side,
                amount=amount,
                price=price,
                order_type=self.config['trading'].get('order_type', 'limit')
            )
            
            if result:
                order['status'] = 'open'
                order['exchange_order_id'] = result.get('id')
                self.orders[order_id] = order
                logger.info(f"Order placed: {order_id} - {side.upper()} {amount} {pair} at {price}")
                return order
            else:
                logger.error(f"Failed to place order on {exchange}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """Get status of an order
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status or None
        """
        if order_id in self.orders:
            return self.orders[order_id].get('status')
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        try:
            if order_id not in self.orders:
                logger.warning(f"Order not found: {order_id}")
                return False
            
            order = self.orders[order_id]
            result = self.exchange_manager.cancel_order(
                exchange=order['exchange'],
                order_id=order.get('exchange_order_id')
            )
            
            if result:
                order['status'] = 'cancelled'
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                logger.error(f"Failed to cancel order: {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def close_all_positions(self):
        """Close all open positions by cancelling pending orders"""
        logger.info("Closing all open positions...")
        
        for order_id, order in list(self.orders.items()):
            if order.get('status') in ['pending', 'open']:
                self.cancel_order(order_id)
    
    def get_order_history(self, limit: int = 100) -> list:
        """Get recent order history
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            List of recent orders
        """
        orders_list = sorted(
            self.orders.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )
        return orders_list[:limit]
