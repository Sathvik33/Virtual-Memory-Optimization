# src/main.py
import argparse
import os
from typing import List, Optional
from memory_simulator import MemorySimulator
from visualization import plot_memory, plot_faults_over_time
from gui import start_gui
from utils import setup_logger, validate_page_sequence, validate_frame_count

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get project root
output_file_path = os.path.join(base_path, "data", "output.txt")  # Correct path


def run_simulation(pages: Optional[List[int]] = None, frame_count: int = 16, algorithm: str = "FIFO"):
    """
    Runs the virtual memory simulation with the given parameters.
    Args:
        pages: List of page numbers to simulate (if None, read from addresses.txt).
        frame_count: Number of physical memory frames.
        algorithm: Page replacement algorithm to use.
    """
    logger = setup_logger("simulation.log")
    logger.info("Starting simulation with frame_count=%d, algorithm=%s", frame_count, algorithm)

    # Initialize simulator
    simulator = MemorySimulator(frame_count=frame_count)
    simulator.algorithm = algorithm

    # If pages are not provided, read from addresses.txt
    if pages is None:
        try:
            with open("data/addresses.txt", "r") as f:
                pages = [int(line.strip()) for line in f]
        except FileNotFoundError:
            logger.error("File 'data/addresses.txt' not found.")
            raise
        except ValueError:
            logger.error("Invalid data in 'data/addresses.txt'. Ensure all lines are integers.")
            raise

    # For Optimal algorithm, set future references
    if algorithm == "Optimal":
        simulator.set_future_references(pages)

    # Run simulation
    try:
        with open(output_file_path, "w") as out_f:
            for step, page in enumerate(pages):
                physical_addr, value = simulator.translate_address(page, out_f, step)
                # Plot memory state after each step
                plot_memory(list(simulator.physical_memory.values()) + [None] * (frame_count - len(simulator.physical_memory)),
                           simulator.faults, algorithm, step + 1)

        # Plot faults over time
        plot_faults_over_time(simulator.faults_history, algorithm)

        # Calculate rates
        address_count = len(pages)
        page_fault_rate = simulator.faults / address_count if address_count > 0 else 0
        tlb_hit_rate = simulator.hits / address_count if address_count > 0 else 0

        # Log and print results
        result_str = (f"Number of translated addresses: {address_count}\n"
                      f"Number of page faults: {simulator.faults}\n"
                      f"Page fault rate: {page_fault_rate:.2f}\n"
                      f"Number of TLB hits: {simulator.hits}\n"
                      f"TLB hit rate: {tlb_hit_rate:.2f}\n")
        logger.info(result_str)
        print(result_str)

    except Exception as e:
        logger.error(f"An error occurred during simulation: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual Memory Simulator")
    parser.add_argument("--pages", type=str, help="Comma-separated page sequence (e.g., 1,2,3,4)")
    parser.add_argument("--frames", type=int, default=16, help="Number of frames (default: 16)")
    parser.add_argument("--algorithm", type=str, choices=["FIFO", "LRU", "Optimal", "Clock", "LFU"], default="FIFO",
                        help="Page replacement algorithm (default: FIFO)")
    parser.add_argument("--gui", action="store_true", help="Run with GUI (default: False)")
    args = parser.parse_args()

    if args.gui:
        start_gui()
    else:
        pages = None
        if args.pages:
            try:
                pages = validate_page_sequence(args.pages)
            except ValueError as e:
                print(f"Error: {str(e)}")
                exit(1)
        try:
            validate_frame_count(str(args.frames))
        except ValueError as e:
            print(f"Error: {str(e)}")
            exit(1)
        run_simulation(pages=pages, frame_count=args.frames, algorithm=args.algorithm)