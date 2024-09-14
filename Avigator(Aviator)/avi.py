import turtle
import random
import time

# Setup screen
screen = turtle.Screen()
screen.title("Aviator Game Simulation")
screen.bgcolor("black")
screen.setup(width=1280, height=720)

# Set background image
screen.bgpic("Avigator(Aviator)/bg.gif")

# Create turtle for drawing the betting interface
betting_turtle = turtle.Turtle()
betting_turtle.hideturtle()
betting_turtle.penup()
betting_turtle.color("white")
betting_turtle.goto(0, 0)

# Create the "plane" turtle (use an image instead of a triangle)
plane = turtle.Turtle()
# Load the plane image
screen.addshape("Avigator(Aviator)/plane.gif")
plane.shape("Avigator(Aviator)/plane.gif")
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

# Game variables
balance = 1000  # Player's starting balance
bet_amount = 0
target_multiplier = 0
multiplier = 1.0
running = False
crash_point = 0
speed = 0.01

# Display multiplier and winnings on screen
multiplier_turtle = turtle.Turtle()
multiplier_turtle.hideturtle()
multiplier_turtle.penup()
multiplier_turtle.color("white")
multiplier_turtle.goto(-600, 300)

winnings_turtle = turtle.Turtle()
winnings_turtle.hideturtle()
winnings_turtle.penup()
winnings_turtle.color("white")
winnings_turtle.goto(-600, 270)

balance_turtle = turtle.Turtle()
balance_turtle.hideturtle()
balance_turtle.penup()
balance_turtle.color("white")
balance_turtle.goto(-600, 240)

# Function to display betting screen
def show_betting_screen():
    betting_turtle.clear()
    betting_turtle.goto(0, 100)
    betting_turtle.write("Welcome to Aviator!", align="center", font=("Courier", 24, "bold"))
    betting_turtle.goto(400, 300)
    betting_turtle.write(f"Your Balance: ${balance:.2f}", align="center", font=("Courier", 18, "normal"))
    betting_turtle.goto(0, 50)
    betting_turtle.write("Enter your bet amount in dollars:", align="center", font=("Courier", 18, "normal"))

# Function to handle betting input
def handle_bet_input():
    global bet_amount, target_multiplier, running, crash_point, balance
    try:
        bet_amount = float(turtle.textinput("Bet Amount", "Enter your bet amount in dollars:"))
        if bet_amount > balance:
            betting_turtle.clear()
            betting_turtle.write(f"Insufficient balance. Your balance is ${balance:.2f}", align="center", font=("Courier", 18, "normal"))
            turtle.ontimer(handle_bet_input, 2000)
        else:
            target_multiplier = float(turtle.textinput("Target Multiplier", "Enter your target multiplier:"))
            if bet_amount > 0 and target_multiplier > 1:
                betting_turtle.clear()
                betting_turtle.goto(0, 0)
                betting_turtle.write(f"Your bet: ${bet_amount:.2f}", align="center", font=("Courier", 18, "normal"))
                betting_turtle.goto(0, -50)
                betting_turtle.write(f"Target Multiplier: {target_multiplier:.2f}x", align="center", font=("Courier", 18, "normal"))
                crash_point = random.uniform(1.5, 10.0)
                running = True
                turtle.ontimer(start_flying, 2000)
            else:
                betting_turtle.write("Invalid input. Try again.", align="center", font=("Courier", 18, "normal"))
    except ValueError:
        betting_turtle.write("Please enter valid numbers.", align="center", font=("Courier", 18, "normal"))

# Function to start the game
def start_flying():
    global bet_amount, target_multiplier, multiplier, running, speed, crash_point, balance
    current_winnings = bet_amount
    heading_increment = 0.02

    if running:
        betting_turtle.clear()
        trail_turtle.clear()
        trail_turtle.penup()
        trail_turtle.goto(-610, -340)
        trail_turtle.pendown()
        trail_turtle.begin_fill()
        
        while running:
            screen.update()
            screen.tracer(0)

            plane.forward(1)
            multiplier += 0.01

            current_heading = plane.heading()
            plane.setheading(current_heading + heading_increment)

            current_winnings = bet_amount * multiplier

            trail_turtle.goto(plane.xcor(), plane.ycor())

            multiplier_turtle.clear()
            multiplier_turtle.write(f"Multiplier: {multiplier:.2f}x", font=("Courier", 16, "normal"))
            winnings_turtle.clear()
            winnings_turtle.write(f"Current Winnings: ${current_winnings:.2f}", font=("Courier", 16, "normal"))

            if multiplier >= 1.5:
                speed = max(0.001, speed - 0.0005)

            if multiplier >= crash_point:
                running = False
                betting_turtle.clear()
                betting_turtle.goto(0, 0)
                if multiplier >= target_multiplier:
                    winnings = bet_amount * target_multiplier
                    balance += winnings - bet_amount  # Add winnings and subtract bet amount from balance
                    betting_turtle.write(f"You won ${winnings:.2f}!\nFinal Multiplier: {multiplier:.2f}x\nNew Balance: ${balance:.2f}", align="center", font=("Courier", 24, "bold"))
                else:
                    balance -= bet_amount  # Subtract the bet amount from balance
                    betting_turtle.write(f"You lost!\nFinal Multiplier: {multiplier:.2f}x\nNew Balance: ${balance:.2f}", align="center", font=("Courier", 24, "bold"))
                
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
    global bet_amount, target_multiplier, multiplier, running, crash_point, speed
    bet_amount = 0
    target_multiplier = 0
    multiplier = 1.0
    running = False
    crash_point = 0
    speed = 0.01
    plane.goto(-610, -340)
    plane.setheading(20)
    show_betting_screen()
    turtle.ontimer(handle_bet_input, 1000)

# Initialize game setup
show_betting_screen()
turtle.ontimer(handle_bet_input, 1000)

# Keep the screen open until the user closes it
screen.mainloop()

# Thanks for this info Agrestic