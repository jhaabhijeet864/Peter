import tkinter as tk
import sys
import base64

def show_popup(text, window_title="Terminal | Peter System"):
    root = tk.Tk()
    root.overrideredirect(True) # Borderless window
    root.attributes('-topmost', True) # Always on top
    root.configure(bg='#1a1c1d') # Obsidian/Dark Iron background
    
    # Dynamic height calculation
    lines = text.split('\n')
    display_lines = min(25, len(lines)) # Cap at 25 lines
    height = display_lines * 16 + 40
    width = 600
    
    # Position in bottom-right, just above the system tray
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - width - 20
    y = screen_h - height - 60
    
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Metallic Title Bar
    title = tk.Label(
        root, 
        text=window_title, 
        bg='#434b4d', # Gunmetal
        fg='#e0e0e0', # Off-white
        font=("Consolas", 10, "bold"), 
        anchor="w", 
        padx=10,
        pady=2
    )
    title.pack(fill="x")
    
    # Scrollable Text Area
    frame = tk.Frame(root, bg='#1a1c1d')
    frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    txt = tk.Text(
        frame, 
        bg='#1a1c1d', 
        fg='#20C20E', # Matrix Green for terminal feel
        font=("Consolas", 10), 
        wrap="word", 
        bd=0, 
        highlightthickness=0,
        padx=10, 
        pady=10
    )
    txt.insert("1.0", text)
    txt.config(state="disabled") # Read-only
    txt.pack(side="left", fill="both", expand=True)
    
    # Auto close after 12 seconds
    root.after(12000, root.destroy)
    
    # Close on click
    root.bind("<Button-1>", lambda e: root.destroy())
    txt.bind("<Button-1>", lambda e: root.destroy())
    title.bind("<Button-1>", lambda e: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_text = base64.b64decode(sys.argv[1]).decode('utf-8')
        w_title = "Terminal | Peter System"
        if len(sys.argv) > 2:
            w_title = base64.b64decode(sys.argv[2]).decode('utf-8')
        show_popup(raw_text, w_title)
