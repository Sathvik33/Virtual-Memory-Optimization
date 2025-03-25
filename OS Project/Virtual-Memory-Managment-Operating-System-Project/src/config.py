# src/config.py
# Default configuration settings for the Virtual Memory Simulator

# Memory Settings
DEFAULT_FRAME_COUNT = 16  # Default number of physical memory frames
PAGE_SIZE = 256  # Size of each page in bytes (fixed in the original project)
TLB_SIZE = 16  # Maximum number of entries in the Translation Lookaside Buffer

# Simulation Settings
SUPPORTED_ALGORITHMS = ["FIFO", "LRU", "Optimal", "Clock", "LFU"]  # List of supported page replacement algorithms

# File Paths
BACKING_STORE_PATH = "data/BACKING_STORE.bin"  # Path to the backing store file
ADDRESSES_FILE_PATH = "data/addresses.txt"  # Path to the input addresses file
OUTPUT_FILE_PATH = "data/output.txt"  # Path to the output file

# Visualization Settings
PLOT_FIGURE_SIZE = (8, 4)  # Default figure size for plots (width, height in inches)