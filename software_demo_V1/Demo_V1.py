import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import os
from datetime import datetime

# Dictionary to store active serial connections
serial_conns = {}
# Available baud rates for selection
baud_rates = [9600, 115200, 230400, 460800, 921600]
# Dictionary to store received messages per port
received_messages = {}
# Variable to store the last received data
last_received_data = ""
# Counter for tracking program runs
program_count = 0

# Function to get available serial ports
def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to establish a serial connection
def connect():
    global program_count
    port = port_var.get()
    baud_rate = int(baud_var.get())
    if not port:
        messagebox.showerror("Error", "No port selected!")
        return
    try:
        # Open the serial connection
        serial_conns[port] = serial.Serial(port=port, baudrate=baud_rate, timeout=1)
        connect_button.config(state=tk.DISABLED)
        disconnect_button.config(state=tk.NORMAL)
        send_button.config(state=tk.NORMAL)
        upload_button.config(state=tk.NORMAL)
        output_label.config(text=f"Connected to {port} at {baud_rate} baud")
        received_messages[port] = []
        # Start a new thread to receive data continuously
        threading.Thread(target=receive_continuous, args=(port,), daemon=True).start()
        program_count += 1
        update_program_info()
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))

# Function to disconnect the serial port
def disconnect():
    port = port_var.get()
    if port in serial_conns:
        serial_conns[port].close()
        del serial_conns[port]
        connect_button.config(state=tk.NORMAL)
        disconnect_button.config(state=tk.DISABLED)
        send_button.config(state=tk.DISABLED)
        upload_button.config(state=tk.DISABLED)
        output_label.config(text="Disconnected")

# Function to send data through serial port
def send_data():
    port = port_var.get()
    if port in serial_conns:
        data = entry.get()
        if data:
            serial_conns[port].write(data.encode() + b'\n')
            output_label.config(text=f"Sent to {port}: {data}")
    else:
        messagebox.showwarning("Warning", "Not connected to any port")

# Function to continuously receive data from the serial port
def receive_continuous(port):
    global last_received_data
    while port in serial_conns:
        try:
            if serial_conns[port].in_waiting > 0:
                received = serial_conns[port].readline().decode().strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                received_messages[port].append(f"[{timestamp}] {received}")
                last_received_data = received
                update_received_window()
        except Exception:
            break
        time.sleep(0.1)

# Function to update the received messages display
def update_received_window():
    received_text.delete(1.0, tk.END)
    for port, messages in received_messages.items():
        received_text.insert(tk.END, f"\n{port} Messages:\n" + "\n".join(messages) + "\n")
    received_text.insert(tk.END, f"\nLast Received Data: {last_received_data}\n")
    received_text.yview(tk.END)
    root.after(1000, update_received_window)  # Update every second

# Function to upload and display HEX file information
def upload_hex_file():
    file_path = filedialog.askopenfilename(filetypes=[("HEX files", "*.hex")])
    if file_path:
        file_size = os.path.getsize(file_path)
        last_modified = time.ctime(os.path.getmtime(file_path))
        output_label.config(text=f"HEX file: {file_path} | Size: {file_size} bytes | Last Modified: {last_modified}")

# Function to refresh available ports
def refresh_ports():
    port_dropdown.config(values=get_available_ports())

# Function to update program run information
def update_program_info():
    program_info_label.config(text=f"Program Runs: {program_count}")

# Create the main GUI window
root = tk.Tk()
root.title("SPIC - Serial Communication")
root.geometry("800x600")
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

# UI Components for serial port selection
tk.Label(frame, text="Select Port:", font=("Arial", 14)).grid(row=0, column=0, padx=5)
port_var = tk.StringVar(value="")
port_dropdown = ttk.Combobox(frame, textvariable=port_var, values=get_available_ports(), width=20, font=("Arial", 12))
port_dropdown.grid(row=0, column=1, padx=5)
refresh_button = tk.Button(frame, text="Refresh", command=refresh_ports, font=("Arial", 12))
refresh_button.grid(row=0, column=2, padx=5)

# UI Components for baud rate selection
tk.Label(frame, text="Baud Rate:", font=("Arial", 14)).grid(row=1, column=0, padx=5)
baud_var = tk.StringVar(value=str(baud_rates[0]))
baud_dropdown = ttk.Combobox(frame, textvariable=baud_var, values=baud_rates, width=15, font=("Arial", 12))
baud_dropdown.grid(row=1, column=1, padx=5)

# Connection buttons
connect_button = tk.Button(frame, text="Connect", command=connect, font=("Arial", 12))
connect_button.grid(row=2, column=0, padx=5, pady=10)
disconnect_button = tk.Button(frame, text="Disconnect", command=disconnect, state=tk.DISABLED, font=("Arial", 12))
disconnect_button.grid(row=2, column=1, padx=5, pady=10)

# Data sending UI
entry = tk.Entry(frame, width=30, font=("Arial", 12))
entry.grid(row=3, column=0, padx=5)
send_button = tk.Button(frame, text="Send", command=send_data, state=tk.DISABLED, font=("Arial", 12))
send_button.grid(row=3, column=1, padx=5)

# Received messages display
received_text = tk.Text(frame, height=15, width=60, font=("Arial", 12))
received_text.grid(row=4, column=0, columnspan=3, pady=10)

# HEX file upload UI
upload_button = tk.Button(frame, text="Upload HEX", command=upload_hex_file, state=tk.DISABLED, font=("Arial", 12))
upload_button.grid(row=5, column=1, padx=5)

# Status labels
output_label = tk.Label(frame, text="Not connected", font=("Arial", 14))
output_label.grid(row=6, column=0, columnspan=3, pady=5)
program_info_label = tk.Label(root, text="", font=("Arial", 12))
program_info_label.pack(pady=10)

# Start updating received messages# Start updating received messages\update_received_window()

# Run the Tkinter main event loop
root.mainloop()
