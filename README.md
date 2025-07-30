Supermarket Billing System

A modern and intuitive Supermarket Billing System built with Python's Tkinter for the GUI and MySQL for robust data management. This application provides comprehensive functionalities for managing customers, products, and sales transactions, including PDF bill generation and stock alerts.

✨ Features
User Authentication: Secure login, account creation, and deletion with hashed passwords.

Customer Management:

Add, view, and search customer details.

Delete customers (with cascading deletion of associated bills).

Product Management:

Add, view, and search product details.

Restock products with quantity updates.

Automated low stock alerts.

Delete products (retaining historical data in bills).

Billing & Sales:

Create new bills by selecting customers and adding products.

Real-time total amount calculation.

Generate professional PDF bills for each transaction.

View historical bills and their details.

Delete all bills functionality.

Modern UI/UX:

Sleek dark theme with clear visual hierarchy.

Smooth animations for window transitions and button hovers.

Custom rounded entry widgets for improved aesthetics.

Tabbed interface for easy navigation between sections.

Robust Database Handling:

Uses MySQL for reliable data storage.

Includes automatic database and table setup on first run.

Ensures data integrity with foreign key constraints and transaction management for billing operations.

🚀 Technologies Used
Frontend: Python (Tkinter, ttk, PIL - Pillow)

Backend: MySQL

Core Libraries:

mysql.connector: For connecting Python to MySQL.

fpdf: For generating PDF bills.

Pillow (PIL): For image manipulation (e.g., background images).

hashlib: For secure password hashing.

datetime: For handling dates and times in bills.

subprocess, os, time, messagebox, filedialog: Standard Python modules for system interaction, messaging, and timing.

🛠️ Setup and Installation
Follow these steps to get the project up and running on your local machine.

1. Prerequisites
Python 3.9+: Download Python (Python 3.11 or 3.12 is recommended for best compatibility).

MySQL Server: You need a running MySQL server. [suspicious link removed]

During MySQL installation, remember your root password.

Git: Download Git

2. Clone the Repository
Open your terminal or command prompt and clone the project:
