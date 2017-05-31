import organism
import pygame
import time, math, random
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

# OpenGL/pygame stuff

def resize(screen):
    width, height = screen
    if height == 0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, -1000.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_ALPHA_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glAlphaFunc(GL_NOTEQUAL,0.0)

screensize = 750.0

pygame.init()
width = int(screensize)
Screen = (width,int(screensize))
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Avida Clone")
Surface = pygame.display.set_mode(Screen,OPENGL|DOUBLEBUF)
resize(Screen)
init()

grid_size = 150
gridW = range(grid_size)
scale = screensize/grid_size
grid = [[None for i in range(grid_size)] for j in range(grid_size)]

ancestor = organism.organism()

# The ancestor's genome (Look in organism.py for reference)
ancestor.setGenome([17,20,2,0,21,2,20,19,24,2,0,18,21,0,1])
grid[grid_size/2][grid_size/2] = ancestor
del ancestor


# Display

def draw():
    glPointSize(scale*1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glPushMatrix()
    glScalef(scale,scale,scale)

    # Draw the organisms
    glBegin(GL_POINTS)
    for i,row in enumerate(grid):
        for j,instance in enumerate(row):
            if instance!=None:
                glColor3f(instance.colour[0],instance.colour[1],instance.colour[2])
                glVertex3f(i,j,0.0)
    glEnd()

    glPopMatrix()

    pygame.display.flip()


minSize = 8
maxSize = 200
ageLimit = 400

def update(generation):
    oldest = 0
    totalAge = 0
    populationSize = 0

    random.shuffle(gridW)
    for i in gridW:
        for j in range(len(grid[i])):
            instance = grid[i][j]
            if instance != None:

                if instance.age > ageLimit:
                    grid[i][j] = None
                    break

                populationSize += 1
                if instance.age>oldest:
                    oldest = instance.age
                totalAge += instance.age

                result = instance.execute(0) # Execute one step for this organism

                if result!=None and len(result) > minSize and len(result) < maxSize: # If it has produced offspring
                    offspring = organism.organism()
                    # Insertion and deletion mutations
                    if random.random() < organism.birth_insert_mutation_rate:
                        locus = random.randint(0,len(result))
                        result = result[:locus] + [random.randint(0,organism.number_of_instructions)] + result[locus:]
                    if random.random() < organism.birth_delete_mutation_rate:
                        locus = random.randint(1,len(result))
                        result = result[:locus-1] + result[locus:]
                    offspring.setGenome(result)

                    if instance.oldGenome == offspring.genome:
                        offspring.colour = instance.colour
                    else:
                        offspring.randomColour()
                    if instance.genome != instance.oldGenome:
                        instance.randomColour()
                    instance.oldGenome = instance.genome[:]

                    if len(instance.genome) > maxSize or len(instance.genome) < minSize:
                        grid[i][j] = None

                    highestAge = 0 # Look for somewhere to put it
                    positionOfOldest = None
                    placed = False
                    for i2 in range(i-1,i+2):
                        for j2 in range(j-1,j+2):
                            if grid[i2%grid_size][j2%grid_size] == None:
                                placed = True # If it's an empty space, put the offspring there
                                grid[i2%grid_size][j2%grid_size] = offspring
                    if not(placed):
                        grid[(i+random.randint(-1,1))%grid_size][(j+random.randint(-1,1))%grid_size] = offspring

paused = False

def interaction():
    global grid, grid_size, gridW, scale, paused
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == 32: # Grow the grid, leaving the original in the bottom left
                for i,row in enumerate(grid):
                    grid[i] += [None] * grid_size
                grid += [[None] * grid_size*2 for i in range(grid_size)]
                grid_size *= 2
                gridW = range(grid_size)
                scale = screensize/grid_size
            if event.key == 120: # Grow the grid by expansion
                for i,row in enumerate(grid):
                    grid[i] = [val for pair in zip(grid[i], [None] * grid_size) for val in pair]
                grid = [val for pair in zip(grid, [[None] * grid_size*2 for i in range(grid_size)]) for val in pair]
                grid_size *= 2
                gridW = range(grid_size)
                scale = screensize/grid_size
            if event.key == 122: # Contract the grid
                grid = grid[::2]
                for i,row in enumerate(grid):
                    grid[i] = grid[i][::2]
                grid_size = len(grid)
                gridW = range(grid_size)
                scale = screensize/grid_size
            if event.key == 112:
                paused = not paused


def main(generations=10000):
    drawFPS=24
    drawClock=time.time()
    updateFPS=1000000
    updateClock=time.time()

    for generation in range(generations):
        interaction()
        if time.time()-updateClock>(1.0/updateFPS):
            if not paused:
                update(generation)
            updateClock=time.time()
        if time.time()-drawClock>(1.0/drawFPS):
            draw()
            drawClock=time.time()

if __name__ == "__main__":
    main()
