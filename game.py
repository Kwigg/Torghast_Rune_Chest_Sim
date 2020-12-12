import sys
import os
import pygame
import random

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Rune(pygame.sprite.Sprite):
    def __init__(self, xPos):
        super(Rune, self).__init__()
        self.currentState = 0
        self.idealState = 1
        self.affectedRunes = [0]
        self.xPos = xPos
        self.rect = pygame.rect.Rect(xPos, 410, 150, 150)


class Chain(pygame.sprite.Sprite):
    def __init__(self, xPos):
        super(Chain, self).__init__()
        self.xPos = xPos
        self.active = False

#File IO

#Wrapper script for pyinstaller to work
#Shamelessly taken from stackoverflow: https://stackoverflow.com/a/54926684
def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

blueSigil = pygame.image.load(resource_path("Sprites/BlueSigil.png"))
greenSigil = pygame.image.load(resource_path("Sprites/GreenSigil.png"))
orangeSigil = pygame.image.load(resource_path("Sprites/OrangeSigil.png"))
purpleSigil = pygame.image.load(resource_path("Sprites/PurpleSigil.png"))
chainSprite = pygame.image.load(resource_path("Sprites/StackingChains.png"))

startButton = pygame.image.load(resource_path("Sprites/StartButton.png"))
quitButton = pygame.image.load(resource_path("Sprites/QuitButton.png"))
resetButton = pygame.image.load(resource_path("Sprites/ResetButton.png"))

successText = pygame.image.load(resource_path("Sprites/SuccessText.png"))

menuRects = []
menuRects.append(pygame.rect.Rect((SCREEN_WIDTH - 200)/2, (SCREEN_HEIGHT - 150)/2 - 90,200,150))
menuRects.append(pygame.rect.Rect((SCREEN_WIDTH - 200)/2, (SCREEN_HEIGHT - 150)/2 + 90,200,150))

resetRects = []
resetRects.append(pygame.rect.Rect((SCREEN_WIDTH - 200)/2 - 110, (SCREEN_HEIGHT - 150)/2,200,150))
resetRects.append(pygame.rect.Rect((SCREEN_WIDTH - 200)/2 + 110, (SCREEN_HEIGHT - 150)/2,200,150))

successRect = pygame.rect.Rect((SCREEN_WIDTH - 500)/2, (SCREEN_HEIGHT - 50)/2 - 140,200,150)
# 0 = blue
# 1 = green
# 2 = orange
# 3 = purple
# 4 = chain
spriteList = [blueSigil, greenSigil, orangeSigil, purpleSigil, chainSprite]

runes = []
runes.append( Rune(60)  )
runes.append( Rune(230) )
runes.append( Rune(400) )
runes.append( Rune(570) )

chains = []
chains.append( Chain(60) )
chains.append( Chain(230) )
chains.append( Chain(400) )
chains.append( Chain(570) )

shouldRun = True
isMenuOpen = True
isChestOpen = False

#Drawing functions

def draw_runes():
    for x in runes:
        screen.blit(spriteList[x.currentState], (x.xPos, 410))

def draw_chains():
    for x in range(0,4):
        if runes[x].currentState != runes[x].idealState:
            chains[x].active = True
            screen.blit(chainSprite, (chains[x].xPos, 80))
            screen.blit(chainSprite, (chains[x].xPos, 230))

def draw_reset_buttons():
    screen.blit(resetButton, resetRects[0].topleft)
    screen.blit(quitButton, resetRects[1].topleft)
    screen.blit(successText, successRect.topleft)

def draw_game():
    draw_runes()
    if isChestOpen == False:
        draw_chains()
    else:
        draw_reset_buttons()

def draw_menu():
    screen.blit(startButton, menuRects[0].topleft)
    screen.blit(quitButton, menuRects[1].topleft)

def draw():
    screen.fill((0,0,0))
    if isMenuOpen == True:
        draw_menu()
    else:
        draw_game()
    pygame.display.flip()

# Interaction functions
def clickRune(rune):
    for x in rune.affectedRunes:
        runes[x].currentState += 1
        if runes[x].currentState > 3:
            runes[x].currentState = 0

# Victory checking
def checkVictory():
    runesClean = True
    for rune in runes:
        if rune.currentState != rune.idealState:
            runesClean = False
    return runesClean

# Initialisation functions
def initialiseRunes():
    numberList = [0, 1, 2, 3]
    for x in range(0,4):
        currentIndex = random.choice(numberList)
        runes[currentIndex].idealState = random.choice([0,1,2,3])
        runes[currentIndex].currentState = random.choice([0,1,2,3])
        runes[currentIndex].affectedRunes = [currentIndex]
        numberList.remove(currentIndex)
        assignmentList = numberList.copy()
        if len(assignmentList) > 0:
            for y in range(0, (3-x)):
                newIndex = random.choice(assignmentList)
                runes[currentIndex].affectedRunes.append(newIndex)
                assignmentList.remove(newIndex)
    # Make sure we don't start into a pre-solved state. 
    # (What are the odds?!)
    if checkVictory() == True:
        initialiseRunes()

while shouldRun:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                shouldRun = False
        elif event.type == QUIT:
            shouldRun = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if isMenuOpen == True:
                for x in range(0,2):
                        if menuRects[x].collidepoint(pos):
                            if x == 0:
                                initialiseRunes()
                                isChestOpen = False
                                isMenuOpen = False
                            else:
                                shouldRun = False
            else:
                if isChestOpen == True:
                    for x in range(0,2):
                        if resetRects[x].collidepoint(pos):
                            if x == 0:
                                initialiseRunes()
                                isChestOpen = False
                            else:
                                shouldRun = False
                else:
                    # Update runes
                    for rune in runes:
                        if rune.rect.collidepoint(pos):
                            clickRune(rune)
                    # Now check. We have to check after updating them as
                    # runes alter the value of others, including preceding
                    # ones in the list
                    isChestOpen = checkVictory()
    draw()

