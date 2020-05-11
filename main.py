import pygame 
import py_midicsv
import sys
import time
import math
from pygame.locals import *


class Note: #struct
    def __init__(self, t, p, v):
        self.time = t
        self.pitch = p
        self.velocity = v

def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print("Warning: Zero input range")
        return None

    if nMin == nMax:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return int(result)


clock = pygame.time.Clock()

#midiFile = "C:\\Users\\katzb\\Downloads\\simple.mid"
#midiFile = "C:\\Users\\katzb\\Downloads\\midi for ben.mid"
#midiFile = "C:\\Users\\katzb\\Downloads\\midi for ben_modified.mid"
midiFile = "C:\\Users\\katzb\\Downloads\\midi2.mid"
csv_string = py_midicsv.midi_to_csv(midiFile)

noteOnList = []
noteOffList = []
pairedNotes = []

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1000
PIANO_OFFSET = SCREEN_HEIGHT - SCREEN_HEIGHT/4

TIME_SCALE = 1
FPS = 60

#scrape string and create on and off note lists
for index in range(len(csv_string)):
    tempList = csv_string[index].split(',')
    if(tempList[2] == " Note_on_c"):
        noteOnList.append(Note(int(tempList[1]), remap(int(tempList[4]),0, 88, 0, SCREEN_WIDTH), int(tempList[5])))
    if(tempList[2] == " Note_off_c"):
        noteOffList.append(Note(int(tempList[1]), remap(int(tempList[4]),0, 88, 0, SCREEN_WIDTH), int(tempList[5])))

#print(len(noteOnList))
#print(len(noteOffList))

#pair on and off notes to be rectangles
if len(noteOnList) == len(noteOffList):
    for i in range(len(noteOnList)):
        for j in range(len(noteOffList)):
            if noteOnList[i].pitch == noteOffList[j].pitch and ((noteOffList[j].time - noteOnList[i].time) > 0):
                height = noteOffList[j].time - noteOnList[i].time#height is the difference in time
                yStart = -noteOnList[i].time*TIME_SCALE#start the ys at the negative of time so they start above the screen and will come down
                yStart = yStart - height + PIANO_OFFSET #need to subtract the height since (x, y) is in the upper left corner, add offset to time with music
                width = math.floor(SCREEN_WIDTH/88)# split screen into 89 sections, 88 keys plus a little buffer
                pairedNotes.append(pygame.Rect(noteOffList[j].pitch, yStart, width, height))
                break

notesYfloat = []
notesHfloat = []
for index in range(len(pairedNotes)):
    notesYfloat.append(float(pairedNotes[index].y))
    notesHfloat.append(float(pairedNotes[index].height))


pygame.init() 
white = (255, 255, 255) 
green = (0, 255, 0) 
blue = (0, 0, 255) 
black = (0, 0, 0) 
red = (255, 0, 0) 
grey = (37, 37, 38)


display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT )) 
pygame.display.set_caption('Drawing') 




pygame.mixer.music.load(midiFile)
pygame.mixer.music.play()


running=True

deltaY = float(195/(FPS/TIME_SCALE))
#deltaY = float(146/(FPS/TIME_SCALE))

while running:
    display_surface.fill(grey)#clear screen

    for index in range(len(pairedNotes)):
        keyHit = False#keyHit indicator
        #change float values
        notesYfloat[index] += + deltaY
        if notesYfloat[index] + notesHfloat[index]  > PIANO_OFFSET:#if the note is passing the piano offset shorten the height
            keyHit = True
            notesHfloat[index] -= deltaY
        
        #use floats to assign new positions and heights
        pairedNotes[index].y =  notesYfloat[index]
        pairedNotes[index].height = notesHfloat[index]

        if pairedNotes[index].y < PIANO_OFFSET: #if y is above the piano then display it
            if keyHit: 
                pygame.draw.rect(display_surface,blue,pairedNotes[index])
            else:
                pygame.draw.rect(display_surface,black,pairedNotes[index])


   
    #generate piano
    for i in range(89):
        if i%12 == 0 or i%12 == 2 or i%12 == 4 or i%12 == 5 or i%12 == 7 or i%12 == 9 or i%12 == 11:#white keys
            pygame.draw.rect(display_surface, white, pygame.Rect(i*math.floor(SCREEN_WIDTH/88), PIANO_OFFSET, math.floor(SCREEN_WIDTH/88), 100))
        else:
            pygame.draw.rect(display_surface, black,  pygame.Rect(i*math.floor(SCREEN_WIDTH/88), PIANO_OFFSET, math.floor(SCREEN_WIDTH/88), 80))

    pygame.draw.rect(display_surface,red,pygame.Rect(0, PIANO_OFFSET, SCREEN_WIDTH, 15))#where notes hit

    clock.tick(FPS)#fps (delay)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    pygame.display.update() 
pygame.quit()



