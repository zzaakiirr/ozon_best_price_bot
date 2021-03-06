import sys
import threading
import tkinter as tk

import gui.gui_helpers as gui_helpers
from gui.main.main_window_action_handler import MainWindowActionHandler

from gui.gui_config import (
  SIDEBAR_BG_COLOR,
  TEXT_BOX_BG_COLOR,
  TEXT_BOX_FG_COLOR,
  BUTTON_BG_COLOR,
  BUTTON_FG_COLOR,
  START_ROW_LABEL_FG_COLOR,
  START_ROW_ENTRY,
  PRICE_TAG_CLASS_ROW_LABEL_FG_COLOR,
  PRICE_TAG_CLASS_ROW_ENTRY,
  BUTTON_SIZE,
  VERTICAL_SPACE_BETWEEN_BUTTONS,
  INF_MODE_FILE,
  INF_MODE_GIF_FRAMES_COUNT,
)


# MARK: - Main classes

class MainWindowPresenter:

    # MARK: - Init

    def __init__(self,
                 window_title='OzonBot',
                 start_button_text='Start',
                 infinite_mode_text='Infinite mode',
                 start_row_label_text='Start from row:',
                 best_price_tag_attrs_label_text='Price tag class:',
                 best_price_tag_row_entry_text='span,_i_J',
                 get_new_prices_button_text='Get new prices',
                 exit_button_text='Exit'):

        self.window_title = window_title
        self.start_button_text = start_button_text
        self.infinite_mode_text = infinite_mode_text
        self.start_row_label_text = start_row_label_text
        self.best_price_tag_attrs_label_text = best_price_tag_attrs_label_text
        self.best_price_tag_row_entry_text = best_price_tag_row_entry_text
        self.get_new_prices_button_text = get_new_prices_button_text
        self.exit_button_text = exit_button_text

    # MARK: - Public methods

    def start(self):
        self.__init_ui_elements()
        self.__configure_window(self.window_title)
        self.__pack_widgets()
        self.__configure_infinite_mode_gif()
        self.window.mainloop()

    # MARK: - Private methods

    def __init_ui_elements(self):
        self.window = tk.Tk()
        self.sidebar_frame = tk.Frame(self.window, bg=SIDEBAR_BG_COLOR)
        self.infinite_mode_wrapper = tk.Frame(
            self.sidebar_frame,
            bg=SIDEBAR_BG_COLOR
        )
        self.start_row_wrapper = tk.Frame(
            self.sidebar_frame,
            bg=SIDEBAR_BG_COLOR
        )
        self.best_price_tag_attrs_row_wrapper = tk.Frame(
            self.sidebar_frame,
            bg=SIDEBAR_BG_COLOR
        )
        self.buttons_wrapper = tk.Frame(
            self.sidebar_frame,
            bg=SIDEBAR_BG_COLOR
        )
        self.text_box = tk.Text(
            master=self.window,
            state='disabled',
            bg=TEXT_BOX_BG_COLOR,
            fg=TEXT_BOX_FG_COLOR
        )

        sys.stdout = StdoutRedirector(self.text_box)
        self.action_handler = MainWindowActionHandler(self.window)

        self.infinite_mode = tk.IntVar()
        self.infinite_mode_checkbox = tk.Checkbutton(
            self.infinite_mode_wrapper,
            text = self.infinite_mode_text,
            variable=self.infinite_mode,
            bg=SIDEBAR_BG_COLOR
        )
        self.infinite_mode_label = tk.Label(
            self.infinite_mode_wrapper,
            bg=SIDEBAR_BG_COLOR
        )
        self.infinite_mode_gif_frames = [
            tk.PhotoImage(file=INF_MODE_FILE, format=f'gif -index {frame}')
            for frame in range(INF_MODE_GIF_FRAMES_COUNT)
        ]

        self.start_row_label = tk.Label(
            self.start_row_wrapper,
            text=self.start_row_label_text,
            bg=SIDEBAR_BG_COLOR,
            fg=START_ROW_LABEL_FG_COLOR
        )
        start_row_entry_var = tk.StringVar(
            self.start_row_wrapper,
            # FIXME: SOLID principle!
            value=self.action_handler.sheet_redactor.start_index,
        )
        self.start_row_entry = tk.Entry(
            self.start_row_wrapper,
            textvariable=start_row_entry_var,
            width=START_ROW_ENTRY['width'],
            bg=START_ROW_ENTRY['bg_color'],
            fg=START_ROW_ENTRY['fg_color']
        )

        self.best_price_tag_attrs_row_label = tk.Label(
            self.best_price_tag_attrs_row_wrapper,
            text=self.best_price_tag_attrs_label_text,
            bg=SIDEBAR_BG_COLOR,
            fg=PRICE_TAG_CLASS_ROW_LABEL_FG_COLOR
        )
        best_price_tag_attrs_row_entry_var = tk.StringVar(
            self.best_price_tag_attrs_row_wrapper,
            # FIXME: SOLID principle!
            value=self.action_handler.target_tag_attrs,
        )
        self.best_price_tag_attrs_row_entry = tk.Entry(
            self.best_price_tag_attrs_row_wrapper,
            textvariable=best_price_tag_attrs_row_entry_var,
            width=PRICE_TAG_CLASS_ROW_ENTRY['width'],
            bg=PRICE_TAG_CLASS_ROW_ENTRY['bg_color'],
            fg=PRICE_TAG_CLASS_ROW_ENTRY['fg_color']
        )

        start_button_command = lambda: self.__start_submit_thread(
            lambda: self.action_handler.start_button_tapped(
                self.best_price_tag_attrs_row_entry.get(),
                self.start_row_entry.get(),
                self.infinite_mode.get()
            )
        )
        self.start_button = tk.Button(
            self.buttons_wrapper,
            text=self.start_button_text,
            command=start_button_command,
            width=BUTTON_SIZE['width'],
            height=BUTTON_SIZE['height'],
            bg=BUTTON_BG_COLOR,
            fg=BUTTON_FG_COLOR
        )

        get_new_prices_button_command = lambda: self.__start_submit_thread(
            self.action_handler.get_new_prices_button_tapped
        )
        self.get_new_prices_button = tk.Button(
            self.buttons_wrapper,
            text=self.get_new_prices_button_text,
            command=get_new_prices_button_command,
            width=BUTTON_SIZE['width'],
            height=BUTTON_SIZE['height'],
            bg=BUTTON_BG_COLOR,
            fg=BUTTON_FG_COLOR
        )

        self.exit_button = tk.Button(
            self.buttons_wrapper,
            text=self.exit_button_text,
            command=self.action_handler.on_exit,
            width=BUTTON_SIZE['width'],
            height=BUTTON_SIZE['height'],
            bg=BUTTON_BG_COLOR,
            fg=BUTTON_FG_COLOR
        )

    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', self.action_handler.on_exit)

    def __configure_infinite_mode_gif(self):
        self.infinite_mode_wrapper.after(
            0, gui_helpers.update_frames, 0,
            self.infinite_mode_gif_frames,
            self.infinite_mode_label,
            self.infinite_mode_wrapper,
        )

    # MARK: - Packing

    def __pack_widgets(self):
        self.__pack_base_elements()
        self.__pack_infinite_mode_element()
        self.__pack_start_row_elements()
        self.__pack_best_price_tag_attrs_row_elements()
        self.__pack_buttons()

    def __pack_base_elements(self, sidebar_side=tk.LEFT, text_side=tk.RIGHT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.text_box.pack(side=text_side)

    def __pack_infinite_mode_element(self):
        self.infinite_mode_wrapper.pack()
        self.infinite_mode_label.pack()
        self.infinite_mode_checkbox.pack()

    def __pack_start_row_elements(self):
        self.start_row_wrapper.pack()
        self.start_row_label.pack(side=tk.LEFT)
        self.start_row_entry.pack()

    def __pack_best_price_tag_attrs_row_elements(self):
        self.best_price_tag_attrs_row_wrapper.pack()
        self.best_price_tag_attrs_row_label.pack(side=tk.LEFT)
        self.best_price_tag_attrs_row_entry.pack()

    def __pack_buttons(self):
        self.buttons_wrapper.pack()
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
