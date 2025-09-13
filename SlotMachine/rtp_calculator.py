"""
RTP (Return to Player) and House Edge calculation and adjustment utilities
"""

import math
from typing import Dict, List, Tuple
from config_manager import ConfigManager

class RTPCalculator:
    """Calculate and adjust RTP based on game configuration"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.config_data
    
    def calculate_symbol_probabilities(self) -> Dict[str, float]:
        """Calculate probability of each symbol appearing"""
        weights = self.config['symbols']['weights']
        total_weight = sum(weights.values())
        
        probabilities = {}
        for symbol, weight in weights.items():
            probabilities[symbol] = weight / total_weight
        
        return probabilities
    
    def calculate_combination_probability(self, combination: str) -> float:
        """Calculate probability of a specific 3-symbol combination"""
        if len(combination) < 3:
            return 0.0
        
        probabilities = self.calculate_symbol_probabilities()
        
        # Extract first 3 symbols from combination
        symbols = [combination[i] for i in range(3)]
        
        total_prob = 1.0
        for symbol in symbols:
            if symbol in probabilities:
                total_prob *= probabilities[symbol]
            else:
                return 0.0  # Invalid symbol
        
        return total_prob
    
    def calculate_theoretical_rtp(self) -> float:
        """Calculate theoretical RTP percentage"""
        paytable = self.config['paytable']
        expected_return_per_bet = 0.0
        
        for combination, payout in paytable.items():
            probability = self.calculate_combination_probability(combination)
            expected_return_per_bet += probability * payout
        
        # Add multiplier effects
        multiplier_bonus = self._calculate_multiplier_bonus()
        expected_return_per_bet += multiplier_bonus
        
        # Add bonus round contribution
        bonus_contribution = self._calculate_bonus_contribution()
        expected_return_per_bet += bonus_contribution
        
        return expected_return_per_bet * 100  # Convert to percentage
    
    def _calculate_multiplier_bonus(self) -> float:
        """Calculate expected return from multiplier symbols"""
        probabilities = self.calculate_symbol_probabilities()
        multipliers = self.config['symbols']['special_symbols']['multipliers']
        
        multiplier_bonus = 0.0
        for multiplier in multipliers:
            if multiplier in probabilities:
                multiplier_value = int(multiplier[1])  # Extract number from 'x2', 'x3', etc.
                prob = probabilities[multiplier]
                # Assume multiplier applies to average base win
                avg_base_win = self._calculate_average_base_win()
                multiplier_bonus += prob * (multiplier_value - 1) * avg_base_win
        
        return multiplier_bonus
    
    def _calculate_average_base_win(self) -> float:
        """Calculate average base win amount"""
        paytable = self.config['paytable']
        probabilities = self.calculate_symbol_probabilities()
        
        total_expected = 0.0
        for combination, payout in paytable.items():
            prob = self.calculate_combination_probability(combination)
            total_expected += prob * payout
        
        return total_expected
    
    def _calculate_bonus_contribution(self) -> float:
        """Calculate expected return from bonus rounds"""
        bonus_settings = self.config['bonus_settings']
        probabilities = self.calculate_symbol_probabilities()
        
        bonus_symbol = self.config['symbols']['special_symbols']['bonus']
        if bonus_symbol not in probabilities:
            return 0.0
        
        # Probability of getting at least one bonus symbol in 5 reels
        prob_no_bonus = (1 - probabilities[bonus_symbol]) ** 5
        prob_bonus = 1 - prob_no_bonus
        
        # Expected return from bonus round
        bonus_spins = bonus_settings['bonus_spins']
        bonus_multiplier = bonus_settings.get('bonus_multiplier', 1.0)
        avg_base_win = self._calculate_average_base_win()
        
        expected_bonus_return = prob_bonus * bonus_spins * bonus_multiplier * avg_base_win
        
        return expected_bonus_return
    
    def calculate_house_edge(self) -> float:
        """Calculate house edge percentage"""
        rtp = self.calculate_theoretical_rtp()
        return 100 - rtp
    
    def adjust_rtp_to_target(self, target_rtp: float) -> Dict[str, float]:
        """Adjust symbol weights to achieve target RTP"""
        current_rtp = self.calculate_theoretical_rtp()
        
        if abs(current_rtp - target_rtp) < 0.1:
            return self.config['symbols']['weights']
        
        # Simple adjustment: scale payout multipliers
        adjustment_factor = target_rtp / current_rtp
        
        # Adjust paytable values
        adjusted_paytable = {}
        for combination, payout in self.config['paytable'].items():
            adjusted_paytable[combination] = round(payout * adjustment_factor, 2)
        
        return adjusted_paytable
    
    def analyze_variance(self) -> Dict[str, float]:
        """Calculate game variance metrics"""
        paytable = self.config['paytable']
        probabilities = self.calculate_symbol_probabilities()
        
        # Calculate variance
        payouts = []
        probs = []
        
        for combination, payout in paytable.items():
            prob = self.calculate_combination_probability(combination)
            payouts.append(payout)
            probs.append(prob)
        
        # Expected value
        expected_value = sum(p * prob for p, prob in zip(payouts, probs))
        
        # Variance calculation
        variance = sum(prob * (payout - expected_value) ** 2 
                      for payout, prob in zip(payouts, probs))
        
        standard_deviation = math.sqrt(variance)
        
        # Classify variance level
        if standard_deviation < 10:
            variance_level = "Low"
        elif standard_deviation < 30:
            variance_level = "Medium"
        else:
            variance_level = "High"
        
        return {
            'variance': variance,
            'standard_deviation': standard_deviation,
            'variance_level': variance_level,
            'expected_value': expected_value
        }
    
    def get_rtp_analysis_report(self) -> str:
        """Generate comprehensive RTP analysis report"""
        theoretical_rtp = self.calculate_theoretical_rtp()
        house_edge = self.calculate_house_edge()
        variance_analysis = self.analyze_variance()
        probabilities = self.calculate_symbol_probabilities()
        
        report = f"""
🔍 RTP ANALYSIS REPORT 🔍
========================

📊 CORE METRICS:
• Theoretical RTP: {theoretical_rtp:.2f}%
• House Edge: {house_edge:.2f}%
• Target RTP: {self.config['rtp_settings']['target_rtp']}%
• RTP Difference: {theoretical_rtp - self.config['rtp_settings']['target_rtp']:+.2f}%

📈 VARIANCE ANALYSIS:
• Variance Level: {variance_analysis['variance_level']}
• Standard Deviation: {variance_analysis['standard_deviation']:.2f}
• Expected Win per Spin: ${variance_analysis['expected_value']:.4f}

🎯 SYMBOL PROBABILITIES:
"""
        
        for symbol, prob in probabilities.items():
            report += f"  {symbol}: {prob:.4f} ({prob*100:.2f}%)\n"
        
        report += "\n🏆 COMBINATION ANALYSIS:\n"
        for combination, payout in self.config['paytable'].items():
            prob = self.calculate_combination_probability(combination)
            frequency = 1 / prob if prob > 0 else float('inf')
            contribution = prob * payout * 100  # Contribution to RTP
            
            report += f"  {combination}: ${payout} | 1 in {frequency:.0f} | +{contribution:.3f}% RTP\n"
        
        # RTP optimization suggestions
        report += "\n💡 OPTIMIZATION SUGGESTIONS:\n"
        if theoretical_rtp > self.config['rtp_settings']['target_rtp'] + 1:
            report += "  • Consider reducing paytable values to lower RTP\n"
            report += "  • Increase house edge by adjusting symbol weights\n"
        elif theoretical_rtp < self.config['rtp_settings']['target_rtp'] - 1:
            report += "  • Consider increasing paytable values to raise RTP\n"
            report += "  • Decrease house edge by adjusting symbol weights\n"
        else:
            report += "  • RTP is well-balanced and close to target\n"
        
        if variance_analysis['variance_level'] == "Low":
            report += "  • Consider adding higher-value combinations for more excitement\n"
        elif variance_analysis['variance_level'] == "High":
            report += "  • Consider balancing with more frequent smaller wins\n"
        
        return report

def create_rtp_calculator(config_file: str = "config.json") -> RTPCalculator:
    """Create RTP calculator with loaded configuration"""
    from config_manager import ConfigManager
    
    config_manager = ConfigManager(config_file)
    config_manager.load_config()
    
    return RTPCalculator(config_manager)