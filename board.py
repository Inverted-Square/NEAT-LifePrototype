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

    def draw(self, surface: Surface | SurfaceType) -> None:
        surface.fill((40, 40, 40))

        column_width: int = surface.get_width() // self.COLUMNS
        row_height: int = surface.get_height() // self.ROWS
        for row, column in self.__live_cell_positions:
            x_pos: float = column_width * (column + 0.5)
            y_pos: float = row_height * (row + 0.5)
            if self.__cells[row][column]:
                pygame.draw.circle(surface, (200, 200, 200), (x_pos, y_pos), column_width // 2)
