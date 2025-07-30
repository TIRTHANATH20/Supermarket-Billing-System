import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import os
from tkinter import filedialog
import time
from PIL import Image, ImageTk
import sqlite3
from fpdf import FPDF
import subprocess
import hashlib
from PIL import ImageFilter

# Modern color scheme with light theme
COLORS = {
    'primary': '#ffffff',      # White
    'secondary': '#f8f9fa',    # Light gray
    'surface': '#ffffff',      # White
    'background': '#f0f2f5',   # Light blue-gray
    'card': '#ffffff',         # White
    'input': '#f8f9fa',       # Light gray
    'text': '#202124',        # Dark gray (almost black)
    'text_secondary': '#5f6368', # Medium gray
    'accent': '#1a73e8',      # Google Blue
    'hover': '#1557b0',       # Darker blue
    'success': '#0f9d58',     # Google Green
    'danger': '#d93025',      # Google Red
    'warning': '#f29900',     # Google Yellow
    'border': '#dadce0',      # Light gray border
    'highlight': '#1a73e8',   # Google Blue
    'scrollbar': '#dadce0',   # Light gray
    'disabled': '#9aa0a6',    # Medium gray
    'selection': '#e8f0fe'    # Light blue selection
}

# Animation settings with dark theme colors and timing
ANIMATION = {
    # Animation timing settings
    'fade_speed': 0.01,  # Faster fade animation
    'shake_speed': 0.02,  # Faster shake animation
    'hover_speed': 0.05,  # Faster hover animation
    'transition_speed': 0.08,  # Faster transition animation
    'slide_speed': 0.03,  # Faster slide animation
    
    # Dark theme colors
    'primary': '#0a0a14',      # Darkest navy (outer background)
    'secondary': '#12121f',    # Very dark navy
    'surface': '#1e1e2e',      # Surface color for cards and containers
    'background': '#0a0a14',   # Darkest background
    'card': '#1e1e2e',        # Card background
    'input': '#12121f',       # Input field background
    'text': '#e6e6e6',        # Light grey text
    'text_secondary': '#94a3b8', # Secondary text color
    'accent': '#3498db',      # Blue accent
    'hover': '#2980b9',       # Darker blue for hover
    'success': '#27ae60',     # Green
    'danger': '#e74c3c',      # Red
    'warning': '#f39c12',     # Orange
    'border': '#2e2e3e',      # Border color
    'highlight': '#3498db',   # Highlight color
    'scrollbar': '#2e2e3e',   # Scrollbar color
    'disabled': '#4b5563',    # Disabled state color
    'selection': '#2563eb'    # Selection highlight color
}

def fade_in(window):
    window.attributes('-alpha', 0)
    window.update()
    for i in range(11):
        window.attributes('-alpha', i/10)
        window.update()
        time.sleep(ANIMATION['fade_speed'])

def fade_out(window):
    for i in range(10, -1, -1):
        window.attributes('-alpha', i/10)
        window.update()
        time.sleep(ANIMATION['fade_speed'])

def shake_window(window, x, y):
    for _ in range(3):
        window.geometry(f"400x500+{x+5}+{y}")
        window.update()
        time.sleep(ANIMATION['shake_speed'])
        window.geometry(f"400x500+{x-5}+{y}")
        window.update()
        time.sleep(ANIMATION['shake_speed'])
    window.geometry(f"400x500+{x}+{y}")

def smooth_hover(widget, color1, color2):
    def on_enter(e):
        widget['bg'] = color2
        widget['fg'] = COLORS['text']
    
    def on_leave(e):
        widget['bg'] = color1
        widget['fg'] = COLORS['text']
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def slide_in(widget, start_x, end_x, y):
    for x in range(start_x, end_x + 1, 5):
        widget.place(x=x, y=y)
        widget.update()
        time.sleep(ANIMATION['slide_speed'])

def set_background_image(window, image_path):
    try:
        # Load and resize the image
        img = Image.open(image_path)
        img = img.resize((window.winfo_screenwidth(), window.winfo_screenheight()), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage directly without overlay
        photo = ImageTk.PhotoImage(img)
        
        # Create a label for the background image
        background_label = Label(window, image=photo)
        background_label.image = photo  # Keep a reference
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        return background_label
    except Exception as e:
        print(f"Error setting background image: {e}")
        return None

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change this to your MySQL username
    'password': 'tirtha2006',  # Change this to your MySQL password
    'database': 'supermarket_billing_system'
}

def setup_database():
    """Set up the database and required tables"""
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                CustomerID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Contact VARCHAR(20),
                Email VARCHAR(100),
                Address TEXT
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                ProductID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Category VARCHAR(50) NOT NULL,
                Price DECIMAL(10, 2) NOT NULL,
                Stock INT NOT NULL DEFAULT 0
            )
        """)
        
        # Create bills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                BillID INT AUTO_INCREMENT PRIMARY KEY,
                CustomerID INT,
                BillDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                TotalAmount DECIMAL(10, 2) NOT NULL,
                PDFPath VARCHAR(255),
                FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
            )
        """)
        
        # Drop existing bill_items table if it exists to recreate with new schema
        cursor.execute("DROP TABLE IF EXISTS bill_items")
        
        # Create bill_items table with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_items (
                BillItemID INT AUTO_INCREMENT PRIMARY KEY,
                BillID INT,
                ProductID INT,
                ProductName VARCHAR(100),
                Quantity INT NOT NULL,
                Price DECIMAL(10, 2) NOT NULL,
                SubTotal DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (BillID) REFERENCES bills(BillID),
                FOREIGN KEY (ProductID) REFERENCES products(ProductID) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database setup completed successfully")
        return True
        
    except mysql.connector.Error as err:
        print(f"Error setting up database: {err}")
        return False

def connect_db():
    """Connect to the MySQL database"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="tirtha2006",  # Updated password
            database="supermarket_billing_system"  # Updated database name
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error connecting to database: {str(e)}")
        return None

def create_gradient_frame(parent, color1, color2):
    """Create a gradient frame"""
    gradient_frame = Canvas(parent, highlightthickness=0)
    gradient_frame.pack(fill=BOTH, expand=True)
    
    # Create gradient
    for i in range(100):
        # Calculate color for current line
        r1, g1, b1 = parent.winfo_rgb(color1)
        r2, g2, b2 = parent.winfo_rgb(color2)
        
        # Linear interpolation
        r = (r1 + (r2 - r1) * i / 100) / 256
        g = (g1 + (g2 - g1) * i / 100) / 256
        b = (b1 + (b2 - b1) * i / 100) / 256
        
        color = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
        gradient_frame.create_line(0, i*6, 800, i*6, fill=color, width=6)
    
    return gradient_frame

class RoundedEntry(Entry):
    """Custom Entry widget with rounded corners"""
    def __init__(self, master=None, **kwargs):
        Entry.__init__(self, master, **kwargs)
        self.config(borderwidth=0, highlightthickness=0)
        self.bg_color = kwargs.get('bg', COLORS['input'])  # Use input color as default background
        
        # Create rounded frame
        self.frame = Frame(master, bg=COLORS['surface'])  # Use surface color for frame
        self.frame.place(in_=self, relx=0, rely=0, relwidth=1, relheight=1)
        
        # Create canvas for rounded rectangle
        self.canvas = Canvas(self.frame, bg=self.bg_color, highlightthickness=0, 
                           height=45, bd=0)  # Increased height
        self.canvas.pack(fill='both', expand=True)
        
        # Draw rounded rectangle
        self.canvas.create_roundrectangle = self._create_roundrectangle
        self.canvas.bind('<Configure>', self._on_resize)
        
    def _create_roundrectangle(self, x1, y1, x2, y2, r=20, **kwargs):  # Increased radius
        points = [
            x1+r, y1, x2-r, y1, # Top line
            x2-r, y1, x2, y1, x2, y1+r, # Top right corner
            x2, y1+r, x2, y2-r, # Right line
            x2, y2-r, x2, y2, x2-r, y2, # Bottom right corner
            x2-r, y2, x1+r, y2, # Bottom line
            x1+r, y2, x1, y2, x1, y2-r, # Bottom left corner
            x1, y2-r, x1, y1+r, # Left line
            x1, y1+r, x1, y1, x1+r, y1 # Top left corner
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)
    
    def _on_resize(self, event):
        # Redraw the rounded rectangle when the widget is resized
        self.canvas.delete('all')
        bg = self.canvas.create_roundrectangle(
            2, 2, event.width-2, event.height-2,
            fill=self.bg_color, outline=COLORS['accent'], width=1
        )
        # Bind enter/leave events for hover effect
        self.canvas.tag_bind(bg, '<Enter>', 
            lambda e: self.canvas.itemconfig(bg, fill=COLORS['hover']))  # Use hover color
        self.canvas.tag_bind(bg, '<Leave>', 
            lambda e: self.canvas.itemconfig(bg, fill=self.bg_color))

# Login Window with enhanced UI
def login_window():
    """Create the login window with modern UI"""
    global login
    login = Tk()
    login.title("Supermarket Billing System - Login")
    login.state('zoomed')
    
    # Set background image using the modified function
    background_label = set_background_image(login, "assets/supermarket_bg.jpg")
    if not background_label:
        login.configure(bg='#1a1a1a')
    
    # Create main container with very light background
    main_frame = Frame(login, bg='#cd7f32')
    main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    # Create glass morphism container with extremely light background
    glass_frame = Frame(main_frame, 
                       bg='#fdfbd4',
                       padx=30,
                       pady=30,
                       highlightthickness=1,
                       highlightbackground='#e0e0e0')
    glass_frame.pack(padx=20, pady=20)
    
    # Add decorative top line
    canvas = Canvas(glass_frame, width=340, height=2, bg='#fdfbd4', highlightthickness=0)
    canvas.pack(pady=(0, 20))
    
    # Title with modern font and icon
    title_frame = Frame(glass_frame, bg='#fdfbd4')
    title_frame.pack(fill=X, pady=(0, 20))
    
    title_icon = Label(title_frame,
                      text="🛒",
                      font=('Segoe UI', 24),
                      bg='#fdfbd4',
                      fg='#2ecc71')
    title_icon.pack()
    
    title_label = Label(title_frame,
                       text="SUPERMARKET BILLING",
                       font=('Segoe UI', 20, 'bold'),
                       bg='#fdfbd4',
                       fg='#333333')
    title_label.pack()
    
    subtitle_label = Label(title_frame,
                         text="Welcome back! Please login to continue",
                         font=('Segoe UI', 11),
                         bg='#fdfbd4',
                         fg='#666666')
    subtitle_label.pack()
    
    # Username field with floating label effect
    username_frame = Frame(glass_frame, bg='#fdfbd4')
    username_frame.pack(fill=X, pady=10)
    
    username_icon = Label(username_frame,
                         text="👤",
                         font=('Segoe UI', 14),
                         bg='#fdfbd4',
                         fg='#2ecc71')
    username_icon.pack(side=LEFT, padx=(0, 10))
    
    username_var = StringVar()
    username_entry = Entry(username_frame,
                         textvariable=username_var,
                         font=('Segoe UI', 11),
                         bg='#fdfbd4',
                         fg='#333333',
                         insertbackground='#333333',
                         relief=FLAT)
    username_entry.pack(fill=X, ipady=6)
    
    # Add bottom border
    username_border = Frame(username_frame, height=2, bg='#2ecc71')
    username_border.pack(fill=X, pady=(0, 5))
    
    # Password field with floating label effect
    password_frame = Frame(glass_frame, bg='#fdfbd4')
    password_frame.pack(fill=X, pady=10)
    
    password_icon = Label(password_frame,
                         text="🔒",
                         font=('Segoe UI', 14),
                         bg='#fdfbd4',
                         fg='#2ecc71')
    password_icon.pack(side=LEFT, padx=(0, 10))
    
    password_var = StringVar()
    password_entry = Entry(password_frame,
                         textvariable=password_var,
                         font=('Segoe UI', 11),
                         bg='#fdfbd4',
                         fg='#333333',
                         show="●",
                         insertbackground='#333333',
                         relief=FLAT)
    password_entry.pack(fill=X, ipady=6)
    
    # Add bottom border
    password_border = Frame(password_frame, height=2, bg='#2ecc71')
    password_border.pack(fill=X, pady=(0, 5))
    
    def validate_login():
        """Validate login credentials"""
        username = username_var.get().strip()
        password = password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Check credentials - using %s placeholder for MySQL
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                         (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                login.destroy()
                main_application()
            else:
                messagebox.showerror("Error", "Invalid username or password")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
    
    # Login button with hover effect
    login_button = Button(glass_frame,
                         text="LOGIN",
                         font=('Segoe UI', 12, 'bold'),
                         bg='#2ecc71',
                         fg='white',
                         activebackground='#27ae60',
                         activeforeground='white',
                         relief=FLAT,
                         cursor='hand2',
                         width=20,
                         command=validate_login)
    login_button.pack(pady=25)
    
    # Create account link
    create_account_label = Label(glass_frame,
                               text="Create New Account",
                               font=('Segoe UI', 11),
                               bg='#fdfbd4',
                               fg='#2ecc71',
                               cursor='hand2')
    create_account_label.pack()
    create_account_label.bind('<Button-1>', lambda e: create_account())
    
    # Delete account link
    delete_account_label = Label(glass_frame,
                               text="Delete Account",
                               font=('Segoe UI', 11),
                               bg='#fdfbd4',
                               fg='#f44336',  # Red color for delete
                               cursor='hand2')
    delete_account_label.pack(pady=5)
    delete_account_label.bind('<Button-1>', lambda e: delete_account())
    
    # Center the window
    login.update_idletasks()
    width = login.winfo_width()
    height = login.winfo_height()
    x = (login.winfo_screenwidth() // 2) - (width // 2)
    y = (login.winfo_screenheight() // 2) - (height // 2)
    login.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Make sure the login window stays on top
    login.lift()
    login.focus_force()
    
    # Bind Enter key to validate_login
    login.bind('<Return>', lambda e: validate_login())
    
    login.mainloop()

# Main Application Window with enhanced UI
def main_application():
    """Create the main application window with enhanced UI"""
    global root
    root = Tk()
    root.title("Supermarket Billing System")
    root.state('zoomed')
    root.configure(bg=ANIMATION['primary'])  # Changed to dark theme
    
    # Initialize database first
    try:
        # Ensure database and tables exist
        setup_database()
        
        # Test database connection
        conn = connect_db()
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to database. Please check your database configuration.")
            root.destroy()
            return
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
        root.destroy()
        return
    
    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure modern styles for all widgets with dark theme
    style.configure('TFrame', 
                   background=ANIMATION['surface'])
    
    style.configure('TLabel', 
                   background=ANIMATION['surface'], 
                   foreground=ANIMATION['text'],
                   font=('Segoe UI', 10))
    
    style.configure('TButton', 
                   background=ANIMATION['accent'],
                   foreground=ANIMATION['text'],
                   padding=(10, 5),
                   font=('Segoe UI', 10))
    
    style.map('TButton',
              background=[('active', ANIMATION['hover'])],
              foreground=[('active', ANIMATION['text'])])
    
    style.configure('TEntry',
                   fieldbackground=ANIMATION['input'],
                   foreground=ANIMATION['text'],
                   insertcolor=ANIMATION['text'])
    
    style.configure('TCombobox',
                   fieldbackground=ANIMATION['input'],
                   background=ANIMATION['text'],
                   foreground=ANIMATION['text'],
                   arrowcolor=ANIMATION['text'])
    
    style.map('TCombobox',
             fieldbackground=[('readonly', ANIMATION['input'])],
             selectbackground=[('readonly', ANIMATION['accent'])])
    
    style.configure('Treeview',
                   background=ANIMATION['surface'],
                   foreground=ANIMATION['text'],
                   fieldbackground=ANIMATION['surface'],
                   rowheight=30)
    
    style.configure('Treeview.Heading',
                   background=ANIMATION['secondary'],
                   foreground=ANIMATION['text'],
                   padding=5,
                   font=('Segoe UI', 10, 'bold'))
    
    style.map('Treeview',
              background=[('selected', ANIMATION['selection'])],
              foreground=[('selected', ANIMATION['text'])])
    
    # Create main container
    main_container = ttk.Frame(root)
    main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Create notebook for tabs
    notebook = ttk.Notebook(main_container)
    notebook.pack(fill=BOTH, expand=True)
    
    # Configure notebook style
    style.configure('TNotebook',
                   background=ANIMATION['primary'],
                   borderwidth=0)
    
    style.configure('TNotebook.Tab',
                   background=ANIMATION['surface'],
                   foreground=ANIMATION['text'],
                   padding=[15, 5],
                   font=('Segoe UI', 10))
    
    style.map('TNotebook.Tab',
              background=[('selected', ANIMATION['accent'])],
              foreground=[('selected', ANIMATION['text'])])
    
    # Create and add tabs with dark theme
    customers_tab = ttk.Frame(notebook, style='TFrame')
    products_tab = ttk.Frame(notebook, style='TFrame')
    billing_tab = ttk.Frame(notebook, style='TFrame')
    
    notebook.add(customers_tab, text='Customers')
    notebook.add(products_tab, text='Products')
    notebook.add(billing_tab, text='Billing')
    
    # Initialize tabs with data
    initialize_customers_tab(customers_tab)
    initialize_products_tab(products_tab)
    initialize_billing_tab(billing_tab)
    
    # Add some sample data if tables are empty
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Check if customers table is empty
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                # Add sample customer
                cursor.execute("""
                    INSERT INTO customers (Name, Contact, Email, Address)
                    VALUES ('John Doe', '1234567890', 'john@example.com', '123 Main St')
                """)
            
            # Check if products table is empty
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                # Add sample product
                cursor.execute("""
                    INSERT INTO products (Name, Category, Price, Stock)
                    VALUES ('Sample Product', 'General', 9.99, 10)
                """)
            
            conn.commit()
            conn.close()
            
            # Refresh all tabs
            view_customers(customers_tree)
            view_products(products_tree)
            load_bills(bills_tree)
            
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize sample data: {str(e)}")
    
    root.mainloop()

def initialize_customers_tab(tab):
    """Initialize the customers tab with search and list functionality"""
    # Search frame
    search_frame = ttk.Frame(tab)
    search_frame.pack(fill=X, padx=20, pady=20)
    
    # Search controls
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
    
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)  # Reduced width to match button
    search_entry.pack(side=LEFT, padx=5, ipady=4)  # Reduced ipady to match button height
    
    ttk.Button(search_frame, text="Search",
              command=lambda: view_customers(customers_tree, search_var.get())).pack(side=LEFT, padx=5)
    
    ttk.Button(search_frame, text="Clear",
              command=lambda: [search_var.set(''), view_customers(customers_tree)]).pack(side=LEFT, padx=5)
    
    # Action buttons
    action_frame = ttk.Frame(search_frame)
    action_frame.pack(side=RIGHT, padx=10)
    
    ttk.Button(action_frame, text="Add Customer",
              command=lambda: add_customer_ui(customers_tree)).pack(side=LEFT, padx=5)
    
    ttk.Button(action_frame, text="Delete Customer",
              command=lambda: delete_customer(customers_tree)).pack(side=LEFT, padx=5)
    
    # Customers treeview
    global customers_tree
    customers_tree = ttk.Treeview(tab,
                                columns=("ID", "Name", "Contact", "Email", "Address"),
                               show='headings')
    
    # Configure columns
    customers_tree.heading("ID", text="ID")
    customers_tree.heading("Name", text="Name")
    customers_tree.heading("Contact", text="Contact")
    customers_tree.heading("Email", text="Email")
    customers_tree.heading("Address", text="Address")
    
    customers_tree.column("ID", width=80, anchor=CENTER)
    customers_tree.column("Name", width=200, anchor=CENTER)
    customers_tree.column("Contact", width=150, anchor=CENTER)
    customers_tree.column("Email", width=200, anchor=CENTER)
    customers_tree.column("Address", width=300, anchor=CENTER)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=customers_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    customers_tree.configure(yscrollcommand=scrollbar.set)
    customers_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Load initial data
    view_customers(customers_tree)
    
def initialize_products_tab(tab):
    """Initialize the products tab with search and list functionality"""
    global products_tree
    
    # Search frame
    search_frame = ttk.Frame(tab)
    search_frame.pack(fill=X, padx=20, pady=20)
    
    # Search controls
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
    
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side=LEFT, padx=5, ipady=4)
    
    ttk.Button(search_frame, text="Search",
              command=lambda: view_products(products_tree, search_var.get())).pack(side=LEFT, padx=5)
    
    ttk.Button(search_frame, text="Clear",
              command=lambda: [search_var.set(''), view_products(products_tree)]).pack(side=LEFT, padx=5)
    
    # Action buttons
    btn_frame = ttk.Frame(tab)
    btn_frame.pack(fill=X, padx=20, pady=(0, 20))
    
    ttk.Button(btn_frame, text="Add Product",
              command=lambda: add_product()).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Delete Product",
              command=lambda: delete_product(products_tree)).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Restock",
              command=lambda: restock_product_ui(products_tree)).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Check Stock Alerts",
              command=lambda: check_stock_alerts(products_tree)).pack(side=LEFT, padx=5)
    
    # Products treeview
    products_tree = ttk.Treeview(tab,
                               columns=("ID", "Name", "Category", "Price", "Stock"),
                               show='headings')
    
    # Configure columns
    products_tree.heading("ID", text="ID")
    products_tree.heading("Name", text="Name")
    products_tree.heading("Category", text="Category")
    products_tree.heading("Price", text="Price")
    products_tree.heading("Stock", text="Stock")
    
    products_tree.column("ID", width=80, anchor=CENTER)
    products_tree.column("Name", width=200, anchor=CENTER)
    products_tree.column("Category", width=150, anchor=CENTER)
    products_tree.column("Price", width=100, anchor=CENTER)
    products_tree.column("Stock", width=100, anchor=CENTER)
    
    # Configure tag for low stock items
    products_tree.tag_configure('low_stock', foreground='red')
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=products_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    products_tree.configure(yscrollcommand=scrollbar.set)
    products_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Load initial data
    view_products(products_tree)
    
    return products_tree
    
def initialize_billing_tab(tab):
    """Initialize the billing tab with search and list functionality"""
    # Control frame
    control_frame = ttk.Frame(tab)
    control_frame.pack(fill=X, padx=20, pady=20)
    
    # Left side buttons
    left_buttons_frame = ttk.Frame(control_frame)
    left_buttons_frame.pack(side=LEFT, fill=X)
    
    # Create New Bill button
    ttk.Button(left_buttons_frame, text="Create New Bill",
              command=create_bill_ui).pack(side=LEFT, padx=5)
    
    # Delete All Bills button
    ttk.Button(left_buttons_frame, text="Delete All Bills",
              command=lambda: delete_all_bills(bills_tree)).pack(side=LEFT, padx=5)
    
    # Search frame
    search_frame = ttk.Frame(control_frame)
    search_frame.pack(side=RIGHT, padx=10)
    
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
    
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)  # Reduced width to match button
    search_entry.pack(side=LEFT, padx=5, ipady=4)  # Reduced ipady to match button height
    
    ttk.Button(search_frame, text="Search",
              command=lambda: load_bills(bills_tree, search_var.get())).pack(side=LEFT, padx=5)
    
    ttk.Button(search_frame, text="Clear",
              command=lambda: [search_var.set(''), load_bills(bills_tree)]).pack(side=LEFT, padx=5)
    
    # Bills treeview
    global bills_tree
    bills_tree = ttk.Treeview(tab,
                           columns=("Bill ID", "Customer", "Date", "Amount"),
                           show='headings')
    
    # Configure columns
    bills_tree.heading("Bill ID", text="Bill ID")
    bills_tree.heading("Customer", text="Customer")
    bills_tree.heading("Date", text="Date")
    bills_tree.heading("Amount", text="Amount")
    
    bills_tree.column("Bill ID", width=100, anchor=CENTER)
    bills_tree.column("Customer", width=200, anchor=CENTER)
    bills_tree.column("Date", width=150, anchor=CENTER)
    bills_tree.column("Amount", width=150, anchor=CENTER)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=bills_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    bills_tree.configure(yscrollcommand=scrollbar.set)
    bills_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Action buttons frame
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill=X, padx=20, pady=(0, 20))
    
    ttk.Button(button_frame, text="View Bill Details",
              command=lambda: view_bill_details(bills_tree)).pack(side=LEFT, padx=5)
    
    # Load initial bills
    load_bills(bills_tree)

def view_customers(tree, search_term=None):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    try:
        conn = connect_db()
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to database")
            tree.insert('', 'end', values=('', 'Database connection failed', '', '', ''))
            return
        
        cursor = conn.cursor()
        
        # Check if customers table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'customers'
        """)
        
        if cursor.fetchone()[0] == 0:
            messagebox.showinfo("Info", "Customers table does not exist. Creating it now...")
            setup_database()
        
        # Execute search query
        if search_term:
            query = """
                SELECT CustomerID, Name, Contact, Email, Address 
                FROM customers 
                WHERE Name LIKE %s OR Contact LIKE %s OR Email LIKE %s
                ORDER BY CustomerID ASC
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        else:
            cursor.execute("""
                SELECT CustomerID, Name, Contact, Email, Address 
                FROM customers 
                ORDER BY CustomerID ASC
            """)
        
        customers = cursor.fetchall()
        
        if not customers:
            tree.insert('', 'end', values=('', 'No customers found', '', '', ''))
            if messagebox.askyesno("No Customers", "Would you like to add a sample customer?"):
                cursor.execute("""
                    INSERT INTO customers (Name, Contact, Email, Address)
                    VALUES ('John Doe', '1234567890', 'john@example.com', '123 Main St')
                """)
                conn.commit()
                view_customers(tree)
        else:
            for row in customers:
                row = tuple('' if v is None else v for v in row)
                tree.insert('', 'end', values=row)
        
        conn.close()
    
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load customers: {str(e)}")
        tree.insert('', 'end', values=('', f'Error: {str(e)}', '', '', ''))

def delete_product(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a product to delete")
        return
            
    product_name = tree.item(selected_item[0])['values'][1]
        
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {product_name}? Historical bills containing this product will be preserved."):
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                
                # Get product ID
                cursor.execute("SELECT ProductID FROM products WHERE Name = %s", (product_name,))
                product = cursor.fetchone()
                
                if product:
                    product_id = product[0]
                    
                    # Delete the product - the ON DELETE SET NULL in the foreign key will handle bill_items
                    cursor.execute("DELETE FROM products WHERE ProductID = %s", (product_id,))
                    
                    conn.commit()
                    
                    # Refresh the product list
                    view_products(tree)
                    messagebox.showinfo("Success", "Product deleted successfully!")
                else:
                    messagebox.showerror("Error", "Product not found!")
                    
                conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete product: {str(e)}")

def view_bill_details(tree):
    """View bill details in a simplified window"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to view")
        return
        
    # Get bill ID from selected item
    bill_id = tree.item(selected[0])['values'][0]
    
    # Create new window
    window = Toplevel()
    window.title("Bill Details")
    
    # Set window size and position
    window_width = 400
    window_height = 420
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    window.minsize(400, 420)  # Set minimum size
    window.configure(bg='#1e1e2d')  # Dark navy background
    
    # Create main frame
    main_frame = Frame(window, bg='#1e1e2d')
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
    
    # Add title
    Label(main_frame,
          text="Bill Details",
          font=('Segoe UI', 16, 'bold'),
          fg='white',
          bg='#1e1e2d').pack(pady=5)
    
    # Create details frame
    details_frame = Frame(main_frame, bg='#1e1e2d')
    details_frame.pack(fill=BOTH, expand=True, pady=5)
    
    try:
        conn = connect_db()
        if not conn:
            messagebox.showerror("Error", "Could not connect to database")
            return
            
        cursor = conn.cursor()
        
        # Get bill details
        cursor.execute("""
            SELECT b.BillID, c.Name, c.Contact, c.Email, b.BillDate, b.TotalAmount
            FROM bills b
            JOIN customers c ON b.CustomerID = c.CustomerID
            WHERE b.BillID = %s
        """, (bill_id,))
        
        bill = cursor.fetchone()
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
            
        # Display customer details
        details = [
            ("Bill Information", [
                ("Bill ID:", bill[0]),
                ("Date:", bill[4].strftime("%Y-%m-%d %H:%M:%S"))
            ]),
            ("Customer Details", [
                ("Name:", bill[1]),
                ("Contact:", bill[2]),
                ("Email:", bill[3])
            ]),
            ("Payment Details", [
                ("Total Amount:", f"₹{bill[5]:.2f}")
            ])
        ]
        
        for section_title, fields in details:
            # Section title
            section_frame = Frame(details_frame, bg='#1e1e2d')
            section_frame.pack(fill=X, pady=2)
            
            Label(section_frame,
                  text=section_title,
                  font=('Segoe UI', 12, 'bold'),
                  fg=ANIMATION['accent'],
                  bg='#1e1e2d').pack(anchor=W)
            
            # Create fields frame with border
            fields_frame = Frame(section_frame,
                               bg='#1e1e2d',
                               highlightbackground='#2d2d3d',  # Slightly lighter border
                               highlightthickness=1)
            fields_frame.pack(fill=X, pady=(0, 5))
            
            # Add fields
            for label, value in fields:
                field_frame = Frame(fields_frame, bg='#1e1e2d')
                field_frame.pack(fill=X, padx=5, pady=2)
                
                Label(field_frame,
                      text=label,
                      font=('Segoe UI', 11),
                      fg='#a0a0a0',  # Lighter gray for labels
                      bg='#1e1e2d').pack(side=LEFT)
                      
                Label(field_frame,
                      text=str(value),
                      font=('Segoe UI', 11, 'bold'),
                      fg='white',
                      bg='#1e1e2d').pack(side=RIGHT)
        
        conn.close()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch bill details: {str(e)}")
        return
    
    # Create button frame at the bottom
    button_frame = Frame(window, bg='#1e1e2d', height=45)
    button_frame.pack(side=BOTTOM, fill=X, padx=10, pady=(0, 10))
    button_frame.pack_propagate(False)
    
    # Center the buttons
    button_container = Frame(button_frame, bg='#1e1e2d')
    button_container.pack(expand=True)
    
    # View PDF button
    pdf_button = Button(button_container,
                       text="View PDF",
                       font=('Segoe UI', 11),
                       bg=ANIMATION['accent'],
                       fg='white',
                       bd=0,
                       padx=25,
                       pady=5,
                       cursor='hand2',
                       command=lambda: view_pdf(bill_id))
    pdf_button.pack(side=LEFT, padx=5)
    
    # Close button
    close_button = Button(button_container,
                         text="Close",
                         font=('Segoe UI', 11),
                         bg=ANIMATION['danger'],
                         fg='white',
                         bd=0,
                         padx=25,
                         pady=5,
                         cursor='hand2',
                         command=window.destroy)
    close_button.pack(side=LEFT, padx=5)
    
    # Add hover effects
    smooth_hover(pdf_button, ANIMATION['accent'], ANIMATION['hover'])
    smooth_hover(close_button, ANIMATION['danger'], ANIMATION['hover'])
    
    # Make sure window appears on top
    window.transient(window.master)
    window.grab_set()
    window.focus_set()

def generate_pdf(bill_id, details_window=None):
    try:
        # Get bill details from database
        conn = connect_db()
        if not conn:
            raise Exception("Failed to connect to database")
        
        cursor = conn.cursor()
        
        # Get bill and customer details
        cursor.execute("""
            SELECT b.BillID, b.BillDate, b.TotalAmount,
                   c.Name, c.Contact, c.Address
            FROM bills b
            LEFT JOIN customers c ON b.CustomerID = c.CustomerID
            WHERE b.BillID = %s
        """, (bill_id,))
        
        bill_details = cursor.fetchone()
        if not bill_details:
            raise Exception("Bill not found")
        
        # Get bill items
        cursor.execute("""
            SELECT p.Name, bi.Quantity, bi.Price, bi.SubTotal
            FROM bill_items bi
            JOIN products p ON bi.ProductID = p.ProductID
            WHERE bi.BillID = %s
        """, (bill_id,))
        
        bill_items = cursor.fetchall()
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set font to Helvetica (built-in font)
        pdf.set_font('Helvetica', 'B', 16)
        
        # Header
        pdf.cell(0, 10, 'Supermarket Bill', 0, 1, 'C')
        pdf.ln(10)
        
        # Bill details
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 10, f'Bill ID: {bill_details[0]}', 0, 1)
        pdf.cell(0, 10, f'Date: {bill_details[1]}', 0, 1)
        pdf.cell(0, 10, f'Customer: {bill_details[3]}', 0, 1)
        pdf.cell(0, 10, f'Contact: {bill_details[4]}', 0, 1)
        if bill_details[5]:
            pdf.cell(0, 10, f'Address: {bill_details[5]}', 0, 1)
        pdf.ln(10)
        
        # Items table header
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(80, 10, 'Item', 1)
        pdf.cell(30, 10, 'Quantity', 1)
        pdf.cell(40, 10, 'Price', 1)
        pdf.cell(40, 10, 'Subtotal', 1)
        pdf.ln()
        
        # Items
        pdf.set_font('Helvetica', '', 12)
        for item in bill_items:
            pdf.cell(80, 10, str(item[0]), 1)
            pdf.cell(30, 10, str(item[1]), 1)
            pdf.cell(40, 10, f'Rs. {item[2]:.2f}', 1)
            pdf.cell(40, 10, f'Rs. {item[3]:.2f}', 1)
            pdf.ln()
        
        # Total
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(150, 10, 'Total:', 0)
        pdf.cell(40, 10, f'Rs. {bill_details[2]:.2f}', 1)
        
        # Save PDF
        pdf_dir = os.path.join(os.getcwd(), 'bills')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'bill_{bill_id}.pdf')
        pdf.output(pdf_path)
        
        # Update PDF path in database
        cursor.execute("""
            UPDATE bills
            SET PDFPath = %s
            WHERE BillID = %s
        """, (pdf_path, bill_id))
        
        conn.commit()
        conn.close()
        
        # Try multiple methods to open the PDF
        try:
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            else:  # Linux/Mac
                subprocess.run(['xdg-open', pdf_path])
        except Exception as e:
            print(f"Failed to open PDF: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"Failed to generate PDF: {str(e)}")
        if conn:
            conn.close()
        return False

def check_stock_alerts(tree):
    """Check and display products with low stock"""
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ProductID, Name, Category, Stock 
                FROM products 
                WHERE Stock <= 10
                ORDER BY Stock ASC
            """)
            low_stock_items = cursor.fetchall()
            conn.close()
            
            if not low_stock_items:
                messagebox.showinfo("Stock Alert", "No products with low stock!")
                return
            
            # Create alert message
            alert_msg = "Products with low stock:\n\n"
            for item in low_stock_items:
                alert_msg += f"• {item[1]} ({item[2]}): {item[3]} units remaining\n"
            
            messagebox.showerror("Low Stock Alert", alert_msg)
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check stock alerts: {str(e)}")

def update_stock_in_treeview(tree, product_id, new_stock):
    """Update stock value in treeview and refresh color coding"""
    # Find the item with matching product_id
    for item in tree.get_children():
        if tree.item(item)['values'][0] == product_id:
            values = list(tree.item(item)['values'])
            values[4] = new_stock  # Update stock value
            
            # Update tag based on new stock level
            tag = 'low_stock' if new_stock <= 5 else 'normal_stock'
            tree.item(item, values=values, tags=(tag,))
            break
    
    # Ensure tag colors are configured
    tree.tag_configure('low_stock', foreground='red')
    tree.tag_configure('normal_stock', foreground='white')

def restock_product_ui(tree):
    """Create a window for restocking a product"""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a product to restock")
        return
        
    product_id = tree.item(selected_item[0])['values'][0]
    product_name = tree.item(selected_item[0])['values'][1]
    current_stock = tree.item(selected_item[0])['values'][4]
    
    # Create restock window
    restock_window = Toplevel()
    restock_window.title("Restock Product")
    restock_window.configure(bg=ANIMATION['surface'])
    restock_window.resizable(False, False)
    
    # Set window size and position
    window_width = 280
    window_height = 220
    screen_width = restock_window.winfo_screenwidth()
    screen_height = restock_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    restock_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container
    main_frame = Frame(restock_window, bg=ANIMATION['surface'])
    main_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)
    
    # Title
    title_label = Label(main_frame,
                       text=f"Restock: {product_name}",
                       font=('Segoe UI', 11, 'bold'),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'],
                       wraplength=250)
    title_label.pack(pady=(0, 5))
    
    # Current stock
    stock_label = Label(main_frame,
                       text=f"Current Stock: {current_stock}",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    stock_label.pack(pady=2)
    
    # Quantity frame
    quantity_frame = Frame(main_frame, bg=ANIMATION['surface'])
    quantity_frame.pack(fill=X, pady=5)
    
    quantity_label = Label(quantity_frame,
                         text="Add Quantity:",
                         font=('Segoe UI', 10),
                         bg=ANIMATION['surface'],
                         fg=ANIMATION['text'])
    quantity_label.pack(anchor=W)
    
    quantity_var = StringVar()
    quantity_entry = Entry(quantity_frame,
                         textvariable=quantity_var,
                         font=('Segoe UI', 10),
                         bg=ANIMATION['input'],
                         fg=ANIMATION['text'],
                         insertbackground=ANIMATION['text'],
                         relief=FLAT)
    quantity_entry.pack(fill=X, pady=2, ipady=4)
    
    # Error message
    error_label = Label(main_frame,
                       text="",
                       font=('Segoe UI', 9),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['danger'],
                       wraplength=250)
    error_label.pack(pady=2)
    
    def save_restock():
        try:
            quantity = int(quantity_var.get())
            
            if quantity <= 0:
                error_label.config(text="Quantity must be greater than 0")
                return
                
            if quantity > 1000:
                error_label.config(text="Maximum restock quantity is 1000")
                return
                
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                
                # Update stock
                new_stock = current_stock + quantity
                cursor.execute("""
                    UPDATE products 
                    SET Stock = Stock + %s 
                    WHERE ProductID = %s
                """, (quantity, product_id))
                
                conn.commit()
                conn.close()
                
                # Update stock in treeview
                update_stock_in_treeview(products_tree, product_id, new_stock)
                
                # Show success message and close window
                messagebox.showinfo("Success", f"Added {quantity} units to stock")
                restock_window.destroy()
                
        except ValueError:
            error_label.config(text="Please enter a valid number")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
    
    # Button frame
    button_frame = Frame(main_frame, bg=ANIMATION['surface'])
    button_frame.pack(side=BOTTOM, fill=X, pady=(5, 0))
    
    # Save button
    save_btn = Button(button_frame,
                     text="Save",
                     font=('Segoe UI', 10, 'bold'),
                     bg=ANIMATION['success'],
                     fg=ANIMATION['text'],
                     activebackground=ANIMATION['hover'],
                     activeforeground=ANIMATION['text'],
                     relief=FLAT,
                     cursor='hand2',
                     command=save_restock)
    save_btn.pack(side=LEFT, fill=X, expand=True, padx=2, ipady=3)
    
    # Cancel button
    cancel_btn = Button(button_frame,
                       text="Cancel",
                       font=('Segoe UI', 10, 'bold'),
                       bg=ANIMATION['danger'],
                       fg=ANIMATION['text'],
                       activebackground=ANIMATION['hover'],
                       activeforeground=ANIMATION['text'],
                       relief=FLAT,
                       cursor='hand2',
                       command=restock_window.destroy)
    cancel_btn.pack(side=LEFT, fill=X, expand=True, padx=2, ipady=3)
    
    # Set focus to quantity field
    quantity_entry.focus()
    
    # Bind Enter key to save
    restock_window.bind('<Return>', lambda e: save_restock())

def initialize_products_tab(tab):
    """Initialize the products tab with search and list functionality"""
    global products_tree
    
    # Search frame
    search_frame = ttk.Frame(tab)
    search_frame.pack(fill=X, padx=20, pady=20)
    
    # Search controls
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
    
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side=LEFT, padx=5, ipady=4)
    
    ttk.Button(search_frame, text="Search",
              command=lambda: view_products(products_tree, search_var.get())).pack(side=LEFT, padx=5)
    
    ttk.Button(search_frame, text="Clear",
              command=lambda: [search_var.set(''), view_products(products_tree)]).pack(side=LEFT, padx=5)
    
    # Action buttons
    btn_frame = ttk.Frame(tab)
    btn_frame.pack(fill=X, padx=20, pady=(0, 20))
    
    ttk.Button(btn_frame, text="Add Product",
              command=lambda: add_product()).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Delete Product",
              command=lambda: delete_product(products_tree)).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Restock",
              command=lambda: restock_product_ui(products_tree)).pack(side=LEFT, padx=5)
    
    ttk.Button(btn_frame, text="Check Stock Alerts",
              command=lambda: check_stock_alerts(products_tree)).pack(side=LEFT, padx=5)
    
    # Products treeview
    products_tree = ttk.Treeview(tab,
                               columns=("ID", "Name", "Category", "Price", "Stock"),
                               show='headings')
    
    # Configure columns
    products_tree.heading("ID", text="ID")
    products_tree.heading("Name", text="Name")
    products_tree.heading("Category", text="Category")
    products_tree.heading("Price", text="Price")
    products_tree.heading("Stock", text="Stock")
    
    products_tree.column("ID", width=80, anchor=CENTER)
    products_tree.column("Name", width=200, anchor=CENTER)
    products_tree.column("Category", width=150, anchor=CENTER)
    products_tree.column("Price", width=100, anchor=CENTER)
    products_tree.column("Stock", width=100, anchor=CENTER)
    
    # Configure tag for low stock items
    products_tree.tag_configure('low_stock', foreground='red')
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=products_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    products_tree.configure(yscrollcommand=scrollbar.set)
    products_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Load initial data
    view_products(products_tree)
    
    return products_tree
    
def initialize_billing_tab(tab):
    """Initialize the billing tab with search and list functionality"""
    # Control frame
    control_frame = ttk.Frame(tab)
    control_frame.pack(fill=X, padx=20, pady=20)
    
    # Left side buttons
    left_buttons_frame = ttk.Frame(control_frame)
    left_buttons_frame.pack(side=LEFT, fill=X)
    
    # Create New Bill button
    ttk.Button(left_buttons_frame, text="Create New Bill",
              command=create_bill_ui).pack(side=LEFT, padx=5)
    
    # Delete All Bills button
    ttk.Button(left_buttons_frame, text="Delete All Bills",
              command=lambda: delete_all_bills(bills_tree)).pack(side=LEFT, padx=5)
    
    # Search frame
    search_frame = ttk.Frame(control_frame)
    search_frame.pack(side=RIGHT, padx=10)
    
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
    
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)  # Reduced width to match button
    search_entry.pack(side=LEFT, padx=5, ipady=4)  # Reduced ipady to match button height
    
    ttk.Button(search_frame, text="Search",
              command=lambda: load_bills(bills_tree, search_var.get())).pack(side=LEFT, padx=5)
    
    ttk.Button(search_frame, text="Clear",
              command=lambda: [search_var.set(''), load_bills(bills_tree)]).pack(side=LEFT, padx=5)
    
    # Bills treeview
    global bills_tree
    bills_tree = ttk.Treeview(tab,
                           columns=("Bill ID", "Customer", "Date", "Amount"),
                           show='headings')
    
    # Configure columns
    bills_tree.heading("Bill ID", text="Bill ID")
    bills_tree.heading("Customer", text="Customer")
    bills_tree.heading("Date", text="Date")
    bills_tree.heading("Amount", text="Amount")
    
    bills_tree.column("Bill ID", width=100, anchor=CENTER)
    bills_tree.column("Customer", width=200, anchor=CENTER)
    bills_tree.column("Date", width=150, anchor=CENTER)
    bills_tree.column("Amount", width=150, anchor=CENTER)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=bills_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    bills_tree.configure(yscrollcommand=scrollbar.set)
    bills_tree.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Action buttons frame
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill=X, padx=20, pady=(0, 20))
    
    ttk.Button(button_frame, text="View Bill Details",
              command=lambda: view_bill_details(bills_tree)).pack(side=LEFT, padx=5)
    
    # Load initial bills
    load_bills(bills_tree)

def view_products(tree, search_term=None):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
        
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            if search_term:
                cursor.execute("""
                    SELECT ProductID, Name, Category, Price, Stock
                    FROM products 
                    WHERE Name LIKE %s OR Category LIKE %s
                """, (f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT ProductID, Name, Category, Price, Stock FROM products")
                
            products = cursor.fetchall()
            
            for product in products:
                # Determine tag based on stock level
                tag = 'low_stock' if product[4] <= 5 else 'normal'
                tree.insert('', 'end', values=product, tags=(tag,))
            
            conn.close()
            
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load products: {str(e)}")

def load_bills(tree, search_term=None):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        if not conn:
            messagebox.showerror("Database Error", "Could not connect to database")
            tree.insert('', 'end', values=('', 'Database connection failed', '', ''))
            return
        
        # First check if the bills table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'bills'
        """)
        
        if cursor.fetchone()[0] == 0:
            messagebox.showinfo("Info", "Bills table does not exist. Creating it now...")
            setup_database()
            return
        
        # Check if there are any bills in the table
        cursor.execute("SELECT COUNT(*) FROM bills")
        bill_count = cursor.fetchone()[0]
        
        if bill_count == 0:
            tree.insert('', 'end', values=('', 'No bills found. Create a new bill to get started.', '', ''))
            conn.close()
            return
        
        if search_term:
            query = """
                SELECT b.BillID, c.Name, b.BillDate, b.TotalAmount
                FROM bills b
                LEFT JOIN customers c ON b.CustomerID = c.CustomerID
                WHERE b.BillID LIKE %s OR c.Name LIKE %s
                ORDER BY b.BillDate DESC
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
        else:
            cursor.execute("""
                SELECT b.BillID, c.Name, b.BillDate, b.TotalAmount
                FROM bills b
                LEFT JOIN customers c ON b.CustomerID = c.CustomerID
                ORDER BY b.BillDate DESC
            """)
        
        bills = cursor.fetchall()
        
        if not bills:
            tree.insert('', 'end', values=('', 'No bills found matching your search', '', ''))
        else:
            for bill in bills:
                bill_id, customer_name, bill_date, total_amount = bill
                formatted_date = bill_date.strftime('%Y-%m-%d %H:%M:%S') if bill_date else ''
                formatted_amount = f"₹{float(total_amount):.2f}" if total_amount is not None else ''
                tree.insert('', 'end', values=(
                    bill_id or '',
                    customer_name or '',
                    formatted_date,
                    formatted_amount
                ))
        
        conn.close()
        
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load bills: {str(e)}")
        tree.insert('', 'end', values=('', f'Error: {str(e)}', '', ''))

def add_customer_ui(tree):
    """Add a new customer with enhanced UI"""
    # Create a new window for adding customer
    add_window = Toplevel()
    add_window.title("Add New Customer")
    add_window.configure(bg=ANIMATION['surface'])
    
    # Set window size and position
    window_width = 500
    window_height = 600
    screen_width = add_window.winfo_screenwidth()
    screen_height = add_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    add_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container
    main_frame = Frame(add_window, bg=ANIMATION['surface'])
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = Label(main_frame, 
                       text="Add New Customer",
                       font=('Segoe UI', 16, 'bold'),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    title_label.pack(pady=10)
    
    # Form frame
    form_frame = Frame(main_frame, bg=ANIMATION['surface'])
    form_frame.pack(fill=BOTH, expand=True, pady=10)
    
    # Name field
    name_frame = Frame(form_frame, bg=ANIMATION['surface'])
    name_frame.pack(fill=X, pady=5)
    
    name_label = Label(name_frame,
                      text="Name *",
                      font=('Segoe UI', 10),
                      bg=ANIMATION['surface'],
                      fg=ANIMATION['text'])
    name_label.pack(anchor=W)
    
    name_var = StringVar()
    name_entry = Entry(name_frame,
                      textvariable=name_var,
                      font=('Segoe UI', 10),
                      bg=ANIMATION['input'],
                      fg=ANIMATION['text'],
                      insertbackground=ANIMATION['text'],
                      relief=FLAT)
    name_entry.pack(fill=X, pady=2, ipady=8)
    
    # Contact field
    contact_frame = Frame(form_frame, bg=ANIMATION['surface'])
    contact_frame.pack(fill=X, pady=5)
    
    contact_label = Label(contact_frame,
                         text="Contact * (must be unique)",
                         font=('Segoe UI', 10),
                         bg=ANIMATION['surface'],
                         fg=ANIMATION['text'])
    contact_label.pack(anchor=W)
    
    contact_var = StringVar()
    contact_entry = Entry(contact_frame,
                         textvariable=contact_var,
                         font=('Segoe UI', 10),
                         bg=ANIMATION['input'],
                         fg=ANIMATION['text'],
                         insertbackground=ANIMATION['text'],
                         relief=FLAT)
    contact_entry.pack(fill=X, pady=2, ipady=8)
    
    # Email field
    email_frame = Frame(form_frame, bg=ANIMATION['surface'])
    email_frame.pack(fill=X, pady=5)
    
    email_label = Label(email_frame,
                       text="Email (must be unique if provided)",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    email_label.pack(anchor=W)
    
    email_var = StringVar()
    email_entry = Entry(email_frame,
                       textvariable=email_var,
                       font=('Segoe UI', 10),
                       bg=ANIMATION['input'],
                       fg=ANIMATION['text'],
                       insertbackground=ANIMATION['text'],
                       relief=FLAT)
    email_entry.pack(fill=X, pady=2, ipady=8)
    
    # Address field
    address_frame = Frame(form_frame, bg=ANIMATION['surface'])
    address_frame.pack(fill=X, pady=5)
    
    address_label = Label(address_frame,
                         text="Address",
                         font=('Segoe UI', 10),
                         bg=ANIMATION['surface'],
                         fg=ANIMATION['text'])
    address_label.pack(anchor=W)
    
    address_var = StringVar()
    address_entry = Entry(address_frame,
                         textvariable=address_var,
                         font=('Segoe UI', 10),
                         bg=ANIMATION['input'],
                         fg=ANIMATION['text'],
                         insertbackground=ANIMATION['text'],
                         relief=FLAT)
    address_entry.pack(fill=X, pady=2, ipady=8)
    
    # Error message label
    error_label = Label(form_frame,
                       text="",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['danger'],
                       wraplength=400)
    error_label.pack(pady=10)
    
    def save_customer():
        name = name_var.get().strip()
        contact = contact_var.get().strip()
        email = email_var.get().strip()
        address = address_var.get().strip()
        
        if not name:
            error_label.config(text="Name is required")
            return
            
        if not contact:
            error_label.config(text="Contact is required")
            return
            
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                
                # Check for duplicate contact
                cursor.execute("SELECT CustomerID FROM customers WHERE Contact = %s", (contact,))
                if cursor.fetchone():
                    error_label.config(text="This contact number is already registered")
                    return
                
                # Check for duplicate email if provided
                if email:
                    cursor.execute("SELECT CustomerID FROM customers WHERE Email = %s", (email,))
                    if cursor.fetchone():
                        error_label.config(text="This email is already registered")
                        return
                
                # Insert new customer
                cursor.execute("""
                    INSERT INTO customers (Name, Contact, Email, Address)
                    VALUES (%s, %s, %s, %s)
                """, (name, contact, email, address))
                
                conn.commit()
                conn.close()
                
                # Refresh the treeview
                view_customers(tree)
                
                # Close the window
                add_window.destroy()
                
                messagebox.showinfo("Success", "Customer added successfully")
            else:
                error_label.config(text="Failed to connect to database")
                
        except Exception as e:
            if "Duplicate entry" in str(e):
                error_label.config(text="This contact number or email is already registered")
            else:
                error_label.config(text=f"Error: {str(e)}")
    
    # Button frame
    button_frame = Frame(form_frame, bg=ANIMATION['surface'])
    button_frame.pack(fill=X, pady=10)
    
    # Save button
    save_btn = Button(button_frame,
                     text="Save Customer",
                     font=('Segoe UI', 10, 'bold'),
                     bg=ANIMATION['accent'],
                     fg=ANIMATION['text'],
                     activebackground=ANIMATION['hover'],
                     activeforeground=ANIMATION['text'],
                     relief=FLAT,
                     cursor='hand2',
                     command=save_customer)
    save_btn.pack(side=LEFT, fill=X, expand=True, pady=10, padx=5, ipady=8)
    
    # Cancel button
    cancel_btn = Button(button_frame,
                       text="Cancel",
                       font=('Segoe UI', 10, 'bold'),
                       bg=ANIMATION['danger'],
                       fg=ANIMATION['text'],
                       activebackground=ANIMATION['hover'],
                       activeforeground=ANIMATION['text'],
                       relief=FLAT,
                       cursor='hand2',
                       command=add_window.destroy)
    cancel_btn.pack(side=LEFT, fill=X, expand=True, pady=10, padx=5, ipady=8)
    
    # Set focus to name field
    name_entry.focus()
    
    # Bind Enter key to save
    add_window.bind('<Return>', lambda e: save_customer())

def add_product():
    """Add a new product with enhanced UI"""
    # Create a new window for adding product
    add_window = Toplevel()
    add_window.title("Add New Product")
    add_window.configure(bg=ANIMATION['surface'])
    
    # Set window size and position
    window_width = 500
    window_height = 600
    screen_width = add_window.winfo_screenwidth()
    screen_height = add_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    add_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container
    main_frame = Frame(add_window, bg=ANIMATION['surface'])
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = Label(main_frame, 
                       text="Add New Product",
                       font=('Segoe UI', 16, 'bold'),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    title_label.pack(pady=10)
    
    # Form frame
    form_frame = Frame(main_frame, bg=ANIMATION['surface'])
    form_frame.pack(fill=BOTH, expand=True, pady=10)
    
    # Name field
    name_frame = Frame(form_frame, bg=ANIMATION['surface'])
    name_frame.pack(fill=X, pady=5)
    
    name_label = Label(name_frame,
                      text="Name * (must be unique)",
                      font=('Segoe UI', 10),
                      bg=ANIMATION['surface'],
                      fg=ANIMATION['text'])
    name_label.pack(anchor=W)
    
    name_var = StringVar()
    name_entry = Entry(name_frame,
                      textvariable=name_var,
                      font=('Segoe UI', 10),
                      bg=ANIMATION['input'],
                      fg=ANIMATION['text'],
                      insertbackground=ANIMATION['text'],
                      relief=FLAT)
    name_entry.pack(fill=X, pady=2, ipady=8)
    
    # Category field
    category_frame = Frame(form_frame, bg=ANIMATION['surface'])
    category_frame.pack(fill=X, pady=5)
    
    category_label = Label(category_frame,
                         text="Category",
                         font=('Segoe UI', 10),
                         bg=ANIMATION['surface'],
                         fg=ANIMATION['text'])
    category_label.pack(anchor=W)
    
    category_var = StringVar()
    category_entry = Entry(category_frame,
                         textvariable=category_var,
                         font=('Segoe UI', 10),
                         bg=ANIMATION['input'],
                         fg=ANIMATION['text'],
                         insertbackground=ANIMATION['text'],
                         relief=FLAT)
    category_entry.pack(fill=X, pady=2, ipady=8)
    
    # Price field
    price_frame = Frame(form_frame, bg=ANIMATION['surface'])
    price_frame.pack(fill=X, pady=5)
    
    price_label = Label(price_frame,
                       text="Price *",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    price_label.pack(anchor=W)
    
    price_var = StringVar()
    price_entry = Entry(price_frame,
                       textvariable=price_var,
                       font=('Segoe UI', 10),
                       bg=ANIMATION['input'],
                       fg=ANIMATION['text'],
                       insertbackground=ANIMATION['text'],
                       relief=FLAT)
    price_entry.pack(fill=X, pady=2, ipady=8)
    
    # Stock field
    stock_frame = Frame(form_frame, bg=ANIMATION['surface'])
    stock_frame.pack(fill=X, pady=5)
    
    stock_label = Label(stock_frame,
                       text="Stock *",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    stock_label.pack(anchor=W)
    
    stock_var = StringVar()
    stock_entry = Entry(stock_frame,
                       textvariable=stock_var,
                       font=('Segoe UI', 10),
                       bg=ANIMATION['input'],
                       fg=ANIMATION['text'],
                       insertbackground=ANIMATION['text'],
                       relief=FLAT)
    stock_entry.pack(fill=X, pady=2, ipady=8)
    
    # Error message label
    error_label = Label(form_frame,
                       text="",
                       font=('Segoe UI', 10),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['danger'],
                       wraplength=400)
    error_label.pack(pady=10)
    
    def save_product():
        name = name_var.get().strip()
        category = category_var.get().strip()
        price = price_var.get().strip()
        stock = stock_var.get().strip()
        
        if not name:
            error_label.config(text="Name is required")
            return
            
        if not price:
            error_label.config(text="Price is required")
            return
            
        if not stock:
            error_label.config(text="Stock is required")
            return
            
        try:
            price = float(price)
            stock = int(stock)
            
            if price <= 0:
                error_label.config(text="Price must be greater than 0")
                return
            
            if stock < 0:
                error_label.config(text="Stock cannot be negative")
                return
            
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                
                # Check if product name already exists
                cursor.execute("SELECT ProductID FROM products WHERE Name = %s", (name,))
                if cursor.fetchone():
                    error_label.config(text="A product with this name already exists")
                    return
                
                # Insert new product
                cursor.execute("""
                    INSERT INTO products (Name, Category, Price, Stock)
                    VALUES (%s, %s, %s, %s)
                """, (name, category or None, price, stock))
                
                conn.commit()
                
                # Get the new product's ID
                product_id = cursor.lastrowid
                
                conn.close()
                
                # Update products tree
                products_tree.insert('', 'end', values=(product_id, name, category, f"₹{price:.2f}", stock))
                
                # Update product combobox in billing tab
                refresh_product_list()
                
                # Show success message and close window
                messagebox.showinfo("Success", "Product added successfully!")
                add_window.destroy()
                
        except ValueError:
            error_label.config(text="Please enter valid numbers for price and stock")
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
    
    # Button frame
    button_frame = Frame(form_frame, bg=ANIMATION['surface'])
    button_frame.pack(fill=X, pady=10)
    
    # Save button
    save_btn = Button(button_frame,
                     text="Save Product",
                     font=('Segoe UI', 10, 'bold'),
                     bg=ANIMATION['accent'],
                     fg=ANIMATION['text'],
                     activebackground=ANIMATION['hover'],
                     activeforeground=ANIMATION['text'],
                     relief=FLAT,
                     cursor='hand2',
                     command=save_product)
    save_btn.pack(side=LEFT, fill=X, expand=True, pady=10, padx=5, ipady=8)
    
    # Cancel button
    cancel_btn = Button(button_frame,
                       text="Cancel",
                       font=('Segoe UI', 10, 'bold'),
                       bg=ANIMATION['danger'],
                       fg=ANIMATION['text'],
                       activebackground=ANIMATION['hover'],
                       activeforeground=ANIMATION['text'],
                       relief=FLAT,
                       cursor='hand2',
                       command=add_window.destroy)
    cancel_btn.pack(side=LEFT, fill=X, expand=True, pady=10, padx=5, ipady=8)
    
    # Set focus to name field
    name_entry.focus()
    
    # Bind Enter key to save
    add_window.bind('<Return>', lambda e: save_product())

def delete_all_bills(tree):
    """Delete all bills from the database"""
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL bills? This action cannot be undone."):
        return
        
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Delete all bill items first (due to foreign key constraint)
            cursor.execute("DELETE FROM bill_items")
            
            # Then delete all bills
            cursor.execute("DELETE FROM bills")
            
            # Reset the auto-increment counter for bills table
            cursor.execute("ALTER TABLE bills AUTO_INCREMENT = 1")
            
            conn.commit()
            conn.close()
            
            # Refresh the bills view
            load_bills(tree)
            
            messagebox.showinfo("Success", "All bills have been deleted successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete bills: {str(e)}")

def add_customer():
    """Add a new customer to the database"""
    name = name_var.get().strip()
    contact = contact_var.get().strip()
    email = email_var.get().strip()
    address = address_text.get("1.0", END).strip()
    
    if not name or not contact:
        messagebox.showerror("Error", "Name and Contact are required fields!")
        return
        
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Check if contact already exists
            cursor.execute("SELECT CustomerID FROM customers WHERE Contact = %s", (contact,))
            if cursor.fetchone():
                messagebox.showerror("Error", "A customer with this contact number already exists!")
                return
                
            # Check if email already exists (if provided)
            if email:
                cursor.execute("SELECT CustomerID FROM customers WHERE Email = %s", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "A customer with this email already exists!")
                    return
            
            cursor.execute("""
                INSERT INTO customers (Name, Contact, Email, Address)
                VALUES (%s, %s, %s, %s)
            """, (name, contact, email, address))
            
            conn.commit()
            conn.close()
            
            # Clear the form
            name_var.set("")
            contact_var.set("")
            email_var.set("")
            address_text.delete("1.0", END)
            
            # Refresh the customer list
            view_customers(customers_tree)
            
            messagebox.showinfo("Success", "Customer added successfully!")
                
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to add customer: {str(e)}")

def delete_customer(tree):
    """Delete selected customer from the database"""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a customer to delete!")
        return
        
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
        return
        
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Get customer ID
            customer_id = tree.item(selected_item)['values'][0]
            
            # Check if customer has any bills
            cursor.execute("SELECT COUNT(*) FROM bills WHERE CustomerID = %s", (customer_id,))
            bill_count = cursor.fetchone()[0]
            
            if bill_count > 0:
                if not messagebox.askyesno("Warning", 
                    "This customer has existing bills. Deleting will also delete all their bills and bill items. Continue?"):
                    conn.close()
                    return
                
                # Delete related bill items first
                cursor.execute("""
                    DELETE bi FROM bill_items bi
                    INNER JOIN bills b ON bi.BillID = b.BillID
                    WHERE b.CustomerID = %s
                """, (customer_id,))
                
                # Delete bills
                cursor.execute("DELETE FROM bills WHERE CustomerID = %s", (customer_id,))
            
            # Finally delete the customer
            cursor.execute("DELETE FROM customers WHERE CustomerID = %s", (customer_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh the customer list
            view_customers(tree)
            
            messagebox.showinfo("Success", "Customer deleted successfully!")
            
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to delete customer: {str(e)}")

def update_stock_in_treeview(tree, product_id, new_stock):
    """Update stock value in treeview and refresh color coding"""
    # Find the item with matching product_id
    for item in tree.get_children():
        if tree.item(item)['values'][0] == product_id:
            values = list(tree.item(item)['values'])
            values[4] = new_stock  # Update stock value
            
            # Update tag based on new stock level
            tag = 'low_stock' if new_stock <= 5 else 'normal_stock'
            tree.item(item, values=values, tags=(tag,))
            break
    
    # Ensure tag colors are configured
    tree.tag_configure('low_stock', foreground='red')
    tree.tag_configure('normal_stock', foreground='white')

def add_to_bill():
    if not current_product:
        messagebox.showerror("Error", "Please select a product")
        return
            
    try:
        quantity = int(quantity_spinbox.get())
        if quantity <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        
        # Get fresh stock value from database
        conn = connect_db()
        if not conn:
            messagebox.showerror("Error", "Failed to connect to database")
            return
            
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT Stock, Name, Price
                FROM products
                WHERE ProductID = %s
            """, (current_product[0],))
            
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Product not found")
                return
                
            available_stock = result[0]
            product_name = result[1]
            current_price = float(result[2])
            
            if quantity > available_stock:
                messagebox.showerror("Error", 
                    f"Only {available_stock} units available in stock")
                return
            
            # Calculate subtotal
            subtotal = current_price * quantity
            
            # Add to bill items with correct structure
            item = {
                'product_id': current_product[0],
                'product': product_name,  # Using 'product' instead of 'name'
                'quantity': quantity,
                'price': current_price,
                'subtotal': subtotal
            }
            
            bill_items.append(item)
            
            # Update treeview
            items_tree.insert('', 'end', values=(
                product_name,
                quantity,
                f"₹{current_price:.2f}",
                f"₹{subtotal:.2f}"
            ))
            
            # Update total
            total = sum(item['subtotal'] for item in bill_items)
            total_label.config(text=f"₹{total:.2f}")
            
            # Enable save button if customer is selected
            if current_customer:
                save_button.config(state=NORMAL)
            
            # Reset product selection
            product_combo.set('')
            quantity_var.set(1)
            update_product_details()
            
        finally:
            conn.close()
            
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid quantity")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        print(f"Error details: {str(e)}")  # For debugging

def save_bill():
    """Save the current bill to database"""
    if not current_customer:
        messagebox.showerror("Error", "Please select a customer")
        return
    
    if not bill_items:
        messagebox.showerror("Error", "No items in bill")
        return
    
    try:
        conn = connect_db()
        if not conn:
            messagebox.showerror("Error", "Failed to connect to database")
            return
            
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute("START TRANSACTION")
            
            # Calculate total amount
            total_amount = sum(float(item['subtotal']) for item in bill_items)
            
            # Insert bill
            cursor.execute("""
                INSERT INTO bills (CustomerID, TotalAmount)
                VALUES (%s, %s)
            """, (current_customer[0], total_amount))
            
            bill_id = cursor.lastrowid
            
            # Insert bill items and update stock
            for item in bill_items:
                # Insert bill item
                cursor.execute("""
                    INSERT INTO bill_items (BillID, ProductID, ProductName, Quantity, Price, SubTotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    bill_id,
                    item['product_id'],
                    item['product'],  # Changed from 'name' to 'product'
                    int(item['quantity']),
                    float(item['price']),
                    float(item['subtotal'])
                ))
                
                # Update stock
                cursor.execute("""
                    UPDATE products 
                    SET Stock = Stock - %s 
                    WHERE ProductID = %s
                """, (int(item['quantity']), item['product_id']))
            
            # Commit transaction
            cursor.execute("COMMIT")
            
            # Generate PDF
            success = generate_pdf(bill_id)
            
            # Refresh the bills table
            load_bills(bills_tree)
            
            # Clear the current bill
            bill_items.clear()
            for item in items_tree.get_children():
                items_tree.delete(item)
            total_label.config(text="₹0.00")
            save_button.config(state=DISABLED)
            
            # Reset customer and product selections
            customer_combo.set('')
            product_combo.set('')
            quantity_var.set(1)
            update_customer_details()
            update_product_details()
            
            # Show success message
            if success:
                messagebox.showinfo("Success", "Bill saved and PDF generated successfully!")
            else:
                messagebox.showwarning("Warning", "Bill saved but PDF generation failed!")
            
        except Exception as e:
            # Rollback transaction on error
            cursor.execute("ROLLBACK")
            raise e
            
        finally:
            conn.close()
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
        print(f"Error details: {str(e)}")  # For debugging

def update_customer_details(event=None):
    """Update customer details when a customer is selected or typed"""
    global current_customer
    selected = customer_combo.get().strip()
    
    # Reset labels
    customer_name_label.config(text="Name: N/A")
    customer_contact_label.config(text="Contact: N/A")
    customer_email_label.config(text="Email: N/A")
    customer_address_label.config(text="Address: N/A")
    
    if not selected:
        current_customer = None
        save_button.config(state=DISABLED)
        return
    
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # For dropdown selection, exact match
            if event and event.type == '35': # <<ComboboxSelected>>
                name = selected.split(' (')[0] if ' (' in selected else selected
                cursor.execute("""
                    SELECT CustomerID, Name, Contact, Email, Address
                    FROM customers
                    WHERE Name = %s
                    LIMIT 1
                """, (name,))
            else:
                # For typing, partial match
                cursor.execute("""
                    SELECT CustomerID, Name, Contact, Email, Address
                    FROM customers
                    WHERE Name LIKE %s OR Contact LIKE %s
                    ORDER BY Name
                    LIMIT 1
                """, (f"%{selected}%", f"%{selected}%"))
            
            customer = cursor.fetchone()
            if customer:
                current_customer = customer
                customer_name_label.config(text=f"Name: {customer[1]}")
                customer_contact_label.config(text=f"Contact: {customer[2]}")
                customer_email_label.config(text=f"Email: {customer[3] or 'N/A'}")
                customer_address_label.config(text=f"Address: {customer[4] or 'N/A'}")
                
                # Enable save button if there are items
                if bill_items:
                    save_button.config(state=NORMAL)
            
            # Only update dropdown list when typing
            if not event or event.type != '35':
                cursor.execute("""
                    SELECT Name, Contact
                    FROM customers
                    WHERE Name LIKE %s OR Contact LIKE %s
                    ORDER BY Name
                """, (f"%{selected}%", f"%{selected}%"))
                
                matches = cursor.fetchall()
                if matches:
                    customer_combo['values'] = [f"{name} ({contact})" for name, contact in matches]
            
            conn.close()
            
    except Exception as e:
        print(f"Error updating customer details: {str(e)}")
        current_customer = None
        save_button.config(state=DISABLED)

def update_product_details(event=None):
    """Update product details when a product is selected or typed"""
    global current_product
    selected = product_combo.get().strip()
    
    # Reset labels and button state
    product_name_label.config(text="Name: N/A")
    product_price_label.config(text="Price: N/A")
    product_stock_label.config(text="Stock: N/A")
    add_button.config(state=DISABLED)
    
    if not selected:
        current_product = None
        return
            
    try:
        conn = connect_db()
        if not conn:
            messagebox.showerror("Error", "Failed to connect to database")
            return
            
        cursor = conn.cursor()
        
        try:
            # For dropdown selection, exact match
            if event and event.type == '35': # <<ComboboxSelected>>
                name = selected.split(' - ')[0] if ' - ' in selected else selected
                cursor.execute("""
                    SELECT ProductID, Name, Category, Price, Stock
                    FROM products
                    WHERE Name = %s AND Stock > 0
                    LIMIT 1
                """, (name,))
            else:
                # For typing, partial match
                cursor.execute("""
                    SELECT ProductID, Name, Category, Price, Stock
                    FROM products
                    WHERE (Name LIKE %s OR Category LIKE %s) AND Stock > 0
                    ORDER BY Name
                    LIMIT 1
                """, (f"%{selected}%", f"%{selected}%"))
            
            product = cursor.fetchone()
            if product:
                current_product = [
                    product[0],  # ProductID
                    product[1],  # Name
                    product[2],  # Category
                    float(product[3]),  # Price
                    int(product[4])   # Stock
                ]
                
                product_name_label.config(text=f"Name: {product[1]}")
                product_price_label.config(text=f"Price: ₹{float(product[3]):.2f}")
                product_stock_label.config(text=f"Stock: {product[4]}")
                
                # Enable add button if stock is available
                if product[4] > 0:
                    add_button.config(state=NORMAL)
                else:
                    add_button.config(state=DISABLED)
            
            # Only update dropdown list when typing
            if not event or event.type != '35':
                cursor.execute("""
                    SELECT Name, Category, Price, Stock
                    FROM products
                    WHERE (Name LIKE %s OR Category LIKE %s) AND Stock > 0
                    ORDER BY Name
                """, (f"%{selected}%", f"%{selected}%"))
                
                matches = cursor.fetchall()
                if matches:
                    product_combo['values'] = [f"{name} - {category} (₹{float(price)}) [Stock: {stock}]" 
                                            for name, category, price, stock in matches]
            
            conn.close()
            
        except Exception as e:
            print(f"Error updating product details: {str(e)}")
            current_product = None
            
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        current_product = None

def remove_selected():
    selected = items_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select an item to remove")
        return
    
    # Remove from bill items
    index = items_tree.index(selected[0])
    bill_items.pop(index)
    
    # Remove from treeview
    items_tree.delete(selected[0])
    
    # Update total
    total = sum(item['subtotal'] for item in bill_items)
    total_label.config(text=f"₹{total:.2f}")
    
    # Disable save button if no items
    if not bill_items:
        save_button.config(state=DISABLED)
    
def clear_all():
    if not bill_items:
        return
    
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all items?"):
        bill_items.clear()
        for item in items_tree.get_children():
            items_tree.delete(item)
        total_label.config(text="₹0.00")
        save_button.config(state=DISABLED)
    
def save_bill():
    if not current_customer:
        messagebox.showerror("Error", "Please select a customer")
        return
    
    if not bill_items:
        messagebox.showerror("Error", "No items in bill")
        return
    
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # Calculate total amount
            total_amount = sum(item['subtotal'] for item in bill_items)
            
            # Insert bill
            cursor.execute("""
                INSERT INTO bills (CustomerID, TotalAmount)
                VALUES (%s, %s)
            """, (current_customer[0], total_amount))
            
            bill_id = cursor.lastrowid
            
            # Insert bill items and update stock
            for item in bill_items:
                cursor.execute("""
                    INSERT INTO bill_items (BillID, ProductID, Quantity, Price, SubTotal, ProductName)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (bill_id, item['product_id'], item['quantity'], item['price'], item['subtotal'], item['product']))
                
                # Update stock in database
                cursor.execute("""
                    UPDATE products 
                    SET Stock = Stock - %s 
                    WHERE ProductID = %s
                """, (item['quantity'], item['product_id']))
                
                # Get updated stock value
                cursor.execute("""
                    SELECT Stock
                    FROM products
                    WHERE ProductID = %s
                """, (item['product_id'],))
                new_stock = cursor.fetchone()[0]
                
                # Update stock in treeview directly
                update_stock_in_treeview(products_tree, item['product_id'], new_stock)
            
            conn.commit()
            
            # Generate PDF
            if generate_pdf(bill_id):
                messagebox.showinfo("Success", "Bill saved and PDF generated successfully!")
            else:
                messagebox.showwarning("Warning", "Bill saved but PDF generation failed!")
            
            # Refresh the bills table
            load_bills(bills_tree)
            
            # Clear the current bill
            bill_items.clear()
            for item in items_tree.get_children():
                items_tree.delete(item)
            total_label.config(text="₹0.00")
            save_button.config(state=DISABLED)
            
            # Reset customer and product selections
            customer_combo.set('')
            product_combo.set('')
            quantity_var.set(1)
            update_customer_details()
            update_product_details()
            
            # Update product combobox
            refresh_product_list()
            
            conn.close()
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
    
    # Bind events
    add_button.config(command=add_to_bill)
    save_button.config(command=save_bill)
    
    # Bind events for both selection and typing
    customer_combo.bind('<<ComboboxSelected>>', update_customer_details)
    customer_combo.bind('<KeyRelease>', lambda e: update_customer_details())
    product_combo.bind('<<ComboboxSelected>>', update_product_details)
    product_combo.bind('<KeyRelease>', lambda e: update_product_details())
    
    # Load customers into combobox
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT CustomerID, Name, Contact FROM customers ORDER BY Name")
            customers = cursor.fetchall()
            customer_list = [f"{row[1]} ({row[2]})" for row in customers]
            customer_combo['values'] = customer_list
            conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    # Load products into combobox
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ProductID, Name, Category, Price, Stock FROM products WHERE Stock > 0 ORDER BY Name")
            products = cursor.fetchall()
            product_list = [f"{row[1]} - {row[2]} (₹{row[3]}) [Stock: {row[4]}]" for row in products]
            product_combo['values'] = product_list
            conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load products: {str(e)}")
    
    # Configure style for Comboboxes
    style = ttk.Style()
    style.configure('TCombobox',
                   background=ANIMATION['input'],
                   fieldbackground=ANIMATION['input'],
                   foreground=ANIMATION['text'],
                   arrowcolor=ANIMATION['text'])

def update_stock_and_ui(product_ids=None, check_low=True):
    """Update stock in UI and optionally check for low stock"""
    try:
        conn = connect_db()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # Get products with stock > 0
        cursor.execute("""
            SELECT p.ProductID, p.Name, p.Category, p.Price, p.Stock,
                   CASE WHEN p.Stock <= 5 AND p.Stock > 0 THEN 1 ELSE 0 END as is_low
            FROM products p
            WHERE p.Stock > 0 OR p.ProductID IN %s
            ORDER BY p.Name
        """, (tuple(product_ids) if product_ids else (-1,),))
        
        products = cursor.fetchall()
        low_stock_items = []
        
        # Update UI elements
        if 'products_tree' in globals():
            for item in products_tree.get_children():
                for product in products:
                    if int(products_tree.item(item)['values'][0]) == product[0]:
                        values = list(products_tree.item(item)['values'])
                        values[4] = product[4]  # Update stock
                        products_tree.item(item, values=values)
                        break
        
        # Update product combobox
        if 'product_combo' in globals():
            product_list = [f"{p[1]} - {p[2]} (₹{p[3]}) [Stock: {p[4]}]" for p in products]
            product_combo['values'] = product_list
            
        # Collect low stock items
        if check_low:
            low_stock_items = [(p[1], p[4]) for p in products if p[5] == 1]
            
            if low_stock_items:
                alert_message = "Low Stock Alert:\n\n" + \
                              "\n".join(f"• {name}: {stock} units remaining" 
                                      for name, stock in low_stock_items)
                messagebox.showwarning("Low Stock Alert", alert_message)
        
        conn.close()
        
    except Exception as e:
        print(f"Error updating stock and UI: {str(e)}")

def create_bill_ui():
    """Create a new bill with modern UI"""
    global current_product, current_customer, bill_items, product_combo, customer_combo, items_tree, total_label, save_button, add_button, quantity_spinbox, quantity_var, customer_name_label, customer_contact_label, customer_email_label, customer_address_label, product_name_label, product_price_label, product_stock_label

    # Initialize global variables
    current_product = None
    current_customer = None
    bill_items = []

    # Create bill window
    bill_window = Toplevel()
    bill_window.title("Create New Bill")
    bill_window.state('zoomed')
    bill_window.configure(bg=ANIMATION['primary'])

    # Configure style for widgets
    style = ttk.Style()
    style.configure('TCombobox',
                   background=ANIMATION['input'],
                   fieldbackground=ANIMATION['input'],
                   foreground=ANIMATION['text'],
                   arrowcolor=ANIMATION['text'])
    
    # Main container with padding
    main_frame = Frame(bill_window, bg=ANIMATION['primary'])
    main_frame.pack(fill=BOTH, expand=True, padx=30, pady=20)
    
    # Header frame with title and date
    header_frame = Frame(main_frame, bg=ANIMATION['primary'])
    header_frame.pack(fill=X, pady=(0, 20))
    
    # Title with larger font
    title_label = Label(header_frame,
                       text="Create New Bill",
                       font=('Segoe UI', 28, 'bold'),
                       bg=ANIMATION['primary'],
                       fg=ANIMATION['text'])
    title_label.pack(side=LEFT)
    
    # Date with gray color
    date_label = Label(header_frame,
                      text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      font=('Segoe UI', 14),
                      bg=ANIMATION['primary'],
                      fg=ANIMATION['text_secondary'])
    date_label.pack(side=RIGHT, pady=8)
    
    # Content frame with left and right panels
    content_frame = Frame(main_frame, bg=ANIMATION['primary'])
    content_frame.pack(fill=BOTH, expand=True)
    
    # Left panel for customer and product selection
    left_panel = Frame(content_frame, bg=ANIMATION['primary'], width=400)
    left_panel.pack(side=LEFT, fill=BOTH, padx=(0, 20))
    left_panel.pack_propagate(False)
    
    # Customer section
    customer_frame = Frame(left_panel, bg=ANIMATION['surface'], relief=FLAT, bd=1)
    customer_frame.pack(fill=X, pady=(0, 15))
    
    Label(customer_frame,
          text="Customer Details",
          font=('Segoe UI', 14, 'bold'),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text']).pack(fill=X, padx=20, pady=10)
    
    # Customer search frame
    customer_search_frame = Frame(customer_frame, bg=ANIMATION['surface'])
    customer_search_frame.pack(fill=X, padx=20, pady=(0, 10))
    
    Label(customer_search_frame,
          text="Select Customer",
          font=('Segoe UI', 10),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text_secondary']).pack(anchor=W, pady=(0, 5))
    
    # Customer Combobox
    customer_var = StringVar()
    customer_combo = ttk.Combobox(customer_search_frame,
                                textvariable=customer_var,
                                font=('Segoe UI', 12))
    customer_combo.pack(fill=X, ipady=4)
    
    # Customer info frame
    customer_info_frame = Frame(customer_frame, bg=ANIMATION['surface'])
    customer_info_frame.pack(fill=X, padx=20, pady=(0, 15))
    
    customer_name_label = Label(customer_info_frame,
                              text="Name: N/A",
                              font=('Segoe UI', 11),
                              bg=ANIMATION['surface'],
                              fg=ANIMATION['text'])
    customer_name_label.pack(fill=X, pady=2)
    
    customer_contact_label = Label(customer_info_frame,
                                 text="Contact: N/A",
                                 font=('Segoe UI', 11),
                                 bg=ANIMATION['surface'],
                                 fg=ANIMATION['text'])
    customer_contact_label.pack(fill=X, pady=2)
    
    customer_email_label = Label(customer_info_frame,
                               text="Email: N/A",
                               font=('Segoe UI', 11),
                               bg=ANIMATION['surface'],
                               fg=ANIMATION['text'])
    customer_email_label.pack(fill=X, pady=2)
    
    customer_address_label = Label(customer_info_frame,
                                 text="Address: N/A",
                                 font=('Segoe UI', 11),
                                 bg=ANIMATION['surface'],
                                 fg=ANIMATION['text'])
    customer_address_label.pack(fill=X, pady=2)
    
    # Product section
    product_frame = Frame(left_panel, bg=ANIMATION['surface'], relief=FLAT, bd=1)
    product_frame.pack(fill=X)
    
    Label(product_frame,
          text="Product Details",
          font=('Segoe UI', 14, 'bold'),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text']).pack(fill=X, padx=20, pady=10)
    
    # Product search frame
    product_search_frame = Frame(product_frame, bg=ANIMATION['surface'])
    product_search_frame.pack(fill=X, padx=20, pady=(0, 10))
    
    Label(product_search_frame,
          text="Select Product",
          font=('Segoe UI', 10),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text_secondary']).pack(anchor=W, pady=(0, 5))
    
    # Product Combobox
    product_var = StringVar()
    product_combo = ttk.Combobox(product_search_frame,
                               textvariable=product_var,
                               font=('Segoe UI', 12))
    product_combo.pack(fill=X, ipady=4)
    
    # Product info frame
    product_info_frame = Frame(product_frame, bg=ANIMATION['surface'])
    product_info_frame.pack(fill=X, padx=20, pady=(0, 10))
    
    product_name_label = Label(product_info_frame,
                             text="Name: N/A",
                             font=('Segoe UI', 11),
                             bg=ANIMATION['surface'],
                             fg=ANIMATION['text'])
    product_name_label.pack(fill=X, pady=2)
    
    product_price_label = Label(product_info_frame,
                              text="Price: N/A",
                              font=('Segoe UI', 11),
                              bg=ANIMATION['surface'],
                              fg=ANIMATION['text'])
    product_price_label.pack(fill=X, pady=2)
    
    product_stock_label = Label(product_info_frame,
                              text="Stock: N/A",
                              font=('Segoe UI', 11),
                              bg=ANIMATION['surface'],
                              fg=ANIMATION['text'])
    product_stock_label.pack(fill=X, pady=2)
    
    # Quantity frame
    quantity_frame = Frame(product_frame, bg=ANIMATION['surface'])
    quantity_frame.pack(fill=X, padx=20, pady=(5, 15))
    
    Label(quantity_frame,
          text="Quantity:",
          font=('Segoe UI', 11),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text']).pack(side=LEFT)
    
    quantity_var = IntVar(value=1)
    quantity_spinbox = Spinbox(quantity_frame,
                             from_=1,
                             to=999,
                             textvariable=quantity_var,
                             font=('Segoe UI', 11),
                             width=5,
                             bg=ANIMATION['input'],
                             fg=ANIMATION['text'])
    quantity_spinbox.pack(side=LEFT, padx=10)
    
    # Add to bill button
    add_button = Button(product_frame,
                       text="Add to Bill",
                       font=('Segoe UI', 12, 'bold'),
                       bg='#3498db',
                       fg='white',
                       state=DISABLED,
                       command=lambda: add_to_bill())
    add_button.pack(fill=X, padx=20, pady=(0, 15), ipady=8)
    
    # Right panel for bill items
    right_panel = Frame(content_frame, bg=ANIMATION['primary'])
    right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
    
    # Bill items frame
    items_frame = Frame(right_panel, bg=ANIMATION['surface'], relief=FLAT, bd=1)
    items_frame.pack(fill=BOTH, expand=True)
    
    # Action buttons frame
    action_frame = Frame(items_frame, bg=ANIMATION['surface'])
    action_frame.pack(fill=X, padx=20, pady=10)
    
    Label(action_frame,
          text="Bill Items",
          font=('Segoe UI', 14, 'bold'),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text']).pack(side=LEFT)
    
    Button(action_frame,
           text="Clear All",
           font=('Segoe UI', 11),
           bg=ANIMATION['warning'],
           fg='white',
           command=lambda: clear_all()).pack(side=RIGHT, padx=5)
    
    # Create treeview
    tree_frame = Frame(items_frame, bg=ANIMATION['surface'])
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 10))
    
    columns = ("Product", "Quantity", "Price", "Subtotal")
    items_tree = ttk.Treeview(tree_frame,
                             columns=columns,
                             show="headings")
    
    # Configure columns
    items_tree.heading("Product", text="Product")
    items_tree.heading("Quantity", text="Quantity")
    items_tree.heading("Price", text="Price")
    items_tree.heading("Subtotal", text="Subtotal")
    
    items_tree.column("Product", width=300)
    items_tree.column("Quantity", width=100, anchor=CENTER)
    items_tree.column("Price", width=150, anchor=E)
    items_tree.column("Subtotal", width=150, anchor=E)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=items_tree.yview)
    items_tree.configure(yscrollcommand=scrollbar.set)
    
    items_tree.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    # Bill summary frame
    summary_frame = Frame(right_panel, bg=ANIMATION['surface'], height=100)
    summary_frame.pack(fill=X, pady=(15, 0))
    summary_frame.pack_propagate(False)
    
    # Total amount
    total_frame = Frame(summary_frame, bg=ANIMATION['surface'])
    total_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20)
    
    Label(total_frame,
          text="Total Amount",
          font=('Segoe UI', 12),
          bg=ANIMATION['surface'],
          fg=ANIMATION['text_secondary']).pack(anchor=W, pady=(10, 2))
    
    total_label = Label(total_frame,
                       text="₹0.00",
                       font=('Segoe UI', 24, 'bold'),
                       bg=ANIMATION['surface'],
                       fg=ANIMATION['text'])
    total_label.pack(anchor=W)
    
    # Save button
    save_frame = Frame(summary_frame, bg=ANIMATION['surface'])
    save_frame.pack(side=RIGHT, fill=Y, padx=20, pady=20)
    
    save_button = Button(save_frame,
                        text="Save Bill",
                        font=('Segoe UI', 12, 'bold'),
                        bg='#2ecc71',
                        fg='white',
                        width=15,
                        state=DISABLED,
                        command=lambda: save_bill())
    save_button.pack(fill=Y)
    
    # Bind events for both selection and typing
    customer_combo.bind('<<ComboboxSelected>>', update_customer_details)
    customer_combo.bind('<KeyRelease>', lambda e: bill_window.after(100, update_customer_details))
    product_combo.bind('<<ComboboxSelected>>', update_product_details)
    product_combo.bind('<KeyRelease>', lambda e: bill_window.after(100, update_product_details))
    
    # Load initial data
    refresh_customer_list()
    refresh_product_list()
    
    # Center the window
    bill_window.update_idletasks()
    width = bill_window.winfo_width()
    height = bill_window.winfo_height()
    x = (bill_window.winfo_screenwidth() // 2) - (width // 2)
    y = (bill_window.winfo_screenheight() // 2) - (height // 2)
    bill_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Make window modal
    bill_window.transient(bill_window.master)
    bill_window.grab_set()
    bill_window.focus_set()

def refresh_customer_list():
    """Refresh the customer list in the combobox"""
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT CustomerID, Name, Contact FROM customers ORDER BY Name")
            customers = cursor.fetchall()
            customer_combo['values'] = [f"{row[1]} ({row[2]})" for row in customers]
            conn.close()
    except Exception as e:
        print(f"Error refreshing customer list: {str(e)}")

def refresh_product_list():
    """Refresh the product list in combobox with current stock values"""
    try:
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ProductID, Name, Category, Price, Stock 
                FROM products 
                WHERE Stock > 0 
                ORDER BY Name
            """)
            products = cursor.fetchall()
            product_list = [f"{row[1]} - {row[2]} (₹{row[3]}) [Stock: {row[4]}]" for row in products]
            
            # Only update if product_combo exists and is a valid widget
            if 'product_combo' in globals() and isinstance(product_combo, ttk.Combobox):
                product_combo['values'] = product_list
                
            conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load products: {str(e)}")

def create_account():
    """Create a new user account"""
    # Create a new window for account creation
    create_window = Toplevel()
    create_window.title("Create New Account")
    create_window.configure(bg='#1e1e2d')  # Dark navy background
    
    # Set window size and position - reduced height
    window_width = 400
    window_height = 400  # Reduced from 450
    screen_width = create_window.winfo_screenwidth()
    screen_height = create_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    create_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container with reduced padding
    main_frame = Frame(create_window, bg='#1e1e2d')
    main_frame.pack(fill=BOTH, expand=True, padx=30, pady=15)  # Reduced padding
    
    # Title with reduced padding
    title_label = Label(main_frame,
                       text="Create New Account",
                       font=('Segoe UI', 20, 'bold'),  # Reduced font size
                       bg='#1e1e2d',
                       fg='white')
    title_label.pack(pady=(0, 15))  # Reduced padding
    
    # Username field with reduced spacing
    username_frame = Frame(main_frame, bg='#1e1e2d')
    username_frame.pack(fill=X, pady=3)  # Reduced padding
    
    username_label = Label(username_frame,
                         text="Username",
                         font=('Segoe UI', 11),  # Slightly smaller font
                         bg='#1e1e2d',
                         fg='white')
    username_label.pack(anchor=W)
    
    username_entry = Entry(username_frame,
                         font=('Segoe UI', 11),
                         bg='#2d2d3d',
                         fg='white',
                         insertbackground='white',
                         relief=FLAT)
    username_entry.pack(fill=X, pady=(3, 0), ipady=6)  # Reduced padding
    
    # Password field with reduced spacing
    password_frame = Frame(main_frame, bg='#1e1e2d')
    password_frame.pack(fill=X, pady=3)  # Reduced padding
    
    password_label = Label(password_frame,
                         text="Password",
                         font=('Segoe UI', 11),
                         bg='#1e1e2d',
                         fg='white')
    password_label.pack(anchor=W)
    
    password_entry = Entry(password_frame,
                         font=('Segoe UI', 11),
                         bg='#2d2d3d',
                         fg='white',
                         insertbackground='white',
                         relief=FLAT,
                         show="●")
    password_entry.pack(fill=X, pady=(3, 0), ipady=6)
    
    # Confirm Password field with reduced spacing
    confirm_frame = Frame(main_frame, bg='#1e1e2d')
    confirm_frame.pack(fill=X, pady=3)  # Reduced padding
    
    confirm_label = Label(confirm_frame,
                        text="Confirm Password",
                        font=('Segoe UI', 11),
                        bg='#1e1e2d',
                        fg='white')
    confirm_label.pack(anchor=W)
    
    confirm_entry = Entry(confirm_frame,
                        font=('Segoe UI', 11),
                        bg='#2d2d3d',
                        fg='white',
                        insertbackground='white',
                        relief=FLAT,
                        show="●")
    confirm_entry.pack(fill=X, pady=(3, 0), ipady=6)
    
    confirm_entry.pack(fill=X, pady=(5, 0), ipady=8)
    
    # Error label
    error_label = Label(main_frame,
                      text="",
                      font=('Segoe UI', 10),
                      bg='#1e1e2d',
                      fg='#f64e60',  # Red color for errors
                      wraplength=300)
    error_label.pack(pady=10)
    
    def save_account():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_entry.get().strip()
        
        if not username or not password or not confirm_password:
            error_label.config(text="Please fill in all fields")
            return
        
        if password != confirm_password:
            error_label.config(text="Passwords do not match")
            return
        
        try:
            conn = connect_db()
            if not conn:
                error_label.config(text="Database connection failed")
                return
            
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT UserID FROM users WHERE Username = %s", (username,))
            if cursor.fetchone():
                error_label.config(text="Username already exists")
                return
            
            # Hash password and insert user
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (Username, Password)
                VALUES (%s, %s)
            """, (username, hashed_password))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Account created successfully!")
            create_window.destroy()
            
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
    
    # Create account button with hover effect
    create_btn = Button(main_frame,
                       text="Create Account",
                       font=('Segoe UI', 12, 'bold'),
                       bg='#3699ff',  # Blue color
                       fg='white',
                       activebackground='#1e88e5',  # Darker blue for hover
                       activeforeground='white',
                       relief=FLAT,
                       cursor='hand2',
                       command=save_account)
    create_btn.pack(fill=X, ipady=10, pady=(10, 5))
    
    def on_enter(e):
        create_btn.config(bg='#1e88e5')
    
    def on_leave(e):
        create_btn.config(bg='#3699ff')
    
    create_btn.bind('<Enter>', on_enter)
    create_btn.bind('<Leave>', on_leave)
    
    # Links frame for multiple options
    links_frame = Frame(main_frame, bg='#1e1e2d')
    links_frame.pack(fill=X, pady=5)
    
    # Delete Account link
    delete_label = Label(links_frame,
                      text="Delete Account",
                      font=('Segoe UI', 10),
                      bg='#1e1e2d',
                      fg='#f64e60',  # Red color for delete
                      cursor='hand2')
    delete_label.pack(side=LEFT, padx=5)
    delete_label.bind('<Button-1>', lambda e: [create_window.destroy(), delete_account()])
    
    # Back to Login link
    back_label = Label(links_frame,
                      text="Back to Login",
                      font=('Segoe UI', 10),
                      bg='#1e1e2d',
                      fg='#3699ff',
                      cursor='hand2')
    back_label.pack(side=RIGHT, padx=5)
    back_label.bind('<Button-1>', lambda e: create_window.destroy())
    
    # Set focus to username field
    username_entry.focus()
    
    # Bind Enter key to save
    create_window.bind('<Return>', lambda e: save_account())
    
    # Make window modal
    create_window.transient(create_window.master)
    create_window.grab_set()
    create_window.focus_force()

def view_pdf(bill_id):
    """View the PDF file for a bill"""
    try:
        conn = connect_db()
        if not conn:
            raise Exception("Failed to connect to database")
        
        cursor = conn.cursor()
        
        # Check if PDF exists
        cursor.execute("SELECT PDFPath FROM bills WHERE BillID = %s", (bill_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            # Generate new PDF if not exists
            if generate_pdf(bill_id):
                cursor.execute("SELECT PDFPath FROM bills WHERE BillID = %s", (bill_id,))
                result = cursor.fetchone()
            else:
                raise Exception("Failed to generate PDF")
        
        pdf_path = result[0]
        conn.close()
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            # Try to generate new PDF
            if generate_pdf(bill_id):
                # Get new path
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT PDFPath FROM bills WHERE BillID = %s", (bill_id,))
                result = cursor.fetchone()
                pdf_path = result[0]
                conn.close()
            else:
                raise Exception("PDF file not found and generation failed")
        
        # Open PDF
        try:
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            else:  # Linux/Mac
                subprocess.run(['xdg-open', pdf_path])
        except Exception as e:
            raise Exception(f"Failed to open PDF: {str(e)}")
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_account():
    """Delete an existing user account"""
    delete_window = Toplevel()
    delete_window.title("Delete Account")
    delete_window.configure(bg='#1e1e2d')
    
    # Set window size and position
    window_width = 400
    window_height = 350  # Increased height to accommodate button
    screen_width = delete_window.winfo_screenwidth()
    screen_height = delete_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    delete_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container
    main_frame = Frame(delete_window, bg='#1e1e2d')
    main_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)
    
    # Title
    title_label = Label(main_frame,
                       text="Delete Account",
                       font=('Segoe UI', 20, 'bold'),
                       bg='#1e1e2d',
                       fg='white')
    title_label.pack(pady=(0, 20))
    
    # Username field
    username_frame = Frame(main_frame, bg='#1e1e2d')
    username_frame.pack(fill=X, pady=5)
    
    username_label = Label(username_frame,
                         text="Username",
                         font=('Segoe UI', 11),
                         bg='#1e1e2d',
                         fg='white')
    username_label.pack(anchor=W)
    
    username_entry = Entry(username_frame,
                         font=('Segoe UI', 11),
                         bg='#2d2d3d',
                         fg='white',
                         insertbackground='white',
                         relief=FLAT)
    username_entry.pack(fill=X, pady=(3, 0), ipady=6)
    
    # Password field for confirmation
    password_frame = Frame(main_frame, bg='#1e1e2d')
    password_frame.pack(fill=X, pady=5)
    
    password_label = Label(password_frame,
                         text="Password",
                         font=('Segoe UI', 11),
                         bg='#1e1e2d',
                         fg='white')
    password_label.pack(anchor=W)
    
    password_entry = Entry(password_frame,
                         font=('Segoe UI', 11),
                         bg='#2d2d3d',
                         fg='white',
                         insertbackground='white',
                         relief=FLAT,
                         show="●")
    password_entry.pack(fill=X, pady=(3, 0), ipady=6)
    
    # Error label
    error_label = Label(main_frame,
                      text="",
                      font=('Segoe UI', 10),
                      bg='#1e1e2d',
                      fg='#f64e60',
                      wraplength=300)
    error_label.pack(pady=10)
    
    def confirm_delete():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            error_label.config(text="Please fill in all fields")
            return
        
        try:
            conn = connect_db()
            if not conn:
                error_label.config(text="Database connection failed")
                return
            
            cursor = conn.cursor()
            
            # Verify credentials
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("SELECT UserID FROM users WHERE Username = %s AND Password = %s",
                         (username, hashed_password))
            user = cursor.fetchone()
            
            if not user:
                error_label.config(text="Invalid username or password")
                return
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete your account?\nThis action cannot be undone!",
                                 icon='warning'):
                # Delete the user
                cursor.execute("DELETE FROM users WHERE UserID = %s", (user[0],))
                conn.commit()
                messagebox.showinfo("Success", "Account deleted successfully!")
                delete_window.destroy()
            
            conn.close()
            
        except Exception as e:
            error_label.config(text=f"Error: {str(e)}")
    
    # Button frame
    button_frame = Frame(main_frame, bg='#1e1e2d')
    button_frame.pack(fill=X, pady=10)
    
    # Delete button with hover effect
    delete_btn = Button(button_frame,
                       text="Delete Account",
                       font=('Segoe UI', 11, 'bold'),
                       bg='#f64e60',  # Red color for delete
                       fg='white',
                       activebackground='#e5404f',  # Darker red for hover
                       activeforeground='white',
                       relief=FLAT,
                       cursor='hand2',
                       command=confirm_delete)
    delete_btn.pack(fill=X, ipady=8)
    
    def on_enter(e):
        delete_btn.config(bg='#e5404f')
    
    def on_leave(e):
        delete_btn.config(bg='#f64e60')
    
    delete_btn.bind('<Enter>', on_enter)
    delete_btn.bind('<Leave>', on_leave)
    
    # Back to login link
    back_label = Label(main_frame,
                      text="Back to Login",
                      font=('Segoe UI', 10),
                      bg='#1e1e2d',
                      fg='#3699ff',
                      cursor='hand2')
    back_label.pack(pady=5)
    back_label.bind('<Button-1>', lambda e: delete_window.destroy())
    
    # Set focus to username field
    username_entry.focus()
    
    # Bind Enter key
    delete_window.bind('<Return>', lambda e: confirm_delete())
    
    # Make window modal
    delete_window.transient(delete_window.master)
    delete_window.grab_set()
    delete_window.focus_force()

# Start the application
if __name__ == "__main__":
    # Start with login window
    login_window()