"""
=====================================
MicroBit Abnormal Behaviour Game
=====================================
:Author: jhirst1
:Date: Sun May  5 18:29:19 2019

=====================================
Patch notes
=====================================
    0.1: added delay onto a_or_b() if you haven't authenticated to give you more time
         added in daily peer count into risk score
    0.2  delay amended for a_or_b() to shorten delay between next show_a(), show_b()
    0.3 taking out timed element from a or b
    0.4 added compass element
        fixed ssl < 0 logic mistake
        added in piazzo buzzer on gameover
    0.5 altered the image on south to face south
        compass check amended to come before timer started
        add exclaim if accessing more cust accounts than peers
        changed number of accounts accessed to 12 and 15 for abnormal
=====================================
Purpose
=====================================

This game makes use of the MicroBit's internal sensors, such as the compass,
directional tilt, user input buttons, and motion control. 

The aim is to remain undetected on "Bob's" network for as long as possible, 
however there are anomaly detection rules in place to identify 
'unusual' behaviour for bob. You need to emulater Bob's working pattern 
to remain undetected. The more abnormal your behaviour is compared to Bob's,
then the higher your abnormality risk score will go. If you reach a risk
score of 10, then you lose the game. 

=====================================
Game Rules
=====================================

1) bobs password expires every week, so you only have 5 days of access, see how many customer records can you steal without getting caught?
2) if you get flagged by UBA, it's game over
3) bob's peers usually access upto 10 customer records a day. abnormal 
4) bob usually starts work at 9 and finishes at 5 - press A and B together to finish your day - you can work late, but the later you work the more abnormal the behaviour
5) in the morning bob usually faces north, then in the afternoon changes workstation and faces south - abnormal
6) bob always stops for lunch at 12 and starts work again at 1pm
7) before you can access the customer credentials each day, you have to pass the ssl handshake- v abnormal
8) end of each day you get shown your risk score 

"""

####Packages####   
from microbit import *
import random

####Variable Assignment & initialisation####

PEERS = (12, 15)
DAYS = {0: "DAY ONE", 1: "DAY TWO", 2: "DAY THREE", 3: "DAY FOUR", 4: "DAY FIVE"}
DAY = 0
level = 0
score = 0
total_score = 0
risk_score = 0
gameover = False

LOCK = Image("09990:"
             "90009:"
             "99999:"
             "90909:"
             "99999")

####Custom Functions####

def show_a():
    display.clear()
    display.show("A")

def show_b():
    display.clear()
    display.show("B")
    
def show_lock():
    display.clear()
    display.show(LOCK)
    sleep(1000)
    
def show_tick():
    display.clear()
    display.set_pixel(0, 3, 9)
    display.set_pixel(1, 4, 9)
    display.set_pixel(2, 3, 9)
    display.set_pixel(3, 2, 9)
    display.set_pixel(4, 1, 9)
    
def show_cross():
    display.clear()
    display.show("X")
    

def show_s():
    display.clear()
    display.show(Image.ARROW_S)
    sleep(500)
    
def show_exclaim():
    display.clear()
    display.show("!")
    sleep(150)
    
def display_intro(x):
    display.scroll(DAYS[x])  #display the day number at the start
    
    for x in range(3,-1,-1): #countdown 3,2,1,0
        display.show(str(x))
        sleep(1000)
    
def start_timer():
    global started, now
    started = running_time() #start timer for morning
    now = running_time() #time in morning        

def wait_for_button(rightbutton, wrongbutton):
    global ssl
    rightpressed = False
    wrongpressed = False
    
    started = running_time()
    now = running_time()
    
    if ssl > 0:
        while not(rightpressed or wrongpressed):
            if rightbutton.is_pressed():
                rightpressed = True
            if wrongbutton.is_pressed():
                wrongpressed = True
            now = running_time()
    else: 
         while not(rightpressed or wrongpressed):
            ssl_handshake() # checking handshake
            if rightbutton.is_pressed():
                rightpressed = True
            if wrongbutton.is_pressed():
                wrongpressed = True
            now = running_time()       
        
    if (rightpressed == True and wrongpressed == False):
        return True
    else:
        return False

def a_or_b():
    global score, gameover
    #randomly pick an A or B button
    action = random.randint(0, 1)
    
    #wait for the button to be pressed
    if action == 0:
        show_a()
        success = wait_for_button(button_a, button_b)
    elif action == 1:
        show_b()
        success = wait_for_button(button_b, button_a)
        
    if ssl < 1:
        show_lock()
        v_abnormal()
        
    elif success:
        show_tick()
        score = score + 1
        
        if (score + 1) in PEERS:
            show_exclaim() 
        
        if score in PEERS:
            abnormal()
            
    else: # if not authenticated
        show_cross()
        abnormal()

def abnormal():
    global risk_score, gameover
    risk_score = risk_score + 1
    if risk_score > 9:
        pin0.write_digital(1)
        sleep(500)
        pin0.write_digital(0)
        display.scroll("GAMEOVER")
        gameover = True
        
def v_abnormal():
    global risk_score, gameover
    risk_score = risk_score + 3
    if risk_score > 9:
        pin0.write_digital(1)
        sleep(500)
        pin0.write_digital(0)        
        display.scroll("GAMEOVER")
        gameover = True
        
def ssl_handshake():
    global ssl
    gesture = accelerometer.current_gesture()
    if gesture == "shake":
        ssl = ssl + 1
        
def check_compass(x):
    heading = compass.heading()

    if x == 0 and 90 <= compass.heading() <= 270:
        show_s()
        show_cross()
        abnormal()
    elif x == 1 and not(90 <= compass.heading() <= 270):
        abnormal()
        show_s()
        show_cross()



while True:
    while gameover == False:
        success = False
        ssl = 0
        score = 0
        
        '''INTRO SCREEN'''
        display_intro(DAY)
        
        '''MORNING TIME'''
        check_compass(0) # check compass is facing north
        start_timer()
        
        while now - started < 8000 and gameover == False: #the morning lasts 15 hours (1hr=3sec)
            a_or_b()
            sleep(500)
            now = running_time()
        
        '''LUNCH TIME'''
        display.show(Image.CLOCK12)
        start_timer()
        while now - started < 2000 and gameover == False:
            if button_a.is_pressed() or button_b.is_pressed():
                abnormal()
            now = running_time()
        display.show(Image.CLOCK1)
        sleep(1000)
            
        '''AFTERNOON TIME'''    
        check_compass(1) # check compass is facing south
        start_timer()
        while now - started < 8000 and gameover == False: #the morning lasts 15 hours (1hr=3sec)
            a_or_b()
            sleep(500)
            now = running_time()
        
        total_score = total_score + score
        
        if gameover == False:
            display.scroll("{} RISK SCORE".format(risk_score))
            DAY = DAY + 1
        if DAY == 5:
            display.scroll("YOU DID IT!")
            gameover = True
        
    display.scroll("{} CUSTOMER RECORDS".format(total_score))
