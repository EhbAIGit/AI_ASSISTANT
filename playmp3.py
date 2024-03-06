import pygame
import sys
parameter1 = sys.argv[1]

def play_mp3(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Initialiseer Pygame voor audio afspelen
pygame.mixer.init()

play_mp3(parameter1)
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)   




