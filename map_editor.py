import base64
from pathlib import Path

import flet as ft

GRID_SIZE = 11
CELL_SIZE = 48
COINS_TOTAL = 14

TEXTURE_FILES = {
    "empty": "textures/empty.png",
    "mountain": "textures/mountain.png",
    "cave": "textures/cave.png",
    "grass": "textures/grass.png",
    "forest": "textures/forest.png",
    "water": "textures/water.png",
    "house": "textures/house.png",
    "hero": "textures/hero.png",
    "star": "textures/star.png",
    "cross": "textures/cross.png",
    "monster": "textures/monster.png",
}


class MapEditorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Map Editor - Cartographers Style (Flet)"
        self.page.padding = 16
        self.page.scroll = ft.ScrollMode.ADAPTIVE

        self.current_texture = "grass"
        self.map_data = [["empty" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.coins = [True for _ in range(COINS_TOTAL)]
        self.texture_src = self.load_texture_sources()

        self.cells = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.coin_controls = []
        self.score_fields = []
        self.total_field = ft.TextField(label="Total", width=120, read_only=True, value="0")
        self.current_texture_text = ft.Text(value=f"Current: {self.current_texture}")

        self.apply_preset_one(redraw=False)
        self.build_ui()
        self.refresh_board()
        self.refresh_coins()

    def load_texture_sources(self):
        sources = {}
        base_dir = Path(__file__).resolve().parent

        for tex_name, relative_path in TEXTURE_FILES.items():
            file_path = base_dir / relative_path
            if file_path.exists():
                raw = file_path.read_bytes()
                b64 = base64.b64encode(raw).decode("ascii")
                sources[tex_name] = f"data:image/png;base64,{b64}"
            else:
                sources[tex_name] = ""

        return sources

    def build_ui(self):
        board_column = ft.Column(spacing=2)

        header = [
            ft.Container(width=32, height=32)
        ] + [
            ft.Container(
                width=CELL_SIZE,
                height=32,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(str(i + 1), weight=ft.FontWeight.BOLD),
            )
            for i in range(GRID_SIZE)
        ]
        board_column.controls.append(ft.Row(controls=header, spacing=2))

        for y in range(GRID_SIZE):
            row_controls = [
                ft.Container(
                    width=32,
                    height=CELL_SIZE,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(str(y + 1), weight=ft.FontWeight.BOLD),
                )
            ]

            for x in range(GRID_SIZE):
                cell = ft.Container(
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    border=ft.Border.all(1, ft.Colors.BLACK_54),
                    padding=0,
                    on_click=lambda e, cx=x, cy=y: self.on_cell_click(cx, cy),
                )
                self.cells[y][x] = cell
                row_controls.append(cell)

            board_column.controls.append(ft.Row(controls=row_controls, spacing=2))

        coins_row = ft.Row(spacing=6, wrap=True)
        for i in range(COINS_TOTAL):
            coin = ft.Container(
                width=28,
                height=28,
                border_radius=999,
                border=ft.Border.all(1, ft.Colors.BLACK),
                alignment=ft.Alignment.CENTER,
                on_click=lambda e, idx=i: self.toggle_coin(idx),
            )
            self.coin_controls.append(coin)
            coins_row.controls.append(coin)

        board_panel = ft.Column(
            controls=[
                board_column,
                ft.Container(height=8),
                ft.Text("Coins", weight=ft.FontWeight.BOLD),
                coins_row,
            ],
            spacing=4,
        )

        texture_buttons = []
        for tex_name in TEXTURE_FILES.keys():
            texture_buttons.append(
                ft.Container(
                    width=96,
                    content=ft.ElevatedButton(
                        on_click=lambda e, t=tex_name: self.set_texture(t),
                        content=ft.Column(
                            controls=[
                                ft.Image(src=self.texture_src[tex_name], width=44, height=44, fit=ft.BoxFit.CONTAIN),
                                ft.Text(tex_name, size=8),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                        ),
                    ),
                )
            )

        texture_panel = ft.Column(
            controls=[
                ft.Text("Board", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Board 1", on_click=lambda e: self.apply_preset_one()),
                        ft.ElevatedButton("Board 2", on_click=lambda e: self.apply_preset_two()),
                    ],
                    wrap=True,
                ),
                ft.Divider(),
                ft.Text("Choose texture", size=16, weight=ft.FontWeight.BOLD),
                self.current_texture_text,
                ft.Row(controls=texture_buttons, wrap=True, spacing=8, run_spacing=8),
            ],
            width=430,
            spacing=8,
        )

        score_panel = ft.Column(
            controls=[
                ft.Text("Points", size=18, weight=ft.FontWeight.BOLD),
                self.build_score_section("Spring"),
                self.build_score_section("Summer"),
                self.build_score_section("Autumn"),
                self.build_score_section("Winter"),
                self.total_field,
            ],
            width=280,
            spacing=10,
        )

        layout = ft.ResponsiveRow(
            controls=[
                ft.Container(content=board_panel, col={"xs": 12, "lg": 5}),
                ft.Container(content=texture_panel, col={"xs": 12, "lg": 4}),
                ft.Container(content=score_panel, col={"xs": 12, "lg": 3}),
            ],
            spacing=16,
            run_spacing=16,
        )

        self.page.add(layout)

    def build_score_section(self, title: str) -> ft.Container:
        fields = []
        row_controls = []

        for _ in range(4):
            field = ft.TextField(width=52, text_align=ft.TextAlign.CENTER, on_change=self.update_total_score)
            fields.append(field)
            row_controls.append(field)

        self.score_fields.append(fields)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, weight=ft.FontWeight.W_600),
                    ft.Row(controls=row_controls, spacing=6),
                ],
                spacing=6,
            ),
            border=ft.Border.all(1, ft.Colors.BLACK_26),
            border_radius=8,
            padding=8,
        )

    def clear_map(self):
        self.map_data = [["empty" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def set_cells(self, coords, texture):
        for x, y in coords:
            self.map_data[y - 1][x - 1] = texture

    def apply_preset_one(self, redraw=True):
        mountains = [(2, 2), (9, 4), (4, 6), (6, 10), (10, 9)]
        self.clear_map()
        self.set_cells(mountains, "mountain")
        if redraw:
            self.refresh_board()
            self.page.update()

    def apply_preset_two(self, redraw=True):
        mountains = [(10, 2), (4, 4), (7, 6), (3, 9), (10, 9)]
        caves = [(2, 2), (2, 3), (10, 6), (11, 6), (10, 7), (1, 10), (2, 10)]
        self.clear_map()
        self.set_cells(mountains, "mountain")
        self.set_cells(caves, "cave")
        if redraw:
            self.refresh_board()
            self.page.update()

    def set_texture(self, tex_name: str):
        self.current_texture = tex_name
        self.current_texture_text.value = f"Current: {tex_name}"
        self.page.update()

    def on_cell_click(self, x: int, y: int):
        self.map_data[y][x] = self.current_texture
        self.update_single_cell(x, y)
        self.page.update()

    def update_single_cell(self, x: int, y: int):
        texture_name = self.map_data[y][x]
        self.cells[y][x].content = ft.Image(
            src=self.texture_src[texture_name],
            fit=ft.BoxFit.COVER,
            width=CELL_SIZE,
            height=CELL_SIZE,
        )

    def refresh_board(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.update_single_cell(x, y)

    def toggle_coin(self, idx: int):
        self.coins[idx] = not self.coins[idx]
        self.refresh_coins()
        self.page.update()

    def refresh_coins(self):
        for i, coin in enumerate(self.coin_controls):
            is_active = self.coins[i]
            coin.bgcolor = ft.Colors.AMBER if is_active else ft.Colors.GREY_400
            coin.content = ft.Text("" if is_active else "X", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)

    def update_total_score(self, e=None):
        total = 0
        for row in self.score_fields:
            for field in row:
                try:
                    total += int(field.value or "0")
                except ValueError:
                    pass

        self.total_field.value = str(total)
        self.page.update()


def main(page: ft.Page):
    MapEditorApp(page)


if __name__ == "__main__":
    ft.run(main, assets_dir=".")
