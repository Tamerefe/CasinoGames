import random
import time
import os
import logging
import csv
import json
import msvcrt  # For Windows key detection
from datetime import datetime
from colorama import Fore, Style, init
from database.db import initialize_db, fetch_initial_values, update_jackpot_pool, save_analytics_to_db, get_historical_analytics, save_balance, load_balance, create_user_profile, start_session, end_session, get_user_sessions, update_user_stats, get_user_profile, get_user_profile_by_username, get_session_stats, get_db_connection
from config_manager import load_game_config, get_config_manager
from rtp_calculator import create_rtp_calculator

init(autoreset=True)

# Load game configuration
game_config = load_game_config()
config_manager = get_config_manager()
rtp_calculator = create_rtp_calculator()

# Configure logging (reduced verbosity for better flow)
logging.basicConfig(
    filename='slot.log',
    level=logging.WARNING,  # Only log warnings and errors
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Load configuration-based game data
paytable = game_config.paytable
jackpot_symbol = "💰💰💰💰"
bonus_symbol = config_manager.config_data['symbols']['special_symbols']['bonus']
wild_symbol = config_manager.config_data['symbols']['special_symbols']['wild']
multipliers = config_manager.config_data['symbols']['special_symbols']['multipliers']

# Game flow settings for better experience
AUTO_PLAY_MODE = False
QUICK_SPIN_MODE = True
SHOW_ANALYTICS = False

# Auto-play variables
auto_start_balance = 0
auto_target_high = 0
auto_target_low = 0
auto_spin_count = 0

def log_spin_data(reels, bet, win_result, balance, jackpot_pool):
    """Simplified logging - only big wins for better performance"""
    if isinstance(win_result, int) and win_result > bet * 10:  # Only log big wins
        logging.info(f"Big win: ${win_result} on bet ${bet}")
    
    # Simplified CSV logging
    csv_filename = 'slot_analytics.csv'
    file_exists = os.path.isfile(csv_filename)
    
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'bet_amount', 'win_amount', 'balance_after']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bet_amount': bet,
            'win_amount': win_result if isinstance(win_result, int) else 0,
            'balance_after': balance
        })

def calculate_analytics():
    """Calculate RTP and other analytics from CSV data"""
    csv_filename = 'slot_analytics.csv'
    
    if not os.path.isfile(csv_filename):
        return None
    
    total_bets = 0
    total_wins = 0
    total_spins = 0
    win_count = 0
    bonus_count = 0
    jackpot_count = 0
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                total_spins += 1
                total_bets += float(row['bet_amount'])
                win_amount = float(row['win_amount'])
                total_wins += win_amount
                
                if win_amount > 0:
                    win_count += 1
                
                if row['win_type'] == 'bonus_round':
                    bonus_count += 1
                elif row['win_type'] == 'jackpot':
                    jackpot_count += 1
        
        # Calculate RTP (Return to Player)
        rtp = (total_wins / total_bets * 100) if total_bets > 0 else 0
        win_rate = (win_count / total_spins * 100) if total_spins > 0 else 0
        avg_bet = total_bets / total_spins if total_spins > 0 else 0
        avg_win = total_wins / win_count if win_count > 0 else 0
        
        return {
            'total_spins': total_spins,
            'total_bets': total_bets,
            'total_wins': total_wins,
            'net_result': total_wins - total_bets,
            'rtp_percentage': round(rtp, 2),
            'win_rate_percentage': round(win_rate, 2),
            'win_count': win_count,
            'bonus_count': bonus_count,
            'jackpot_count': jackpot_count,
            'average_bet': round(avg_bet, 2),
            'average_win': round(avg_win, 2)
        }
    
    except Exception as e:
        logging.error(f"Error calculating analytics: {e}")
        return None

def display_analytics():
    """Display analytics report to user"""
    analytics = calculate_analytics()
    
    if not analytics:
        print(Fore.YELLOW + "No analytics data available yet. Play some spins first!")
        return
    
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*60)
    print(Fore.CYAN + Style.BRIGHT + "📊 SLOT MACHINE ANALYTICS REPORT 📊")
    print(Fore.CYAN + Style.BRIGHT + "="*60)
    
    print(Fore.GREEN + f"🎰 Total Spins: {analytics['total_spins']}")
    print(Fore.YELLOW + f"💰 Total Bets: ${analytics['total_bets']:.2f}")
    print(Fore.YELLOW + f"🏆 Total Wins: ${analytics['total_wins']:.2f}")
    print(Fore.RED + f"📈 Net Result: ${analytics['net_result']:.2f}")
    
    print(Fore.MAGENTA + "\n--- PERCENTAGES ---")
    print(Fore.BLUE + f"📊 RTP (Return to Player): {analytics['rtp_percentage']:.2f}%")
    print(Fore.BLUE + f"🎯 Win Rate: {analytics['win_rate_percentage']:.2f}%")
    
    print(Fore.MAGENTA + "\n--- WIN STATISTICS ---")
    print(Fore.GREEN + f"✅ Winning Spins: {analytics['win_count']}")
    print(Fore.CYAN + f"🎁 Bonus Rounds: {analytics['bonus_count']}")
    print(Fore.YELLOW + f"💎 Jackpots: {analytics['jackpot_count']}")
    
    print(Fore.MAGENTA + "\n--- AVERAGES ---")
    print(Fore.WHITE + f"💵 Average Bet: ${analytics['average_bet']:.2f}")
    print(Fore.WHITE + f"🏅 Average Win: ${analytics['average_win']:.2f}")
    
    # RTP Analysis
    print(Fore.MAGENTA + "\n--- RTP ANALYSIS ---")
    if analytics['rtp_percentage'] > 95:
        print(Fore.GREEN + "🔥 Excellent RTP! Players are getting great returns!")
    elif analytics['rtp_percentage'] > 85:
        print(Fore.YELLOW + "👍 Good RTP! Balanced gameplay.")
    elif analytics['rtp_percentage'] > 70:
        print(Fore.ORANGE + "⚠️ Low RTP. House edge is high.")
    else:
        print(Fore.RED + "🚨 Very Low RTP! Players losing heavily.")
    
    print(Fore.CYAN + Style.BRIGHT + "="*60 + "\n")

def display_historical_analytics():
    """Display historical analytics from database"""
    history = get_historical_analytics()
    
    if not history:
        print(Fore.YELLOW + "No historical data available yet.")
        return
    
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*80)
    print(Fore.CYAN + Style.BRIGHT + "📈 HISTORICAL ANALYTICS (Last 10 Sessions) 📈")
    print(Fore.CYAN + Style.BRIGHT + "="*80)
    
    print(f"{'Date':<12} {'Spins':<8} {'Total Bet':<12} {'Total Win':<12} {'RTP%':<8} {'Win%':<8} {'Bonus':<7} {'Jackpot':<8}")
    print("-" * 80)
    
    for row in history:
        date, spins, bets, wins, rtp, win_rate, bonus, jackpot = row
        print(f"{date:<12} {spins:<8} ${bets:<11.2f} ${wins:<11.2f} {rtp:<7.1f} {win_rate:<7.1f} {bonus:<7} {jackpot:<8}")
    
    print(Fore.CYAN + Style.BRIGHT + "="*80 + "\n")

def show_config_menu():
    """Display configuration menu and options"""
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*60)
    print(Fore.CYAN + Style.BRIGHT + "⚙️  GAME CONFIGURATION MENU  ⚙️")
    print(Fore.CYAN + Style.BRIGHT + "="*60)
    
    print(Fore.YELLOW + "Current Configuration:")
    print(config_manager.get_config_summary())
    
    print(Fore.MAGENTA + "\nConfiguration Options:")
    print(Fore.WHITE + "1. View RTP Analysis")
    print(Fore.WHITE + "2. Change Difficulty Level")
    print(Fore.WHITE + "3. View Symbol Probabilities")
    print(Fore.WHITE + "4. Export Current Config")
    print(Fore.WHITE + "5. Return to Game")
    
    try:
        choice = input(Fore.YELLOW + "Choose option (1-5): ").strip()
        
        if choice == "1":
            print(rtp_calculator.get_rtp_analysis_report())
            input(Fore.GREEN + "Press Enter to continue...")
            
        elif choice == "2":
            show_difficulty_menu()
            
        elif choice == "3":
            show_symbol_probabilities()
            
        elif choice == "4":
            export_config()
            
        elif choice == "5":
            return
            
        # Show menu again after each action (except return)
        if choice in ["1", "2", "3", "4"]:
            show_config_menu()
            
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def show_difficulty_menu():
    """Show difficulty selection menu"""
    presets = config_manager.config_data.get('difficulty_presets', {})
    
    print(Fore.CYAN + "\n🎮 DIFFICULTY LEVELS:")
    for i, (name, settings) in enumerate(presets.items(), 1):
        rtp = settings.get('target_rtp', 'N/A')
        balance = settings.get('starting_balance', 'N/A')
        print(Fore.WHITE + f"{i}. {name.capitalize()}: RTP {rtp}%, Starting ${balance}")
    
    try:
        choice = input(Fore.YELLOW + f"Choose difficulty (1-{len(presets)}): ").strip()
        difficulty_names = list(presets.keys())
        
        if choice.isdigit() and 1 <= int(choice) <= len(difficulty_names):
            selected_difficulty = difficulty_names[int(choice) - 1]
            config_manager.apply_difficulty_preset(selected_difficulty)
            
            # Update global variables
            global game_config, paytable, rtp_calculator
            game_config = config_manager.game_config
            paytable = game_config.paytable
            rtp_calculator = create_rtp_calculator()
            
            print(Fore.GREEN + f"✅ Applied '{selected_difficulty}' difficulty!")
            
    except Exception as e:
        print(Fore.RED + f"Error changing difficulty: {e}")

def show_symbol_probabilities():
    """Display symbol probability analysis"""
    probabilities = rtp_calculator.calculate_symbol_probabilities()
    
    print(Fore.CYAN + "\n🎯 SYMBOL PROBABILITIES:")
    print("-" * 40)
    
    for symbol, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
        percentage = prob * 100
        frequency = 1 / prob if prob > 0 else float('inf')
        print(f"{symbol}: {percentage:6.2f}% (1 in {frequency:4.1f})")
    
    input(Fore.GREEN + "\nPress Enter to continue...")

def export_config():
    """Export current configuration to a new file"""
    try:
        filename = f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_manager.config_data, f, indent=2, ensure_ascii=False)
        
        print(Fore.GREEN + f"✅ Configuration exported to: {filename}")
        
    except Exception as e:
        print(Fore.RED + f"Error exporting config: {e}")
    
    input(Fore.GREEN + "Press Enter to continue...")

def spin_reel():
    """Spin a single reel using configuration-based symbol weights"""
    symbols = list(game_config.symbol_weights.keys())
    weights = list(game_config.symbol_weights.values())
    return random.choices(symbols, weights=weights)[0]

def spin_slot_machine():
    return [spin_reel(), spin_reel(), spin_reel(), spin_reel(), spin_reel()]  # 5-reel system

def quick_spin_animation():
    """Fast but visually appealing animation"""
    if not game_config.enable_animations:
        return spin_slot_machine()
    
    # Clear screen for better effect
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # All possible symbols for spinning animation
    all_symbols = list(game_config.symbol_weights.keys())
    
    # Fast animation settings
    spin_frames = 8  # Reduced from 15+
    reel_delay = 0.05  # Much faster than original
    
    print(Fore.CYAN + Style.BRIGHT + "🎰 SPINNING REELS... 🎰")
    print(Fore.MAGENTA + "=" * 40)
    
    # Generate final results first
    final_reels = [spin_reel() for _ in range(5)]
    
    # Fast spinning animation for all reels
    for frame in range(spin_frames):
        # Clear previous line
        print('\r', end='')
        
        # Show spinning symbols
        display_reels = []
        for reel_idx in range(5):
            if frame > reel_idx + 2:  # Each reel stops progressively
                display_reels.append(final_reels[reel_idx])  # Stopped
            else:
                display_reels.append(random.choice(all_symbols))  # Still spinning
        
        # Beautiful reel display
        reel_display = f"│ {display_reels[0]}  │ {display_reels[1]}  │ {display_reels[2]}  │ {display_reels[3]}  │ {display_reels[4]}  │"
        
        print(Fore.YELLOW + "┌─────┬─────┬─────┬─────┬─────┐")
        print(Fore.YELLOW + reel_display)
        print(Fore.YELLOW + "└─────┴─────┴─────┴─────┴─────┘")
        
        # Status bar
        progress = "█" * (frame + 1) + "░" * (spin_frames - frame - 1)
        print(Fore.GREEN + f"Progress: [{progress}]")
        
        time.sleep(reel_delay)
        
        # Clear for next frame (except last)
        if frame < spin_frames - 1:
            print('\033[4A', end='')  # Move cursor up 4 lines
    
    # Final dramatic blink effect (very quick)
    for blink in range(3):
        if blink % 2 == 0:
            color = Fore.YELLOW + Style.BRIGHT
        else:
            color = Fore.RED + Style.BRIGHT
        
        print('\033[3A', end='')  # Move up to reel display
        print(color + "┌─────┬─────┬─────┬─────┬─────┐")
        print(color + f"│ {final_reels[0]}  │ {final_reels[1]}  │ {final_reels[2]}  │ {final_reels[3]}  │ {final_reels[4]}  │")
        print(color + "└─────┴─────┴─────┴─────┴─────┘")
        time.sleep(0.15)
    
    print(Fore.GREEN + Style.BRIGHT + "\n🎉 SPIN COMPLETE! 🎉")
    time.sleep(0.3)  # Brief pause to appreciate result
    
    return final_reels

def check_win(reels, bet, jackpot_pool):
    combination = ''.join(reels[:3])
    
    multiplier = 1
    for reel in reels:
        if reel in multipliers:
            multiplier = int(reel[1])  # Determine the multiplier
    
    if combination in paytable:
        return paytable[combination] * multiplier
    elif ''.join(reels) == jackpot_symbol:
        jackpot_winnings = jackpot_pool
        jackpot_pool = 500  # Jackpot resets
        update_jackpot_pool(jackpot_pool)
        return jackpot_winnings
    elif bonus_symbol in reels:
        return "bonus"
    return 0

def quick_bonus_round():
    """Fast but exciting bonus round"""
    bonus_spins = game_config.bonus_spins
    print(Fore.YELLOW + Style.BRIGHT + f"🎁 BONUS ROUND! {bonus_spins} FREE SPINS! 🎁")
    print(Fore.MAGENTA + "=" * 50)
    
    total_bonus_winnings = 0
    
    for spin_num in range(bonus_spins):
        print(Fore.CYAN + f"\n🎰 Bonus Spin {spin_num + 1}/{bonus_spins}:")
        
        # Quick mini-animation for bonus
        for i in range(3):
            symbols = [random.choice(list(game_config.symbol_weights.keys())) for _ in range(5)]
            print(f"\r🎲 [ {' | '.join(symbols)} ]", end="", flush=True)
            time.sleep(0.08)
        
        # Final result
        reels = spin_slot_machine()
        winnings = check_win(reels, 0, 0)
        
        print(f"\r✨ [ {' | '.join(reels)} ]", end="")
        
        if isinstance(winnings, int) and winnings > 0:
            total_bonus_winnings += winnings
            print(Fore.GREEN + f" → WIN ${winnings}! 🎉")
        else:
            print(Fore.WHITE + " → No win")
        
        time.sleep(0.2)  # Brief pause between spins
    
    print(Fore.MAGENTA + "\n" + "=" * 50)
    if total_bonus_winnings > 0:
        print(Fore.GREEN + Style.BRIGHT + f"🏆 TOTAL BONUS WIN: ${total_bonus_winnings}! 🏆")
    else:
        print(Fore.YELLOW + "💔 No bonus wins this time - but free spins are always fun! 💔")
    print(Fore.MAGENTA + "=" * 50)
    
    time.sleep(0.5)  # Brief celebration pause
    return total_bonus_winnings

def display_slot_machine(reels, jackpot_pool, win_result=None, bet=None):
    """Clean, compact result display"""
    print(f"\n{'='*50}")
    print(Fore.YELLOW + f"💰 Jackpot: ${jackpot_pool:.2f}")
    print(Fore.CYAN + f"🎰 [ {' | '.join(reels)} ]")
    
    if win_result is not None and bet is not None:
        if isinstance(win_result, int) and win_result > 0:
            profit = win_result - bet
            print(Fore.GREEN + f"✅ WIN: ${win_result} (Profit: +${profit})")
        elif win_result == "bonus":
            print(Fore.YELLOW + "🎁 BONUS ROUND!")
        else:
            print(Fore.RED + f"❌ Loss: -${bet}")
    
    print(f"{'='*50}")

def show_legal_warning():
    """Display legal warning before game starts"""
    print(Fore.RED + Style.BRIGHT + "\n" + "="*60)
    print(Fore.RED + Style.BRIGHT + "⚠️  WARNING: EDUCATIONAL SOFTWARE ONLY ⚠️")
    print(Fore.RED + Style.BRIGHT + "="*60)
    print(Fore.YELLOW + Style.BRIGHT + "• NO REAL MONEY INVOLVED")
    print(Fore.YELLOW + Style.BRIGHT + "• NOT REAL GAMBLING")
    print(Fore.YELLOW + Style.BRIGHT + "• FOR EDUCATIONAL PURPOSES ONLY")
    print(Fore.YELLOW + Style.BRIGHT + "• AGE 18+ ONLY")
    print(Fore.RED + Style.BRIGHT + "="*60)
    print(Fore.CYAN + "This game demonstrates programming concepts and game mechanics.")
    print(Fore.CYAN + "All monetary values are fictional and for educational purposes only.")
    print(Fore.RED + Style.BRIGHT + "="*60)
    input(Fore.GREEN + "Press Enter to continue...")
    print("\n" + "="*60 + "\n")

def user_login_menu():
    """Handle user login/registration process"""
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*60)
    print(Fore.CYAN + Style.BRIGHT + "👤 USER PROFILE SYSTEM 👤")
    print(Fore.CYAN + Style.BRIGHT + "="*60)
    
    while True:
        print(Fore.MAGENTA + "\nUser Options:")
        print(Fore.WHITE + "1. Login with existing user")
        print(Fore.WHITE + "2. Create new user profile")
        print(Fore.WHITE + "3. Play as guest (no profile)")
        print(Fore.WHITE + "4. Exit game")
        
        try:
            choice = input(Fore.YELLOW + "Choose option (1-4): ").strip()
            
            if choice == "1":
                return login_existing_user()
            elif choice == "2":
                return create_new_user()
            elif choice == "3":
                return None  # Guest mode
            elif choice == "4":
                print(Fore.CYAN + "Thanks for playing! Goodbye!")
                exit()
            else:
                print(Fore.RED + "Invalid option. Please try again.")
                
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

def login_existing_user():
    """Login with existing user profile"""
    username = input(Fore.YELLOW + "Enter username: ").strip()
    
    if not username:
        print(Fore.RED + "Username cannot be empty!")
        return None
    
    user_profile = get_user_profile_by_username(username)
    
    if not user_profile:
        print(Fore.RED + f"User '{username}' not found!")
        print(Fore.CYAN + "Would you like to create a new profile instead? (y/n)")
        if input().strip().lower() == 'y':
            return create_user_profile(username, game_config.starting_balance)
        return None
    
    print(Fore.GREEN + f"Welcome back, {username}!")
    print(Fore.CYAN + f"Current balance: ${user_profile['balance']:.2f}")
    print(Fore.CYAN + f"Total sessions: {user_profile['session_count']}")
    print(Fore.CYAN + f"Total spins: {user_profile['total_spins']}")
    print(Fore.CYAN + f"Biggest win: ${user_profile['biggest_win']:.2f}")
    
    return user_profile

def create_new_user():
    """Create new user profile"""
    username = input(Fore.YELLOW + "Enter new username: ").strip()
    
    if not username:
        print(Fore.RED + "Username cannot be empty!")
        return None
    
    # Check if user already exists
    existing_user = get_user_profile_by_username(username)
    if existing_user:
        print(Fore.RED + f"User '{username}' already exists!")
        return None
    
    # Create new user profile
    user_profile = create_user_profile(username, game_config.starting_balance)
    
    if user_profile:
        print(Fore.GREEN + f"User profile created successfully!")
        print(Fore.CYAN + f"Welcome to the casino, {username}!")
        print(Fore.CYAN + f"Starting balance: ${user_profile['balance']:.2f}")
        return user_profile
    else:
        print(Fore.RED + "Failed to create user profile!")
        return None

def display_user_profile_menu(user_profile):
    """Display user profile and statistics menu"""
    if not user_profile:
        return
    
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + f"👤 USER PROFILE: {user_profile['username']} 👤")
    print(Fore.CYAN + Style.BRIGHT + "="*70)
    
    print(Fore.GREEN + f"💰 Current Balance: ${user_profile['balance']:.2f}")
    print(Fore.YELLOW + f"🎲 Total Sessions: {user_profile['session_count']}")
    print(Fore.YELLOW + f"🎰 Total Spins: {user_profile['total_spins']}")
    print(Fore.YELLOW + f"💸 Total Bets: ${user_profile['total_bets']:.2f}")
    print(Fore.YELLOW + f"🏆 Total Wins: ${user_profile['total_wins']:.2f}")
    print(Fore.YELLOW + f"💎 Biggest Win: ${user_profile['biggest_win']:.2f}")
    
    # Calculate additional statistics
    if user_profile['total_bets'] > 0:
        user_rtp = (user_profile['total_wins'] / user_profile['total_bets']) * 100
        net_result = user_profile['total_wins'] - user_profile['total_bets']
        avg_bet = user_profile['total_bets'] / user_profile['total_spins'] if user_profile['total_spins'] > 0 else 0
        
        print(Fore.MAGENTA + f"\n📊 Personal Statistics:")
        print(Fore.WHITE + f"📈 Personal RTP: {user_rtp:.2f}%")
        print(Fore.WHITE + f"💵 Net Result: ${net_result:.2f}")
        print(Fore.WHITE + f"🎯 Average Bet: ${avg_bet:.2f}")
        
        # Performance analysis
        if user_rtp > 100:
            print(Fore.GREEN + "🔥 You're winning overall! Great luck!")
        elif user_rtp > 90:
            print(Fore.YELLOW + "👍 You're doing well! Close to break-even.")
        else:
            print(Fore.RED + "📉 House edge is working. Try different strategies!")
    
    print(Fore.MAGENTA + f"\n📅 Account Information:")
    print(Fore.WHITE + f"📅 Member Since: {user_profile['created_at']}")
    print(Fore.WHITE + f"🕐 Last Login: {user_profile['last_login']}")
    
    # Show recent sessions
    sessions = get_user_sessions(user_profile['user_id'], limit=5)
    if sessions:
        print(Fore.CYAN + f"\n📊 Recent Sessions (Last 5):")
        print(f"{'Date':<12} {'Duration':<10} {'Spins':<7} {'Start':<8} {'End':<8} {'Result':<10}")
        print("-" * 60)
        
        for session in sessions:
            session_id, user_id, start_balance, end_balance, spins, bets, wins, duration, started_at, ended_at = session
            result = end_balance - start_balance if end_balance else 0
            duration_str = f"{duration:.0f}min" if duration else "Active"
            result_str = f"${result:+.2f}"
            result_color = Fore.GREEN if result >= 0 else Fore.RED
            
            print(f"{started_at[:10]:<12} {duration_str:<10} {spins:<7} ${start_balance:<7.2f} ${end_balance or 0:<7.2f} {result_color}{result_str}{Fore.RESET:<10}")
        
        # Session statistics summary
        if len(sessions) > 1:
            total_session_result = sum((s[3] or s[2]) - s[2] for s in sessions)  # end_balance - start_balance
            avg_session_result = total_session_result / len(sessions)
            winning_sessions = sum(1 for s in sessions if (s[3] or s[2]) - s[2] > 0)
            win_rate = (winning_sessions / len(sessions)) * 100
            
            print(Fore.CYAN + f"\n🎯 Session Performance:")
            print(Fore.WHITE + f"📊 Total Result (Last 5): ${total_session_result:+.2f}")
            print(Fore.WHITE + f"📈 Average per Session: ${avg_session_result:+.2f}")
            print(Fore.WHITE + f"🏆 Winning Sessions: {winning_sessions}/{len(sessions)} ({win_rate:.1f}%)")
    
    print(Fore.CYAN + Style.BRIGHT + "="*70)
    
    # Profile menu options
    print(Fore.MAGENTA + "\nProfile Options:")
    print(Fore.WHITE + "1. View detailed session history")
    print(Fore.WHITE + "2. Reset statistics (keep balance)")
    print(Fore.WHITE + "3. Delete profile")
    print(Fore.WHITE + "4. Return to game")
    
    try:
        choice = input(Fore.YELLOW + "Choose option (1-4): ").strip()
        
        if choice == "1":
            display_detailed_session_history(user_profile['user_id'])
        elif choice == "2":
            confirm_reset_stats(user_profile)
        elif choice == "3":
            confirm_delete_profile(user_profile)
        elif choice == "4":
            return
        
        # Show profile menu again after each action (except return)
        if choice in ["1", "2", "3"]:
            # Refresh user data
            updated_profile = get_user_profile_by_username(user_profile['username'])
            if updated_profile:
                display_user_profile_menu(updated_profile)
                
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def display_detailed_session_history(user_id):
    """Display detailed session history for a user"""
    sessions = get_user_sessions(user_id, limit=20)
    
    if not sessions:
        print(Fore.YELLOW + "No session history available.")
        input(Fore.GREEN + "Press Enter to continue...")
        return
    
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*90)
    print(Fore.CYAN + Style.BRIGHT + "📈 DETAILED SESSION HISTORY 📈")
    print(Fore.CYAN + Style.BRIGHT + "="*90)
    
    print(f"{'ID':<4} {'Date':<12} {'Start Time':<10} {'Duration':<10} {'Spins':<7} {'Bets':<10} {'Wins':<10} {'Result':<10}")
    print("-" * 90)
    
    total_result = 0
    for session in sessions:
        session_id, user_id, start_balance, end_balance, spins, bets, wins, duration, started_at, ended_at = session
        result = (end_balance or start_balance) - start_balance
        total_result += result
        
        duration_str = f"{duration:.0f}min" if duration else "Active"
        result_str = f"${result:+.2f}"
        result_color = Fore.GREEN if result >= 0 else Fore.RED
        
        date_part = started_at[:10]
        time_part = started_at[11:16]
        
        print(f"{session_id:<4} {date_part:<12} {time_part:<10} {duration_str:<10} {spins:<7} ${bets:<9.2f} ${wins:<9.2f} {result_color}{result_str}{Fore.RESET}")
    
    print("-" * 90)
    print(Fore.CYAN + f"Total Result: ${total_result:+.2f}")
    print(Fore.CYAN + Style.BRIGHT + "="*90)
    
    input(Fore.GREEN + "Press Enter to continue...")

def confirm_reset_stats(user_profile):
    """Confirm and reset user statistics while keeping balance"""
    print(Fore.YELLOW + f"\n⚠️  Reset Statistics for {user_profile['username']}?")
    print(Fore.RED + "This will reset all statistics but keep your current balance.")
    print(Fore.WHITE + "The following will be reset to 0:")
    print(Fore.WHITE + "  • Session count")
    print(Fore.WHITE + "  • Total spins")  
    print(Fore.WHITE + "  • Total bets")
    print(Fore.WHITE + "  • Total wins")
    print(Fore.WHITE + "  • Biggest win")
    print(Fore.GREEN + f"Your balance of ${user_profile['balance']:.2f} will be kept.")
    
    confirm = input(Fore.YELLOW + "\nType 'RESET' to confirm: ").strip()
    
    if confirm == "RESET":
        # Reset user statistics
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute('''UPDATE user_profiles SET 
                         session_count = 0, total_spins = 0, total_bets = 0.0,
                         total_wins = 0.0, biggest_win = 0.0
                         WHERE user_id = ?''', (user_profile['user_id'],))
            conn.commit()
            print(Fore.GREEN + "✅ Statistics reset successfully!")
        except Exception as e:
            print(Fore.RED + f"❌ Error resetting statistics: {e}")
        finally:
            conn.close()
    else:
        print(Fore.CYAN + "Reset cancelled.")
    
    input(Fore.GREEN + "Press Enter to continue...")

def confirm_delete_profile(user_profile):
    """Confirm and delete user profile"""
    print(Fore.RED + f"\n⚠️  DELETE PROFILE: {user_profile['username']}?")
    print(Fore.RED + "This will permanently delete your profile and all data!")
    print(Fore.YELLOW + "This action cannot be undone.")
    
    confirm1 = input(Fore.YELLOW + f"Type the username '{user_profile['username']}' to confirm: ").strip()
    
    if confirm1 == user_profile['username']:
        confirm2 = input(Fore.RED + "Type 'DELETE' to permanently delete: ").strip()
        
        if confirm2 == "DELETE":
            # Delete user profile
            conn = get_db_connection()
            c = conn.cursor()
            
            try:
                c.execute('UPDATE user_profiles SET is_active = 0 WHERE user_id = ?', (user_profile['user_id'],))
                conn.commit()
                print(Fore.GREEN + "✅ Profile deleted successfully!")
                print(Fore.CYAN + "You will be returned to the main menu.")
                input(Fore.GREEN + "Press Enter to continue...")
                return True  # Indicate profile was deleted
            except Exception as e:
                print(Fore.RED + f"❌ Error deleting profile: {e}")
            finally:
                conn.close()
    
    print(Fore.CYAN + "Delete cancelled.")
    input(Fore.GREEN + "Press Enter to continue...")
    return False

def slot_machine():
    # Show legal warning first
    show_legal_warning()
    
    initialize_db()
    jackpot_pool, win_probability = fetch_initial_values()
    
    # Game flow settings
    global AUTO_PLAY_MODE, auto_start_balance, auto_target_high, auto_target_low, auto_spin_count
    AUTO_PLAY_MODE = False
    auto_start_balance = 0
    auto_target_high = 0
    auto_target_low = 0
    auto_spin_count = 0
    
    # User login/registration
    user_profile = user_login_menu()
    
    # Set up balance based on user profile or guest mode
    if user_profile:
        balance = user_profile['balance']
        current_user_id = user_profile['user_id']
        session_id = start_session(current_user_id, balance)
        
        print(Fore.GREEN + Style.BRIGHT + "\n" + "="*50)
        print(Fore.GREEN + Style.BRIGHT + f"\tWelcome back, {user_profile['username']}!")
        print(Fore.GREEN + Style.BRIGHT + "="*50 + "\n")
        print(Fore.GREEN + Style.BRIGHT + f"\tYour current balance: ${balance}")
    else:
        # Guest mode
        balance = game_config.starting_balance
        current_user_id = None
        session_id = None
        
        print(Fore.GREEN + Style.BRIGHT + "\n" + "="*50)
        print(Fore.GREEN + Style.BRIGHT + "\tWelcome to the Configurable Slot Machine!")
        print(Fore.GREEN + Style.BRIGHT + "="*50 + "\n")
        print(Fore.GREEN + Style.BRIGHT + f"\tYour starting balance: ${balance}")
    
    print(Fore.CYAN + f"\tCurrent RTP Target: {game_config.target_rtp}%")
    print(Fore.CYAN + f"\tHouse Edge: {game_config.house_edge}%\n")
    
    # Game statistics for this session
    session_spins = 0
    session_bets = 0
    session_wins = 0
    biggest_win_this_session = 0
    
    # Default bet for first spin
    current_bet = game_config.min_bet
    
    while balance > 0:
        try:
            # Get bet amount - different logic for auto vs manual mode
            if AUTO_PLAY_MODE:
                bet = current_bet  # Use current bet in auto mode
                if bet > balance:
                    print(Fore.YELLOW + f"💸 Auto-play stopping - insufficient balance for ${bet} bet")
                    AUTO_PLAY_MODE = False
                    continue
            else:
                # Manual mode - ask for bet
                bet_input = input(Fore.YELLOW + f"Enter bet ${game_config.min_bet}-${game_config.max_bet} (last: ${current_bet}, 0=exit): ").strip()
                if bet_input == "0":
                    print(Fore.CYAN + "Exiting the game...")
                    break
                elif bet_input == "":
                    bet = current_bet  # Use last bet if Enter pressed
                else:
                    bet = int(bet_input)
                    current_bet = bet  # Remember this bet
                
                if bet > balance:
                    print(Fore.RED + "Insufficient balance! Try again.")
                    continue
                if bet < game_config.min_bet or bet > game_config.max_bet:
                    print(Fore.RED + f"Bet must be between ${game_config.min_bet} and ${game_config.max_bet}!")
                    continue
            
            balance -= bet
            jackpot_pool += bet * game_config.jackpot_contribution_rate
            update_jackpot_pool(jackpot_pool)
            
            # Update session statistics
            session_spins += 1
            session_bets += bet
            
            # Use quick spin instead of slow animation
            reels = quick_spin_animation()
            
            win_result = check_win(reels, bet, jackpot_pool)
            display_slot_machine(reels, jackpot_pool, win_result, bet)
            
            # Log the spin data
            log_spin_data(reels, bet, win_result, balance, jackpot_pool)
            
            # Save balance to user profile if logged in
            if user_profile:
                save_balance(current_user_id, balance)
            
            win_amount = 0
            if isinstance(win_result, int) and win_result > 0:
                win_amount = win_result
                balance += win_result
                session_wins += win_result
                
                if win_result > biggest_win_this_session:
                    biggest_win_this_session = win_result
                
                print(Fore.GREEN + f"\nCongratulations! You won: ${win_result}")
                
            elif win_result == "bonus":
                bonus_win = quick_bonus_round()
                balance += bonus_win
                session_wins += bonus_win
                
                if bonus_win > biggest_win_this_session:
                    biggest_win_this_session = bonus_win
                    
                print(Fore.CYAN + f"\nYou won a bonus round! Bonus win: ${bonus_win}")
                
            else:
                print(Fore.RED + "\nBetter luck next time!")
            
            print(Fore.CYAN + f"Balance: ${balance}")
            
            # Quick continue - no forced menu
            if not AUTO_PLAY_MODE:
                quick_choice = input(Fore.YELLOW + "Press Enter to continue (or 'a'=auto, 's'=settings, 'q'=quit): ").strip().lower()
                if quick_choice == 'q':
                    break
                elif quick_choice == 'a':
                    # Start intelligent auto-play mode
                    AUTO_PLAY_MODE = True
                    auto_start_balance = balance
                    auto_target_high = auto_start_balance * 1.2  # 20% profit target
                    auto_target_low = auto_start_balance * 0.6   # 40% loss limit
                    auto_spin_count = 0
                    
                    print(Fore.GREEN + Style.BRIGHT + f"🚀 AUTO-PLAY MODE ACTIVATED! 🚀")
                    print(Fore.CYAN + f"💰 Starting Balance: ${auto_start_balance:.2f}")
                    print(Fore.GREEN + f"🎯 Target (Stop at): ${auto_target_high:.2f} (+20%)")
                    print(Fore.RED + f"🛑 Limit (Stop at): ${auto_target_low:.2f} (-40%)")
                    print(Fore.YELLOW + f"💸 Current Bet: ${bet}")
                    print(Fore.MAGENTA + "Press 'q' anytime to stop auto-play\n")
                    
                elif quick_choice == 's':
                    show_config_menu()
            else:
                # Auto-play logic with intelligent stopping
                auto_spin_count += 1
                
                # Check stopping conditions
                profit_target_reached = balance >= auto_target_high
                loss_limit_reached = balance <= auto_target_low
                insufficient_balance = balance < bet
                
                if profit_target_reached:
                    print(Fore.GREEN + Style.BRIGHT + f"\n🎉 PROFIT TARGET REACHED! 🎉")
                    print(Fore.GREEN + f"💰 Started with: ${auto_start_balance:.2f}")
                    print(Fore.GREEN + f"💰 Ended with: ${balance:.2f}")
                    print(Fore.GREEN + f"📈 Profit: ${balance - auto_start_balance:+.2f}")
                    print(Fore.GREEN + f"🎰 Auto spins completed: {auto_spin_count}")
                    AUTO_PLAY_MODE = False
                    input(Fore.YELLOW + "Press Enter to continue manual play...")
                    
                elif loss_limit_reached:
                    print(Fore.RED + Style.BRIGHT + f"\n🛑 LOSS LIMIT REACHED! 🛑")
                    print(Fore.RED + f"💰 Started with: ${auto_start_balance:.2f}")
                    print(Fore.RED + f"💰 Ended with: ${balance:.2f}")
                    print(Fore.RED + f"📉 Loss: ${balance - auto_start_balance:+.2f}")
                    print(Fore.RED + f"🎰 Auto spins completed: {auto_spin_count}")
                    AUTO_PLAY_MODE = False
                    input(Fore.YELLOW + "Press Enter to continue manual play...")
                    
                elif insufficient_balance:
                    print(Fore.YELLOW + Style.BRIGHT + f"\n💸 INSUFFICIENT BALANCE FOR AUTO-PLAY 💸")
                    print(Fore.YELLOW + f"Current balance: ${balance:.2f}, Bet: ${bet}")
                    AUTO_PLAY_MODE = False
                    
                else:
                    # Continue auto-play - show progress every 10 spins
                    if auto_spin_count % 10 == 0:
                        current_profit = balance - auto_start_balance
                        profit_percent = (current_profit / auto_start_balance) * 100
                        print(Fore.CYAN + f"🤖 Auto-play progress: Spin #{auto_spin_count} | Balance: ${balance:.2f} | P&L: ${current_profit:+.2f} ({profit_percent:+.1f}%)")
                    
                    # Check for 'q' key press to stop auto-play
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'q':
                            print(Fore.YELLOW + f"\n⏹️ AUTO-PLAY STOPPED BY USER")
                            print(Fore.CYAN + f"🎰 Auto spins completed: {auto_spin_count}")
                            current_profit = balance - auto_start_balance
                            print(Fore.CYAN + f"💰 Final P&L: ${current_profit:+.2f}")
                            AUTO_PLAY_MODE = False
                            input(Fore.YELLOW + "Press Enter to continue manual play...")
                    
                    time.sleep(0.3)  # Short pause between auto spins
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
    
    # Game ending - save data and update user profile
    final_analytics = calculate_analytics()
    if final_analytics:
        save_analytics_to_db(final_analytics)
        print(Fore.GREEN + "Analytics data saved!")
    
    # Update user profile and end session if logged in
    if user_profile and session_id:
        # Update user statistics
        update_user_stats(current_user_id, session_spins, session_bets, session_wins, biggest_win_this_session)
        
        # End the session
        end_session(session_id, balance, session_spins, session_bets, session_wins)
        
        # Final save of balance
        save_balance(current_user_id, balance)
        
        print(Fore.CYAN + f"\nSession ended for user: {user_profile['username']}")
        print(Fore.YELLOW + f"Session stats:")
        print(Fore.WHITE + f"  • Spins: {session_spins}")
        print(Fore.WHITE + f"  • Total bets: ${session_bets:.2f}")
        print(Fore.WHITE + f"  • Total wins: ${session_wins:.2f}")
        print(Fore.WHITE + f"  • Biggest win: ${biggest_win_this_session:.2f}")
        print(Fore.WHITE + f"  • Final balance: ${balance:.2f}")
    
    print(Fore.CYAN + f"\nGame over. Your final balance: ${balance}")
    
    # Show a nice goodbye message
    if user_profile:
        print(Fore.GREEN + f"Thanks for playing, {user_profile['username']}! Your progress has been saved.")
    else:
        print(Fore.GREEN + "Thanks for playing as a guest!")
    
    print(Fore.CYAN + "Come back soon! 🎰")

if __name__ == "__main__":
    slot_machine()
