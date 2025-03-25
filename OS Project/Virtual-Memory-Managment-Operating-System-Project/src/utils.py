import logging
from typing import Dict, List

def validate_page_sequence(pages_input: str) -> List[int]:
    """
    Validates a page sequence input string.
    Args:
        pages_input: String of comma-separated page numbers (e.g., "1,2,3,4").
    Returns:
        List of integers representing the page sequence.
    Raises:
        ValueError if the input is invalid.
    """
    if not pages_input:
        raise ValueError("Page sequence cannot be empty.")
    try:
        pages = [int(page.strip()) for page in pages_input.split(",")]
        if not pages:
            raise ValueError("Page sequence must contain at least one page.")
        for page in pages:
            if page < 0:
                raise ValueError("Page numbers must be non-negative.")
        return pages
    except ValueError:
        raise ValueError("Page sequence must be comma-separated integers (e.g., 1,2,3,4).")

def validate_frame_count(frames_input: str) -> int:
    """
    Validates the number of frames input.
    Args:
        frames_input: String representing the number of frames (e.g., "3").
    Returns:
        Integer representing the number of frames.
    Raises:
        ValueError if the input is invalid.
    """
    if not frames_input:
        raise ValueError("Number of frames cannot be empty.")
    try:
        frames = int(frames_input)
        if frames <= 0:
            raise ValueError("Number of frames must be positive.")
        return frames
    except ValueError:
        raise ValueError("Number of frames must be a positive integer.")

def setup_logger(log_file: str = "simulation.log") -> logging.Logger:
    """
    Sets up a logger for the simulation.
    Args:
        log_file: Path to the log file.
    Returns:
        Configured logger object.
    """
    logger = logging.getLogger("VirtualMemorySimulator")
    logger.setLevel(logging.INFO)
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    # Create formatters and add to handlers
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def format_memory_state(memory: Dict[int, List[str]]) -> str:
    """
    Formats the memory state as a string for logging.
    Args:
        memory: Dictionary mapping frame numbers to page data (list of 256 bytes).
    Returns:
        String representation of the memory state.
    """
    if not memory:
        return "Memory: Empty"
    memory_str = "Memory: {"
    for frame, data in memory.items():
        memory_str += f"Frame {frame}: Page {frame}, "
    memory_str = memory_str.rstrip(", ") + "}"
    return memory_str