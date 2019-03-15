import random
import sys
import pygame

from pygame.locals import *
FPS = 20
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8
BOXSIZE = 40
GAPSIZE = 10
BOARDWIDTH = 10
BOARDHEIGHT = 7

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOUR = NAVYBLUE
LIGHTBGCOLOUR = GRAY
BOXCOLOUR = WHITE
HIGHLIGHTCOLOUR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLOURS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLOURS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT


def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    mousex = 0
    mousey = 0
    pygame.display.set_caption('memorypuzzle')

    mainBoard = random.getstate
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None

    DISPLAYSURF.fill(BGCOLOUR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOUR)
        drawBoard(mainBoard, revealedBoxes)

        for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key ==
                                           K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey)
        if boxx is not None and boxy is not None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])

                if firstSelection is None:
                    firstSelection = (boxx, boxy)
                else:
                    icon1shape, icon1colour = getShapeAndColour(mainBoard,
                                                                firstSelection[0], firstSelection[1])
                    icon2shape, icon2colour = getShapeAndColour(mainBoard,
                                                               boxx, boxy)
                    if icon1shape != icon2shape or icon1colour != icon2colour:
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        mainBoard = random.getstate
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes

def getRanomizedBoard():
        icons = []
        for colour in ALLCOLOURS:
            for shape in ALLSHAPES:
                icons.append( (shape, colour) )

        random.shuffle(icons)
        numIconsUsed = int(BOARDWIDTH * BOARDHEIGHT / 2)
        icons = icons[:numIconsUsed] * 2
        random.shuffle(icons)


        board = []
        for x in range(BOARDWIDTH):
            column = []
            for y in range(BOARDHEIGHT):
                column.append(icons[0])
                del  icons[0]
            board.append(column)
        return board


def splitIntoGroupsOf(groupSize, theList):
     result = []
     for i in range(0, len(theList), groupSize):
         result.append(theList[i:i + groupSize])
         return result


def leftTopCoordsOfBox(boxx, boxy):  # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)




def drawIcon(shape, colour, boxx, boxy):
    quarter = int(BOXSIZE * 0.25)  # syntactic sugar
    half = int(BOXSIZE * 0.5)  # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy)

    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, colour, (left + half, top + half),
                           half - 5)
        pygame.draw.circle(DISPLAYSURF, BGCOLOUR, (left + half, top + half),
                           quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, colour, (left + quarter, top +
quarter, BOXSIZE - half, BOXSIZE - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, colour, ((left + half, top),
                                                  (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1), (left, top +half)))
    elif shape == LINES:
        for i in range(0, BOXSIZE, 4):
            pygame.draw.line(DISPLAYSURF, colour, (left, top + i), (left +
                                                                    i, top))
            pygame.draw.line(DISPLAYSURF, colour, (left + i, top + BOXSIZE -
                                                   1), (left + BOXSIZE - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, colour, (left, top + quarter,
                                                  BOXSIZE, half))


def getShapeAndColour(board, boxx, boxy):
        return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, BGCOLOUR, (left, top, BOXSIZE, BOXSIZE))
        shape, colour = getShapeAndColour(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])

        if coverage > 0:  # only draw the cover if there is an coverage

            pygame.draw.rect(DISPLAYSURF, BOXCOLOUR, (left, top, coverage, BOXSIZE))

    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):  # Do "box reveal" animation.
    for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, - REVEALSPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):  # Do the "box cover" animation.
    for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
            drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
             # Draw a covered box.
                pygame.draw.rect(DISPLAYSURF, BOXCOLOUR, (left, top,
                                                 BOXSIZE, BOXSIZE))
            else:
                shape, colour = getShapeAndColour(board, boxx, boxy)
                drawIcon(shape, colour, boxx, boxy)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOUR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)


def startGameAnimation(board):  # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append((x, y))
        random.shuffle(boxes)
        boxGroups = splitIntoGroupsOf(8, boxes)

        drawBoard(board, coveredBoxes)
        for boxGroup in boxGroups:
            revealBoxesAnimation(board, boxGroup)
            coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    coveredBoxes = generateRevealedBoxesData(True)
    colour1 = LIGHTBGCOLOUR
    colour2 = BGCOLOUR

    for i in range(13):
        colour1, colour2 = colour2, colour1  # swap colors
        DISPLAYSURF.fill(colour1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False  # return False if any boxes are covered.
    return True


if __name__ == '__main__':
    main()
