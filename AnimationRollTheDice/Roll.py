from logging import root
import random
from tkinter import *

root = Tk()
root.geometry("400x600")
root.title('Roll The Dice')

bg = PhotoImage(file = "AnimationRollTheDice/Dice.png")

myL = Label(image=bg)
myL.place(x=0,y=0,relwidth=1,relheight=1)

myT = Label(text="Roll Your Destiny",font=("Helvetica", 18), fg="black").pack(pady=50)

label = Label(root, text="",font=("times",60))
label1 = Label(root, text="",font=("Arial Unicode MS",20))
label2 = Label(font=("Helvetica", 18), fg="green", bg="black")    


def roll():
    dice=['\u2680','\u2681','\u2682','\u2683','\u2684','\u2685']
    Fdice, Sdice = random.choice(dice),random.choice(dice)

    if Fdice == '\u2680' :
        fd = 1
    elif Fdice == '\u2681' :
        fd = 2
    elif Fdice == '\u2682' :
        fd = 3
    elif Fdice == '\u2683' :
        fd = 4
    elif Fdice == '\u2684' :
        fd = 5
    elif Fdice == '\u2685' :
        fd = 6 

    if Sdice == '\u2680' :
        sd = 1
    elif Sdice == '\u2681' :
        sd = 2
    elif Sdice == '\u2682' :
        sd = 3
    elif Sdice == '\u2683' :
        sd = 4
    elif Sdice == '\u2684' :
        sd = 5
    elif Sdice == '\u2685' :
        sd = 6


    if sd == fd:
        label2.configure(text=f'Double') 
        label2.pack()
    else:
        label2.pack_forget()

    label.configure(text=f'{Fdice}{Sdice}')
    label1.configure(text=f'Total = {fd + sd}')

    label.pack(pady=20)
    label1.pack(pady=10)

# ROUNDED BUTTON
Button(root, text="Let's Roll...", width=10, height=2, font=10, bg="white", bd=2, command=roll).pack(padx=10,pady=10)

root.mainloop()
