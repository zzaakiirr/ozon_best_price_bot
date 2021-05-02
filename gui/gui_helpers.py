import tkinter as tk


CELL_WIDTH = 15
CELL_HEIGHT = 5


def show_table(window, table_height, table_width, data, headers=None):
    first_row = 0

    if headers:
      for column in range(width):
        title = headers[column]
        cell = tk.Label(window, text=title, width=CELL_WIDTH, height=CELL_HEIGHT)
        cell.grid(row=0, column=column)

      first_row += 1

    for row in range(first_row, table_height):
        for column in range(table_width):
            value = data[row][column]
            cell = tk.Label(window, text=value, width=CELL_WIDTH, height=CELL_HEIGHT)
            cell.grid(row=row, column=column)


def show_table(window):
    scrollbar = Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    list_box = Listbox(window, yscrollcommand=scrollbar.set)
    for line in range(100):
       list_box.insert(tk.END, f'{product_title} --- {product_price}')

    list_box.pack(side=tk.LEFT, fill=BOTH)
    scrollbar.config(command=list_box.yview)
