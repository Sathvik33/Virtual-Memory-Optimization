Virtual Memory Optimizer

A graphical simulation tool to visualize and analyze various page replacement algorithms, including LRU (Least Recently Used), FIFO (First In First Out), Optimal, and Clock algorithms.

Features

Supports multiple page replacement algorithms:

LRU (Least Recently Used)

FIFO (First In First Out)

Optimal Page Replacement

Clock Algorithm

Clock-2 (Enhanced Clock Algorithm)

Dynamic visualization of memory frames using Matplotlib.

Logs page hits and misses in real-time.

Adjustable frame size and custom page reference string input.

Prerequisites

Ensure you have the following installed:

Python 3.x

Required libraries: tkinter, matplotlib

You can install the dependencies using:

pip install matplotlib

How to Run

Clone or download the repository.

Navigate to the project directory:

cd virtual-memory-optimizer

Run the Python script:
python OS.py

Usage

Input Page Reference String: Enter a sequence of page numbers separated by spaces (e.g., 1 2 3 4 1 2 5 1 2 3 4 5).

Frame Size: Specify the number of available memory frames.

Algorithm Selection: Choose the page replacement algorithm from the dropdown list:

LRU (Least Recently Used)

FIFO (First In First Out)

Optimal

Clock

Clock-2

Start Simulation: Click the "Start Simulation" button to begin the visualization.

Explanation of Algorithms

LRU (Least Recently Used):

Replaces the page that has not been used for the longest time.

FIFO (First In First Out):

Replaces the oldest page in memory.

Optimal:

Replaces the page that will not be used for the longest time in the future (theoretical best case).

Clock Algorithm:

Uses a circular buffer and a reference bit to track page usage.

Clock-2 (Enhanced Clock Algorithm):

Similar to Clock but with an additional pass to handle reference bits more efficiently.

Output

Visualization: Displays the state of memory frames in real-time.

Log: Provides a real-time log of page hits and misses along with timestamps.

Summary: Shows the total number of page faults when the simulation completes.

Example Input

Page Reference String: 7 0 1 2 0 3 4 2 3 0 3 2 1 2 0 1 7 0 1

Frame Size: 3

Example Output

[12:45:01] Page 7 → MISS (Frames: [7])
[12:45:02] Page 0 → MISS (Frames: [7, 0])
[12:45:03] Page 1 → MISS (Frames: [7, 0, 1])
[12:45:04] Page 2 → MISS (Frames: [0, 1, 2])
...
Simulation complete! Total Page Faults: 12

Customization

Frame Size: Adjustable through the input field.

Simulation Speed: Modify the delay in root.after() for faster/slower animation.

Algorithms: Easily extendable by adding new algorithms in the run_algorithm() function.

Troubleshooting

Ensure all dependencies are installed using:

pip install matplotlib

If the UI does not display properly, ensure you're using a supported Python version (3.4).

License

This project is open-source and available under the MIT License.

Contributions

Contributions and improvements are welcome! Feel free to submit pull requests or report issues.

Author
Sathvik
