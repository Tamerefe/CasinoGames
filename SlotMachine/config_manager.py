"""
Configuration management for Slot Machine
Handles loading, validation, and management of game settings
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GameConfig:
    """Game configuration data class"""
    starting_balance: int
    jackpot_reset: int
    initial_jackpot_pool: int
    jackpot_contribution_rate: float
    max_bet: int
    min_bet: int
    symbol_weights: Dict[str, int]
    paytable: Dict[str, int]
    target_rtp: float
    house_edge: float
    bonus_spins: int
    enable_animations: bool
    
class ConfigManager:
    """Manages game configuration loading and validation"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_data = None
        self.game_config = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Config file '{self.config_file}' not found")
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
                
            self.validate_config()
            self.game_config = self._create_game_config()
            
            print(f"✅ Configuration loaded successfully from {self.config_file}")
            return self.config_data
            
        except FileNotFoundError as e:
            print(f"❌ Config file error: {e}")
            self._create_default_config()
            return self.load_config()
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            raise
            
        except Exception as e:
            print(f"❌ Config loading error: {e}")
            raise
    
    def validate_config(self):
        """Validate configuration data"""
        required_sections = ['game_settings', 'symbols', 'paytable', 'rtp_settings']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate RTP settings
        rtp = self.config_data['rtp_settings']['target_rtp']
        house_edge = self.config_data['rtp_settings']['house_edge']
        
        if rtp < 70 or rtp > 99:
            raise ValueError(f"Invalid RTP: {rtp}%. Must be between 70-99%")
            
        if abs(rtp + house_edge - 100) > 0.1:
            print(f"⚠️ Warning: RTP ({rtp}%) + House Edge ({house_edge}%) ≠ 100%")
        
        # Validate symbol weights
        weights = self.config_data['symbols']['weights']
        if not weights or sum(weights.values()) == 0:
            raise ValueError("Symbol weights must be positive and sum > 0")
        
        print("✅ Configuration validation passed")
    
    def _create_game_config(self) -> GameConfig:
        """Create GameConfig object from loaded data"""
        game_settings = self.config_data['game_settings']
        symbols = self.config_data['symbols']
        rtp_settings = self.config_data['rtp_settings']
        bonus_settings = self.config_data['bonus_settings']
        animation_settings = self.config_data['animation_settings']
        
        return GameConfig(
            starting_balance=game_settings['starting_balance'],
            jackpot_reset=game_settings['jackpot_reset'],
            initial_jackpot_pool=game_settings['initial_jackpot_pool'],
            jackpot_contribution_rate=game_settings['jackpot_contribution_rate'],
            max_bet=game_settings['max_bet'],
            min_bet=game_settings['min_bet'],
            symbol_weights=symbols['weights'],
            paytable=self.config_data['paytable'],
            target_rtp=rtp_settings['target_rtp'],
            house_edge=rtp_settings['house_edge'],
            bonus_spins=bonus_settings['bonus_spins'],
            enable_animations=animation_settings['enable_animations']
        )
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "game_settings": {
                "starting_balance": 1000,
                "jackpot_reset": 500,
                "initial_jackpot_pool": 500,
                "jackpot_contribution_rate": 0.1,
                "max_bet": 500,
                "min_bet": 1
            },
            "symbols": {
                "weights": {
                    "🍒": 30, "🍋": 25, "🔔": 20, "⭐": 15,
                    "7️⃣": 7, "🍉": 3, "💰": 1, "🎁": 5,
                    "🃏": 8, "x2": 5, "x3": 3, "x5": 2
                }
            },
            "paytable": {
                "🍒🍒🍒": 5, "🍋🍋🍋": 7, "🔔🔔🔔": 10,
                "⭐⭐⭐": 20, "7️⃣7️⃣7️⃣": 50, "🍉🍉🍉": 100, "🃏🃏🃏": 200
            },
            "rtp_settings": {
                "target_rtp": 94.5,
                "house_edge": 5.5
            },
            "bonus_settings": {
                "bonus_spins": 3
            },
            "animation_settings": {
                "enable_animations": True
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Created default config file: {self.config_file}")
    
    def get_difficulty_preset(self, difficulty: str) -> Dict[str, Any]:
        """Get configuration for specific difficulty level"""
        if 'difficulty_presets' not in self.config_data:
            return {}
            
        presets = self.config_data['difficulty_presets']
        if difficulty not in presets:
            available = list(presets.keys())
            raise ValueError(f"Unknown difficulty '{difficulty}'. Available: {available}")
        
        return presets[difficulty]
    
    def apply_difficulty_preset(self, difficulty: str):
        """Apply difficulty preset to current configuration"""
        preset = self.get_difficulty_preset(difficulty)
        
        # Update RTP settings
        if 'target_rtp' in preset:
            self.config_data['rtp_settings']['target_rtp'] = preset['target_rtp']
        if 'house_edge' in preset:
            self.config_data['rtp_settings']['house_edge'] = preset['house_edge']
        if 'starting_balance' in preset:
            self.config_data['game_settings']['starting_balance'] = preset['starting_balance']
        
        # Recreate game config
        self.game_config = self._create_game_config()
        print(f"🎮 Applied '{difficulty}' difficulty preset")
    
    def calculate_theoretical_rtp(self) -> float:
        """Calculate theoretical RTP based on paytable and symbol weights"""
        weights = self.config_data['symbols']['weights']
        paytable = self.config_data['paytable']
        
        total_weight = sum(weights.values())
        total_combinations = total_weight ** 3  # For 3-reel combinations
        
        expected_return = 0
        
        for combination, payout in paytable.items():
            if len(combination) >= 3:
                # Get symbols in combination (first 3 chars)
                symbols = [combination[i] for i in range(0, min(len(combination), 3))]
                
                # Calculate probability of this combination
                prob = 1
                for symbol in symbols:
                    if symbol in weights:
                        prob *= weights[symbol] / total_weight
                
                expected_return += prob * payout
        
        return expected_return * 100  # Convert to percentage
    
    def get_config_summary(self) -> str:
        """Get formatted configuration summary"""
        if not self.config_data:
            return "No configuration loaded"
        
        theoretical_rtp = self.calculate_theoretical_rtp()
        
        summary = f"""
🎰 SLOT MACHINE CONFIGURATION 🎰
================================
💰 Starting Balance: ${self.game_config.starting_balance}
🎯 Target RTP: {self.game_config.target_rtp}%
🏠 House Edge: {self.game_config.house_edge}%
📊 Theoretical RTP: {theoretical_rtp:.2f}%
💎 Jackpot Pool: ${self.game_config.initial_jackpot_pool}
🔄 Jackpot Reset: ${self.game_config.jackpot_reset}
🎁 Bonus Spins: {self.game_config.bonus_spins}
🎬 Animations: {'Enabled' if self.game_config.enable_animations else 'Disabled'}

📋 Symbol Weights:
"""
        
        for symbol, weight in self.game_config.symbol_weights.items():
            percentage = (weight / sum(self.game_config.symbol_weights.values())) * 100
            summary += f"  {symbol}: {weight} ({percentage:.1f}%)\n"
        
        summary += "\n💰 Paytable:\n"
        for combo, payout in self.game_config.paytable.items():
            summary += f"  {combo}: ${payout}\n"
        
        return summary

# Global config manager instance
config_manager = ConfigManager()

def load_game_config(config_file: str = "config.json") -> GameConfig:
    """Load and return game configuration"""
    config_manager.config_file = config_file
    config_manager.load_config()
    return config_manager.game_config

def get_config_manager() -> ConfigManager:
    """Get the global config manager instance"""
    return config_manager