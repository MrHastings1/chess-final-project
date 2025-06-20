import  pygame 

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

class Game:

    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()
        self.next_player = "white"
        self.hovered_sqr = None 
        self.config = Config()

    # Blitz Methods

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                #  Color 
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark # if (row + col) % 2 == 0:  color = (234, 235, 200) # Light green else: color = (119, 154, 88) # dark green
                # rect 
                rect  = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                #blit
                pygame.draw.rect(surface, color, rect)

                # row  coordinates
                if  col == 0:
                    #color  
                    color = theme.bg.dark if row %  2 == 0  else theme.bg.light 
                    # Label 
                    lbl= self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit  
                    surface.blit(lbl, lbl_pos)

                # col coordinates 
                if  row == 7:
                    #color  
                    color = theme.bg.dark if (row + col) % 2 == 0  else theme.bg.light 
                    # Label 
                    lbl= self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit  
                    surface.blit(lbl, lbl_pos)


    def show_pieces(self, surface):
        for row in range(ROWS):
            for col  in range(COLS):
                #Piece ? 
                if self.board.squares[row][col].has_piece():
                  piece = self.board.squares[row][col].piece

                  # All piece except for the one we are dragging 
                  if piece is  not self.dragger.piece:
                    piece.set_texture(size=80)
                    img = pygame.image.load(piece.texture)
                    img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                    piece.texture_rect = img.get_rect(center=img_center) 
                    surface.blit(img, piece.texture_rect) 

    def show_moves(self, surface):
        theme = self.config.theme 

        if self.dragger.dragging:
            piece = self.dragger.piece 

            # loop all valid moves
            for move in piece.moves:
                # Color 
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect 
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit 
                pygame.draw.rect(surface, color, rect)
    
    def show_last_move(self, surface):
        theme  = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final 

            for pos in [initial, final]:
                # Color 
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark 
                # Rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # Blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # Color 
            color = (180, 180, 180)
            # Rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # Blit
            pygame.draw.rect(surface, color, rect, width=3)

    # Other Methods 

    def next_turn(self):
        self.next_player = 'white' if  self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

