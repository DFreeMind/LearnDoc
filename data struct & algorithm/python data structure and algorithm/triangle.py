import turtle
import random
def drawst(Linelen, t):
    if Linelen > 20:
        t.forward(Linelen)
        t.left(120)
        drawst(Linelen/2, t)
        t.forward(Linelen)
        t.left(120)
        drawst(Linelen/2, t)
        t.forward(Linelen)
        t.left(120)
        drawst(Linelen/2, t)
    
def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    turtle.colormode(255)
    t.speed(1)
    t.backward(100)

    drawst(300,t)
    myWin.exitonclick()
main()