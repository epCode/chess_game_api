import pygame
import sys, time
from multiprocessing import Process
import chess.engine
import asyncio



global to_play
to_play = "w"

from stockfish import Stockfish
stockfish = Stockfish(path="/usr/bin/stockfish")
# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 8
SQUARE_SIZE = WIDTH // GRID_SIZE
WTIME,BTIME = 10, 10

# Colors
WHITE = (200, 200, 250)
BLACK = (120, 120, 200)

# Initialize pygame
pygame.init()

PIECES = {}

def round_nearest(x,num=75):
    return int(round(float(x)/num)*num)


def san_to_coords(move):

    # Define the starting and ending ranks and files as integers
    start_ranks = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }
    start_files = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }




    # Convert the starting and ending ranks and files to integers
    start_rank = start_ranks[move[1]]
    start_file = start_files[move[0]]
    end_rank = start_ranks[move[3]]
    end_file = start_files[move[2]]

    # Return the x,y coordinates of the move as a list of lists
    return [[start_file, start_rank], [end_file, end_rank]]



def board_to_fen(chess_board):
    fen = ""
    empty_count = 0
    for rank in chess_board:
        for cell in rank:
            if cell == '':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                fen += cell
        if empty_count > 0:
            fen += str(empty_count)
            empty_count = 0
        if rank != chess_board[-1]:
            fen += '/'
    return fen


# Create the chess board
global chess_board

chess_board = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
]

global threats_board
threats_board = []
global dot_board
dot_board = []

def reset_dots():
    global dot_board
    dot_board = [
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
    ]
reset_dots()
def reset_threats():
    global threats_board
    threats_board = [
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
    ]
reset_threats()

global selected_piece
selected_piece = None

def update_threats():
    reset_threats()
    global threats_board
    y = -1
    for row in chess_board:
        y += 1
        x = -1
        for p in row:
            x += 1
            if p != '':
                for move in get_legal_moves(PIECES[p.lower()], x, y, True):
                    if threats_board[move[1]][move[0]] != '' and threats_board[move[1]][move[0]] != get_color(p):
                        threats_board[move[1]][move[0]] = '&'
                    else:
                        threats_board[move[1]][move[0]] = get_color(p)



def move_piece(y1, x1, y, x):
    global chess_board
    if x1 < 8 and y1 < 8 and x < 8 and y < 8 and x1 > -1 and y1 > -1 and x > -1 and y > -1:

        selected_piece = None


        orpiece = chess_board[y1][x1]
        if orpiece == '' or (x1==x and y1==y):
            return
        if not [x, y] in get_legal_moves(PIECES[chess_board[y1][x1].lower()], x1, y1):
            return
        reset_dots()
        chess_board[y1][x1] = ''
        leftover = chess_board[y][x]
        chess_board[y][x] = orpiece
        #update_threats()


        after_move()
        if leftover != '':
            return leftover
        else:
            return True

def after_move():
    global to_play
    if to_play == "w":
        to_play = "b"
    else:
        to_play = "w"

# Set up the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))



pygame.display.set_caption("Chess Board API")


# Function to register a piece and its movement type
def register_piece(l, properties):
    tex = properties["img"]
    wprops = properties
    wprops["img"] = pygame.image.load("textures/"+tex+"_w.png")
    wprops["imgb"] = pygame.image.load("textures/"+tex+"_b.png")
    PIECES[l.lower()] = wprops


register_piece("p", {
    "img": "pawn",
    "movef":[[0,1], [0,1], [-1,1,False,True], [1,1,False,True]],
    "attacf":True
})
register_piece("n", {
    "img": "knight",
    "movef": [
        [1,2],
        [-1,2],
        [2,1],
        [2,-1],
        [1,-2],
        [-1,-2],
        [-2,1],
        [-2,-1]
    ]
})
register_piece("b", {
    "img": "bishop",
    "movef":[
        [1,1,True],
        [-1,-1,True],
        [1,-1,True],
        [-1,1,True],
    ]
})
register_piece("r", {
    "img": "rook",
    "movef":[
        [1,0,True],
        [-1,0,True],
        [0,-1,True],
        [0,1,True],
    ]

})
register_piece("q", {
    "img": "queen",
    "movef":[
        [1,1,True],
        [-1,-1,True],
        [1,-1,True],
        [-1,1,True],
        [1,0,True],
        [-1,0,True],
        [0,-1,True],
        [0,1,True],
    ]

})
register_piece("k", {
    "img": "king",
    "movef":[
        [1,1],
        [-1,-1],
        [1,-1],
        [-1,1],
        [1,0],
        [-1,0],
        [0,-1],
        [0,1],
    ]
})


# Function to draw the chess board
def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

dragged_piece = None





dotimg = pygame.image.load("textures/dot.png")
circleimg = pygame.image.load("textures/circle.png")
redimg = pygame.image.load("textures/red.png")
yelimg = pygame.image.load("textures/yellow.png")

# Function to draw the pieces on the board
def draw_pieces():
    rowix = -1
    for row in range(GRID_SIZE):
        rowix+=1
        colix = -1
        for col in range(GRID_SIZE):
            colix+=1
            piece = chess_board[row][col]
            dot = dot_board[row][col]
            threat = threats_board[row][col]

            img = redimg
            if threat == '&':
                img = yelimg


            img = pygame.transform.scale(img, (75,75))
            imgrec = img.get_rect()
            imgrec.center = (colix*75+37.5,rowix*75+37.5)
            if threat != '':
                screen.blit(img, imgrec)

            if piece:
                myimage = {}
                if piece.lower() == piece:
                    myimage = PIECES[piece.lower()]["imgb"]
                else:
                    myimage = PIECES[piece.lower()]["img"]

                myimage = pygame.transform.scale(myimage, (65,65))
                imagerect = myimage.get_rect()

                imagerect.center = (colix*75+37.5,rowix*75+37)
                if dragged_piece:
                    if dragged_piece[1] == rowix and dragged_piece[0] == colix:
                        x, y = pygame.mouse.get_pos()
                        imagerect.center = (x, y)


                screen.blit(myimage, imagerect)
            img = dotimg
            if dot == "o":
                img = circleimg

            img = pygame.transform.scale(img, (75,75))
            imgrec = dotimg.get_rect()
            imgrec.center = (colix*75+9,rowix*75+9)
            if dot != '':
                screen.blit(img, imgrec)

def get_color(l):
    if l != '':
        if l.lower() == l:
            return "b"
        else:
            return "w"

def get_legal_moves(piece_type, x, y, attac=False):
    moves = []

    pawn = chess_board[y][x].lower() == "p"
    king = chess_board[y][x].lower() == "k"

    color = get_color(chess_board[y][x])
    winvert = 1
    if color == "b":
        winvert = -1
    final_mtype = None
    rng = 1
    if pawn and (y == 6 or y == 1) and chess_board[y-winvert][x].lower() == '':
        piece_type["movef"][1] = [0,2]
    for mtype in piece_type["movef"]:
        if 0 <= 2 < len(mtype) and mtype[2]:
            rng = 20
        for i in range(rng):
            nx, ny = x+(mtype[0]*winvert*(i+1)), y-(mtype[1]*winvert*(i+1))
            if 0 <= nx < 8 and 0 <= ny < 8:
                if get_color(chess_board[ny][nx]) == color:
                    break
                if get_color(chess_board[ny][nx]) != None:
                    if not "attacf" in piece_type or "attacf" in piece_type and len(mtype)>3 and mtype[3]:
                        moves.append([nx,ny])
                    break
                if not (len(mtype)>3 and mtype[3]):
                    moves.append([nx,ny])



    if pawn:
        piece_type["movef"][1] = [0,1]

    return moves

def stockfish_play():
    stockfish.set_fen_position(f"{board_to_fen(chess_board)} b - 0 2")
    stfmove = san_to_coords(stockfish.get_best_move(wtime=WTIME*1000, btime=BTIME*1000))
    move_piece(stfmove[0][1], stfmove[0][0], stfmove[1][1], stfmove[1][0])



# Main game loop
while True:


    screen.fill(WHITE)
    draw_board()
    draw_pieces()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if not dragged_piece and event.type == pygame.MOUSEBUTTONDOWN:

            x,y = event.pos
            x = round(round_nearest(x-37.5)/75)
            y = round(round_nearest(y-37.5)/75)
            if event.button == 1 and get_color(chess_board[y][x]) == to_play: # 1 == left button
                if selected_piece and move_piece(selected_piece[1], selected_piece[0], y, x):
                    pass
                else:
                    dragged_piece = [x, y]
                    if chess_board[y][x] != '':
                        reset_dots()
                        selected_piece = [x,y]
                        for pos in get_legal_moves(PIECES[chess_board[y][x].lower()], x, y):
                            if chess_board[pos[1]][pos[0]] != '':
                                dot_board[pos[1]][pos[0]] = 'o'
                            else:
                                dot_board[pos[1]][pos[0]] = '.'
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragged_piece:
                x,y = event.pos
                x = round(round_nearest(x-37.5)/75)
                y = round(round_nearest(y-37.5)/75)

                if move_piece(dragged_piece[1], dragged_piece[0], y, x):
                    pass


                dragged_piece = None



    pygame.display.flip()
    pygame.time.Clock().tick(60)

async def analyze_position(fen_position):
    transport, engine = await chess.engine.popen_uci("path/to/stockfish") # Replace "path/to/stockfish" with the path to your Stockfish executable

    async with engine.analysis() as analysis:
        board = chess.Board(fen_position)
        analysis.add_board(board)

        async for info in analysis:
            print(info.get("score"), info.get("pv"))

    await engine.quit()

async def main():
    fen_position = board_to_fen(chess_board)
    await analyze_position(fen_position)

if __name__ == "__main__":
    asyncio.run(main())
