import sys
import threading
import tkinter as tk

import gui.main.main_window_action_handler as main_window_action_handler

from gui.gui_config import (
  SIDEBAR_BG_COLOR,
  TEXT_BOX_BG_COLOR,
  TEXT_BOX_FG_COLOR,
  BUTTON_BG_COLOR,
  BUTTON_SIZE,
  VERTICAL_SPACE_BETWEEN_BUTTONS
)


# MARK: - Main classes

class MainWindowPresenter:

    # MARK: - Init

    def __init__(self,
                 window_title='OzonBot',
                 start_button_text='Start',
                 get_new_prices_button_text='Get new prices',
                 exit_button_text='Exit'): 

        self.window_title = window_title
        self.start_button_text = start_button_text
        self.get_new_prices_button_text = get_new_prices_button_text
        self.exit_button_text = exit_button_text

    # MARK: - Public methods

    def start(self):
        self.__init_ui_elements()
        self.__configure_window(self.window_title)
        self.__pack_widgets()
        self.window.mainloop()

    # MARK: - Private methods

    def __init_ui_elements(self):
        self.window = tk.Tk()
        self.sidebar_frame = tk.Frame(self.window, bg=SIDEBAR_BG_COLOR)
        self.text_box = tk.Text(master=self.window,
                                state='disabled',
                                bg=TEXT_BOX_BG_COLOR,
                                fg=TEXT_BOX_FG_COLOR)

        sys.stdout = StdoutRedirector(self.text_box)
        action_handler = main_window_action_handler.MainWindowActionHandler(self.window)

        start_button_command = lambda: self.__start_submit_thread(
            action_handler.start_button_tapped
        )
        self.start_button = tk.Button(self.sidebar_frame,
                                      text=self.start_button_text,
                                      command=start_button_command,
                                      width=BUTTON_SIZE['width'],
                                      height=BUTTON_SIZE['height'],
                                      bg=BUTTON_BG_COLOR)

        get_new_prices_button_command = lambda: self.__start_submit_thread(
            action_handler.get_new_prices_button_tapped
        )
        self.get_new_prices_button = tk.Button(self.sidebar_frame,
                                               text=self.get_new_prices_button_text,
                                               command=get_new_prices_button_command,
                                               width=BUTTON_SIZE['width'],
                                               height=BUTTON_SIZE['height'],
                                               bg=BUTTON_BG_COLOR)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=self.exit_button_text,
                                     command=self.window.destroy,
                                     width=BUTTON_SIZE['width'],
                                     height=BUTTON_SIZE['height'],
                                     bg=BUTTON_BG_COLOR)

    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)

    def __pack_widgets(self, sidebar_side=tk.LEFT, text_side=tk.RIGHT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.text_box.pack(side=text_side)
        self.start_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)
        self.get_new_prices_button.pack()
        self.exit_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)

    # MARK: - Threading

    def __start_submit_thread(self, event):
        self.submit_thread = threading.Thread(target=event)
        self.submit_thread.daemon = True
        self.submit_thread.start()
        self.window.after(20, self.__check_submit_thread)
        self.get_new_prices_button.configure(state='disable')
        self.start_button.configure(state='disable')

    def __check_submit_thread(self):
        if self.submit_thread.is_alive():
            self.window.after(20, self.__check_submit_thread)
        else:
            self.get_new_prices_button.configure(state='normal')
            self.start_button.configure(state='normal')


# MARK: - Helpers

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
