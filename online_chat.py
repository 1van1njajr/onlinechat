from customtkinter import *
from PIL import Image
from socket import *
from threading import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("Online Chat")


        self.menu_frame = CTkFrame(self, width = 60, height = 300, fg_color="pink")
        self.menu_frame.pack_propagate(0)
        self.menu_frame.place(x = 0, y = 0)

        self.is_show_menu = False

        self.on_off_menu = CTkButton(self, text = ">", width = 70,command=self.menu_flag, fg_color="pink", text_color="purple",hover_color="pink", corner_radius = 0)
        self.on_off_menu.place(x = 0, y = 0)


        self.message_viewer = CTkScrollableFrame(self, fg_color="cyan", corner_radius = 0)
        self.message_viewer.place(x = 0, y = 0)

        self.message_entry = CTkEntry(self, placeholder_text="Type your message here", height = 40,fg_color="cyan",placeholder_text_color="blue", corner_radius = 0)
        self.message_entry.place(x = 0, y = 0)

        self.but_path = "send_but.png"
        self.but_bg = Image.open(self.but_path)
        self.but_ctk = CTkImage(dark_image=self.but_bg, size=(30, 30))
        self.but_but = CTkButton(self, image=self.but_ctk, text="", fg_color="cyan", hover_color="cyan", bg_color="cyan", command = self.send_message, corner_radius = 0, border_color="cyan")

        self.but_but.place(x = 0, y = 0)

        self.username = "Biba"

        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect(("localhost", 8080))
            self.hello = f"{self.username} приєднався до чату!\n"
            self.socket.send(self.hello.encode())
            Thread(target = self.recv_message, daemon = True).start()
        except Exception as e:
            print(f"Упс, у вас виникла помилка - {e}")

        self.adaptive_ui()

    def add_message(self, text):
        message = CTkLabel(self.message_viewer, text = text)
        message.pack(pady = 3, padx = 5)

    def send_message(self):
        # Отримуємо текст з поля вводу (message_entry). Цей рядок витягує все, що користувач ввів у поле.
        # Приклад: Якщо користувач ввів "Привіт", то message = "Привіт".
        message = self.message_entry.get()
        
        # Перевіряємо, чи повідомлення не порожнє (має символи). Якщо порожнє — ігноруємо, щоб не надсилати пусті рядки.
        # Приклад: Якщо message = "", то if не спрацьовує і функція переходить до очищення поля.
        if message:
            
            # Формуємо повне повідомлення з ім'ям користувача. Це те, що побачать у чаті (локально і в інших клієнтів).
            # Приклад: Якщо username = "Biba" і message = "Привіт", то full_msg = "Biba : Привіт".
            full_msg = f"{self.username} : {message}"
            
            # Додаємо повідомлення в локальний чат (викликаємо метод add_message). Тут без \n, бо це тільки для відображення.
            # Приклад: Після цього рядка в чаті з'явиться новий лейбл з текстом "Biba : Привіт".
            self.add_message(full_msg)                   # без \n
            
            # Створюємо дані для надсилання: додаємо \n в кінець. \n — це розділювач, щоб на сервері/інших клієнтах знали, де закінчується повідомлення.
            # Без \n повідомлення можуть "злипнутися" в потоці даних (TCP — це потік байтів, не окремі пакети).
            # Приклад: Якщо full_msg = "Biba : Привіт", то data = "Biba : Привіт\n". Без \n resv_message не обробить правильно.
            data = f"{full_msg}\n"                       # з \n для мережі
            
            # Блок try-except для безпечної надсилання. Якщо помилка (сервер від'єднаний) — ігноруємо, щоб програма не впала.
            # Приклад: Якщо з'єднання OK, надсилає байти; якщо ні — просто pass (ігнорує).
            try:
                
                # Надсилаємо дані через сокет. sendall гарантує, що ВСІ байти надішлються (на відміну від send, який може надіслати частину).
                # encode() перетворює рядок на байти (UTF-8 для підтримки української/емодзі).
                # Приклад: data.encode() = b'Biba : \xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd1\x96\xd1\x82\n' (байти для "Biba : Привіт\n").
                self.socket.sendall(data.encode())
            except:
                
                # Порожній except: просто ігноруємо помилку (наприклад, якщо сервер впав). Можна додати лог, але тут pass для простоти.
                pass
        
        # Очищаємо поле вводу після надсилання (або якщо порожнє). delete(0, END) видаляє від початку до кінця.
        # Приклад: Після натискання кнопки поле стає порожнім, готовим до нового повідомлення.
        self.message_entry.delete(0, END)

    def recv_message(self):
        # Ініціалізуємо буфер — рядок, де накопичуємо неповні/часткові дані з сокета.
        # Приклад: Спочатку buffer = "", потім може стати "Biba : Привіт\nAnna : Добрий день".
        buffer = ""
        
        # Нескінченний цикл: постійно слухаємо сервер, поки з'єднання живе.
        # Приклад: Цикл крутиться в окремому потоці, не блокує UI.
        while True:
            
            # Блок try для ловлі помилок під час recv (отримання даних).
            # Приклад: Якщо все OK — обробляємо дані; якщо помилка — обробляємо в except.
            try:
                
                # Отримуємо дані з сокета: до 4096 байтів за раз. Це блокує, але в потоці OK.
                # Приклад: Якщо сервер надіслав "Biba : Привіт\n", то data = b'Biba : \xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd1\x96\xd1\x82\n'.
                data = self.socket.recv(4096)
                
                # Якщо даних немає (b''), значить з'єднання закрито сервером.
                # Приклад: Якщо сервер впав, data = b'', і ми виходимо з циклу.
                if not data:
                    
                    # Додаємо системне повідомлення в чат про від'єднання.
                    # Приклад: В чаті з'явиться "[SYSTEM] Сервер від'єднався.".
                    self.add_message("[SYSTEM] Сервер від'єднався.")
                    
                    # Виходимо з циклу (завершуємо потік).
                    break

                # Декодуємо байти в рядок (UTF-8 для української).
                # Приклад: data = b'Biba : \xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd1\x96\xd1\x82\n' → decoded = "Biba : Привіт\n".
                decoded = data.decode("utf-8")
                
                # Додаємо декодовані дані до буфера. Буфер накопичує, якщо повідомлення прийшло частинами.
                # Приклад: Якщо раніше buffer = "Biba : При", а decoded = "віт\n", то buffer = "Biba : Привіт\n".
                buffer += decoded

                # Цикл: поки в буфері є \n — обробляємо повні повідомлення.
                # Приклад: Якщо buffer = "Повідомлення1\nПовідомлення2\nЧастина3", то обробить перші два, залишить "Частина3".
                while "\n" in buffer:
                    
                    # Розбиваємо буфер на перше повне повідомлення (до \n) і залишок.
                    # split("\n", 1): 1 — значить розділити тільки на перший \n, не на всі.
                    # Приклад: buffer = "Biba : Привіт\nAnna : Добрий" → message = "Biba : Привіт", buffer = "Anna : Добрий".
                    message, buffer = buffer.split("\n", 1)
                    
                    # Якщо повідомлення не порожнє (після strip() — видалення пробілів).
                    # Приклад: Якщо message = "   " — ігноруємо; якщо "Biba : Привіт" — додаємо.
                    if message.strip():
                        
                        # Додаємо очищене повідомлення в чат.
                        # Приклад: В чаті з'явиться "Biba : Привіт" (без пробілів з боків).
                        self.add_message(message.strip())

            # Обробка помилки: якщо сокет non-blocking і даних ще немає — просто продовжуємо цикл.
            # Приклад: В Tkinter це часто трапляється; без цього цикл впаде з помилкою.
            except BlockingIOError:
                continue
            
            # Інші помилки (наприклад, з'єднання розірвано) — додаємо в чат і виходимо.
            # Приклад: Якщо сервер впав, e = "Connection reset by peer" → "[ERROR] Помилка отримання: Connection reset by peer".
            except Exception as e:
                self.add_message(f"[ERROR] Помилка отримання: {e}")
                break

        # Після циклу: намагаємось закрити сокет безпечно.
        # Приклад: Якщо сокет вже закритий — pass; інакше закриваємо.
        try:
            self.socket.close()
        except:
            pass

    def adaptive_ui(self):
        self.menu_frame.configure(height = self.winfo_height()) 

        self.message_viewer.place(x = self.menu_frame.winfo_width())
        self.message_viewer.configure(
            width = self.winfo_width() - self.menu_frame.winfo_width() - 20,
            height = self.winfo_height() - 40

        )
        self.but_but.place(x = self.winfo_width() - self.but_but.winfo_width(), y = self.winfo_height() - 40)
       
        self.message_entry.place(x = self.menu_frame.winfo_width(), y = self.but_but.winfo_y())
        self.message_entry.configure(width = self.winfo_width() - self.menu_frame.winfo_width() - self.but_but.winfo_width())

        self.after(50, self.adaptive_ui)

    color_fg= "pink"
    color_fg2= "purple"
    color_text="cyan"
    color_hover="pink"
    def menu_flag(self):
        if self.is_show_menu:
            print(111, self.is_show_menu)
            self.is_show_menu = False
            self.direction = -1    
            self.test = -5
            self.on_off_menu.configure(text=">")
            self.making_animation()
        else:
            print(222, self.is_show_menu)
            self.is_show_menu = True
            self.direction = 1  
            self.test = 10
            self.on_off_menu.configure(text="<")
            self.making_animation()

            self.username_entry = CTkEntry(self.menu_frame, placeholder_text="Enter new username:", fg_color=self.color_fg2,placeholder_text_color=self.color_text)
            self.username_entry.pack(pady = 30) 

            self.change_username = CTkButton(self.menu_frame, text = "Change username", width = 60, fg_color=self.color_fg, text_color=self.color_text, hover_color=self.color_hover, command = self.change)
            self.change_username.pack()

            self.sett_path = "setting.png"
            self.sett_bg = Image.open(self.sett_path)
            self.sett_ctk = CTkImage(dark_image=self.sett_bg, size=(30, 30))
            self.sett_but = CTkButton(self.menu_frame, image=self.sett_ctk, text="", fg_color=self.color_fg, hover_color=self.color_hover, command=self.open_sett)

            self.sett_but.pack(pady = 30)

    def change(self):
        new_username= self.username_entry.get()
        if new_username and new_username != self.username:
            old_username = self.username
            self.username = new_username

            message = f"{old_username} change mickname to {new_username}\n"
            
            try:
                self.socket.sendall(message.encode())
            except:
                pass

        self.username_entry.delete(0, END)


    def open_sett(self):
        sett_win = CTkToplevel(self)
        sett_win.geometry("300x200")
        sett_win.title("SETTINGS")
        theme_def = StringVar(value = "light")

        sett_win.attributes("-topmost", True)
        
        dark_radio = CTkRadioButton(sett_win, text = "Dark", variable=theme_def, command= self.dark_theme,text_color="grey")
        dark_radio.pack(pady = 5, padx=3)

        light_radio = CTkRadioButton(sett_win, text = "Light", variable=theme_def, command= self.light_theme, text_color="grey")
        light_radio.pack(pady = 5, padx=3)
        def checking(self):
            if StringVar(value = "light"):
                sett_win.configure(fg_color="white")
            if StringVar(value = "dark"): 
                sett_win.configure(fg_color="black")

            self.after(10, self.checking)


    def dark_theme(self):
        # global sett_window
        set_appearance_mode("dark")
        self.menu_frame.configure(fg_color="black")
        self.on_off_menu.configure(fg_color="black",text_color="white", hover_color="grey")
        # self.sett_win.configure(fg_color="black ")
        self.sett_but.configure(fg_color="black",hover_color= "grey")
        self.change_username.configure(fg_color="black",text_color= "white",hover_color="grey")
        self.username_entry.configure(fg_color="grey", placeholder_text_color= "white")
        self.but_but.configure(fg_color="black", hover_color="grey",border_color="black")
        self.message_entry.configure(fg_color="black",placeholder_text_color="white")
        self.message_viewer.configure(fg_color="black")
        self.color_fg = "black"
        self.color_fg2 = "grey"
        self.color_text = "white"
        self.color_hover= "grey"

    def light_theme(self):
        set_appearance_mode("light")
        self.menu_frame.configure(fg_color="white")
        self.on_off_menu.configure(fg_color="white",text_color="black", hover_color="grey")
        self.sett_but.configure(fg_color="white",hover_color= "grey")
        self.change_username.configure(fg_color="white",text_color= "black",hover_color="grey")
        self.username_entry.configure(fg_color="grey", placeholder_text_color= "black")
        self.but_but.configure(fg_color="white", hover_color="grey",border_color="white")
        self.message_entry.configure(fg_color="white",placeholder_text_color="black")
        self.message_viewer.configure(fg_color="white")
        self.color_fg = "white"
        self.color_fg2 = "grey"
        self.color_text = "black"
        self.color_hover= "grey"

    def making_animation(self):
        self.menu_frame.configure(width = self.menu_frame.winfo_width() + self.test)
        self.on_off_menu.place(x = self.menu_frame.winfo_width() - 50)

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.making_animation)
        elif self.menu_frame.winfo_width() >= 50 and not self.is_show_menu:
            self.after(10, self.making_animation)
            if self.username_entry and self.change_username and self.sett_but:
                self.username_entry.destroy() 
                self.change_username.destroy()
                self.sett_but.destroy()

win = MainWindow()
win.mainloop()