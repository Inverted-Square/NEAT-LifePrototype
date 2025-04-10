from math import ceil, log2, comb

import pygame
from pygame import Surface, SurfaceType


class Board:
    ROWS: int = 200
    COLUMNS: int = 200

    def __init__(self) -> None:
        self.__cells: list[list[bool]] = [[False for _ in range(Board.COLUMNS)] for _ in range(Board.ROWS)]
        self.__live_cell_positions: list[tuple[int, int]] = []
        self.__dead_cell_neighbours: dict[tuple[int, int], int] = {}
        # self.__cell_periodicity: list[list[int]] = [[0 for _ in range(Board.COLUMNS)] for _ in range(Board.ROWS)]
        self.__cell_activities: dict[tuple[int, int], int] = {}

    def set_cell(self, row: int, column: int, state: bool) -> None:
        if not self.__cells[row][column] and state:
            self.__live_cell_positions.append((row, column))
        elif self.__cells[row][column] and not state:
            self.__live_cell_positions.remove((row, column))

        self.__cells[row][column] = state

    def get_cells_range(self, start_row: int, end_row: int, start_column: int, end_column: int) -> list[bool]:
        cells_1d = []
        for row in self.__cells[start_row:end_row]:
            cells_1d += row[start_column:end_column]

        return cells_1d

    def get_total_live(self) -> int:
        return len(self.__live_cell_positions)

    def get_average_activity(self) -> float:
        activities: list[int] = list(self.__cell_activities.values())
        return 0 if len(activities) == 0 else sum(activities) / len(activities)

    def update_generation(self) -> None:
        next_generation: list[list[bool]] = [[False for _ in range(Board.COLUMNS)] for _ in range(Board.ROWS)]
        next_live_cells: list[tuple[int, int]] = []

        for live_cell in self.__live_cell_positions:
            if self.__cell_stays_live(live_cell[0], live_cell[1]):
                next_generation[live_cell[0]][live_cell[1]] = True
                next_live_cells.append((live_cell[0], live_cell[1]))
                self.__update_activity(live_cell, -1)
            else:
                self.__update_activity(live_cell, 0, set_activity=True)

        for dead_cell in self.__dead_cell_neighbours:
            if self.__dead_cell_neighbours[dead_cell] == 3:
                next_generation[dead_cell[0]][dead_cell[1]] = True
                next_live_cells.append((dead_cell[0], dead_cell[1]))
                self.__update_activity(dead_cell, 50)
            else:
                self.__update_activity(dead_cell, 0, set_activity=True)

        self.__cells = next_generation
        self.__live_cell_positions = next_live_cells
        self.__dead_cell_neighbours.clear()

    def __update_activity(self, row_column: tuple[int, int], activity: int, set_activity: bool = False) -> None:
        if row_column in self.__cell_activities:
            if set_activity:
                self.__cell_activities[row_column] = activity
            else:
                self.__cell_activities[row_column] += activity
        else:
            self.__cell_activities.update({row_column: activity})

        if self.__cell_activities[row_column] <= 0:
            self.__cell_activities.pop(row_column)

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
        if not self.__live_cell_positions:
            return 0, 0

        top_bound: int = 0
        bottom_bound: int = Board.ROWS - 1
        left_bound: int = 0
        right_bound: int = Board.COLUMNS - 1
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

    def draw(self, surface: Surface | SurfaceType, view_attributes: list[int]) -> None:
        surface.fill((40, 40, 40))

        view_top: int = view_attributes[0]
        view_left: int = view_attributes[1]
        view_bottom: int = view_attributes[2]
        view_right: int = view_attributes[3]
        column_width: float = surface.get_width() / (view_right - view_left)
        row_height: float = surface.get_height() / (view_bottom - view_top)
        for row, column in self.__live_cell_positions:
            if self.__cells[row][column] and view_top <= row <= view_bottom and view_left <= column <= view_right:
                x_pos: float = column_width * (column - view_left + 0.5)
                y_pos: float = row_height * (row - view_top + 0.5)
                pygame.draw.rect(surface, (200, 200, 200), (column_width * column, row_height * row, column_width, row_height))

        pygame.display.update()
