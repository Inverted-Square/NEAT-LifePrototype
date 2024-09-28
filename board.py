from math import ceil, log2, comb

import pygame
from pygame import Surface, SurfaceType


class Board:
    ROWS: int = 175
    COLUMNS: int = 250

    def __init__(self) -> None:
        self.__cells: list[list[bool]] = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        self.__live_cell_positions: list[tuple[int, int]] = []
        self.__dead_cell_neighbours: dict[tuple[int, int], int] = {}

    def set_cell(self, row: int, column: int, state: bool) -> None:
        if not self.__cells[row][column] and state:
            self.__live_cell_positions.append((row, column))
        elif self.__cells[row][column] and not state:
            self.__live_cell_positions.remove((row, column))

        self.__cells[row][column] = state

    def update_generation(self) -> None:
        next_generation: list[list[bool]] = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        next_live_cells: list[tuple[int, int]] = []

        for live_cell in self.__live_cell_positions:
            if self.__cell_stays_live(live_cell[0], live_cell[1]):
                next_generation[live_cell[0]][live_cell[1]] = True
                next_live_cells.append((live_cell[0], live_cell[1]))

        for dead_cell in self.__dead_cell_neighbours:
            if self.__dead_cell_neighbours[dead_cell] == 3:
                next_generation[dead_cell[0]][dead_cell[1]] = True
                next_live_cells.append((dead_cell[0], dead_cell[1]))

        self.__cells = next_generation
        self.__live_cell_positions = next_live_cells
        self.__dead_cell_neighbours.clear()

    def __cell_stays_live(self, row: int, column: int) -> bool:
        live_neighbour_count: int = 0
        directions: list[tuple[int, int]] = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
        directions.remove((0, 0))
        for row_delta, column_delta in directions:
            row_index: int = (row + row_delta) % len(self.__cells)
            column_index: int = (column + column_delta) % len(self.__cells[row_index])
            if self.__cells[row_index][column_index]:
                live_neighbour_count += 1
                continue

            if (row_index, column_index) in self.__dead_cell_neighbours:
                self.__dead_cell_neighbours[(row_index, column_index)] += 1
            else:
                self.__dead_cell_neighbours.update({(row_index, column_index): 1})

        return live_neighbour_count in [2, 3]

    def get_complexity(self) -> int:
        width: int
        height: int
        width, height = self.__get_min_bounding_box_dimensions()
        width_bits: int = Board.__get_min_bits(width)
        height_bits: int = Board.__get_min_bits(height)
        num_live: int = len(self.__live_cell_positions)
        num_live_bits: int = Board.__get_min_bits(num_live)
        alpha: int = width_bits + height_bits + width * height
        beta: int = width_bits + height_bits + num_live_bits + ceil(log2(comb(width * height, num_live)))
        return 1 + min(alpha, beta)

    def __get_min_bounding_box_dimensions(self) -> tuple[int, int]:
        if len(self.__live_cell_positions) == 0:
            return 0, 0

        top_bound: int = 0
        bottom_bound: int = self.ROWS - 1
        left_bound: int = 0
        right_bound: int = self.COLUMNS - 1
        while not any(self.__cells[top_bound]):
            top_bound += 1

        while not any(self.__cells[bottom_bound]):
            bottom_bound -= 1

        while not any([row[left_bound] for row in self.__cells]):
            left_bound += 1

        while not any([row[right_bound] for row in self.__cells]):
            right_bound -= 1

        return right_bound - left_bound + 1, bottom_bound - top_bound + 1

    @staticmethod
    def __get_min_bits(value: int) -> int:
        return 0 if value == 0 else ceil(log2(value + 1) + log2(value)) + 1

    def draw(self, surface: Surface | SurfaceType) -> None:
        surface.fill((40, 40, 40))

        column_width: int = surface.get_width() // self.COLUMNS
        row_height: int = surface.get_height() // self.ROWS
        for row, column in self.__live_cell_positions:
            x_pos: float = column_width * (column + 0.5)
            y_pos: float = row_height * (row + 0.5)
            if self.__cells[row][column]:
                pygame.draw.circle(surface, (200, 200, 200), (x_pos, y_pos), column_width // 2)
