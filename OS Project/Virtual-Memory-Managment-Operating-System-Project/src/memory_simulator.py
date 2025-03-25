import logging
from typing import List, Tuple, Dict

# Constants
DEFAULT_FRAME_COUNT = 16
TLB_SIZE = 4
BACKING_STORE_PATH = "data/BACKING_STORE.bin"

# Replacement algorithm functions (unchanged)
def lru_replace(access_history: List[int], page_numbers: List[int]) -> int:
    """Replace the least recently used page."""
    last_access = {}
    for idx, pn in enumerate(access_history):
        if pn in page_numbers:
            last_access[pn] = idx
    return min(page_numbers, key=lambda x: last_access.get(x, -1))

def optimal_replace(future_refs: List[int], page_numbers: List[int]) -> int:
    """Replace the page used furthest in the future."""
    max_next_use = -1
    victim = None
    for pn in page_numbers:
        try:
            next_use = future_refs.index(pn)
        except ValueError:
            next_use = len(future_refs)  # Treat as "infinity" if not used again
        if next_use > max_next_use:
            max_next_use = next_use
            victim = pn
    return victim

def clock_replace(clock_pointer: int, ref_bits: List[int], frame_count: int) -> Tuple[int, int]:
    """Clock (Second Chance) replacement."""
    while True:
        if ref_bits[clock_pointer] == 0:
            victim = clock_pointer
            new_pointer = (clock_pointer + 1) % frame_count
            return victim, new_pointer
        ref_bits[clock_pointer] = 0
        clock_pointer = (clock_pointer + 1) % frame_count

def lfu_replace(frequency: Dict[int, int], page_numbers: List[int]) -> int:
    """Replace the least frequently used page."""
    return min(page_numbers, key=lambda x: frequency.get(x, 0))

class Segment:
    def __init__(self, base: int, limit: int, permissions: str = "rwx"):
        """
        Represents a memory segment.
        Args:
            base: Base address of the segment.
            limit: Size of the segment.
            permissions: Access permissions (e.g., "rwx" for read, write, execute).
        """
        self.base = base
        self.limit = limit
        self.permissions = permissions

    def is_valid_address(self, address: int) -> bool:
        """Check if an address is within the segment's bounds."""
        return self.base <= address < self.base + self.limit

class Process:
    def __init__(self, pid: int, pages: List[int]):
        """
        Represents a process with its memory requirements.
        Args:
            pid: Process ID.
            pages: List of page numbers required by the process.
        """
        self.pid = pid
        self.pages = pages
        self.allocated_frames: List[int] = []  # Frames allocated to this process

class MemorySimulator:
    def __init__(self, frame_count: int = DEFAULT_FRAME_COUNT):
        """Initialize the MemorySimulator with given frame count."""
        self.frame_count = frame_count
        self.physical_memory: Dict[int, List[str]] = {}  # {frame_number: page_data}
        self.page_table: Dict[int, int] = {}  # {page_number: frame_number}
        self.segment_table: Dict[str, Segment] = {}  # {segment_name: Segment}
        self.tlb: List[Tuple[int, int]] = []  # TLB entries: [(page_number, frame_number)]
        self.tlb_size = TLB_SIZE
        self.faults = 0
        self.hits = 0
        self.algorithm = "FIFO"
        self.faults_history: List[int] = []  # Track faults over time
        self.access_history: List[int] = []  # Track page access history
        self.future_references: List[int] = []  # Future references for Optimal algorithm
        self.frame_order: List[int] = []  # Tracks frame insertion order for FIFO
        self.clock_pointer = 0  # Pointer for Clock algorithm
        self.reference_bits: List[int] = [0] * frame_count  # Reference bits for Clock algorithm
        self.frequency: Dict[int, int] = {}  # Frequency of page access for LFU
        self.logger = self._setup_logger("simulation.log")
        self.fragmentation_history: List[Dict[str, float]] = []  # Track fragmentation over time
        self.processes: Dict[int, Process] = {}  # {pid: Process}

    def _setup_logger(self, log_file: str) -> logging.Logger:
        """Configure logging for the simulator."""
        logger = logging.getLogger("VirtualMemorySimulator")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def get_optimization_suggestions(self) -> List[str]:
        """
        Analyze simulation data and provide optimization suggestions.
        Returns:
            A list of optimization suggestions.
        """
        suggestions = []

        # Analyze page fault rate
        fault_rate = self.faults / len(self.access_history) if self.access_history else 0
        if fault_rate > 0.5:  # High page fault rate
            suggestions.append("High page fault rate detected. Consider increasing the number of frames.")
        elif fault_rate < 0.1:  # Low page fault rate
            suggestions.append("Low page fault rate. You may reduce the number of frames to save memory.")

        # Analyze fragmentation
        if self.fragmentation_history:
            avg_internal_frag = sum(x["internal"] for x in self.fragmentation_history) / len(self.fragmentation_history)
            avg_external_frag = sum(x["external"] for x in self.fragmentation_history) / len(self.fragmentation_history)
            if avg_internal_frag > 20:  # High internal fragmentation
                suggestions.append("High internal fragmentation. Consider reducing the page size.")
            if avg_external_frag > 20:  # High external fragmentation
                suggestions.append("High external fragmentation. Consider using a different memory allocation strategy.")

        # Analyze algorithm performance
        if self.algorithm == "FIFO" and fault_rate > 0.3:
            suggestions.append("FIFO algorithm may not be optimal for this workload. Consider using LRU or Clock.")
        elif self.algorithm == "LRU" and fault_rate > 0.3:
            suggestions.append("LRU algorithm may not be optimal for this workload. Consider using Optimal or LFU.")

        return suggestions
    
    def add_process(self, pid: int, pages: List[int]):
        """
        Add a new process with its memory requirements.
        Args:
            pid: Process ID.
            pages: List of page numbers required by the process.
        """
        if pid in self.processes:
            raise ValueError(f"Process with PID {pid} already exists.")
        self.processes[pid] = Process(pid, pages)
        self.logger.info(f"Added process: PID={pid}, Pages={pages}")

    def allocate_memory_for_process(self, pid: int):
        """
        Allocate memory for a process.
        Args:
            pid: Process ID.
        """
        if pid not in self.processes:
            raise ValueError(f"Process with PID {pid} not found.")
        process = self.processes[pid]

        for page in process.pages:
            if page not in self.page_table:
                # Handle page fault and allocate a frame
                frame_number = self._page_fault_handler(page)
                process.allocated_frames.append(frame_number)
                self.logger.info(f"Allocated Frame {frame_number} to Process {pid} for Page {page}")
    
    def deallocate_memory_for_process(self, pid: int):
        """
        Deallocate memory for a process.
        Args:
            pid: Process ID.
        """
        if pid not in self.processes:
            raise ValueError(f"Process with PID {pid} not found.")
        process = self.processes[pid]

        for frame in process.allocated_frames:
            # Free the frame and remove it from the page table
            page_number = next(pn for pn, fn in self.page_table.items() if fn == frame)
            del self.page_table[page_number]
            del self.physical_memory[frame]
            self.logger.info(f"Deallocated Frame {frame} from Process {pid}")

        process.allocated_frames.clear()
    
    def calculate_fragmentation(self) -> Dict[str, float]:
        """
        Calculate internal and external fragmentation.
        Returns:
            A dictionary with "internal" and "external" fragmentation percentages.
        """
        total_frames = self.frame_count
        allocated_frames = len(self.physical_memory)
        free_frames = total_frames - allocated_frames

        # Internal fragmentation: wasted space within allocated frames
        internal_fragmentation = 0.0
        for frame_data in self.physical_memory.values():
            used_space = len([x for x in frame_data if x != "0"])
            wasted_space = 256 - used_space  # Assuming page size is 256
            internal_fragmentation += wasted_space
        internal_fragmentation /= (total_frames * 256)  # Normalize to percentage

        # External fragmentation: scattered free memory
        external_fragmentation = 1.0 - (free_frames / total_frames) if free_frames > 0 else 0.0

        return {
            "internal": internal_fragmentation * 100,  # Convert to percentage
            "external": external_fragmentation * 100,
        }
    
    def add_segment(self, name: str, base: int, limit: int, permissions: str = "rwx"):
        """Add a new segment to the segment table."""
        if name in self.segment_table:
            raise ValueError(f"Segment '{name}' already exists.")
        self.segment_table[name] = Segment(base, limit, permissions)
        self.logger.info(f"Added segment: {name} (Base={base}, Limit={limit}, Permissions={permissions})")

    def translate_segment_address(self, segment_name: str, offset: int) -> int:
        """
        Translate a segment-relative address to a physical address.
        Args:
            segment_name: Name of the segment (e.g., "code", "stack").
            offset: Offset within the segment.
        Returns:
            Physical address.
        Raises:
            ValueError if the segment or offset is invalid.
        """
        if segment_name not in self.segment_table:
            raise ValueError(f"Segment '{segment_name}' not found.")
        segment = self.segment_table[segment_name]
        if not segment.is_valid_address(segment.base + offset):
            raise ValueError(f"Offset {offset} is out of bounds for segment '{segment_name}'.")
        return segment.base + offset

    def _setup_logger(self, log_file: str) -> logging.Logger:
        """Configure logging for the simulator."""
        logger = logging.getLogger("VirtualMemorySimulator")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def set_algorithm(self, algorithm: str):
        """Set the page replacement algorithm."""
        valid_algorithms = {"FIFO", "LRU", "Optimal", "Clock", "LFU"}
        if algorithm not in valid_algorithms:
            raise ValueError(f"Invalid algorithm. Valid options: {valid_algorithms}")
        self.algorithm = algorithm
        self.logger.info("Algorithm set to %s", algorithm)

    def set_future_references(self, sequence: List[int]):
        """Set future page references for the Optimal algorithm."""
        self.future_references = sequence.copy()
        self.logger.info("Future references set for Optimal algorithm")

    def translate_address(self, virtual_address: int, index: int = 0) -> Tuple[int, int]:
        """
        Translate a virtual address to a physical address using demand paging.
        Args:
            virtual_address: The virtual address to translate.
            index: The step index (for logging).
        Returns:
            A tuple containing the physical address and the value at that address.
        """
        page_number = virtual_address // 256
        offset = virtual_address % 256
        self.access_history.append(page_number)
        self.frequency[page_number] = self.frequency.get(page_number, 0) + 1

        # Check TLB for a hit
        frame_number = None
        for i, (pn, fn) in enumerate(self.tlb):
            if pn == page_number:
                self.hits += 1
                frame_number = fn
                del self.tlb[i]
                self.tlb.append((pn, fn))  # Move to the end (LRU for TLB)
                if self.algorithm == "Clock":
                    self.reference_bits[fn] = 1
                break

        # Check page table if TLB miss
        if frame_number is None:
            frame_number = self.page_table.get(page_number)
            if frame_number is not None:
                self.hits += 1  # Page table hit
                if self.algorithm == "Clock":
                    self.reference_bits[frame_number] = 1
                if (page_number, frame_number) not in self.tlb:
                    if len(self.tlb) >= self.tlb_size:
                        self.tlb.pop(0)
                    self.tlb.append((page_number, frame_number))
            else:
                # Page fault: load the page into memory (demand paging)
                self.faults += 1
                frame_number = self._page_fault_handler(page_number)

        # Update faults history and fragmentation history
        self.faults_history.append(self.faults)
        self.fragmentation_history.append(self.calculate_fragmentation())

        # Retrieve the value from physical memory
        value = int(self.physical_memory[frame_number][offset])
        physical_address = frame_number * 256 + offset
        return physical_address, value

    def _page_fault_handler(self, page_number: int) -> int:
        """
        Handle a page fault by loading the page into memory (demand paging).
        Args:
            page_number: The page number causing the fault.
        Returns:
            The frame number where the page is loaded.
        """
        if page_number >= 256:
            raise ValueError("Page number out of bounds")

        # Load page data from the backing store (simulate demand paging)
        page_data = ["0"] * 256  # Default dummy data
        try:
            with open(BACKING_STORE_PATH, "rb") as f:
                f.seek(page_number * 256)
                page_data = [str(int.from_bytes(f.read(1), byteorder='big', signed=True)) for _ in range(256)]
        except FileNotFoundError:
            self.logger.warning("Backing store not found")

        # Allocate a frame for the new page
        if len(self.physical_memory) < self.frame_count:
            frame_number = len(self.physical_memory)  # Use the next available frame
            self.physical_memory[frame_number] = page_data
            self.frame_order.append(frame_number)
        else:
            # Replace a page using the selected algorithm
            frame_number = self._replace_page(page_number, page_data)

        # Update the page table and TLB
        self.page_table[page_number] = frame_number
        if (page_number, frame_number) not in self.tlb:
            if len(self.tlb) >= self.tlb_size:
                self.tlb.pop(0)  # Remove the oldest TLB entry
            self.tlb.append((page_number, frame_number))

        self.logger.info(f"Page fault handled: Page {page_number} loaded into Frame {frame_number}")
        return frame_number

    def _replace_page(self, page_number: int, page_data: List[str]) -> int:
        """Replace a page in memory based on the selected algorithm."""
        current_pages = list(self.page_table.keys())
        frame_number = None
        victim_page = None  # Define here to avoid scope issues

        if self.algorithm == "FIFO":
            victim_frame = self.frame_order.pop(0)
            victim_page = next(pn for pn, fn in self.page_table.items() if fn == victim_frame)
            frame_number = victim_frame
            self.frame_order.append(victim_frame)
        elif self.algorithm == "LRU":
            victim_page = lru_replace(self.access_history, current_pages)
            frame_number = self.page_table[victim_page]
        elif self.algorithm == "Optimal":
            victim_page = optimal_replace(self.future_references, current_pages)
            frame_number = self.page_table[victim_page]
        elif self.algorithm == "Clock":
            victim_frame, self.clock_pointer = clock_replace(self.clock_pointer, self.reference_bits, self.frame_count)
            victim_page = next(pn for pn, fn in self.page_table.items() if fn == victim_frame)
            frame_number = victim_frame
            self.reference_bits[victim_frame] = 1
        elif self.algorithm == "LFU":
            victim_page = lfu_replace(self.frequency, current_pages)
            frame_number = self.page_table[victim_page]

        # Update page table, physical memory, and TLB
        del self.page_table[victim_page]
        self.physical_memory[frame_number] = page_data
        self.tlb = [(pn, fn) for pn, fn in self.tlb if pn != victim_page]
        return frame_number

if __name__ == "__main__":
    simulator = MemorySimulator(frame_count=3)
    simulator.set_algorithm("Optimal")
    simulator.set_future_references([1, 2, 3, 4, 1, 2, 5])
    pages = [1, 2, 3, 4, 1, 2, 5]
    for i, page in enumerate(pages):
        addr, val = simulator.translate_address(page * 256, i)
        print(f"Page {page}: Physical Address = {addr}, Value = {val}, Faults = {simulator.faults}, Hits = {simulator.hits}")
        
        
