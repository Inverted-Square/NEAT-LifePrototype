from random import getrandbits

import pygame
from pygame import Surface, SurfaceType

from board import Board


def main() -> None:
    board: Board = Board()
    # board.set_cell(40, 40, True)
    # board.set_cell(39, 40, True)
    # board.set_cell(41, 40, True)
    # board.set_cell(40, 39, True)
    # board.set_cell(39, 41, True)

    # board.set_cell(40, 40, True)
    # board.set_cell(40, 41, True)
    # board.set_cell(40, 42, True)
    # board.set_cell(41, 42, True)
    # board.set_cell(42, 42, True)
    # board.set_cell(42, 41, True)
    # board.set_cell(42, 40, True)

    # board.set_cell(40, 40, True)
    # board.set_cell(40, 41, True)
    # board.set_cell(40, 42, True)
    # board.set_cell(39, 42, True)
    # board.set_cell(38, 41, True)

    for row in range(Board.ROWS):
        for column in range(Board.COLUMNS):
            board.set_cell(row, column, bool(getrandbits(1)))

    print(board.get_complexity())
    board.draw(SURFACE)

    running: bool = True
    while running:
        for event in pygame.event.get():
            running = not (event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

        board.update_generation()
        print(board.get_complexity())
        board.draw(SURFACE)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    WIDTH: int = 1000
    HEIGHT: int = 700
    SURFACE: Surface | SurfaceType = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NEAT Life")

    main()
