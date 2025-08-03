import turtle
import random
import time
import tkinter as tk
from tkinter import messagebox
import os

def show_legal_warning():
    """Display legal warning before game starts"""
    warning_turtle = turtle.Turtle()
    warning_turtle.hideturtle()
    warning_turtle.penup()
    warning_turtle.color("red")
    
    # Clear screen and show warning
    screen.clear()
    screen.bgcolor("black")
    
    warning_turtle.goto(0, 200)
    warning_turtle.write("⚠️  WARNING: EDUCATIONAL SOFTWARE ONLY ⚠️", align="center", font=("Arial", 20, "bold"))
    
    warning_turtle.goto(0, 150)
    warning_turtle.write("• NO REAL MONEY INVOLVED", align="center", font=("Arial", 16, "normal"))
    warning_turtle.goto(0, 120)
    warning_turtle.write("• NOT REAL GAMBLING", align="center", font=("Arial", 16, "normal"))
    warning_turtle.goto(0, 90)
    warning_turtle.write("• FOR EDUCATIONAL PURPOSES ONLY", align="center", font=("Arial", 16, "normal"))
    warning_turtle.goto(0, 60)
    warning_turtle.write("• AGE 18+ ONLY", align="center", font=("Arial", 16, "normal"))
    
    warning_turtle.goto(0, 0)
    warning_turtle.write("This game demonstrates programming concepts and game mechanics.", align="center", font=("Arial", 14, "normal"))
    warning_turtle.goto(0, -30)
    warning_turtle.write("All monetary values are fictional and for educational purposes only.", align="center", font=("Arial", 14, "normal"))
    
    warning_turtle.goto(0, -100)
    warning_turtle.color("yellow")
    warning_turtle.write("Click anywhere to continue...", align="center", font=("Arial", 16, "bold"))
    
    # Wait for user click
    screen.onclick(lambda x, y: start_game())
    screen.mainloop()

def start_game():
    """Initialize the actual game after warning"""
    global screen
    screen.clear()
    screen.bgcolor("black")
    screen.setup(width=1280, height=720)
    screen.tracer(0)  # Turn off animation for better performance

    # Set background image
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set window icon
    ico_path = os.path.join(script_dir, "ico.png")
    if os.path.exists(ico_path):
        try:
            screen._root.iconphoto(True, tk.PhotoImage(file=ico_path))
        except:
            pass  # Silently fail if icon cannot be set
    bg_path = os.path.join(script_dir, "bg.gif")
    plane_path = os.path.join(script_dir, "plane.gif")

    screen.bgpic(bg_path)

    # Create turtle for drawing the betting interface
    global betting_turtle, plane, trail_turtle, dice_turtle, click_turtle, dice_menu_turtle
    global multiplier_turtle, winnings_turtle, balance_turtle, dice_symbols
    global balance, bet_amount, multiplier, running, crash_point, speed
    global dice_roll_result, dice_risk_active, game_phase, dice_animation_running, dice_menu_active

    betting_turtle = turtle.Turtle()
    betting_turtle.hideturtle()
    betting_turtle.penup()
    betting_turtle.color("white")
    betting_turtle.goto(0, 0)

    # Create the "plane" turtle (use an image instead of a triangle)
    plane = turtle.Turtle()
    # Load the plane image
    screen.addshape(plane_path)
    plane.shape(plane_path)
    plane.penup()
    plane.goto(-610, -340)
    plane.setheading(20)

    # Create a turtle for drawing the trail
    trail_turtle = turtle.Turtle()
    trail_turtle.hideturtle()
    trail_turtle.penup()
    trail_turtle.color("#ffd25d")
    trail_turtle.goto(-615, -340)
    trail_turtle.pendown()

    # Create dice display turtle
    dice_turtle = turtle.Turtle()
    dice_turtle.hideturtle()
    dice_turtle.penup()
    dice_turtle.color("white")

    # Create click area turtle
    click_turtle = turtle.Turtle()
    click_turtle.hideturtle()
    click_turtle.penup()
    click_turtle.color("yellow")

    # Create dice menu turtle
    dice_menu_turtle = turtle.Turtle()
    dice_menu_turtle.hideturtle()
    dice_menu_turtle.penup()

    # Game variables
    balance = 1000  # Player's starting balance
    bet_amount = 0
    multiplier = 1.0
    running = False
    crash_point = 0
    speed = 0.01
    dice_roll_result = 0
    dice_risk_active = False
    game_phase = "betting"  # betting, dice_roll, flying, crashed
    dice_animation_running = False
    dice_menu_active = False

    # Display multiplier and winnings on screen
    multiplier_turtle = turtle.Turtle()
    multiplier_turtle.hideturtle()
    multiplier_turtle.penup()
    multiplier_turtle.color("white")

    winnings_turtle = turtle.Turtle()
    winnings_turtle.hideturtle()
    winnings_turtle.penup()
    winnings_turtle.color("white")

    balance_turtle = turtle.Turtle()
    balance_turtle.hideturtle()
    balance_turtle.penup()
    balance_turtle.color("white")

    # Dice symbols for display
    dice_symbols = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']

    # Initialize game setup
    show_betting_screen()
    turtle.ontimer(handle_bet_input, 1000)

def roll_dice():
    """Roll two dice and return the sum"""
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    return dice1 + dice2, dice1, dice2

def create_dice_menu():
    """Create a simple and elegant dice menu"""
    global dice_menu_active
    dice_menu_active = True
    
    # Clear previous displays
    dice_turtle.clear()
    click_turtle.clear()
    
    # Get screen dimensions for responsive design
    screen_width = screen.window_width()
    screen_height = screen.window_height()
    
    # Calculate responsive sizes
    menu_width = min(screen_width * 0.3, 400)
    menu_height = min(screen_height * 0.3, 250)
    
    # Create black menu background
    dice_menu_turtle.clear()
    dice_menu_turtle.goto(-menu_width//2, menu_height//2)
    dice_menu_turtle.pendown()
    dice_menu_turtle.color("black")
    dice_menu_turtle.begin_fill()
    for _ in range(4):
        dice_menu_turtle.forward(menu_width)
        dice_menu_turtle.right(90)
    dice_menu_turtle.end_fill()
    dice_menu_turtle.penup()
    
    # Yellow border
    dice_menu_turtle.goto(-menu_width//2, menu_height//2)
    dice_menu_turtle.pendown()
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.pensize(3)
    for _ in range(4):
        dice_menu_turtle.forward(menu_width)
        dice_menu_turtle.right(90)
    dice_menu_turtle.penup()
    
    # Title
    dice_menu_turtle.goto(0, menu_height//2 - 30)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("🎲 DICE ROLL 🎲", align="center", font=("Arial", 16, "bold"))
    
    # Yellow dice display
    dice_menu_turtle.goto(-50, 0)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("⚀", align="center", font=("Arial", 50))
    
    dice_menu_turtle.goto(50, 0)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("⚀", align="center", font=("Arial", 50))
    
    # Yellow roll button
    dice_menu_turtle.goto(0, -menu_height//2 + 40)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("CLICK TO ROLL", align="center", font=("Arial", 14, "bold"))
    
    # Set click handler
    screen.onclick(handle_dice_menu_click)

# Removed create_dice_card function - no longer needed

def animate_dice_roll():
    """Simple dice rolling animation"""
    global dice_animation_running
    dice_animation_running = True
    
    def animate():
        if dice_animation_running:
            # Random dice during animation
            temp_dice1 = random.randint(1, 6)
            temp_dice2 = random.randint(1, 6)
            
            # Update dice display
            dice_menu_turtle.goto(-50, 0)
            dice_menu_turtle.color("#ffd25d")
            dice_menu_turtle.write(dice_symbols[temp_dice1-1], align="center", font=("Arial", 50))
            
            dice_menu_turtle.goto(50, 0)
            dice_menu_turtle.color("#ffd25d")
            dice_menu_turtle.write(dice_symbols[temp_dice2-1], align="center", font=("Arial", 50))
            
            screen.ontimer(animate, 50)  # Simple animation
    
    animate()

# Removed update_dice_card and animate_card_color functions - no longer needed

def show_dice_result(dice1, dice2, total):
    """Display final dice roll result"""
    global dice_animation_running
    dice_animation_running = False
    
    # Clear previous text to prevent overlap
    dice_menu_turtle.clear()
    
    # Redraw menu background
    screen_width = screen.window_width()
    screen_height = screen.window_height()
    menu_width = min(screen_width * 0.3, 400)
    menu_height = min(screen_height * 0.3, 250)
    
    # Redraw black background
    dice_menu_turtle.goto(-menu_width//2, menu_height//2)
    dice_menu_turtle.pendown()
    dice_menu_turtle.color("black")
    dice_menu_turtle.begin_fill()
    for _ in range(4):
        dice_menu_turtle.forward(menu_width)
        dice_menu_turtle.right(90)
    dice_menu_turtle.end_fill()
    dice_menu_turtle.penup()
    
    # Redraw yellow border
    dice_menu_turtle.goto(-menu_width//2, menu_height//2)
    dice_menu_turtle.pendown()
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.pensize(3)
    for _ in range(4):
        dice_menu_turtle.forward(menu_width)
        dice_menu_turtle.right(90)
    dice_menu_turtle.penup()
    
    # Redraw title
    dice_menu_turtle.goto(0, menu_height//2 - 30)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("🎲 DICE ROLL 🎲", align="center", font=("Arial", 16, "bold"))
    
    # Update final dice values
    dice_menu_turtle.goto(-50, 0)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write(dice_symbols[dice1-1], align="center", font=("Arial", 50))
    
    dice_menu_turtle.goto(50, 0)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write(dice_symbols[dice2-1], align="center", font=("Arial", 50))
    
    # Show total
    dice_menu_turtle.goto(0, -30)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write(f"TOTAL: {total}", align="center", font=("Arial", 16, "bold"))
    
    # Calculate and show risk result with amount
    new_bet_amount = apply_dice_risk(bet_amount, total)
    if total <= 6:
        dice_menu_turtle.goto(0, -60)
        dice_menu_turtle.color("#ffd25d")
        dice_menu_turtle.write("❌ RISK: Bet reduced!", align="center", font=("Arial", 12, "bold"))
        dice_menu_turtle.goto(0, -80)
        dice_menu_turtle.color("#ffd25d")
        dice_menu_turtle.write(f"New bet: ${new_bet_amount:.2f}", align="center", font=("Arial", 14, "bold"))
    else:
        dice_menu_turtle.goto(0, -60)
        dice_menu_turtle.color("#ffd25d")
        dice_menu_turtle.write("✅ SUCCESS: Bet increased!", align="center", font=("Arial", 12, "bold"))
        dice_menu_turtle.goto(0, -80)
        dice_menu_turtle.color("#ffd25d")
        dice_menu_turtle.write(f"New bet: ${new_bet_amount:.2f}", align="center", font=("Arial", 14, "bold"))
    
    # Continue button
    dice_menu_turtle.goto(0, -110)
    dice_menu_turtle.color("#ffd25d")
    dice_menu_turtle.write("Click to continue to flight!", align="center", font=("Arial", 10, "bold"))

def apply_dice_risk(bet_amount, dice_total):
    """Apply dice risk system to the bet amount
    - If dice total <= 6: Reduce bet amount by 50%
    - If dice total >= 7: Increase bet amount by 25%
    """
    if dice_total <= 6:
        # Reduce bet amount by 50%
        return bet_amount * 0.5
    else:
        # Increase bet amount by 25%
        return bet_amount * 1.25

def handle_dice_menu_click(x, y):
    """Handle dice menu click"""
    global game_phase, dice_roll_result, balance, bet_amount, dice_menu_active, dice_animation_running
    
    if game_phase == "dice_roll" and dice_menu_active:
        # If animation is not running, start dice roll
        if not dice_animation_running:
            # Start dice animation
            animate_dice_roll()
            
            # Stop animation after 0.8 seconds and show result
            screen.ontimer(lambda: finish_dice_roll(), 500)
        else:
            # If animation is running, ignore the click
            pass

def finish_dice_roll():
    """Finish dice roll and show result"""
    global dice_roll_result, balance, bet_amount, game_phase, dice_menu_active
    
    # Get final dice result
    dice_total, dice1, dice2 = roll_dice()
    dice_roll_result = dice_total
    
    # Show result
    show_dice_result(dice1, dice2, dice_total)
    
    # Apply dice risk to bet amount
    new_bet_amount = apply_dice_risk(bet_amount, dice_total)
    bet_amount = new_bet_amount
    
    # Wait 0.45 seconds to show the result, then continue
    screen.ontimer(lambda: continue_after_dice_result(new_bet_amount), 450)

def continue_after_dice_result(new_bet_amount):
    """Continue after showing dice result for 3 seconds"""
    global game_phase, dice_menu_active, dice_animation_running
    
    # Show risk result in main area - clear dice menu first
    dice_menu_turtle.clear()
    betting_turtle.clear()
    betting_turtle.goto(0, 100)
    betting_turtle.write(f"Original bet: ${bet_amount:.2f}", align="center", font=("Courier", 18, "normal"))
    betting_turtle.goto(0, 70)
    if new_bet_amount < bet_amount:
        betting_turtle.write(f"Dice Risk: Bet reduced to ${new_bet_amount:.2f}", align="center", font=("Courier", 16, "normal"))
    else:
        betting_turtle.write(f"Dice Risk: Bet increased to ${new_bet_amount:.2f}", align="center", font=("Courier", 16, "normal"))
    betting_turtle.goto(0, 40)
    betting_turtle.write(f"Balance: ${balance:.2f}", align="center", font=("Courier", 16, "normal"))
    betting_turtle.goto(0, 10)
    betting_turtle.write("Click anywhere to start flying!", align="center", font=("Courier", 16, "bold"))
    
    # Change to flying phase and reset animation flag
    game_phase = "ready_to_fly"
    dice_menu_active = False
    dice_animation_running = False
    screen.onclick(handle_fly_click)

def handle_fly_click(x, y):
    """Handle click to start flying"""
    global game_phase, running, crash_point
    if game_phase == "ready_to_fly":
        game_phase = "flying"
        running = True
        crash_point = random.uniform(1.5, 10.0)
        start_flying()

def handle_cashout_click(x, y):
    """Handle cashout click during flight"""
    global running, balance, bet_amount, multiplier, game_phase
    
    if running and game_phase == "flying":
        running = False
        game_phase = "crashed"
        
        # Calculate winnings
        winnings = bet_amount * multiplier
        balance += winnings
        
        # Show result
        betting_turtle.clear()
        betting_turtle.goto(0, 0)
        betting_turtle.write(f"🎉 CASHOUT SUCCESS! 🎉", align="center", font=("Courier", 24, "bold"))
        betting_turtle.goto(0, -30)
        betting_turtle.write(f"You won ${winnings:.2f}!", align="center", font=("Courier", 18, "normal"))
        betting_turtle.goto(0, -60)
        betting_turtle.write(f"Final Multiplier: {multiplier:.2f}x", align="center", font=("Courier", 16, "normal"))
        betting_turtle.goto(0, -90)
        betting_turtle.write(f"New Balance: ${balance:.2f}", align="center", font=("Courier", 16, "normal"))
        
        # Check if the balance is zero, end the game
        if balance <= 0:
            betting_turtle.clear()
            betting_turtle.goto(0, 0)
            betting_turtle.write("Game Over! You have no money left.", align="center", font=("Courier", 24, "bold"))
        else:
            turtle.ontimer(restart_game, 5000)  # Restart game after 5 seconds

# Function to display betting screen
def show_betting_screen():
    global game_phase
    game_phase = "betting"
    betting_turtle.clear()
    dice_turtle.clear()
    click_turtle.clear()
    dice_menu_turtle.clear()
    
    betting_turtle.goto(0, 100)
    betting_turtle.write("Welcome to Aviator with Dice Risk!", align="center", font=("Courier", 24, "bold"))
    betting_turtle.goto(400, 300)
    betting_turtle.write(f"Your Balance: ${balance:.2f}", align="center", font=("Courier", 18, "normal"))
    betting_turtle.goto(0, 50)
    betting_turtle.write("Enter your bet amount in dollars:", align="center", font=("Courier", 18, "normal"))
    betting_turtle.goto(0, 20)
    betting_turtle.write("🎲 Beautiful dice menu after betting!", align="center", font=("Courier", 14, "normal"))
    
    # Remove click handlers
    screen.onclick(None)

# Function to handle betting input
def handle_bet_input():
    global bet_amount, game_phase, balance
    try:
        bet_amount = float(turtle.textinput("Bet Amount", "Enter your bet amount in dollars:"))
        if bet_amount > balance:
            betting_turtle.clear()
            betting_turtle.write(f"Insufficient balance. Your balance is ${balance:.2f}", align="center", font=("Courier", 18, "normal"))
            turtle.ontimer(handle_bet_input, 2000)
        elif bet_amount > 0:
            # Deduct bet amount from balance
            balance -= bet_amount
            
            # Show dice menu
            game_phase = "dice_roll"
            betting_turtle.clear()
            betting_turtle.goto(0, 0)
            betting_turtle.write(f"Your bet: ${bet_amount:.2f}", align="center", font=("Courier", 18, "normal"))
            betting_turtle.goto(0, -30)
            betting_turtle.write("Beautiful dice menu will appear!", align="center", font=("Courier", 18, "normal"))
            
            # Create dice menu immediately
            turtle.ontimer(create_dice_menu, 100)
        else:
            betting_turtle.write("Invalid input. Try again.", align="center", font=("Courier", 18, "normal"))
    except ValueError:
        betting_turtle.write("Please enter valid numbers.", align="center", font=("Courier", 18, "normal"))

# Function to start the game
def start_flying():
    global bet_amount, multiplier, running, speed, crash_point, balance, game_phase
    current_winnings = bet_amount
    heading_increment = 0.02

    if running:
        betting_turtle.clear()
        dice_turtle.clear()
        click_turtle.clear()
        dice_menu_turtle.clear()
        trail_turtle.clear()
        trail_turtle.penup()
        trail_turtle.goto(-610, -340)
        trail_turtle.pendown()
        trail_turtle.begin_fill()
        
        # Draw responsive cashout button
        screen_width = screen.window_width()
        screen_height = screen.window_height()
        button_x = screen_width * 0.3
        button_y = screen_height * 0.2
        button_size = min(150, screen_width * 0.1)
        
        click_turtle.goto(button_x, button_y)
        click_turtle.pendown()
        click_turtle.color("green")
        click_turtle.begin_fill()
        for _ in range(4):
            click_turtle.forward(button_size)
            click_turtle.right(90)
        click_turtle.end_fill()
        click_turtle.penup()
        click_turtle.goto(button_x + button_size//2, button_y + button_size//2)
        click_turtle.write("💰 CASHOUT 💰", align="center", font=("Courier", 12, "bold"))
        
        # Set click handler for cashout
        screen.onclick(handle_cashout_click)
        
        while running:
            screen.update()
            screen.tracer(0)

            plane.forward(1)
            multiplier += 0.01

            current_heading = plane.heading()
            plane.setheading(current_heading + heading_increment)

            current_winnings = bet_amount * multiplier

            trail_turtle.goto(plane.xcor(), plane.ycor())

            # Get responsive positions
            screen_width = screen.window_width()
            screen_height = screen.window_height()
            left_x = -screen_width * 0.4
            top_y = screen_height * 0.4

            multiplier_turtle.clear()
            multiplier_turtle.goto(left_x, top_y)
            multiplier_turtle.write(f"Multiplier: {multiplier:.2f}x", font=("Courier", 16, "normal"))
            winnings_turtle.clear()
            winnings_turtle.goto(left_x, top_y - 30)
            winnings_turtle.write(f"Current Winnings: ${current_winnings:.2f}", font=("Courier", 16, "normal"))
            balance_turtle.clear()
            balance_turtle.goto(left_x, top_y - 60)
            balance_turtle.write(f"Balance: ${balance:.2f}", font=("Courier", 16, "normal"))

            if multiplier >= 1.5:
                speed = max(0.001, speed - 0.0005)

            if multiplier >= crash_point:
                running = False
                game_phase = "crashed"
                betting_turtle.clear()
                betting_turtle.goto(0, 0)
                # Balance already adjusted by dice risk, no need to subtract bet_amount again
                betting_turtle.write(f"💥 CRASH! 💥\nFinal Multiplier: {multiplier:.2f}x\nNew Balance: ${balance:.2f}", align="center", font=("Courier", 24, "bold"))
                
                trail_turtle.goto(plane.xcor(), -340)
                trail_turtle.goto(-615, -340)
                trail_turtle.end_fill()

                # Check if the balance is zero, end the game
                if balance <= 0:
                    betting_turtle.clear()
                    betting_turtle.goto(0, 0)
                    betting_turtle.write("Game Over! You have no money left.", align="center", font=("Courier", 24, "bold"))
                else:
                    turtle.ontimer(restart_game, 5000)  # Restart game after 5 seconds
                break

            time.sleep(speed)

# Function to restart the game after it ends
def restart_game():
    global bet_amount, multiplier, running, crash_point, speed, game_phase
    bet_amount = 0
    multiplier = 1.0
    running = False
    crash_point = 0
    speed = 0.01
    game_phase = "betting"
    plane.goto(-610, -340)
    plane.setheading(20)
    show_betting_screen()
    turtle.ontimer(handle_bet_input, 1000)

# Start the game with legal warning
if __name__ == "__main__":
    # Setup initial screen
    screen = turtle.Screen()
    screen.title("Aviator Game with Dice Risk System - EDUCATIONAL ONLY")
    screen.bgcolor("black")
    screen.setup(width=1280, height=720)
    screen.tracer(0)
    
    # Show legal warning first
    show_legal_warning()

# Thanks for this info Agrestic