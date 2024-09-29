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
        grid_percent_pop: float = board.get_total_live() / (20 * 20) * 100
        output: list[float] = net.activate((row, column, grid_percent_pop))
        if output[0] > 0.5:
            board.set_cell(row + 90, column + 90, True)


def run_starting_pattern(board: Board) -> int:
    board.draw(SURFACE)
    max_complexity: int = board.get_complexity()
    current_complexity: int = max_complexity
    for _ in range(100):
        board.update_generation()
        board.draw(SURFACE)
        current_complexity = board.get_complexity()
        if current_complexity > max_complexity:
            max_complexity = current_complexity

    return max_complexity * current_complexity


def main() -> None:
    local_dir: str = os.path.dirname(__file__)
    config_path: str = os.path.join(local_dir, "neat_config.txt")
    config: Config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                 neat.DefaultStagnation, config_path)
    population: Population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats: StatisticsReporter = neat.StatisticsReporter()
    population.add_reporter(stats)
    winner: object | None = population.run(eval_genomes, 25)
    print(f"\nBest genome:\n{winner}")
    winner_net: FeedForwardNetwork = neat.nn.FeedForwardNetwork.create(winner, config)

    board: Board = Board()
    set_pattern_using_net(board, winner_net)
    board_copy: Board = deepcopy(board)
    board.draw(SURFACE)

    running: bool = True
    start_updates: bool = False
    reset_board: bool = False
    while running:
        CLOCK.tick(60)

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
    GRID_POSITIONS: list[tuple[int, int]] = [(row, column) for row in range(20) for column in range(20)]
    WIDTH: int = 800
    HEIGHT: int = 800
    SURFACE: Surface | SurfaceType = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NEAT Life")
    CLOCK: Clock = pygame.time.Clock()

    main()
