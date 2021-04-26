import tkinter as tk
import sys

import main


class GuiPresenter:

    # MARK: - Init

    def __init__(self, start_button_text='Start', exit_button_text = 'Exit'):
        self.window = tk.Tk()
        self.sidebar_frame = tk.Frame()

        self.text_box = tk.Text(master=self.window)
        sys.stdout = StdoutRedirector(self.text_box)

        self.start_button = tk.Button(self.sidebar_frame,
                                      text=start_button_text,
                                      command=main.main)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=exit_button_text,
                                     command=self.window.destroy)

    # MARK: - Public methods

    def start(self):
        self.__pack_widgets()
        self.window.mainloop()

    # MARK: - Private methods

    def __pack_widgets(self, sidebar_side=tk.LEFT, text_side=tk.RIGHT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.text_box.pack(side=text_side)
        self.start_button.pack()
        self.exit_button.pack()


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)

    def flush(self):
        pass


if __name__ == '__main__':
    gui_presenter = GuiPresenter()
    gui_presenter.start()
