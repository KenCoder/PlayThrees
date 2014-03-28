import random
import pygame
from pygame.sprite import Sprite
import sys

slide_start = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1) }
LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3

def rotate(x, y, n = 1):
    for i in range(n):
        x, y = 3 - y, x
    return x,y

class Board:
    def __init__(self, s = ""):
        self.cells = []
        for row in range(4):
            self.cells.append([0] * 4)

        row, col = 0,0
        for x in s.split():
            self.cells[row][col] = int(x)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def at(self, row, col):
        return self.cells[row][col]

    def put(self, row, col, v):
        self.cells[row][col] = v

    def rotate(self, n):
        res = Board()
        n = (n + 4) % 4
        for row in range(4):
            for col in range(4):
                r, c = rotate(row, col, n)
                res.cells[r][c] = self.cells[row][col]
        return res

# Returns result board, 'move' board (what you draw), and spaces that are exposed
def slideLeft(board):
    res = Board()
    moveBoard = Board() # -1 for spaces that don't draw
    spaces = []
    for row in range(4):
        # Find a cell that can receive the cell to its right
        src = 0
        for col in range(4):
            if src == 4:
                spaces.append((row, 3))
                a = 0
            else:
                a = board.at(row, col)
            move_piece = a

            if src == col and src < 3:
                b = board.at(row, col+1)
                if b != 0 and (a == 0 or a+b == 3 or (a >= 3 and a == b)):
                    move_piece = b # We move piece b into this slot
                    a += b
                    src += 1
            res.put(row, col, a)
            moveBoard.put(row, col, move_piece if src != col and a != 0 else -1)
            src += 1
    return res, moveBoard, spaces

def gen_package(count):
    items = [1,2,3] * count
    random.shuffle(items)
    return items

class Ranker:
    def __init__(self, empty_desire, highway_desire, bignum_desire, bottomright_desire):
        self.empty_desire = empty_desire
        self.highway_desire = highway_desire
        self.bignum_desire = bignum_desire
        self.bottomright_desire = bottomright_desire

        def rank(self, board):


BIG = 3
TERM1 = [4,4,4,0]
TERM2 = [4,4,4,1]

class GameWatcher:
    def __init__(self):
        self.reset()

    def reset(self):
        self.seen = [0, 0, 0, 0] # Count of what we have seen so far 1-3 or big ignore idx 0

    def update_piece(self, p):
        # Handle case where we were maybe expecting a big number, but didn't get it
        if self.seen == TERM1 and p <= 3:
            self.reset()
        i = max(p - 1, 3)
        self.seen[i] += 1
        if self.seen == TERM2:
            self.reset()
        if sum(self.seen) > 13:
            print "Game did not follow expected distribution - got %s " % self.seen

    def probabilities(self):
        possible = [4 - x for x in self.seen[:3]]
        if self.seen[3]:
            possible.append(0)
        else:
            possible.append(0.5)
        tot = sum(possible)
        return [x / tot for x in possible]

class Game:
    def __init__(self):
        self.board = Board()
        self.package = []

        insert = []
        for row in range(4):
            insert += [(row, col) for col in range(4)]
        random.shuffle(insert)
        for row, col in insert[0:9]:
            self.board.put(row, col, self.pop())

    def peek(self):
        if len(self.package) == 0:
            self.package = gen_package(4)
            random.shuffle(self.package)
        return self.package[0]

    def pop(self):
        self.peek() # Force creation of package
        return self.package.pop(0)

    # Updates self with new board, returns the 'move board' for display
    def move(self, shift):
        tmp = self.board.rotate(shift)
        (tmp, move, spaces) = slideLeft(tmp)
        self.peek()
        if len(spaces) > 0:
            row,col = spaces[random.randint(0,len(spaces)-1)]
            tmp.put(row, col, self.package.pop(0))
        self.board = tmp.rotate(-shift)
        return move.rotate(-shift)

def run_game():
    # Game parameters
    CELL_WIDTH = 100
    CELL_HEIGHT = 150
    BORDER = 5
    TOP_START = 100
    SCREEN_WIDTH, SCREEN_HEIGHT = (5 * BORDER + 4*CELL_WIDTH, 5*BORDER + 4*CELL_HEIGHT + TOP_START)
    PEEK_WIDTH = 30
    PEEK_HEIGHT = 45

    BG_COLOR = 0x46,0xF0,0xE4
    RECT_COLOR = 0x3C,0xC7,0xBD
    FPS = 50
    MOVE_SPEED = 0.25 # seconds
    ONEBG = 0, 128, 0
    TWOBG = 128, 0, 0
    THREEBG = 255,255,255

    pygame.init()
    screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = pygame.time.Clock()
    fonts = [pygame.font.Font(None, x) for x in [144, 120, 60, 50, 40]]
    peek_font = pygame.font.Font(None, 20)

    def piece_colors(v):
        fg = 255,255,255
        if v == 0:
            bg = RECT_COLOR
        elif v == 1:
            bg = ONEBG
        elif v == 2:
            bg = TWOBG
        else:
            bg = THREEBG
            fg = 0,0,0
        return fg, bg

    def draw_peek(piece):
        fg, bg = piece_colors(piece)
        rect = pygame.Rect( (SCREEN_WIDTH - PEEK_WIDTH) / 2, (TOP_START - PEEK_HEIGHT) / 2, PEEK_WIDTH, PEEK_HEIGHT)
        pygame.draw.rect(screen, bg, rect)
        if piece > 3:
            txt = "+"
            text = peek_font.render(txt, 1, fg)
            textpos = text.get_rect()
            textpos.center = rect.center
            screen.blit(text, textpos)

    def draw_board(board, x, y):
        for row in range(4):
           for col in range(4):
               v = board.at(row, col)
               if v != -1:
                   fg, bg = piece_colors(v)
                   rect = pygame.Rect( x + col * (CELL_WIDTH + BORDER) + BORDER, y + row * (CELL_HEIGHT + BORDER) + BORDER, CELL_WIDTH, CELL_HEIGHT)
                   pygame.draw.rect(screen, bg, rect)
                   if v > 0:
                       txt = "%d" % v
                       text = fonts[len(txt)-1].render(txt, 1, fg)
                       textpos = text.get_rect()
                       textpos.center = rect.center
                       screen.blit(text, textpos)

    game = Game()

    baseboard = None
    movingboard = None
    x, y, vx, vy = 0,0,0,0

    while True:
        # Limit frame speed to 50 FPS
        #
        time_passed = clock.tick(FPS)
        shift = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    shift = LEFT
                elif event.key == pygame.K_RIGHT:
                    shift = RIGHT
                elif event.key == pygame.K_UP:
                    shift = UP
                elif event.key == pygame.K_DOWN:
                    shift = DOWN

                if shift is not None:
                    baseboard = game.board
                    movingboard = game.move(shift)
                    x, y = slide_start[shift]
                    x *= CELL_WIDTH
                    y *= CELL_HEIGHT
                    # Take 0.5 seconds to slide. Want pixels per frame
                    vx = -x / (FPS * MOVE_SPEED)
                    vy = -y / (FPS * MOVE_SPEED)

        # Redraw the background
        screen.fill(BG_COLOR)

        if baseboard is not None:
            draw_board(baseboard, 0, TOP_START)
            draw_board(movingboard, x, TOP_START + y)
            if (int(x) == 0 or (x+vx < 0) != (x < 0)) and (int(y) == 0 or (y+vy < 0) != (y < 0)):
                baseboard = None
                movingboard = None
            x += vx
            y += vy
        else:
            draw_board(game.board, 0, TOP_START)
        draw_peek(game.peek())

        pygame.display.flip()


def exit_game():
    sys.exit()


run_game()
