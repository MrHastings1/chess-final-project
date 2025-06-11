from const import *
from square import  Square
from move import  Move
from piece import *
import copy
from  sound import Sound
import os
import pygame

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        initial = move.initial 
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # Console board  move updaate 
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece =  piece 

        # Pawn  Promotion 
        if  isinstance(piece , Pawn):
            # En Passant Capture
            diff = final.col  - initial.col 
            if diff !=  0 and en_passant_empty:
                # Console board  move update 
                self.squares[initial.row][initial.col  +  diff].piece = None
                self.squares[final.row][final.col].piece =  piece 
                if not testing:
                    sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "capture.wav"))
                    sound.play()

            # Pawn Promotion
            else:
                self.check_promotion(piece, final)

        # King Castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook # Checking to see if the king is  going  to the left or the right 
                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True 

        # clear valid moves
        piece.clear_moves()

        # Set Last move 
        self.last_move = move 
    
    def valid_move(self, piece, move):
        return move in  piece.moves 
    
    def check_promotion(self, piece, final):
        if  final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board  = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)

        for row in  range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in  p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
        """ 
          This method calculates all the possible moves for a Piece
        """
        def pawn_moves():
            # Steps 
            steps = 1 if piece.moved else 2 # if  piece.moved(): steps = 1 else steps = 2

            # vertical moves
            start = row + piece.dir 
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # Create a new move
                        move = Move(initial, final)

                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

                    # Blocked
                    else: break
                # Not in Range
                else: break

            # Diagonal Moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in  possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # Create initial and  final Move Squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # Create a new move
                        move = Move(initial, final)
                        
                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

        # En Pessant Moves
        r = 3 if piece.color == "white" else 4
        fr = 2 if piece.color == "white" else 5
        # left en pessant
        if Square.in_range(col-1) and row == r:
            if self.squares[row][col-1].has_enemy_piece(piece.color):
                p = self.squares[row][col-1].piece 
                if isinstance(p, Pawn):
                    if p.en_passant:
                        # Create initial and  final Move Squares
                        initial = Square(row, col)
                        final = Square(fr, col-1, p)
                        # Create a new move
                        move = Move(initial, final)
                        
                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

        # Right en Pessant
        if Square.in_range(col+1) and row == r:
            if self.squares[row][col+1].has_enemy_piece(piece.color):
                p = self.squares[row][col+1].piece 
                if isinstance(p, Pawn):
                    if p.en_passant:
                        # Create initial and  final Move Squares
                        initial = Square(row, col)
                        final = Square(fr, col+1, p)
                        # Create a new move
                        move = Move(initial, final)
                        
                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

        def knight_moves():
            # 8  possible  moves  if Knight is in  the  center 
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]
            for  possible_move in  possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # Createe squares of move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece) # piece = piece 
                        # Create new move 
                        move = Move(initial, final)
                        
                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                            else: break
                        else:
                            # append new move
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr 
                possible_move_row = row + row_incr 
                possible_move_col = col + col_incr 

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # Create squares of the  possiblenew  move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final  = Square(possible_move_row, possible_move_col, final_piece)
                        # Create a possible new move
                        move = Move(initial, final)

                        # Empty = continue  looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #Check Potencial  Checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # Append new Move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

                        # Has Enemy Piece = add  move  + break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            #Check Potencial  Checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # Append new Move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
                            break

                        #  Has Team Piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    
                    # Not in  range
                    else: break

                    # Incrementing  the incrs 
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0), # up
                (row-1, col+1), # up-right
                (row+0, col+1), # right
                (row+1, col+1), # down-right
                (row+1, col+0), # down
                (row+1, col-1), # down-left
                (row+0, col-1), # left
                (row-1, col-1), # up-left
            ]

            # normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) # piece=piece
                        # create new move
                        move = Move(initial, final)
                        #Check Potencial  Checks
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new Move
                                piece.add_move(move)
                            else: break
                        else:
                            # append new move
                            piece.add_move(move)

            # castling moves
            if not piece.moved:
                # queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3:
                                # adds left rook to king
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                movek = Move(initial, final)

                                #Check Potencial  Checks
                                if bool:
                                    if not self.in_check(piece, movek) and not self.in_check(left_rook, moveR):
                                        # append new move to  rook 
                                        left_rook.add_move(moveR)
                                        # Append new Move to  king 
                                        piece.add_move(movek)
                                else:
                                    # append new move to rook
                                    left_rook.add_move(moveR)
                                    # append new move king 
                                    piece.add_move(movek)

                # king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            # castling is not possible because there are pieces in between ?
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6:
                                # adds right rook to king
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                movek = Move(initial, final)
                                
                                #Check Potencial  Checks
                                if bool:
                                    if not self.in_check(piece, movek) and not self.in_check(right_rook, moveR):
                                        # append new move to  rook 
                                        right_rook.add_move(moveR)
                                        # Append new Move to  king 
                                        piece.add_move(movek)
                                else:
                                    # append new move to rook
                                    right_rook.add_move(moveR)
                                    # append new move king 
                                    piece.add_move(movek)
            
        if isinstance(piece, Pawn): pawn_moves()

        elif isinstance(piece, Knight): knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left 
                (1, 1), # down-right
                (1, -1) #down-left
            ])
           
        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0), # up
                (0, 1), # right
                (1, 0), # down
                (0, -1) # left
            ])
            
        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left 
                (1, 1), # down-right
                (1, -1), #down-left
                (-1, 0), # up
                (0, 1), # right 
                (1, 0), # down
                (0, -1) # left
            ])
            
        elif isinstance(piece, King): king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1,  0) # if  color == 'white': row_pawn, row_other = (6, 7) else: row_pawn, row_other = (1,0)

        # These are our Pawns 
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        
        # These are the Knights 
        self.squares[row_other][1] = Square(row_other,  1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # These  are the Bishops 
        self.squares[row_other][2] = Square(row_other,  2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))


        # These are the Rooks 
        self.squares[row_other][0] = Square(row_other,  0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))


        # The  Queen
        self.squares[row_other][3] = Square(row_other,  3, Queen(color))


        # The King
        self.squares[row_other][4] = Square(row_other,  4, King(color))


b = Board()
b._create()