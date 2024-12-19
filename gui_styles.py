from ttkbootstrap import Style

def apply_styles(root):
    style = Style(theme="cosmo")
    
    # Custom styles for widgets
    style.configure("TButton", font=("Helvetica", 10))
    style.configure("TLabel", font=("Helvetica", 10))
    style.configure("TLabelframe", font=("Helvetica", 11, "bold"))
    style.configure("TLabelframe.Label", font=("Helvetica", 11, "bold"))
    
    # Custom colors
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabelframe", background="#f0f0f0")
    style.configure("TButton", background="#4CAF50", foreground="white")
    style.map("TButton", background=[("active", "#45a049")])
    
    return style

