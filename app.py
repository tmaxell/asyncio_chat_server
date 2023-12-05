import asyncio
import os
import tkinter as tk
import tkinter.filedialog as tkfd
from typing import IO, Any


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Чат')
        self.resizable(True, True)
        self.is_open = True
        self.client: Any = None

        self.configure(bg='#F1F1F1')

        self.__init_chat_rooms()

    def __init_chat_rooms(self):
        def __join_room(room_name: str) -> None:
            if not room_name:
                return

            self.client.username = username.get()
            asyncio.create_task(self.client.send(
                {'username': self.client.username, 'room': room_name}))

            for widget in self.grid_slaves():
                widget.grid_forget()
                widget.destroy()

            self.__init_room()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        tk.Label(self, text='Имя пользователя', bg='#F1F1F1', padx=10, pady=10, font=('Consolas', 12)).grid(row=0, column=0, sticky='w')
        username = tk.Entry(self, font=('Consolas', 12))
        username.insert(0, 'User')
        username.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text='Войти в чат', bg='#F1F1F1', padx=10, pady=10, font=('Consolas', 14, 'bold')).grid(row=1, column=0, columnspan=2, sticky='w')
        self.available_rooms = tk.Listbox(self, font=('Consolas', 12))
        self.available_rooms.bind(
            '<<ListboxSelect>>', lambda event: __join_room(event.widget.get(0)))
        self.available_rooms.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ns')

        tk.Label(self, text='Создать новый чат', bg='#F1F1F1', padx=10, pady=10, font=('Consolas', 14, 'bold')).grid(
            row=3, column=0, columnspan=2, sticky='w')
        new_room = tk.Entry(self, font=('Consolas', 12))
        new_room.bind(
            '<Return>', lambda event: __join_room(event.widget.get()))
        new_room.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    def __init_room(self):
        def __send(message: str) -> None:
            if not message:
                return

            asyncio.create_task(self.client.send({'text': message}))
            input_text.delete(0, 'end')
            self.history.insert(tk.END, f'Вы > {message}')
            self.history.yview(tk.END)

        def __send_file(file: IO | None) -> None:
            if not file:
                return

            if file.readable():

                file_name = file.name
                base_name = os.path.basename(file_name)

                asyncio.create_task(self.client.send(
                    {'file_name': base_name, 'file_content': file.read()}))
            file.close()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.history = tk.Listbox(self, bg='white', font=('Arial', 12), selectbackground='#D5D5D5', selectforeground='black')  # Изменение цвета списка сообщений
        self.history.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.history.yview)
        scrollbar.grid(row=0, column=1, sticky='ns', pady=10)

        self.history.config(yscrollcommand=scrollbar.set)

        input_text = tk.Entry(self, font=('Arial', 12))
        input_text.bind('<Return>', lambda event: __send(event.widget.get()))
        input_text.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        button_frame = tk.Frame(self, bg='#F1F1F1')  # Создание фрейма для кнопок
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        send_file_button = tk.Button(button_frame, text='Отправить файл', command=lambda: __send_file(
            tkfd.askopenfile()), bg='#0070C0', fg='white',
                                     font=('Consolas', 12, 'bold'))

        send_file_button.pack(side=tk.LEFT, padx=5)

        send_button = tk.Button(button_frame, text='Отправить', command=lambda: __send(input_text.get()), bg='#0070C0',
                                fg='white', font=('Consolas', 12, 'bold'))
        send_button.pack(side=tk.LEFT, padx=5)

    def destroy(self) -> None:
        super().destroy()
        self.is_open = False

    def update(self) -> None:
        super().update()
        self.update_idletasks()

    async def start_event_loop(self):
        while self.is_open:
            self.update()
            await asyncio.sleep(0.05)
