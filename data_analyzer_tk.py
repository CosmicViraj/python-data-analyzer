import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global variable for the DataFrame
df = None

def load_data():
    """Opens a file dialog, loads the CSV into a DataFrame, and updates the status."""
    global df
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        # 1. Pandas: Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Clear previous output
        output_text.delete(1.0, tk.END)

        # Update the status and enable analysis buttons (Uses 'style' for ttk widget)
        status_label.config(text=f"File loaded: {file_path.split('/')[-1]}", style="Green.TLabel")
        analyze_button.config(state=tk.NORMAL)
        visualize_button.config(state=tk.NORMAL)

        # Populate the column dropdown for visualization
        numerical_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        col_select_var.set(numerical_cols[0] if numerical_cols else "")

        # Clear and repopulate the OptionMenu with numerical columns
        col_select_menu['menu'].delete(0, 'end')
        for col in numerical_cols:
            col_select_menu['menu'].add_command(label=col, command=tk._setit(col_select_var, col))

    except Exception as e:
        df = None
        # Update status with error (Uses 'style' for ttk widget)
        status_label.config(text=f"Error loading file: {e}", style="Red.TLabel")
        analyze_button.config(state=tk.DISABLED)
        visualize_button.config(state=tk.DISABLED)
        messagebox.showerror("Loading Error", f"Could not load file. Details: {e}")

def show_statistics():
    """Calculates and displays descriptive statistics using Pandas and NumPy."""
    global df
    if df is None:
        messagebox.showerror("Error", "Please load a dataset first.")
        return

    # Clear previous output
    output_text.delete(1.0, tk.END)

    # 2. Pandas: Generate descriptive statistics
    stats_df = df.describe()

    output_text.insert(tk.END, "### Descriptive Statistics (Pandas) ###\n\n")
    output_text.insert(tk.END, stats_df.to_string())

    # NumPy: Example of explicit NumPy usage: calculating range (Max - Min)
    output_text.insert(tk.END, "\n\n### Additional NumPy Analysis (Range) ###\n")
    for col in stats_df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # NumPy: Calculate range using max and min
            data_range = np.max(df[col]) - np.min(df[col])
            output_text.insert(tk.END, f"Range for **{col}**: {data_range:.2f}\n")

def visualize_data():
    """Generates a histogram for the selected numerical column using Matplotlib."""
    global df
    if df is None:
        messagebox.showerror("Error", "Please load a dataset first.")
        return

    column_name = col_select_var.get()
    if not column_name or column_name not in df.columns or not pd.api.types.is_numeric_dtype(df[column_name]):
        messagebox.showerror("Error", "Please select a valid numerical column for visualization.")
        return

    # Clear previous plot frame content
    for widget in plot_frame.winfo_children():
        widget.destroy()

    # 3. Matplotlib: Create a figure for the histogram
    fig, ax = plt.subplots(figsize=(5, 4))

    # Use Matplotlib to plot the histogram
    df[column_name].hist(ax=ax, bins=20, edgecolor='black')

    ax.set_title(f'Histogram of {column_name}')
    ax.set_xlabel(column_name)
    ax.set_ylabel('Frequency')

    # 4. Tkinter & Matplotlib Integration: Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()


# --- TKINTER GUI SETUP ---
root = tk.Tk()
root.title("Multi-Library Data Analyzer (Pandas/NumPy/Tkinter)")
root.geometry("800x600")

# --- Styling Fix: Define styles for ttk widgets ---
# This fixes the "_tkinter.TclError: unknown option '-fg'" error
style = ttk.Style()
style.configure("Green.TLabel", foreground="green")
style.configure("Red.TLabel", foreground="red")

# --- Top Frame for File Operations and Status ---
top_frame = ttk.Frame(root, padding="10 10 10 10")
top_frame.pack(fill=tk.X)

load_button = ttk.Button(top_frame, text="Load CSV File", command=load_data)
load_button.pack(side=tk.LEFT, padx=5)

status_label = ttk.Label(top_frame, text="No file loaded.", style="Red.TLabel")
status_label.pack(side=tk.LEFT, padx=10)

# --- Middle Frame for Analysis and Visualization Controls ---
control_frame = ttk.Frame(root, padding="10 0 10 10")
control_frame.pack(fill=tk.X)

# Analysis Button
analyze_button = ttk.Button(control_frame, text="Show Statistics", command=show_statistics, state=tk.DISABLED)
analyze_button.pack(side=tk.LEFT, padx=5)

# Visualization Controls
ttk.Label(control_frame, text="Column for Plot:").pack(side=tk.LEFT, padx=(20, 5))
col_select_var = tk.StringVar(root)
col_select_var.set("") # Initial empty value
col_select_menu = ttk.OptionMenu(control_frame, col_select_var, "")
col_select_menu.pack(side=tk.LEFT, padx=5)

visualize_button = ttk.Button(control_frame, text="Plot Histogram", command=visualize_data, state=tk.DISABLED)
visualize_button.pack(side=tk.LEFT, padx=5)

# --- Main Content Area ---
main_paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
main_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

# 1. Output Text Area (Left Pane)
output_frame = ttk.Frame(main_paned_window, width=300)
output_text = tk.Text(output_frame, wrap=tk.WORD, height=10, width=40, font=('Courier', 10))
output_scroll = ttk.Scrollbar(output_frame, command=output_text.yview)
output_text.config(yscrollcommand=output_scroll.set)

output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

main_paned_window.add(output_frame, weight=1)

# 2. Plot Area (Right Pane)
plot_frame = ttk.Frame(main_paned_window, width=500)
main_paned_window.add(plot_frame, weight=2)

root.mainloop()