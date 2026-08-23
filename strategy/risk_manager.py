#!/usr/bin/env python3
"""
Risk Manager
Manages position sizing, exposure limits, and risk controls
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self, config: Dict):
        """Initialize risk manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.risk_config = config['risk']
        self.total_capital = self._get_total_capital()
        self.current_exposure = 0.0
        self.open_positions = []
        self.daily_loss = 0.0
    
    def _get_total_capital(self) -> float:
        """Get total trading capital
        
        Returns:
            Total capital amount
        """
        try:
            return self.config.get('initial_capital', 10000)
        except Exception as e:
            logger.error(f"Error getting total capital: {e}")
            return 10000
    
    def check_position_size(self, amount_usd: float) -> bool:
        """Check if position size is within limits
        
        Args:
            amount_usd: Position size in USD
            
        Returns:
            True if position size is acceptable
        """
        max_size = self.risk_config.get('max_position_size_usd', 1000)
        
        if amount_usd > max_size:
            logger.warning(f"Position size {amount_usd} exceeds max {max_size}")
            return False
        
        return True
    
    def check_exposure(self) -> bool:
        """Check if portfolio exposure is within limits
        
        Returns:
            True if exposure is acceptable
        """
        max_exposure_pct = self.risk_config.get('max_exposure_pct', 0.30)
        max_exposure = self.total_capital * max_exposure_pct
        
        if self.current_exposure > max_exposure:
            logger.warning(f"Exposure {self.current_exposure} exceeds max {max_exposure}")
            return False
        
        return True
    
    def check_daily_loss(self, current_loss: float) -> bool:
        """Check if daily loss exceeds limit
        
        Args:
            current_loss: Current daily loss
            
        Returns:
            True if loss is within acceptable range
        """
        max_daily_loss_pct = self.risk_config.get('max_daily_loss_pct', 0.05)
        max_daily_loss = self.total_capital * max_daily_loss_pct
        
        if current_loss > max_daily_loss:
            logger.error(f"Daily loss {current_loss} exceeds max {max_daily_loss}")
            return False
        
        return True
    
    def calculate_position_size(self, capital_allocation_pct: float = 0.01) -> float:
        """Calculate recommended position size
        
        Args:
            capital_allocation_pct: Percentage of capital to allocate (default 1%)
            
        Returns:
            Recommended position size
        """
        return self.total_capital * capital_allocation_pct
    
    def add_position(self, position: Dict):
        """Add position to tracking
        
        Args:
            position: Position details
        """
        self.open_positions.append(position)
        self.current_exposure += position.get('amount', 0)
    
    def close_position(self, position_id: str):
        """Close a position
        
        Args:
            position_id: ID of position to close
        """
        for i, position in enumerate(self.open_positions):
            if position.get('id') == position_id:
                self.current_exposure -= position.get('amount', 0)
                self.open_positions.pop(i)
                break
    
    def get_position_count(self) -> int:
        """Get number of open positions
        
        Returns:
            Number of open positions
        """
        return len(self.open_positions)
