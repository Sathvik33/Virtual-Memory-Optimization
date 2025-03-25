import matplotlib.pyplot as plt
from typing import List, Optional, Dict

def plot_memory(memory: List[Optional[List[str]]], faults: int, algorithm: str, step: int):
    """
    Plots the memory state as a bar chart, showing occupied and free frames.
    Args:
        memory: List of pages in physical memory (None for free frames, page data for occupied).
        faults: Current number of page faults.
        algorithm: Name of the page replacement algorithm (e.g., "FIFO").
        step: Current step in the simulation (for title).
    """
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(memory)), [1 if x is not None else 0 for x in memory], color='blue')
    plt.title(f"{algorithm} - Memory State at Step {step} (Faults: {faults})")
    plt.xlabel("Frame Number")
    plt.ylabel("Occupied (1) / Free (0)")
    plt.ylim(0, 1.5)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()

def plot_fragmentation(fragmentation_history: List[Dict[str, float]], algorithm: str):
    """
    Plots internal and external fragmentation over time.
    Args:
        fragmentation_history: List of fragmentation percentages over time.
        algorithm: Name of the page replacement algorithm.
    """
    steps = range(len(fragmentation_history))
    internal_frag = [x["internal"] for x in fragmentation_history]
    external_frag = [x["external"] for x in fragmentation_history]

    plt.figure(figsize=(10, 6))
    plt.plot(steps, internal_frag, label="Internal Fragmentation (%)", marker="o")
    plt.plot(steps, external_frag, label="External Fragmentation (%)", marker="x")
    plt.title(f"{algorithm} - Memory Fragmentation Over Time")
    plt.xlabel("Step")
    plt.ylabel("Fragmentation (%)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.show()

def plot_faults_over_time(faults_history: List[int], algorithm: str):
    """
    Plots the number of page faults over time (steps).
    Args:
        faults_history: List of page fault counts at each step.
        algorithm: Name of the page replacement algorithm.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(range(len(faults_history)), faults_history, marker='o', color='red', label='Page Faults')
    plt.title(f"{algorithm} - Page Faults Over Time")
    plt.xlabel("Step")
    plt.ylabel("Cumulative Page Faults")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

def compare_algorithms(algorithm_results: Dict[str, int]):
    """
    Plots a bar chart comparing the total page faults for different algorithms.
    Args:
        algorithm_results: Dictionary mapping algorithm names to their total page faults.
                          Example: {"FIFO": 10, "LRU": 8, "Optimal": 6}
    """
    plt.figure(figsize=(10, 6))
    algorithms = list(algorithm_results.keys())
    faults = list(algorithm_results.values())
    
    # Color scheme for better distinction
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Blue, Orange, Green, Red, Purple
    bars = plt.bar(algorithms, faults, color=colors[:len(algorithms)], edgecolor='black')
    
    plt.title("Algorithm Comparison: Total Page Faults", fontsize=14, fontweight='bold')
    plt.xlabel("Algorithm", fontsize=12)
    plt.ylabel("Total Page Faults", fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()