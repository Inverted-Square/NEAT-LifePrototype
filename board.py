import pygame
from pygame import Surface, SurfaceType


class Board:
    ROWS: int = 100  # ensure this is a factor of the pygame surface height
    COLUMNS: int = 100  # ensure this is a factor of the pygame surface width

    def __init__(self) -> None:
        self.__cells: list[list[bool]] = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def set_cell(self, row: int, column: int, state: bool) -> None:
        self.__cells[row][column] = state

    def update_generation(self) -> None:
        next_generation: list[list[bool]] = [[False for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        for row_index, row in enumerate(self.__cells):
            for column_index, cell in enumerate(row):
                self.__set_next_generation_at(next_generation, row_index, column_index, cell)

        self.__cells = next_generation

    def __set_next_generation_at(self, next_generation: list[list[bool]], row_index: int, column_index: int, current_state: bool) -> None:
        live_neighbour_count: int = self.get_live_neighbour_count(row_index, column_index)
        if live_neighbour_count == 3 and not current_state:
            next_generation[row_index][column_index] = True
        elif live_neighbour_count not in [2, 3] and current_state:
            next_generation[row_index][column_index] = False
        else:
            next_generation[row_index][column_index] = current_state

    def get_live_neighbour_count(self, row_index: int, column_index: int) -> int:
        live_neighbour_count: int = 0
        directions: list[tuple[int, int]] = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1]]
        directions.remove((0, 0))
        for row_delta, column_delta in directions:
            if self.__cells[(row_index + row_delta) % len(self.__cells)][(column_index + column_delta) % len(self.__cells)]:
                live_neighbour_count += 1

        return live_neighbour_count


    def draw(self, surface: Surface | SurfaceType) -> None:
        surface.fill((40, 40, 40))

        column_width: int = surface.get_width() // self.COLUMNS
        row_height: int = surface.get_height() // self.ROWS
        for i, row in enumerate(self.__cells):
            y_pos: float = row_height * (i + 0.5)
            for j, cell in enumerate(row):
                x_pos: float = column_width * (j + 0.5)
                Board.__draw_cell(surface, x_pos, y_pos, column_width // 2, cell)

    @staticmethod
    def __draw_cell(surface: Surface | SurfaceType, x_pos: float, y_pos: float, radius: int, cell: bool) -> None:
        if cell:
            pygame.draw.circle(surface, (200, 200, 200), (x_pos, y_pos), radius)
