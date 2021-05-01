import sys
import threading
import tkinter as tk

import main


SIDEBAR_BG_COLOR = '#323232'
TEXT_BOX_BG_COLOR = '#1E1E1E'
TEXT_BOX_FG_COLOR = '#FFFFFF'
BUTTON_BG_COLOR = '#909090'

BUTTON_SIZE = {
    'width': 15,
    'height': 3
}

VERTICAL_SPACE_BETWEEN_BUTTONS = 5


class GuiPresenter:

    # MARK: - Init

    def __init__(self, title='OzonBot', start_button_text='Start', exit_button_text='Exit'):
        self.window = tk.Tk()
        self.__configure_window(title)

        self.sidebar_frame = tk.Frame(bg=SIDEBAR_BG_COLOR)

        self.text_box = tk.Text(master=self.window,
                                state='disabled',
                                bg=TEXT_BOX_BG_COLOR,
                                fg=TEXT_BOX_FG_COLOR)

        sys.stdout = StdoutRedirector(self.text_box)

        self.start_button = tk.Button(self.sidebar_frame,
                                      text=start_button_text,
                                      command=lambda:self.__start_submit_thread(),
                                      width=BUTTON_SIZE['width'],
                                      height=BUTTON_SIZE['height'],
                                      bg=BUTTON_BG_COLOR)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=exit_button_text,
                                     command=self.window.destroy,
                                     width=BUTTON_SIZE['width'],
                                     height=BUTTON_SIZE['height'],
                                     bg=BUTTON_BG_COLOR)

    # MARK: - Public methods

    def start(self):
        self.__pack_widgets()
        self.window.mainloop()

    # MARK: - Private methods

    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)

    def __pack_widgets(self, sidebar_side=tk.LEFT, text_side=tk.RIGHT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.text_box.pack(side=text_side)
        self.start_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)
        self.exit_button.pack()

    # MARK: - Threading

    def __start_submit_thread(self):
        self.submit_thread = threading.Thread(target=main.submit)
        self.submit_thread.daemon = True
        self.submit_thread.start()
        self.window.after(20, self.__check_submit_thread)
        self.start_button.configure(state='disable')

    def __check_submit_thread(self):
        if self.submit_thread.is_alive():
            self.window.after(20, self.__check_submit_thread)
        else:
            self.start_button.configure(state='normal')


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.configure(state='normal')
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)
        self.text_space.configure(state='disable')

    def flush(self):
        pass


if __name__ == '__main__':
    gui_presenter = GuiPresenter()
    gui_presenter.start()
