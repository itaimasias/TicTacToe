class TicTacToe:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.next_turn = "X"
        self.winner = None

    def make_move(self, row, col, player):
        if self.winner or self.board[row][col] != "" or player != self.next_turn:
            return False
        self.board[row][col] = player
        if self.check_win(player):
            self.winner = player
        elif self.check_draw():
            self.winner = "draw"
        else:
            self.next_turn = "O" if player == "X" else "X"
        return True

    def check_win(self, player):
        b = self.board
        for i in range(3):
            if all([b[i][j] == player for j in range(3)]) or all([b[j][i] == player for j in range(3)]):
                return True
        if b[0][0] == b[1][1] == b[2][2] == player or b[0][2] == b[1][1] == b[2][0] == player:
            return True
        return False

    def check_draw(self):
        return all(cell for row in self.board for cell in row) and not self.winner
