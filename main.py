import tkinter as tk
from constants import COLORS, FONTS
from monitors import get_monitors
from ui_components import ModernButton, MonitorCard
from locales import TRANSLATIONS

class BlackScreenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.monitors = get_monitors()
        self.monitor_vars = []
        self.black_windows = []
        self.current_lang = "ja" # Default to Japanese
        
        self.update_title()
        self.center_window(600, 700)
        self.show_menu()

    def update_title(self):
        self.root.title(TRANSLATIONS[self.current_lang]["app_title"])

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ja" else "ja"
        self.update_title()
        self.show_menu()

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.attributes('-fullscreen', False)
        self.root.configure(background=COLORS["bg"])
        self.root.config(cursor="")
        self.root.unbind('<Key>')
        
        texts = TRANSLATIONS[self.current_lang]
        
        # Language Switch Button (Top Right)
        lang_frame = tk.Frame(self.root, bg=COLORS["bg"])
        lang_frame.pack(fill='x', padx=20, pady=10)
        
        lang_btn = tk.Label(lang_frame, text=texts["lang_switch"], font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_dim"], cursor="hand2")
        lang_btn.pack(side='right')
        lang_btn.bind("<Button-1>", lambda e: self.toggle_language())
        
        # Main Container
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(expand=True, fill='both', padx=50, pady=(10, 50))
        
        # Header
        header = tk.Label(container, text=texts["header"], font=FONTS["header"], bg=COLORS["bg"], fg=COLORS["text"])
        header.pack(pady=(0, 10), anchor='w')
        
        subheader = tk.Label(container, text=texts["subheader"], font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_dim"])
        subheader.pack(pady=(0, 40), anchor='w')
        
        # Monitor List
        monitor_frame = tk.Frame(container, bg=COLORS["bg"])
        monitor_frame.pack(fill='both', expand=True)
        
        # Preserve selection state if possible, or reset? 
        # Let's preserve if the count matches
        old_vars = [var.get() for var in self.monitor_vars]
        self.monitor_vars = []
        
        for i, monitor in enumerate(self.monitors):
            val = old_vars[i] if i < len(old_vars) else True
            var = tk.BooleanVar(value=val)
            self.monitor_vars.append(var)
            
            card = MonitorCard(
                monitor_frame, 
                monitor, 
                i, 
                var, 
                monitor_label=texts["monitor_label"],
                primary_text=texts["monitor_primary"]
            )
            card.pack(fill='x', pady=8)

        # Action Buttons
        btn_frame = tk.Frame(container, bg=COLORS["bg"])
        btn_frame.pack(pady=40, fill='x', side='bottom')
        
        start_btn = ModernButton(btn_frame, text=texts["start_btn"], command=self.start_black_screen)
        start_btn.pack(fill='x', pady=(0, 10))
        
        hint_label = tk.Label(btn_frame, text=texts["instruction_hint"], font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_dim"])
        hint_label.pack(pady=(0, 15))
        
        exit_btn = ModernButton(btn_frame, text=texts["exit_btn"], command=self.root.destroy, bg=COLORS["surface"], hover_bg="#333333")
        exit_btn.pack(fill='x')

    def start_black_screen(self):
        self.close_black_screens()
        
        selected_indices = [i for i, var in enumerate(self.monitor_vars) if var.get()]
        
        if not selected_indices:
            return

        self.root.withdraw()
        
        texts = TRANSLATIONS[self.current_lang]

        for i in selected_indices:
            monitor = self.monitors[i]
            
            win = tk.Toplevel(self.root)
            win.title(f"{texts['black_screen_title']} {i+1}")
            win.overrideredirect(True)
            win.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['x']}+{monitor['y']}")
            win.configure(background='black')
            win.config(cursor="none")
            
            win.bind('<Key>', self.return_to_menu)
            win.bind('<Button-1>', self.return_to_menu)
            
            win.attributes('-topmost', True)
            
            frame = tk.Frame(win, bg='black')
            frame.pack(fill='both', expand=True)
            
            self.black_windows.append(win)
            
        if self.black_windows:
            self.black_windows[0].focus_force()

    def close_black_screens(self):
        for win in self.black_windows:
            try:
                win.destroy()
            except:
                pass
        self.black_windows = []

    def return_to_menu(self, event=None):
        self.close_black_screens()
        self.root.deiconify()
        self.show_menu()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BlackScreenApp()
    app.run()
