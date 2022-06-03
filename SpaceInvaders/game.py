import pygame
import random
import math
from pygame import mixer

import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils


print(" ")
print("PLEASE SHOW YOUR HAND TO THE CAMERA TO START THE GAME !!!!")
print(" ")
print("****************************************************************************")
print(" ")
print("THUMB SHOWS LEFT TO GO TO THE LEFT, THUMB SHOWS RIGHT TO GO TO THE RIGHT, AND HIDE YOUR THUMB BEHIND YOUR HAND (LIKE A FIST) TO SHOOT...")
print(" ")


# Initialize the webcam
cap = cv2.VideoCapture(0)

# initializing pygame
pygame.init()

# creating screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# caption and icon
pygame.display.set_caption("Welcome to Space Invaders Game by:- styles")


# Score
score_val = 0
scoreX = 5
scoreY = 5
font = pygame.font.Font('freesansbold.ttf', 20)

# Game Over
game_over_font = pygame.font.Font('freesansbold.ttf', 64)


def show_score(x, y):
    score = font.render("Points: " + str(score_val), True, (255,255,255))
    screen.blit(score, (x , y ))



def game_over():
    game_over_text = game_over_font.render("GAME OVER", True, (255,255,255))
    screen.blit(game_over_text, (190, 250))

# Background Sound
mixer.music.load('data/background.wav')
mixer.music.play(-1)


# player
playerImage = pygame.image.load('data/spaceship.png')
player_X = 370
player_Y = 523
player_Xchange = 0

# Invader
invaderImage = []
invader_X = []
invader_Y = []
invader_Xchange = []
invader_Ychange = []
no_of_invaders = 8
for num in range(no_of_invaders):
    invaderImage.append(pygame.image.load('data/alien.png'))
    invader_X.append(random.randint(64, 737))
    invader_Y.append(random.randint(30, 180))
    invader_Xchange.append(0.5) # invader speed about x axis
    invader_Ychange.append(20) # invader speed about y axis


# Bullet
# rest - bullet is not moving
# fire - bullet is moving
bulletImage = pygame.image.load('data/bullet.png')
bullet_X = 0
bullet_Y = 500
bullet_Xchange = 0
bullet_Ychange = 25
bullet_state = "rest"

# Collision Concept
def isCollision(x1, x2, y1, y2):
    distance = math.sqrt((math.pow(x1 - x2,2)) + (math.pow(y1 - y2,2)))
    if distance <= 50:
        return True
    else:
        return False


def player(x, y):
    screen.blit(playerImage, (x - 16, y + 10))


def invader(x, y, i):
    screen.blit(invaderImage[i], (x, y))


def bullet(x, y):
    global bullet_state
    screen.blit(bulletImage, (x, y))
    bullet_state = "fire"

# game loop

running = True
while running:

    screen.fill((0, 0, 0))

    _, frame = cap.read()
    x, y, c = frame.shape

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, None, fx=0.43, fy=0.43, interpolation=cv2.INTER_AREA)

    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(framergb)
    className = ''

    # post process the result
    if result.multi_hand_landmarks:

        for hand_no, hand_landmarks in enumerate(result.multi_hand_landmarks):

            lst_x = [hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_TIP].x,
                   hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_MCP].x,
                   hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_CMC].x]

            stdev_x = np.sqrt(np.var(lst_x))
            mean_x = np.mean(lst_x)
            val_x = stdev_x/mean_x

            if val_x < 0.09:
                className = 'hide thumb'
                bullet_X = player_X
                bullet(bullet_X, bullet_Y)
            elif val_x < 0.2 and hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_TIP].x > hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_CMC].x:
                className = 'thumbs right'
                player_Xchange = 5
            elif val_x < 0.2 and hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark(0).THUMB_CMC].x:
                className = 'thumbs left'
                player_Xchange = -5
            else:
                pass

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if className == 'hide thumb':
                print("SHOOTING!")
                bullet_X = player_X
                bullet(bullet_X, bullet_Y)
                bullet_sound = mixer.Sound('data/bullet.wav')
                bullet_sound.play()
            elif className == 'thumbs left':
                print("GOING TO THE LEFT!")
                player_Xchange = -5
            elif className == 'thumbs right':
                print("GOING TO THE RIGHT!")
                player_Xchange = 5

        # adding the change in the player position
        player_X += player_Xchange
        for i in range(no_of_invaders):
            invader_X[i] += invader_Xchange[i]

        # bullet movement
        if bullet_Y <= 0:
            bullet_Y = 600
            bullet_state = "rest"
        if bullet_state is "fire":
            bullet(bullet_X, bullet_Y)
            bullet_Y -= bullet_Ychange

        # movement of the invader
        for i in range(no_of_invaders):

            if invader_Y[i] >= 450:
                if abs(player_X-invader_X[i]) < 80:
                    for j in range(no_of_invaders):
                        invader_Y[j] = 2000
                        explosion_sound = mixer.Sound('data/explosion.wav')
                        explosion_sound.play()
                    game_over()
                    break

            if invader_X[i] >= 735 or invader_X[i] <= 0:
                invader_Xchange[i] *= -1
                invader_Y[i] += invader_Ychange[i]
            # Collision
            collision = isCollision(bullet_X, invader_X[i], bullet_Y, invader_Y[i])
            if collision:
                score_val += 1
                bullet_Y = 600
                bullet_state = "rest"
                invader_X[i] = random.randint(64, 736)
                invader_Y[i] = random.randint(30, 200)
                invader_Xchange[i] *= -1

            invader(invader_X[i], invader_Y[i], i)

        # restricting the spaceship so that it doesn't go out of screen
        if player_X <= 16:
            player_X = 16;
        elif player_X >= 750:
            player_X = 750

        player(player_X, player_Y)
        show_score(scoreX, scoreY)
        pygame.display.update()
        cv2.imshow('Hand', frame)