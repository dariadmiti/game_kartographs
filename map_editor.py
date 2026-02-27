import tkinter as tk
from PIL import Image, ImageTk

GRID_SIZE = 11
CELL_SIZE = 48
OFFSET = 30
COINS_TOTAL = 14
COIN_SIZE = 24

TEXTURES = {
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


class MapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Editor - Cartographers Style")

        self.images = {}
        for name, path in TEXTURES.items():
            img = Image.open(path).resize((CELL_SIZE, CELL_SIZE), Image.NEAREST)
            self.images[name] = ImageTk.PhotoImage(img)

        self.current_texture = "grass"

        canvas_width = GRID_SIZE * CELL_SIZE + OFFSET
        canvas_height = GRID_SIZE * CELL_SIZE + OFFSET + COIN_SIZE + 10
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#ddd")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        self.map_data = [["empty" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.coins = [True for _ in range(COINS_TOTAL)]

        self.create_texture_panel()
        self.create_score_panel()

        self.apply_preset_one(redraw=False)
        self.redraw()

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
            self.redraw()

    def apply_preset_two(self, redraw=True):
        mountains = [(10, 2), (4, 4), (7, 6), (3, 9), (10, 9)]
        caves = [(2, 2), (2, 3), (10, 6), (11, 6), (10, 7), (1, 10), (2, 10)]
        self.clear_map()
        self.set_cells(mountains, "mountain")
        self.set_cells(caves, "cave")
        if redraw:
            self.redraw()

    def create_texture_panel(self):
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=1, sticky="n")

        tk.Label(frame, text="Choose board:").grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Board 1", command=self.apply_preset_one, width=10).grid(
            row=1, column=0, padx=5, pady=5
        )
        tk.Button(frame, text="Board 2", command=self.apply_preset_two, width=10).grid(
            row=1, column=1, padx=5, pady=5
        )

        tk.Label(frame, text="Choose texture:").grid(row=2, column=0, columnspan=2, pady=5)

        for index, tex in enumerate(TEXTURES.keys()):
            row = (index // 2) + 3
            col = index % 2
            b = tk.Button(
                frame,
                text=tex,
                image=self.images[tex],
                compound="top",
                width=80,
                height=80,
                command=lambda t=tex: self.set_texture(t),
            )
            b.grid(row=row, column=col, padx=5, pady=5)

    def create_score_panel(self):
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=2, sticky="n", padx=10)

        tk.Label(frame, text="Points", font=("Arial", 12, "bold")).pack(pady=5)

        self.score_entries = []

        for season in ["Spring", "Summer", "Autumn", "Winter"]:
            cat_frame = tk.Frame(frame, bd=2, relief="groove", padx=5, pady=5)
            cat_frame.pack(pady=5)

            tk.Label(cat_frame, text=season).grid(row=0, column=0, columnspan=4)

            row_entries = []
            for i in range(4):
                e = tk.Entry(cat_frame, width=3, justify="center")
                e.grid(row=1, column=i, padx=2, pady=2)
                e.bind("<KeyRelease>", lambda event: self.update_total_score())
                row_entries.append(e)
            self.score_entries.append(row_entries)

        tk.Label(frame, text="Total:", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        self.total_entry = tk.Entry(frame, width=6, justify="center", state="readonly")
        self.total_entry.pack(pady=(0, 5))

    def update_total_score(self):
        total = 0
        for row in self.score_entries:
            for entry in row:
                try:
                    val = int(entry.get())
                except ValueError:
                    val = 0
                total += val

        self.total_entry.config(state="normal")
        self.total_entry.delete(0, tk.END)
        self.total_entry.insert(0, str(total))
        self.total_entry.config(state="readonly")

    def set_texture(self, tex_name):
        self.current_texture = tex_name

    def on_click(self, event):
        x = (event.x - OFFSET) // CELL_SIZE
        y = (event.y - OFFSET) // CELL_SIZE

        coins_start_y = OFFSET + GRID_SIZE * CELL_SIZE + 5
        coins_start_x = OFFSET
        for i in range(COINS_TOTAL):
            cx1 = coins_start_x + i * (COIN_SIZE + 5)
            cy1 = coins_start_y
            cx2 = cx1 + COIN_SIZE
            cy2 = cy1 + COIN_SIZE
            if cx1 <= event.x <= cx2 and cy1 <= event.y <= cy2:
                self.coins[i] = not self.coins[i]
                self.redraw()
                return

        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.map_data[y][x] = self.current_texture
            self.redraw()

    def redraw(self):
        self.canvas.delete("all")

        for x in range(GRID_SIZE):
            self.canvas.create_text(
                OFFSET + x * CELL_SIZE + CELL_SIZE / 2,
                OFFSET / 2,
                text=str(x + 1),
                font=("Arial", 10, "bold"),
            )

        for y in range(GRID_SIZE):
            self.canvas.create_text(
                OFFSET / 2,
                OFFSET + y * CELL_SIZE + CELL_SIZE / 2,
                text=str(y + 1),
                font=("Arial", 10, "bold"),
            )

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tex = self.map_data[y][x]
                self.canvas.create_image(
                    OFFSET + x * CELL_SIZE,
                    OFFSET + y * CELL_SIZE,
                    anchor="nw",
                    image=self.images[tex],
                )

        for i in range(GRID_SIZE + 1):
            self.canvas.create_line(
                OFFSET,
                OFFSET + i * CELL_SIZE,
                OFFSET + GRID_SIZE * CELL_SIZE,
                OFFSET + i * CELL_SIZE,
            )
            self.canvas.create_line(
                OFFSET + i * CELL_SIZE,
                OFFSET,
                OFFSET + i * CELL_SIZE,
                OFFSET + GRID_SIZE * CELL_SIZE,
            )

        coins_start_y = OFFSET + GRID_SIZE * CELL_SIZE + 5
        coins_start_x = OFFSET
        for i, active in enumerate(self.coins):
            x1 = coins_start_x + i * (COIN_SIZE + 5)
            y1 = coins_start_y
            x2 = x1 + COIN_SIZE
            y2 = y1 + COIN_SIZE
            color = "gold" if active else "gray"
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")
            if not active:
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
                self.canvas.create_line(x1, y2, x2, y1, fill="red", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = MapEditor(root)
    root.mainloop()
