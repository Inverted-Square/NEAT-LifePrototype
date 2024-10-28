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
    board.draw(SURFACE)
    total_complexity: int = 0
    for _ in range(ALLOWED_STEPS):
        board.update_generation()
        board.draw(SURFACE)
        total_complexity += board.get_complexity()

    return total_complexity / ALLOWED_STEPS


def set_manual_pattern(board: Board) -> None:
    board.set_cell(100, 100, True)
    board.set_cell(101, 100, True)
    board.set_cell(102, 100, True)
    board.set_cell(101, 99, True)
    board.set_cell(100, 101, True)


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


def main() -> None:
    board: Board = get_starting_board(use_neat=True)
    board_copy: Board = deepcopy(board)
    board.draw(SURFACE)

    running: bool = True
    start_updates: bool = False
    reset_board: bool = False
    while running:
        CLOCK.tick(30)

        for event in pygame.event.get():
            running = not (event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            start_updates = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or start_updates
            reset_board = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN

        if reset_board:
            board = deepcopy(board_copy)
            board.draw(SURFACE)
            start_updates = False

        if start_updates:
            board.update_generation()
            board.draw(SURFACE)

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
