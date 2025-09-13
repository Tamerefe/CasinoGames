import random
import time
import os
import logging
import csv
import json
from datetime import datetime
from colorama import Fore, Style, init
from database.db import initialize_db, fetch_initial_values, update_jackpot_pool, save_analytics_to_db, get_historical_analytics, save_balance, load_balance, create_user_profile, start_session, end_session, get_user_sessions, update_user_stats, get_user_profile, get_user_profile_by_username, get_session_stats, get_db_connection
from config_manager import load_game_config, get_config_manager
from rtp_calculator import create_rtp_calculator
import msvcrt  # For Windows key detection

init(autoreset=True)

# Load game configuration
game_config = load_game_config()
config_manager = get_config_manager()
rtp_calculator = create_rtp_calculator()

# Configure logging (reduced verbosity)
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

# Game modes
AUTO_PLAY_MODE = False
QUICK_SPIN_MODE = True
SHOW_DETAILED_RESULTS = False

def clear_screen():
    """Clear screen efficiently"""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_spin_data(reels, bet, win_result, balance, jackpot_pool):
    """Simplified logging - only critical data"""
    if isinstance(win_result, int) and win_result > bet * 10:  # Only log big wins
        logging.info(f"Big win: ${win_result} on bet ${bet}")

def spin_reel():
    """Spin a single reel using configuration-based symbol weights"""
    symbols = list(game_config.symbol_weights.keys())
    weights = list(game_config.symbol_weights.values())
    return random.choices(symbols, weights=weights)[0]

def spin_slot_machine():
    return [spin_reel(), spin_reel(), spin_reel(), spin_reel(), spin_reel()]

def quick_spin_animation():
    """Fast, minimal animation for better flow"""
    if not game_config.enable_animations or QUICK_SPIN_MODE:
        return spin_slot_machine()
    
    # Very fast animation (0.1 seconds total)
    print(Fore.CYAN + "🎰 Spinning...")
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(0.03)
    print()
    return spin_slot_machine()

def check_win(reels, bet, jackpot_pool):
    combination = ''.join(reels[:3])
    
    multiplier = 1
    for reel in reels:
        if reel in multipliers:
            multiplier = int(reel[1])
    
    if combination in paytable:
        return paytable[combination] * multiplier
    elif ''.join(reels) == jackpot_symbol:
        jackpot_winnings = jackpot_pool
        jackpot_pool = 500
        update_jackpot_pool(jackpot_pool)
        return jackpot_winnings
    elif bonus_symbol in reels:
        return "bonus"
    return 0

def quick_bonus_round():
    """Fast bonus round without unnecessary pauses"""
    bonus_spins = game_config.bonus_spins
    print(Fore.YELLOW + f"🎁 BONUS ROUND! {bonus_spins} free spins!")
    total_bonus_winnings = 0
    
    for spin_num in range(bonus_spins):
        reels = spin_slot_machine()
        winnings = check_win(reels, 0, 0)
        if isinstance(winnings, int) and winnings > 0:
            total_bonus_winnings += winnings
            print(Fore.GREEN + f"Spin {spin_num+1}: {' | '.join(reels)} → +${winnings}")
        else:
            print(Fore.WHITE + f"Spin {spin_num+1}: {' | '.join(reels)}")
    
    print(Fore.GREEN + f"🏆 Bonus total: ${total_bonus_winnings}")
    return total_bonus_winnings

def display_game_result(reels, win_result, balance, jackpot_pool, bet):
    """Clean, compact result display"""
    print(f"\n{'='*50}")
    print(Fore.YELLOW + f"💰 Jackpot: ${jackpot_pool:.2f}")
    print(Fore.CYAN + f"🎰 [ {' | '.join(reels)} ]")
    
    if isinstance(win_result, int) and win_result > 0:
        profit = win_result - bet
        print(Fore.GREEN + f"✅ WIN: ${win_result} (Profit: +${profit})")
    elif win_result == "bonus":
        print(Fore.YELLOW + "🎁 BONUS ROUND TRIGGERED!")
    else:
        print(Fore.RED + f"❌ Loss: -${bet}")
    
    print(Fore.WHITE + f"💵 Balance: ${balance}")
    print(f"{'='*50}")

def wait_for_key_or_timeout(timeout=1.0):
    """Wait for key press or timeout (Windows only)"""
    if not AUTO_PLAY_MODE:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                msvcrt.getch()  # Consume the key
                return True
            time.sleep(0.05)
    else:
        time.sleep(0.2)  # Very short pause in auto mode
    return False

def show_quick_menu():
    """Simplified menu that doesn't interrupt flow"""
    print(Fore.MAGENTA + "\n⚙️ Quick Options:")
    print(Fore.WHITE + "A) Auto-play toggle | Q) Quick mode | S) Settings | R) Reports | ENTER) Continue")
    
def user_login_menu():
    """Streamlined login process"""
    print(Fore.CYAN + Style.BRIGHT + "🎰 SLOT MACHINE - FLUENT VERSION 🎰\n")
    
    print(Fore.MAGENTA + "Quick Start:")
    print(Fore.WHITE + "1) Login | 2) New User | 3) Guest Mode | 4) Exit")
    
    try:
        choice = input(Fore.YELLOW + "Choice (1-4): ").strip()
        
        if choice == "1":
            username = input(Fore.YELLOW + "Username: ").strip()
            if username:
                user_profile = get_user_profile_by_username(username)
                if user_profile:
                    print(Fore.GREEN + f"Welcome back, {username}! Balance: ${user_profile['balance']:.2f}")
                    return user_profile
                else:
                    print(Fore.RED + "User not found. Creating new profile...")
                    return create_user_profile(username, game_config.starting_balance)
        elif choice == "2":
            username = input(Fore.YELLOW + "New username: ").strip()
            if username:
                return create_user_profile(username, game_config.starting_balance)
        elif choice == "3":
            print(Fore.GREEN + "Guest mode activated!")
            return None
        elif choice == "4":
            exit()
    except:
        pass
    
    return None

def show_settings_menu():
    """Quick settings without interrupting gameplay"""
    global AUTO_PLAY_MODE, QUICK_SPIN_MODE, SHOW_DETAILED_RESULTS
    
    print(Fore.CYAN + "\n⚙️ Quick Settings:")
    print(f"1) Auto-play: {'ON' if AUTO_PLAY_MODE else 'OFF'}")
    print(f"2) Quick spins: {'ON' if QUICK_SPIN_MODE else 'OFF'}")
    print(f"3) Detailed results: {'ON' if SHOW_DETAILED_RESULTS else 'OFF'}")
    print("4) Back to game")
    
    choice = input(Fore.YELLOW + "Choice (1-4): ").strip()
    
    if choice == "1":
        AUTO_PLAY_MODE = not AUTO_PLAY_MODE
        print(Fore.GREEN + f"Auto-play: {'ON' if AUTO_PLAY_MODE else 'OFF'}")
    elif choice == "2":
        QUICK_SPIN_MODE = not QUICK_SPIN_MODE
        print(Fore.GREEN + f"Quick spins: {'ON' if QUICK_SPIN_MODE else 'OFF'}")
    elif choice == "3":
        SHOW_DETAILED_RESULTS = not SHOW_DETAILED_RESULTS
        print(Fore.GREEN + f"Detailed results: {'ON' if SHOW_DETAILED_RESULTS else 'OFF'}")

def auto_play_session(balance, bet, user_profile, current_user_id, session_id, jackpot_pool):
    """Automatic play mode for continuous action"""
    spins = int(input(Fore.YELLOW + "How many auto spins? "))
    if spins <= 0 or spins > 1000:
        print(Fore.RED + "Invalid number of spins!")
        return balance, 0, 0, 0
    
    print(Fore.CYAN + f"🚀 Starting {spins} auto spins with ${bet} bet each...")
    
    session_spins = 0
    session_bets = 0
    session_wins = 0
    biggest_win = 0
    
    for i in range(spins):
        if balance < bet:
            print(Fore.RED + f"Insufficient balance after {i} spins!")
            break
        
        balance -= bet
        session_spins += 1
        session_bets += bet
        
        reels = spin_slot_machine()
        win_result = check_win(reels, bet, jackpot_pool)
        
        win_amount = 0
        if isinstance(win_result, int) and win_result > 0:
            win_amount = win_result
            balance += win_result
            session_wins += win_result
            if win_result > biggest_win:
                biggest_win = win_result
        elif win_result == "bonus":
            bonus_win = quick_bonus_round()
            balance += bonus_win
            session_wins += bonus_win
            if bonus_win > biggest_win:
                biggest_win = bonus_win
        
        # Show progress every 10 spins or on big wins
        if i % 10 == 0 or win_amount > bet * 5:
            print(Fore.WHITE + f"Spin {i+1}/{spins}: {' | '.join(reels)} → Balance: ${balance:.2f}")
        
        # Quick pause between spins
        time.sleep(0.1)
        
        # Save progress periodically
        if user_profile and i % 50 == 0:
            save_balance(current_user_id, balance)
    
    print(Fore.GREEN + f"\n🏁 Auto-play complete!")
    print(Fore.YELLOW + f"Results: {session_spins} spins, ${session_wins:.2f} won, biggest win: ${biggest_win:.2f}")
    
    return balance, session_spins, session_bets, session_wins

def slot_machine():
    """Main game loop - optimized for fluid gameplay"""
    clear_screen()
    
    initialize_db()
    jackpot_pool, win_probability = fetch_initial_values()
    
    # Quick login
    user_profile = user_login_menu()
    
    # Set up balance
    if user_profile:
        balance = user_profile['balance']
        current_user_id = user_profile['user_id']
        session_id = start_session(current_user_id, balance)
        print(Fore.GREEN + f"👤 {user_profile['username']} | 💵 ${balance}")
    else:
        balance = game_config.starting_balance
        current_user_id = None
        session_id = None
        print(Fore.GREEN + f"🎮 Guest Mode | 💵 ${balance}")
    
    # Game statistics
    session_spins = 0
    session_bets = 0
    session_wins = 0
    biggest_win_this_session = 0
    
    # Default bet
    last_bet = game_config.min_bet
    
    print(Fore.CYAN + f"🎯 RTP: {game_config.target_rtp}% | 🏠 House Edge: {game_config.house_edge}%")
    print(Fore.MAGENTA + "💡 Commands: 'A'=Auto-play | 'S'=Settings | 'Q'=Quit | 'F'=Fast Mode | Just numbers for bets")
    
    while balance > 0:
        try:
            # Quick bet input with default
            bet_input = input(Fore.YELLOW + f"Bet ${game_config.min_bet}-${game_config.max_bet} (last: ${last_bet}): ").strip()
            
            # Handle special commands
            if bet_input.lower() == 'q':
                break
            elif bet_input.lower() == 'a':
                balance, auto_spins, auto_bets, auto_wins = auto_play_session(
                    balance, last_bet, user_profile, current_user_id, session_id, jackpot_pool)
                session_spins += auto_spins
                session_bets += auto_bets
                session_wins += auto_wins
                if user_profile:
                    save_balance(current_user_id, balance)
                continue
            elif bet_input.lower() == 's':
                show_settings_menu()
                continue
            elif bet_input.lower() == 'f':
                # Fast mode - 10 quick spins with same bet
                print(Fore.CYAN + f"🚀 Fast mode: 10 spins with ${last_bet} bet each...")
                for i in range(10):
                    if balance < last_bet:
                        print(Fore.RED + f"Balance depleted after {i} spins!")
                        break
                    
                    balance -= last_bet
                    session_spins += 1
                    session_bets += last_bet
                    
                    reels = spin_slot_machine()
                    win_result = check_win(reels, last_bet, jackpot_pool)
                    
                    if isinstance(win_result, int) and win_result > 0:
                        balance += win_result
                        session_wins += win_result
                        print(f"Spin {i+1}: WIN ${win_result} → Balance: ${balance}")
                    elif win_result == "bonus":
                        bonus_win = quick_bonus_round()
                        balance += bonus_win
                        session_wins += bonus_win
                        print(f"Spin {i+1}: BONUS ${bonus_win} → Balance: ${balance}")
                    else:
                        print(f"Spin {i+1}: LOSS → Balance: ${balance}")
                    
                    time.sleep(0.1)
                
                if user_profile:
                    save_balance(current_user_id, balance)
                print(Fore.GREEN + "🏁 Fast mode complete!")
                continue
            
            # Parse bet amount
            if bet_input == "":
                bet = last_bet
            else:
                bet = int(bet_input)
            
            # Validate bet
            if bet > balance:
                print(Fore.RED + "💸 Insufficient balance!")
                continue
            if bet < game_config.min_bet or bet > game_config.max_bet:
                print(Fore.RED + f"🚫 Bet must be ${game_config.min_bet}-${game_config.max_bet}!")
                continue
            
            last_bet = bet
            balance -= bet
            jackpot_pool += bet * game_config.jackpot_contribution_rate
            update_jackpot_pool(jackpot_pool)
            
            session_spins += 1
            session_bets += bet
            
            # Quick spin
            reels = quick_spin_animation()
            win_result = check_win(reels, bet, jackpot_pool)
            
            # Process results
            win_amount = 0
            if isinstance(win_result, int) and win_result > 0:
                win_amount = win_result
                balance += win_result
                session_wins += win_result
                
                if win_result > biggest_win_this_session:
                    biggest_win_this_session = win_result
                    
            elif win_result == "bonus":
                bonus_win = quick_bonus_round()
                balance += bonus_win
                session_wins += bonus_win
                
                if bonus_win > biggest_win_this_session:
                    biggest_win_this_session = bonus_win
            
            # Show results
            display_game_result(reels, win_result, balance, jackpot_pool, bet)
            
            # Log important data only
            log_spin_data(reels, bet, win_result, balance, jackpot_pool)
            
            # Save progress for logged-in users
            if user_profile:
                save_balance(current_user_id, balance)
            
            # Quick continue or pause
            if not AUTO_PLAY_MODE:
                wait_for_key_or_timeout(0.8)  # Shorter timeout for better flow
            
        except ValueError:
            print(Fore.RED + "⚠️ Invalid input!")
        except KeyboardInterrupt:
            print(Fore.CYAN + "\n🛑 Game paused. Press Enter to continue or 'q' to quit.")
            if input().lower() == 'q':
                break
    
    # Game ending
    if user_profile and session_id:
        update_user_stats(current_user_id, session_spins, session_bets, session_wins, biggest_win_this_session)
        end_session(session_id, balance, session_spins, session_bets, session_wins)
        save_balance(current_user_id, balance)
        
        print(Fore.CYAN + f"\n📊 Session Summary for {user_profile['username']}:")
    else:
        print(Fore.CYAN + f"\n📊 Session Summary:")
    
    print(Fore.WHITE + f"🎰 Spins: {session_spins}")
    print(Fore.WHITE + f"💰 Total bets: ${session_bets:.2f}")
    print(Fore.WHITE + f"🏆 Total wins: ${session_wins:.2f}")
    print(Fore.WHITE + f"💎 Biggest win: ${biggest_win_this_session:.2f}")
    print(Fore.WHITE + f"💵 Final balance: ${balance:.2f}")
    
    net_result = session_wins - session_bets
    if net_result > 0:
        print(Fore.GREEN + f"🎉 Session profit: +${net_result:.2f}")
    else:
        print(Fore.RED + f"📉 Session loss: ${net_result:.2f}")
    
    print(Fore.CYAN + "\n🎰 Thanks for playing! Come back soon! 🎰")

if __name__ == "__main__":
    slot_machine()