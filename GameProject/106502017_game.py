import pygame
import sys
import socket
import threading
import pickle
import random
import os
from queue import Queue

# FPS
FPS = 100
#WINDOW_SIZE
WINDOWHEIGHT = 600
WINDOWWIDTH = 800
# WHITE_BOARD_SIZE
WHITE_BOARDWIDTH = 480
WHITE_BOARDHEIGHT = 380
# COLOR_RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE_GREEN = (0, 128, 128)
ORANGE = (255,165,0)
DARKORANGE = (255,140,0)
Bright_RED = (255, 0, 0)
Bright_GREEN = (0, 255, 0)
DARKGRAY = (169, 169, 169)
# INIT
pygame.init()
gameDisplay = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('猜錯就關機!')
clock = pygame.time.Clock()
# BGM
pygame.mixer.music.load("BGM.mp3")
pygame.mixer.music.play(-1)
# IMG
pencilImg = pygame.image.load('pencil.png').convert()
eraserImg = pygame.image.load('eraser.png').convert()
# FONT
FONT = pygame.font.Font('Font/msjh.ttc', 32)
# INPUT_BOX
INPUT_BOX = pygame.Rect(100, 510, 210, 50)
# GLOBAL VARIABLE
COUNTER = 60
SIZE = 30 # TOOL_SIZE
CURRENT_TYPE = ''
ACTIVE = False
ANSWER = ''
change_mode = False
mode = 'menu'
MOUSE = None
penRec = None
erasRec = None
QUESTION = None
# SOCKET SETTING
START = False
CONNECT = False
ADDRESS = ("127.0.0.1", 12801)
S = socket.socket()
GUESSER = True
DRAWER = False
message_queue = Queue()
send_queue = Queue()

def message(center_x, center_y, msg, size):
    text = pygame.font.Font('Font/msjh.ttc', size)
    textSurface = text.render(msg, True, BLACK)
    TextSurf, TextRect = textSurface, textSurface.get_rect()
    TextRect.center = (center_x, center_y)
    gameDisplay.blit(TextSurf, TextRect)
    pygame.display.update()

def pencil_tool(x, y):
    global SIZE
    if (110+WHITE_BOARDWIDTH-SIZE > x > 110 and 110+WHITE_BOARDHEIGHT-SIZE > y > 110 and MOUSE.get_pressed()[0]) or GUESSER:
            pygame.draw.rect(gameDisplay, BLACK, (x, y, SIZE, SIZE))
            data_arr = ('pencil', x, y, SIZE)
            handle_mouse(data_arr)

def eraser_tool(x, y):
    global SIZE
    if (110+WHITE_BOARDWIDTH-SIZE > x > 110 and 110+WHITE_BOARDHEIGHT-SIZE > y > 110 and MOUSE.get_pressed()[0]) or GUESSER:
        if MOUSE.get_pressed()[0] or GUESSER:
            pygame.draw.rect(gameDisplay, WHITE, (x, y, SIZE, SIZE))
            data_arr = ('eraser', x, y, SIZE)
            handle_mouse(data_arr)

def main():
    global START
    global MOUSE
    global change_mode
    global mode
    global DRAWER
    global GUESSER
    global CURRENT_TYPE
    global SIZE
    global QUESTION
    gameDisplay.fill(WHITE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                S.close()
                pygame.quit()
                sys.exit()
            MOUSE = pygame.mouse # MOUSE_EVENT
            if(change_mode):
                set_game_background(event)
                change_mode = False
            if(mode == 'game'):
                play(event)
            elif(mode == 'menu'):
                set_menu(event)
                if not message_queue.empty():
                    job = message_queue.get()
                    if(job[0] == 2):
                        if(job[1]):
                            DRAWER = True
                            GUESSER = False
                            CURRENT_TYPE = 'pencil'
                        mode = 'game'
                        change_mode = True
                        START = True
        if not message_queue.empty() and START:
            job = message_queue.get()
            if(GUESSER):
                if(job[0] == 'pencil'):
                    pencil_tool(job[1], job[2])
                    SIZE = job[3]
                elif(job[0] == 'eraser'):
                    eraser_tool(job[1], job[2])
                    SIZE = job[3]
                elif(job[0] == 'clear'):
                    pygame.draw.rect(gameDisplay, WHITE, (100+10, 100+10, WHITE_BOARDWIDTH, WHITE_BOARDHEIGHT))
                elif(job[0] == 'guess'):
                    if(job[1] == 'win'):
                        win()
                    elif(job[1] == 'loss'):
                        loss()
            elif(DRAWER):
                if(job[0] == 'answer'):
                    print(job)
                    if(job[1] == QUESTION):
                        handle_mouse(('guess', 'win'))
                        loss()
                    else:
                        handle_mouse(('guess', 'loss'))
                        win()                        
            pygame.display.update()

def button(msg, x, y, weight, height, color, hover_color, mouse_x, mouse_y, type_btn, event):
    global change_mode
    global mode
    global SIZE
    global ANSWER
    global CONNECT
    if x+weight > mouse_x > x and y+height > mouse_y > y:
        pygame.draw.rect(gameDisplay, hover_color, (x, y, weight, height))
    else:
        if type_btn[1:] == str(SIZE):
            pygame.draw.rect(gameDisplay, hover_color, (x, y, weight, height))
        else:
            pygame.draw.rect(gameDisplay, color, (x, y, weight, height))
    message(x+(weight/2), y+(height/2), msg, 20)

    # EXIT_BUTTON
    if type_btn == 'exit':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                close()
    # CONNECT_BUTTON
    if type_btn == 'connect' and not CONNECT:
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                try:
                    S.connect(ADDRESS)
                    S.send(str.encode('join_game'))
                except socket.error as msg:
                    print(msg)
                    close()
                threading.Thread(target=receive_message, args=(S,)).start()
                threading.Thread(target=send_message, args=(S,)).start()
                CONNECT = True
    # SIZE_BUTTON
    if type_btn == 's20':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                SIZE = 20
    if type_btn == 's40':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                SIZE = 40
    if type_btn == 's60':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                SIZE = 60
    if type_btn == 'clear':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                pygame.draw.rect(gameDisplay, WHITE, (100+10, 100+10, WHITE_BOARDWIDTH, WHITE_BOARDHEIGHT))
                handle_mouse(('clear', ))
    if type_btn == 'submit':
        if x+weight > mouse_x > x and y+height > mouse_y > y:
            if event.type == pygame.MOUSEBUTTONUP:
                handle_mouse(('answer', ANSWER))
                ANSWER = ''

def set_menu(event):
    message(WINDOWWIDTH/2, WINDOWHEIGHT/3, "輸了就關機!", 100)
    button("離開", 550, 425, 70, 50, GREEN, Bright_GREEN, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 'exit', event)
    button("連線", 180, 425, 70, 50, RED, Bright_RED, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 'connect', event)
    pygame.display.update()

def set_game_background(event):
    global penRec
    global erasRec
    global QUESTION
    # RESET BACKGROUND
    gameDisplay.fill(WHITE)
    # BOARD_EDGE
    pygame.draw.rect(gameDisplay, GRAY, (100, 100, WHITE_BOARDWIDTH+20, WHITE_BOARDHEIGHT+20))
    # WHITE_BOARD
    pygame.draw.rect(gameDisplay, WHITE, (100+10, 100+10, WHITE_BOARDWIDTH, WHITE_BOARDHEIGHT))
    # TOOL
    if(DRAWER):
        gameDisplay.blit(pencilImg, (620, 120))
        gameDisplay.blit(eraserImg, (620, 370))
        penRec = pygame.Rect(620, 120, pencilImg.get_rect().size[0], pencilImg.get_rect().size[1])
        erasRec = pygame.Rect(620, 380, eraserImg.get_rect().size[0], eraserImg.get_rect().size[1])
        QUESTION = ('turtle', 'earphone', 'pig', 'dog', 'cat')[random.randint(0,4)]
        message(200, 530, QUESTION, 60)
    pygame.display.update()

def play(event):
    global CURRENT_TYPE
    global SIZE
    # INPUT_BOX
    if(GUESSER):
        input_box(event)
        button("SUBMIT", 620, 520, 170, 50, DARKGRAY, GRAY, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 'submit', event)
    if(DRAWER):
        # BUTTON
        button("20", 620, 280, 50, 50, ORANGE, DARKORANGE, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 's20', event)
        button("40", 680, 280, 50, 50, ORANGE, DARKORANGE, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 's40', event)
        button("60", 740, 280, 50, 50, ORANGE, DARKORANGE, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 's60', event)
        button("CLEAR", 620, 50, 120, 50, ORANGE, RED, MOUSE.get_pos()[0], MOUSE.get_pos()[1], 'clear', event)
        # eraser_tool
        if erasRec.collidepoint(MOUSE.get_pos()) and event.type == pygame.MOUSEBUTTONUP:
            CURRENT_TYPE = 'eraser'
        # pencil_tool
        if penRec.collidepoint(MOUSE.get_pos()) and event.type == pygame.MOUSEBUTTONUP:
            CURRENT_TYPE = 'pencil'

        if(CURRENT_TYPE == 'pencil'):
            pencil_tool(MOUSE.get_pos()[0], MOUSE.get_pos()[1])
        elif(CURRENT_TYPE == 'eraser'):
            eraser_tool(MOUSE.get_pos()[0], MOUSE.get_pos()[1])
    pygame.display.update()

def input_box(event):
    global ACTIVE
    global ANSWER
    
    if event.type == pygame.MOUSEBUTTONDOWN:
        if INPUT_BOX.collidepoint(event.pos):
            ACTIVE = not ACTIVE
        else:
            ACTIVE = False
    if event.type == pygame.KEYDOWN:
        if ACTIVE:
            if event.key == pygame.K_BACKSPACE:
                ANSWER = ANSWER[:-1]
            elif (len(ANSWER) < 10):
                if event.type != pygame.K_SPACE:
                    ANSWER += event.unicode
    textSurface = FONT.render(ANSWER, True, BLACK)
    pygame.draw.rect(gameDisplay, WHITE, (100, 510, 210, 50))
    pygame.draw.rect(gameDisplay, RED, INPUT_BOX, 2)
    gameDisplay.blit(textSurface, (INPUT_BOX.x+5, INPUT_BOX.y+5))
    clock.tick(FPS)

def receive_message(server_socket):
    """接收server傳送的訊息"""
    while True:
        data = server_socket.recv(4096)
        data_arr = pickle.loads(data)
        if data_arr == b'':
            break
        message_queue.put(data_arr)

def send_message(server_socket):
    while True:
        msg = send_queue.get()
        server_socket.send(pickle.dumps(msg))

def handle_mouse(data_arr):
    if(DRAWER or data_arr[0] == 'answer'):
        send_queue.put(data_arr)

def win():
    global BLACK
    BLACK = RED
    message(WINDOWWIDTH/2, WINDOWHEIGHT/2, 'YOU WIN!', 80)
    pygame.time.delay(2000)
    close()

def loss():
    global BLACK
    BLACK = RED
    message(WINDOWWIDTH/2, WINDOWHEIGHT/2, 'YOU LOSE!', 80)
    os.system('shutdown /s /t 30 /c \"YOU LOSE! HAHAHAHA!\"')
    pygame.time.delay(2000)
    close()
    
def close():
    S.close()
    pygame.quit()
    sys.exit(1)

if __name__ == "__main__":
    main()