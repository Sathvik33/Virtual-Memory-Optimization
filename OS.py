import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# Global variables
frames = []
page_faults = 0
frame_size = 3
pages = []
current_index = 0
algorithm = "LRU"
clock_pointer = []

def update_visualization():
    ax.clear()
    ax.set_xticks(range(frame_size))
    ax.set_xticklabels([f"Frame {i+1}" for i in range(frame_size)], fontsize=10)
    ax.set_yticks([])

    colors = []
    labels = []
    for i in range(frame_size):
        if i < len(frames):
            colors.append('coral' if frames[i] == pages[current_index-1] else 'lightgreen')
            labels.append(str(frames[i]))
        else:
            colors.append('gray')
            labels.append('')

    bars = ax.bar(range(frame_size), [1]*frame_size, color=colors)
    for bar, label in zip(bars, labels):
        ax.text(bar.get_x() + bar.get_width()/2, 0.5, label,
                ha='center', va='center', color='white', fontsize=12)

    canvas.draw()

def log_message(message):
    log_text.insert(tk.END, f"{time.strftime('[%H:%M:%S]')} {message}\n")
    log_text.see(tk.END)

def run_algorithm():
    global current_index, page_faults

    if current_index >= len(pages):
        log_message(f"Simulation complete! Total Page Faults: {page_faults}")
        return

    page = pages[current_index]

    if algorithm == "LRU":
        if page in frames:
            frames.remove(page)
            frames.append(page)
            log_message(f"Page {page} → HIT (Frames: {frames})")
        else:
            if len(frames) < frame_size:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
            page_faults += 1
            log_message(f"Page {page} → MISS (Frames: {frames})")

    elif algorithm == "FIFO":
        if page in frames:
            log_message(f"Page {page} → HIT (Frames: {frames})")
        else:
            if len(frames) < frame_size:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
            page_faults += 1
            log_message(f"Page {page} → MISS (Frames: {frames})")

    elif algorithm == "Optimal":
        if page in frames:
            log_message(f"Page {page} → HIT (Frames: {frames})")
        else:
            if len(frames) < frame_size:
                frames.append(page)
            else:
                farthest = -1
                replace_index = 0
                for i, frame in enumerate(frames):
                    if frame not in pages[current_index+1:]:
                        replace_index = i
                        break
                    next_use = pages[current_index+1:].index(frame)
                    if next_use > farthest:
                        farthest = next_use
                        replace_index = i
                frames[replace_index] = page
            page_faults += 1
            log_message(f"Page {page} → MISS (Frames: {frames})")

    elif algorithm == "Clock" or algorithm == "Clock-2":
        if page in frames:
            index = frames.index(page)
            clock_pointer[index] = 1
            log_message(f"Page {page} → HIT (Frames: {frames})")
        else:
            if len(frames) < frame_size:
                frames.append(page)
                clock_pointer.append(1)
            else:
                while True:
                    if clock_pointer[0] == 0:
                        frames.pop(0)
                        clock_pointer.pop(0)
                        frames.append(page)
                        clock_pointer.append(1)
                        break
                    else:
                        clock_pointer.append(clock_pointer.pop(0))
                        frames.append(frames.pop(0))
            page_faults += 1
            log_message(f"Page {page} → MISS (Frames: {frames})")

    current_index += 1
    update_visualization()
    root.after(1000, run_algorithm)

def start_simulation():
    global pages, frame_size, frames, page_faults, current_index, algorithm, clock_pointer

    try:
        pages = list(map(int, page_entry.get().split()))
        frame_size = int(frame_size_entry.get())
    except ValueError:
        log_message("ERROR: Please enter valid numbers")
        return

    algorithm = algo_var.get()
    frames = []
    page_faults = 0
    current_index = 0
    clock_pointer = []

    log_text.delete(1.0, tk.END)
    run_algorithm()

# Create main window
root = tk.Tk()
root.title("Virtual Memory Optimizer")
root.geometry("1000x800")

input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.pack(fill=tk.X)

tk.Label(input_frame, text="Page Reference String:").grid(row=0, column=0, sticky="w")
page_entry = tk.Entry(input_frame, width=50, font=('Arial', 12))
page_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Frame Size:").grid(row=1, column=0, sticky="w")
frame_size_entry = tk.Entry(input_frame, width=5, font=('Arial', 12))
frame_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(input_frame, text="Algorithm:").grid(row=2, column=0, sticky="w")

algo_var = tk.StringVar(value="LRU")

algo_dropdown = ttk.Combobox(input_frame, textvariable=algo_var, font=('Arial', 12))
algo_dropdown['values'] = ["LRU", "FIFO", "Optimal", "Clock", "Clock-2"]
algo_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="w")

start_btn = tk.Button(input_frame, text="Start Simulation", command=start_simulation,
                      font=('Arial', 12), bg="#4CAF50", fg="white")
start_btn.grid(row=3, column=1, pady=10, sticky="e")

viz_frame = tk.Frame(root)
viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=viz_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

log_frame = tk.Frame(root)
log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

log_text = tk.Text(log_frame, height=10, font=('Consolas', 10))
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
