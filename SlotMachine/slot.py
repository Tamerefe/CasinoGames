import random
from colorama import Fore, Style, init
from database.db import initialize_db, fetch_initial_values, update_jackpot_pool

init(autoreset=True)

paytable = {
    "🍒🍒🍒": 5,
    "🍋🍋🍋": 7,
    "🔔🔔🔔": 10,
    "⭐⭐⭐": 20,
    "7️⃣7️⃣7️⃣": 50,
    "🍉🍉🍉": 100,
    "🃏🃏🃏": 200  # Wild card provides a big win
}

jackpot_symbol = "💰💰💰💰"  # Jackpot symbol
bonus_symbol = "🎁"  # Bonus round symbol
wild_symbol = "🃏"  # Wild card
multipliers = ["x2", "x3", "x5"]  # Multipliers

def spin_reel():
    symbols = ['🍒', '🍋', '🔔', '⭐', '7️⃣ ', '🍉', '💰', '🎁', '🃏', 'x2', 'x3', 'x5']
    return random.choices(symbols, weights=[30, 25, 20, 15, 7, 3, 1, 5, 8, 5, 3, 2])[0]

def spin_slot_machine():
    return [spin_reel(), spin_reel(), spin_reel(), spin_reel(), spin_reel()]  # 5-reel system

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

def bonus_round():
    print(Fore.YELLOW + "You entered the bonus round! You won 3 free spins!")
    total_bonus_winnings = 0
    for _ in range(3):
        reels = spin_slot_machine()
        print(Fore.BLUE + "\n\tBonus Result: ", ' | '.join(reels))
        winnings = check_win(reels, 0, 0)
        if isinstance(winnings, int) and winnings > 0:
            total_bonus_winnings += winnings
    print(Fore.GREEN + f"\nYour total winnings in the bonus round: ${total_bonus_winnings}")
    return total_bonus_winnings

def display_slot_machine(reels, jackpot_pool):
    print(Fore.MAGENTA + f"\t\t\tJackpot Pool: ${jackpot_pool}"+"\n" )
    print(Fore.MAGENTA + " * " * 12)
    print(Fore.BLUE + "\n\t" + ' | '.join(reels))
    print(Fore.MAGENTA + "\n" + " * " * 12)

def slot_machine():
    initialize_db()
    jackpot_pool, win_probability = fetch_initial_values()
    balance = 1000  # Initial balance
    print(Fore.GREEN + Style.BRIGHT + "\n" + "="*50)
    print(Fore.GREEN + Style.BRIGHT + "\tWelcome to the Slot Machine!")
    print(Fore.GREEN + Style.BRIGHT + "="*50 + "\n")
    print(Fore.GREEN + Style.BRIGHT + f"\tYour starting balance: ${balance}\n")
    
    while balance > 0:
        try:
            bet = int(input(Fore.YELLOW + "Enter your bet amount (0 to exit): "))
            if bet == 0:
                print(Fore.CYAN + "Exiting the game...")
                break
            if bet > balance:
                print(Fore.RED + "Insufficient balance! Try again.")
                continue
            
            balance -= bet
            jackpot_pool += bet * 0.1  # 10% of each bet goes to the progressive jackpot
            update_jackpot_pool(jackpot_pool)
            reels = spin_slot_machine()
            display_slot_machine(reels, jackpot_pool)
            
            win_result = check_win(reels, bet, jackpot_pool)
            if isinstance(win_result, int) and win_result > 0:
                balance += win_result
                print(Fore.GREEN + f"\nCongratulations! You won: ${win_result}")
            elif win_result == "bonus":
                print(Fore.CYAN + "\nYou won a bonus round!")
                balance += bonus_round()
            else:
                print(Fore.RED + "\nYou lost! Better luck next time.")
            
            print(Fore.CYAN + f"Your current balance: ${balance}")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
    
    print(Fore.CYAN + "Game over. Your final balance: $", balance)

if __name__ == "__main__":
    slot_machine()
