import threading
import tkinter as tk

from gui.update_prices.update_prices_action_handler import (
    UpdatePricesWindowActionHandler
)

from gui.gui_config import (
  SIDEBAR_BG_COLOR,
  TEXT_BOX_BG_COLOR,
  TEXT_BOX_FG_COLOR,
  BUTTON_BG_COLOR,
  BUTTON_SIZE,
  LIST_BOX,
  VERTICAL_SPACE_BETWEEN_BUTTONS
)


# MARK: - Main classes

class UpdatePricesWindowPresenter:
    def __init__(self,
                 root_window,
                 new_prices_info,
                 window_title='Update prices',
                 update_button_text='Update',
                 exit_button_text='Exit'):

        self.root_window = root_window

        self.window_title = window_title
        self.new_prices_info = new_prices_info
        self.new_prices_api_body = self.__get_new_prices_api_body()

        self.window_title = window_title
        self.update_button_text = update_button_text
        self.exit_button_text = exit_button_text

    # MARK: - Public methods

    def start(self):
        self.__init_ui_elements()
        self.__configure_window(self.window_title)
        self.__configure_scroll_bar()
        self.__show_ui()

    # MARK: - Private methods

    def __init_ui_elements(self):
        self.window = tk.Toplevel(self.root_window)
        self.sidebar_frame = tk.Frame(self.window, bg=SIDEBAR_BG_COLOR)

        action_handler = UpdatePricesWindowActionHandler(
            self.new_prices_api_body
        )
        update_button_command = lambda: self.__start_submit_thread(
            action_handler.update_button_tapped
        )
        self.update_button = tk.Button(self.sidebar_frame,
                                      text=self.update_button_text,
                                      command=update_button_command,
                                      width=BUTTON_SIZE['width'],
                                      height=BUTTON_SIZE['height'],
                                      bg=BUTTON_BG_COLOR)

        self.exit_button = tk.Button(self.sidebar_frame,
                                     text=self.exit_button_text,
                                     command=self.window.destroy,
                                     width=BUTTON_SIZE['width'],
                                     height=BUTTON_SIZE['height'],
                                     bg=BUTTON_BG_COLOR)

        self.scroll_bar = tk.Scrollbar(self.window)
        self.list_box = tk.Listbox(self.window,
                                   yscrollcommand=self.scroll_bar.set,
                                   width=LIST_BOX['width'],
                                   height=LIST_BOX['height'],
                                   font=LIST_BOX['font'])

    def __configure_window(self, title):
        self.window.title(title)
        self.window.configure(bg=SIDEBAR_BG_COLOR)
        self.window.resizable(False, False)

    def __configure_scroll_bar(self):
        self.scroll_bar.config(command=self.list_box.yview)

    def __show_ui(self, sidebar_side=tk.LEFT):
        self.sidebar_frame.pack(side=sidebar_side)
        self.update_button.pack(pady=VERTICAL_SPACE_BETWEEN_BUTTONS)
        self.exit_button.pack()

        self.__populate_list_box()
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

    def __populate_list_box(self):
        for new_price_info in self.new_prices_info:
            product_title = new_price_info['product_title']
            product_price = new_price_info['price']
            self.list_box.insert(tk.END, f'{product_title} --- {product_price}')

    def __get_new_prices_api_body(self):
        new_prices_api_body = []

        for new_price_info in self.new_prices_info:
            try:
                # Price should be float or int
                float(new_price_info['price'])
                new_price_api_body = {
                    'product_id': int(new_price_info['product_id']),
                    'price': new_price_info['price']
                }
            except:
                self.new_prices_info.remove(new_price_info)
                continue

            new_prices_api_body.append(new_price_api_body)

        return new_prices_api_body

    # MARK: - Threading

    # TODO: Fix repeating this in MainWindowPresenter
    def __start_submit_thread(self, event):
        self.submit_thread = threading.Thread(target=event)
        self.submit_thread.daemon = True
        self.submit_thread.start()
        self.window.after(20, self.__check_submit_thread)
        self.update_button.configure(state='disable')

    def __check_submit_thread(self):
        if self.submit_thread.is_alive():
            self.window.after(20, self.__check_submit_thread)
        else:
            self.update_button.configure(state='normal')
