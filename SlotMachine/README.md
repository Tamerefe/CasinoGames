# 🎰 Casino Slot Machine Game

A sophisticated Python-based slot machine simulator with advanced features including configurable RTP (Return to Player), analytics tracking, database persistence, and multiple game modes.

## 🌟 Features

### Core Game Features
- **5-Reel Slot Machine** with emoji symbols
- **Progressive Jackpot System** with configurable contribution rates
- **Wild Cards & Multipliers** for enhanced gameplay
- **Bonus Rounds** with free spins
- **Auto-Play Mode** with customizable parameters
- **Quick Spin Mode** for faster gameplay

### Advanced Configuration
- **Configurable RTP** (Return to Player percentage)
- **Dynamic Symbol Weights** for probability adjustment
- **Multiple Configuration Profiles** (Beginner, High Roller, etc.)
- **Flexible Paytable System**
- **House Edge Calculations**

### Analytics & Tracking
- **Real-time Analytics** with win/loss tracking
- **Session Management** with detailed statistics
- **SQLite Database** for persistent data storage
- **CSV Export** functionality for analysis
- **Historical Performance** tracking

### User Experience
- **Colorful Console Interface** with emoji symbols
- **User Profiles** with persistent balances
- **Session History** tracking
- **Comprehensive Logging** system
- **Windows-optimized** key detection

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Windows OS (optimized for Windows terminal)

### Required Dependencies
```bash
pip install colorama
```

### Setup
1. Clone or download the project files
2. Navigate to the SlotMachine directory
3. Install dependencies:
   ```powershell
   pip install colorama
   ```
4. Run the game:
   ```powershell
   python slot.py
   ```

## 🎮 How to Play

### Basic Gameplay
1. **Start the Game**: Run `python slot.py`
2. **Place Your Bet**: Choose amount between min/max bet limits
3. **Spin the Reels**: Press Enter or use auto-play mode
4. **Check Winnings**: Match symbols across paylines to win
5. **Manage Balance**: Game saves your progress automatically

### Game Controls
- **Enter**: Spin the reels
- **A**: Toggle auto-play mode
- **Q**: Quit game
- **S**: View session statistics
- **P**: View player profile

### Winning Combinations
- **Three of a Kind**: Match 3 identical symbols
- **Wild Cards** (🃏): Substitute for any symbol
- **Multipliers** (x2, x3, x5): Multiply your winnings
- **Bonus Symbols** (🎁): Trigger free spin rounds
- **Jackpot** (💰💰💰): Hit the progressive jackpot!

## ⚙️ Configuration

### Configuration Files
- `config.json` - Default game settings
- `config_beginner.json` - Beginner-friendly settings
- `config_high_roller.json` - High-stakes configuration

### Key Configuration Options

#### Game Settings
```json
{
    "game_settings": {
        "starting_balance": 1000,
        "jackpot_reset": 500,
        "initial_jackpot_pool": 500,
        "jackpot_contribution_rate": 0.1,
        "max_bet": 500,
        "min_bet": 1
    }
}
```

#### Symbol Weights
Adjust probability of each symbol appearing:
```json
{
    "symbols": {
        "weights": {
            "🍒": 30,  // Common symbol (higher chance)
            "🍋": 25,
            "🔔": 20,
            "⭐": 15,
            "7️⃣": 7,
            "🍉": 3,
            "💰": 1    // Rare symbol (lower chance)
        }
    }
}
```

#### RTP Settings
Configure return-to-player percentage:
```json
{
    "rtp_settings": {
        "target_rtp": 95.0,
        "house_edge": 5.0,
        "variance": "medium"
    }
}
```

## 📊 Analytics & Statistics

### Real-time Tracking
- **Win/Loss Ratio**
- **RTP Percentage** (actual vs theoretical)
- **Total Spins** and betting volume
- **Biggest Wins** and losses
- **Session Duration**

### Database Features
- **User Profiles**: Persistent player data
- **Session History**: Detailed gameplay records
- **Balance Tracking**: Automatic save/load
- **Analytics Export**: CSV format for analysis

### Viewing Analytics
```python
# In-game analytics
python slot.py
# Press 'S' during gameplay for session stats

# Direct RTP calculation
python -c "from rtp_calculator import create_rtp_calculator; calc = create_rtp_calculator(); print(f'Theoretical RTP: {calc.calculate_theoretical_rtp():.2f}%')"
```

## 🗂️ Project Structure

```
SlotMachine/
├── slot.py                 # Main game engine
├── config_manager.py       # Configuration management
├── rtp_calculator.py       # RTP calculations and analysis
├── config.json            # Default game configuration
├── config_beginner.json   # Beginner settings
├── config_high_roller.json # High-stakes settings
├── slot.log               # Game activity logs
├── slot_analytics.csv     # Analytics export
├── slot_fluent.py         # Alternative game interface
├── database/
│   ├── db.py             # Database operations
│   ├── case.db           # SQLite database
│   └── __pycache__/      # Python cache files
└── README.md             # This file
```

### Core Modules

#### `slot.py`
Main game engine with:
- Game loop and user interface
- Reel spinning mechanics
- Win calculation logic
- Auto-play functionality
- Session management

#### `config_manager.py`
Configuration system featuring:
- JSON configuration loading
- Validation and error handling
- Multiple configuration profiles
- Game settings management

#### `rtp_calculator.py`
Mathematical engine for:
- Theoretical RTP calculation
- Symbol probability analysis
- House edge verification
- Win frequency predictions

#### `database/db.py`
Data persistence layer:
- SQLite database operations
- User profile management
- Session tracking
- Analytics storage

## 🔧 Advanced Features

### Auto-Play Mode
Configure automated gameplay:
- **Target High**: Stop when balance reaches this amount
- **Target Low**: Stop when balance drops to this amount
- **Spin Count**: Maximum number of auto-spins
- **Balance Monitoring**: Automatic stop conditions

### Configuration Profiles
Switch between different game modes:
```powershell
# Load beginner configuration
python slot.py config_beginner.json

# Load high-roller configuration  
python slot.py config_high_roller.json
```

### RTP Analysis
Analyze game mathematics:
```python
from rtp_calculator import create_rtp_calculator
calc = create_rtp_calculator()

# Get theoretical RTP
rtp = calc.calculate_theoretical_rtp()
print(f"Theoretical RTP: {rtp:.2f}%")

# Analyze symbol probabilities
probs = calc.calculate_symbol_probabilities()
for symbol, prob in probs.items():
    print(f"{symbol}: {prob:.3f}")
```

## 📈 Game Mathematics

### RTP Calculation
The game uses mathematical models to ensure fair gameplay:
- **Theoretical RTP**: Based on paytable and symbol weights
- **Actual RTP**: Tracked through gameplay sessions
- **Variance Control**: Configurable for different player types

### Symbol Probability
Each symbol has weighted probability:
- **High-value symbols**: Lower probability, higher payouts
- **Common symbols**: Higher probability, moderate payouts
- **Special symbols**: Rare, trigger bonus features

### House Edge
Configurable house advantage:
- Default: 5% house edge (95% RTP)
- Adjustable through configuration
- Verified through mathematical analysis

## 🛠️ Development

### Adding New Features
1. **New Symbols**: Add to `config.json` weights and paytable
2. **Bonus Games**: Extend bonus logic in `slot.py`
3. **Analytics**: Add tracking to `database/db.py`
4. **Configuration**: Update validation in `config_manager.py`

### Testing
```powershell
# Test configuration loading
python -c "from config_manager import load_game_config; config = load_game_config(); print('Config OK')"

# Test RTP calculation
python -c "from rtp_calculator import create_rtp_calculator; calc = create_rtp_calculator(); print(f'RTP: {calc.calculate_theoretical_rtp():.2f}%')"

# Test database
python -c "from database.db import initialize_db; initialize_db(); print('Database OK')"
```

### Logging
Game activity is logged to `slot.log`:
- **WARNING** level: Only significant events
- **INFO** level: Big wins and important actions
- **ERROR** level: System errors and exceptions

## 📝 License

This project is open source and available for educational and personal use.

## 🤝 Contributing

Feel free to contribute by:
- Adding new features
- Improving game balance
- Enhancing user interface
- Optimizing performance
- Adding new configuration options

## 🎯 Future Enhancements

- **Multi-line Payouts**: Support for multiple paylines
- **Progressive Bonuses**: More complex bonus games
- **Tournament Mode**: Competitive gameplay
- **Web Interface**: Browser-based version
- **Mobile Support**: Touch-friendly interface
- **Sound Effects**: Audio enhancement
- **Theme System**: Multiple visual themes

---

**Happy Spinning! 🎰✨**