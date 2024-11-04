import os
from copy import deepcopy

import neat
import pygame
from neat import Population, StatisticsReporter, Config, DefaultGenome
from neat.nn import FeedForwardNetwork
from pygame import Surface, SurfaceType
from pygame.time import Clock

from board import Board


def eval_genomes(genomes: list[tuple[int, DefaultGenome]], config: Config) -> None:
    for genome_id, genome in genomes:
        genome.fitness = 0
        net: FeedForwardNetwork = neat.nn.FeedForwardNetwork.create(genome, config)
        board: Board = Board()
        set_pattern_using_net(board, net)
        genome.fitness = run_starting_pattern(board)


def set_pattern_using_net(board: Board, net: FeedForwardNetwork) -> None:
    for row, column in GRID_POSITIONS:
        board_cells: list[bool] = board.get_cells_range(START_OFFSET, START_END, START_OFFSET, START_END)
        net_inputs: tuple = tuple([row, column] + board_cells)
        output: list[float] = net.activate(net_inputs)
        if output[0] > 0:
            board.set_cell(row + START_OFFSET, column + START_OFFSET, True)


def run_starting_pattern(board: Board) -> float:
    board.draw(SURFACE, [0, 0, Board.COLUMNS, Board.ROWS])
    total_complexity: int = 0
    for _ in range(ALLOWED_STEPS):
        board.update_generation()
        board.draw(SURFACE, [0, 0, Board.COLUMNS, Board.ROWS])
        total_complexity += board.get_complexity()

    return total_complexity / ALLOWED_STEPS


def set_manual_pattern(board: Board) -> None:
    board.set_cell(25, 25, True)
    board.set_cell(26, 25, True)
    board.set_cell(27, 25, True)
    board.set_cell(26, 24, True)
    board.set_cell(25, 26, True)


def get_starting_board(use_neat: bool = False) -> Board:
    board: Board = Board()

    if use_neat:
        local_dir: str = os.path.dirname(__file__)
        config_path: str = os.path.join(local_dir, "neat_config.txt")
        config: Config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                     neat.DefaultStagnation, config_path)
        population: Population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats: StatisticsReporter = neat.StatisticsReporter()
        population.add_reporter(stats)
        winner: object | None = population.run(eval_genomes, 20)
        print(f"\nBest genome:\n{winner}")
        winner_net: FeedForwardNetwork = neat.nn.FeedForwardNetwork.create(winner, config)

        set_pattern_using_net(board, winner_net)
    else:
        set_manual_pattern(board)

    return board


def zoom_view(view_attributes: list[int], scroll: int) -> list[int]:
    top: int = view_attributes[0]
    left: int = view_attributes[1]
    bottom: int = view_attributes[2]
    right: int = view_attributes[3]

    top, bottom = (0, bottom - scroll) if top + scroll < 0 else (top + scroll, bottom)
    left, right = (0, right - scroll) if left + scroll < 0 else (left + scroll, right)
    bottom, top = (Board.ROWS, top + scroll) if bottom - scroll > Board.ROWS else (bottom - scroll, top)
    right, left = (Board.COLUMNS, left + scroll) if right - scroll > Board.COLUMNS else (right - scroll, left)
    view_width: int = right - left
    view_height: int = bottom - top
    if not 2 <= view_width <= Board.COLUMNS or not 2 <= view_height <= Board.ROWS:
        return view_attributes

    return [top, left, bottom, right]


def move_view(cond: bool, board: Board, attributes: list[int], indices: tuple[int, int], diff: int) -> None:
    if cond:
        attributes[indices[0]] = attributes[indices[0]] + diff
        attributes[indices[1]] = attributes[indices[1]] + diff
        board.draw(SURFACE, attributes)


def do_scroll(mouse_scroll: int, view_attributes: list[int], board: Board) -> tuple[int, list[int]]:
    if mouse_scroll != 0:
        view_attributes = zoom_view(view_attributes, mouse_scroll)
        view_attributes = zoom_view(view_attributes, mouse_scroll)
        view_attributes = zoom_view(view_attributes, mouse_scroll)
        view_attributes = zoom_view(view_attributes, mouse_scroll)
        board.draw(SURFACE, view_attributes)

    return 0, view_attributes


def main() -> None:
    view_attributes: list[int] = [0, 0, Board.ROWS, Board.COLUMNS]  # top, left, bottom, right
    board: Board = get_starting_board(use_neat=False)
    board_copy: Board = deepcopy(board)
    board.draw(SURFACE, view_attributes)

    running: bool = True
    start_updates: bool = False
    reset_board: bool = False
    mouse_scroll: int = 0
    move_up: bool = False
    move_down: bool = False
    move_left: bool = False
    move_right: bool = False
    while running:
        CLOCK.tick(30)

        for event in pygame.event.get():
            running = not (event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            start_updates = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or start_updates
            reset_board = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            move_up = event.type == pygame.KEYDOWN and event.key == pygame.K_UP
            move_down = event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN
            move_left = event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT
            move_right = event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT
            mouse_scroll = event.y if event.type == pygame.MOUSEWHEEL else 0

        move_view(move_up and view_attributes[0] - 1 >= 0, board, view_attributes, (0, 2), -1)
        move_view(move_down and view_attributes[2] + 1 <= Board.ROWS, board, view_attributes, (0, 2), 1)
        move_view(move_left and view_attributes[1] - 1 >= 0, board, view_attributes, (1, 3), -1)
        move_view(move_right and view_attributes[3] + 1 <= Board.COLUMNS, board, view_attributes, (1, 3), 1)
        mouse_scroll, view_attributes = do_scroll(mouse_scroll, view_attributes, board)

        if reset_board:
            board = deepcopy(board_copy)
            board.draw(SURFACE, view_attributes)
            start_updates = False
            reset_board = False

        if start_updates:
            board.update_generation()
            board.draw(SURFACE, view_attributes)

    pygame.quit()


if __name__ == "__main__":
    START_SIZE: int = 9  # make sure to update the num_inputs parameter in the config file to be START_SIZE^2 + 2
    START_OFFSET: int = Board.ROWS // 2 - START_SIZE // 2
    START_END: int = START_OFFSET + START_SIZE  # because confusing names are funny
    GRID_POSITIONS: list[tuple[int, int]] = [(row, column) for row in range(START_SIZE) for column in range(START_SIZE)]
    ALLOWED_STEPS: int = 100
    WIDTH: int = 800
    HEIGHT: int = 800
    SURFACE: Surface | SurfaceType = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NEAT Life")
    CLOCK: Clock = pygame.time.Clock()

    main()
