import tkinter as tk
from constants import COLORS, FONTS

# --- Animation Helper ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*[int(c) for c in rgb])

def interpolate_color(start_hex, end_hex, t):
    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)
    
    new_rgb = tuple(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * t for i in range(3))
    return rgb_to_hex(new_rgb)

class AnimatedWidget:
    def __init__(self, widget, prop, start_val, end_val, duration=200, steps=20):
        self.widget = widget
        self.prop = prop
        self.start_val = start_val
        self.end_val = end_val
        self.duration = duration
        self.steps = steps
        self.current_step = 0
        self.running = False

    def start(self, reverse=False):
        self.running = True
        self.current_step = 0
        self.reverse = reverse
        self.animate()

    def animate(self):
        if not self.running:
            return
            
        t = self.current_step / self.steps
        if self.reverse:
            t = 1 - t
            
        current_color = interpolate_color(self.start_val, self.end_val, t)
        
        try:
            self.widget.configure(**{self.prop: current_color})
        except:
            self.running = False # Widget destroyed
            return

        self.current_step += 1
        if self.current_step <= self.steps:
            self.widget.after(int(self.duration / self.steps), self.animate)
        else:
            self.running = False
            # Ensure final state
            final_color = self.start_val if self.reverse else self.end_val
            try:
                self.widget.configure(**{self.prop: final_color})
            except:
                pass

class ModernButton(tk.Label):
    def __init__(self, master, text, command, bg=COLORS["accent"], hover_bg=COLORS["accent_hover"], **kwargs):
        super().__init__(master, text=text, bg=bg, fg=COLORS["text"], font=FONTS["button"], cursor="hand2", padx=25, pady=12, **kwargs)
        self.command = command
        self.default_bg = bg
        self.hover_bg = hover_bg
        
        self.animator = AnimatedWidget(self, 'bg', self.default_bg, self.hover_bg, duration=150)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def on_enter(self, event):
        self.animator.start(reverse=False)
        
    def on_leave(self, event):
        self.animator.start(reverse=True)
        
    def on_click(self, event):
        if self.command:
            self.command()

class MonitorCard(tk.Frame):
    def __init__(self, master, monitor, index, variable, monitor_label="Monitor", primary_text=" (Primary)"):
        super().__init__(master, bg=COLORS["surface"], padx=2, pady=2, cursor="hand2") # Padding for border
        self.monitor = monitor
        self.index = index
        self.variable = variable
        self.is_hovered = False
        
        # Inner container for content (to separate border from content)
        self.inner = tk.Frame(self, bg=COLORS["surface"], padx=20, pady=15)
        self.inner.pack(fill='both', expand=True)
        
        # Icon (Canvas)
        self.icon_canvas = tk.Canvas(self.inner, width=40, height=30, bg=COLORS["surface"], highlightthickness=0)
        self.icon_canvas.pack(side='left', padx=(0, 15))
        self.draw_icon(selected=True) # Initial draw
        
        # Text Info
        self.info_frame = tk.Frame(self.inner, bg=COLORS["surface"])
        self.info_frame.pack(side='left', fill='y')
        
        title_text = f"{monitor_label} {index+1}"
        if monitor['is_primary']:
            title_text += primary_text
            
        self.title_label = tk.Label(self.info_frame, text=title_text, font=FONTS["button"], bg=COLORS["surface"], fg=COLORS["text"])
        self.title_label.pack(anchor='w')
        
        self.res_label = tk.Label(self.info_frame, text=f"{monitor['width']} x {monitor['height']}", font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text_dim"])
        self.res_label.pack(anchor='w')
        
        # Animators
        self.bg_animator = AnimatedWidget(self, 'bg', COLORS["surface"], COLORS["border_selected"], duration=200)
        
        # We need to animate the background of inner, info_frame, and labels together
        self.inner_bg_animator = AnimatedWidget(self.inner, 'bg', COLORS["surface"], COLORS["surface_hover"], duration=200)
        self.info_bg_animator = AnimatedWidget(self.info_frame, 'bg', COLORS["surface"], COLORS["surface_hover"], duration=200)
        self.title_bg_animator = AnimatedWidget(self.title_label, 'bg', COLORS["surface"], COLORS["surface_hover"], duration=200)
        self.res_bg_animator = AnimatedWidget(self.res_label, 'bg', COLORS["surface"], COLORS["surface_hover"], duration=200)
        self.icon_bg_animator = AnimatedWidget(self.icon_canvas, 'bg', COLORS["surface"], COLORS["surface_hover"], duration=200)
        
        # Bindings
        self.bind_recursive(self)
        
        self.update_visuals(animate=False)

    def bind_recursive(self, widget):
        widget.bind("<Button-1>", self.toggle)
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)
        for child in widget.winfo_children():
            self.bind_recursive(child)

    def draw_icon(self, selected):
        self.icon_canvas.delete("all")
        color = COLORS["accent"] if selected else COLORS["text_dim"]
        
        # Draw a simple monitor shape
        # Screen
        self.icon_canvas.create_rectangle(2, 2, 38, 24, outline=color, width=2)
        # Stand
        self.icon_canvas.create_line(20, 24, 20, 28, fill=color, width=2)
        self.icon_canvas.create_line(12, 28, 28, 28, fill=color, width=2)
        
        if selected:
            # Checkmark inside
            self.icon_canvas.create_line(12, 12, 18, 18, fill=color, width=2)
            self.icon_canvas.create_line(18, 18, 28, 8, fill=color, width=2)

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self.update_visuals(animate=True)

    def on_enter(self, event):
        if not self.is_hovered:
            self.is_hovered = True
            if not self.variable.get(): # Only hover effect if not selected
                 self.start_hover_anim(reverse=False)

    def on_leave(self, event):
        if self.is_hovered:
            self.is_hovered = False
            if not self.variable.get():
                self.start_hover_anim(reverse=True)

    def start_hover_anim(self, reverse):
        self.inner_bg_animator.start(reverse)
        self.info_bg_animator.start(reverse)
        self.title_bg_animator.start(reverse)
        self.res_bg_animator.start(reverse)
        self.icon_bg_animator.start(reverse)

    def update_visuals(self, animate=True):
        selected = self.variable.get()
        
        # Icon update
        self.draw_icon(selected)
        
        # Colors
        if selected:
            target_border = COLORS["border_selected"]
            target_bg = COLORS["surface_selected"]
            target_text = COLORS["text"]
        else:
            target_border = COLORS["surface"] # Invisible border
            target_bg = COLORS["surface"]
            target_text = COLORS["text_dim"]

        # Apply
        self.configure(bg=target_border)
        self.inner.configure(bg=target_bg)
        self.info_frame.configure(bg=target_bg)
        self.title_label.configure(bg=target_bg, fg=COLORS["text"])
        self.res_label.configure(bg=target_bg, fg=target_text)
        self.icon_canvas.configure(bg=target_bg)
