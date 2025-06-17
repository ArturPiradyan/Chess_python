import pygame

WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8

class ImageProvider:
    def get_image(self, piece):
        raise NotImplementedError("Subclasses must implement get_image.")

class PieceAssetsAdapter(ImageProvider):
    def __init__(self):
        self.images = {}
        self.load_images()

    def load_images(self):
        pieces = ['p', 'r', 'n', 'b', 'q', 'k']
        colors = ['w', 'b']
        for color in colors:
            for piece in pieces:
                name = f"{color}_{piece}"
                self.images[name] = pygame.transform.scale(
                    pygame.image.load(f"assets/{name}.png"), (SQ_SIZE, SQ_SIZE))

    def get_image(self, piece):
        return self.images.get(str(piece))

class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def get_legal_moves(self, board, x, y):
        return []

    def __str__(self):
        return f"{self.color}_{self.symbol}"

class King(Piece):
    symbol = 'k'
    def get_legal_moves(self, board, x, y):
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))
        return moves

class Queen(Piece):
    symbol = 'q'
    def get_legal_moves(self, board, x, y):
        return Rook(self.color).get_legal_moves(board, x, y) + \
               Bishop(self.color).get_legal_moves(board, x, y)

class Rook(Piece):
    symbol = 'r'
    def get_legal_moves(self, board, x, y):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None:
                    moves.append((nx, ny))
                elif target.color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Bishop(Piece):
    symbol = 'b'
    def get_legal_moves(self, board, x, y):
        moves = []
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None:
                    moves.append((nx, ny))
                elif target.color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Knight(Piece):
    symbol = 'n'
    def get_legal_moves(self, board, x, y):
        moves = []
        for dx, dy in [(-2, -1), (-1, -2), (1, -2), (2, -1),
                       (2, 1), (1, 2), (-1, 2), (-2, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves

class Pawn(Piece):
    symbol = 'p'
    def get_legal_moves(self, board, x, y):
        moves = []
        dir = 1 if self.color == 'w' else -1
        start_row = 6 if self.color == 'w' else 1
        if board[y - dir][x] is None:
            moves.append((x, y - dir))
            if y == start_row and board[y - 2*dir][x] is None:
                moves.append((x, y - 2*dir))
        for dx in [-1, 1]:
            nx = x + dx
            ny = y - dir
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target and target.color != self.color:
                    moves.append((nx, ny))
        return moves

class BoardRenderer:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets

    def draw_board(self):
        colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def draw_highlights(self, screen, moves):
        for (x, y) in moves:
            rect = pygame.Rect(x*SQ_SIZE, (7 - y)*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, (0, 255, 0, 80), rect, 5)

    def draw_pieces(self, board):
        for y in range(8):
            for x in range(8):
                piece = board[y][x]
                if piece:
                    img = self.assets.get_image(piece)
                    if img:
                        self.screen.blit(img, pygame.Rect(x*SQ_SIZE, (7 - y)*SQ_SIZE, SQ_SIZE, SQ_SIZE))

class Board:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Board, cls).__new__(cls)
            cls._instance.grid = [[None for _ in range(8)] for _ in range(8)]
            cls._instance.init_pieces()
        return cls._instance

    def init_pieces(self):
        B = self.grid
        for i in range(8):
            B[1][i] = Pawn('b')
            B[6][i] = Pawn('w')
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(order):
            B[0][i] = cls('b')
            B[7][i] = cls('w')


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Custom Chess")
        self.clock = pygame.time.Clock()

        self.assets = PieceAssetsAdapter()
        self.renderer = BoardRenderer(self.screen, self.assets)

        self.selected = None
        self.turn = 'w'
        self.highlight_moves = []

    def get_valid_moves(self, x, y):
        piece = Board().grid[y][x]
        if piece is None or piece.color != self.turn:
            return []
        return piece.get_legal_moves(Board().grid, x, y)

    def run(self):
        running = True
        while running:
            self.renderer.draw_board()
            self.renderer.draw_pieces(Board().grid)
            self.renderer.draw_highlights(self.screen, self.highlight_moves)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    bx, by = x // SQ_SIZE, 7 - (y // SQ_SIZE)
                    clicked = Board().grid[by][bx]

                    if self.selected:
                        from_x, from_y = self.selected
                        piece = Board().grid[from_y][from_x]
                        if piece and piece.color == self.turn:
                            if (bx, by) in self.highlight_moves:
                                Board().grid[by][bx] = piece
                                Board().grid[from_y][from_x] = None
                                self.turn = 'b' if self.turn == 'w' else 'w'
                        self.selected = None
                        self.highlight_moves = []
                    elif clicked and clicked.color == self.turn:
                        self.selected = (bx, by)
                        self.highlight_moves = self.get_valid_moves(bx, by)
            self.clock.tick(30)
        pygame.quit()

class GameManager:
    _instance = None

    @staticmethod
    def get_instance():
        if GameManager._instance is None:
            GameManager()
        return GameManager._instance

    def __init__(self):
        if GameManager._instance is not None:
            raise Exception("This class is a singleton!")
        GameManager._instance = self

        self.current_turn = "white"
        self.game_over = False

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def get_turn(self):
        return self.current_turn

    def is_game_over(self):
        return self.game_over

    def end_game(self):
        self.game_over = True

if __name__ == "__main__":
    Game().run()
