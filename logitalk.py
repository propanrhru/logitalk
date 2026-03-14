from customtkinter import *
from socket import *
import threading
from PIL import Image, ImageDraw  

class Window(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x500') 
        self.minsize(400, 400)
        self.title("Gradient Chat Client")

        # --- НАЛАШТУВАННЯ ГРАДІЄНТА ---
        
        self.color1 = "#A866D8"  
        self.color2 = "#3D1EC9"  
    
        
        self.bg_image_label = None 
        self.current_bg_image = None 

        # --- БІЧНЕ МЕНЮ ---
        
        self.initialize_background()

        self.menu = CTkFrame(self, fg_color="#1a1a1a", corner_radius=0) # Темний фон для меню
        self.menu.place(x=0, y=0, relheight=1)
        self.menu.configure(width=0)
        self.menu.pack_propagate(False)

        self.show_menu = False
        self.menu_width = 0

        self.text = CTkLabel(self.menu, text='Ваш нік', text_color="white", font=("Arial", 14, "bold"))
        self.text.pack(pady=(50, 10))

        self.pole = CTkEntry(self.menu, placeholder_text="Нікнейм...")
        self.pole.pack(padx=10)
        self.pole.insert(0, "User") # Дефолтний нік

        # Кнопка меню (зробимо її прозорою)
        self.btn = CTkButton(self, text='🔱', width=40, height=40, fg_color="transparent", text_color="white", hover_color="#333333", command=self.show_hide)
        self.btn.place(x=5, y=5)

        # --- ЧАТ ---
        self.comm = CTkTextbox(self, state='disable', fg_color=("#f0f0f0", "#2b2b2b"), 
                                border_width=1, border_color="#555555")
        self.comm.place(x=0, y=0)

        # --- ПОЛЕ ВВЕДЕННЯ ---
        self.message_input = CTkEntry(self, placeholder_text="Введіть повідомлення...")
        self.message_input.place(x=0, y=0)
        self.message_input.bind("<Return>", lambda e: self.send_message()) # Відправка по Enter

        
        
        # Початкове ім'я
        self.name = self.pole.get()

        
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("2.tcp.eu.ngrok.io", 14285))
            self.sock.send(self.name.encode("utf-8"))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитись до сервера: {e}")
        self.add_message("Демонстраційний режим (сервер закоментовано)")

        self.adaptive()
        self.bind("<Configure>", self.on_window_resize)

    # --- ЛОГІКА ГРАДІЄНТА ---
    def initialize_background(self):
        """Створює початковий лейбл для фону."""
        self.bg_image_label = CTkLabel(self, text="")
        self.bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_image_label.lower()

    def create_gradient(self, width, height):
        """Генерує зображення вертикального градієнта."""
        if width <= 0 or height <= 0: return None

        base = Image.new('RGB', (width, height), self.color1)
        top_color = self.hex_to_rgb(self.color1)
        bottom_color = self.hex_to_rgb(self.color2)
        
        for y in range(height):
            r = y / float(height - 1) if height > 1 else 0
            
            new_r = int(top_color[0] * (1 - r) + bottom_color[0] * r)
            new_g = int(top_color[1] * (1 - r) + bottom_color[1] * r)
            new_b = int(top_color[2] * (1 - r) + bottom_color[2] * r)
            
        return CTkImage(light_image=base, dark_image=base, size=(width, height))

    def hex_to_rgb(self, hex_color):
        """Конвертує #RRGGBB в (R, G, B) кортеж."""
        hex_color = hex_color.lstrip('#')

        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def on_window_resize(self, event):
        """Викликається при зміні розміру вікна."""
        if event.widget == self:
            new_bg = self.create_gradient(event.width, event.height)
            if new_bg:
                self.current_bg_image = new_bg 
                self.bg_image_label.configure(image=new_bg)

    def adaptive(self):
        menu_w = self.menu.winfo_width()
        win_w = self.winfo_width()
        win_h = self.winfo_height()

        input_h = 35

        padding_x = 15 
        padding_y = 15

        chat_y_start = 55

        self.comm.configure(width=win_w - menu_w - padding_x * 2, height=win_h - input_h - chat_y_start - padding_y * 2 - 10)
        self.comm.place(x=menu_w + padding_x, y=chat_y_start)

        input_w = win_w - menu_w - self.send_btn.winfo_width() - padding_x * 3
        self.message_input.configure(width=input_w, height=input_h)
        self.message_input.place(x=menu_w + padding_x, y=win_h - input_h - padding_y - 120)

        self.loop_id = self.after(30, self.adaptive)

    # --- МЕНЮ ---
    def show_hide(self):
        if hasattr(self, '_menu_after_id'):
            self.after_cancel(self._menu_after_id)
            
        self.name = self.pole.get() 

        if self.show_menu:
            self.show_menu = False
            self.animate_close()
        else:
            self.show_menu = True
            self.animate_open()

    def animate_open(self):
        """Плавно відкриває меню."""
        if self.menu_width < 200:
            self.menu_width += 15 
            self.menu.configure(width=self.menu_width)
            self._menu_after_id = self.after(10, self.animate_open)
        else:
            self.menu_width = 200
            self.menu.configure(width=200)

    def animate_close(self):
        """Плавно закриває меню."""
        if self.menu_width > 0:
            self.menu_width -= 15
            self.menu.configure(width=self.menu_width)
            self._menu_after_id = self.after(10, self.animate_close)
            
            return  
         
        self.menu_width = 0
        self.menu.configure(width=0)

    def add_message(self, text):
        self.comm.configure(state='normal')
        self.comm.insert(END, text + '\n')
        self.comm.see(END)
        self.comm.configure(state='disable')

    def send_message(self):
        self.name = self.pole.get() or "User" 
        message = self.message_input.get()
        if message:
            self.add_message(f"Ви: {message}")
            data = f"TEXT@{self.name}@{message}\n"
            
            if hasattr(self, 'sock'):
                try:
                    self.sock.sendall(data.encode())
                except:
                    self.add_message("⚠️ З'єднання розірвано.")
            
            self.message_input.delete(0, END)

    def receive_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.after(0, self.handle_line, line.strip())
            except:
                break
        if hasattr(self, 'sock'): self.sock.close()
    
    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                if author != self.pole.get():
                    self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"📸 {author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)

if __name__ == "__main__":
    set_appearance_mode("Light") 
    win = Window()
    win.mainloop()