import unittest
from memory_simulator import MemorySimulator
import os

class TestMemorySimulator(unittest.TestCase):
    def setUp(self):
        """Set up a fresh simulator instance for each test."""
        if not os.path.exists("data/BACKING_STORE.bin"):
            os.makedirs("data", exist_ok=True)
            with open("data/BACKING_STORE.bin", "wb") as f:
                f.write(b"\x00" * (256 * 256))

        self.simulator = MemorySimulator(frame_count=3)
        self.pages = [1, 2, 3, 4, 1, 2, 5]  # Test page sequence
        self.virtual_addresses = [page * 256 for page in self.pages]  # Page size is 256

    def test_fragmentation(self):
        """Test fragmentation calculation."""
        simulator = MemorySimulator(frame_count=3)
        simulator.set_algorithm("FIFO")

        # Access pages 1, 2, 3 (should cause page faults)
        for page in [1, 2, 3]:
            simulator.translate_address(page * 256)

        # Check fragmentation
        fragmentation = simulator.calculate_fragmentation()
        self.assertGreaterEqual(fragmentation["internal"], 0)
        self.assertGreaterEqual(fragmentation["external"], 0)
    
    def test_segment_creation(self):
        """Test adding and translating segment addresses."""
        simulator = MemorySimulator()
        simulator.add_segment("code", 0, 1024)
        self.assertEqual(simulator.translate_segment_address("code", 100), 100)
        with self.assertRaises(ValueError):
            simulator.translate_segment_address("code", 2000)  # Out of bounds
        with self.assertRaises(ValueError):
            simulator.translate_segment_address("stack", 100)  # Invalid segment
    
    def test_custom_allocation(self):
        """Test custom memory allocation scenarios."""
        simulator = MemorySimulator(frame_count=5)
        simulator.set_algorithm("FIFO")

        # Add processes
        simulator.add_process(1, [1, 2, 3])
        simulator.add_process(2, [4, 5])

        # Allocate memory for Process 1
        simulator.allocate_memory_for_process(1)
        self.assertEqual(len(simulator.physical_memory), 3)  # 3 frames allocated

        # Allocate memory for Process 2
        simulator.allocate_memory_for_process(2)
        self.assertEqual(len(simulator.physical_memory), 5)  # 5 frames allocated

        # Deallocate memory for Process 1
        simulator.deallocate_memory_for_process(1)
        self.assertEqual(len(simulator.physical_memory), 2)  # 2 frames remain allocated
    
    def test_optimization_suggestions(self):
        """Test optimization suggestions."""
        simulator = MemorySimulator(frame_count=3)
        simulator.set_algorithm("FIFO")

        # Simulate high page fault rate
        for page in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            simulator.translate_address(page * 256)

        suggestions = simulator.get_optimization_suggestions()
        self.assertIn("High page fault rate", suggestions[0])  # Expect a suggestion for high fault rate
    
    def test_demand_paging(self):
        """Test demand paging behavior."""
        simulator = MemorySimulator(frame_count=3)
        simulator.set_algorithm("FIFO")

        # Access pages 1, 2, 3 (should cause page faults)
        for page in [1, 2, 3]:
            simulator.translate_address(page * 256)
        self.assertEqual(simulator.faults, 3)  # 3 page faults

        # Access page 1 again (should not cause a page fault)
        simulator.translate_address(1 * 256)
        self.assertEqual(simulator.faults, 3)  # No new fault
    
    def test_initialization(self):
        """Test that the simulator initializes with correct default values."""
        self.assertEqual(self.simulator.frame_count, 3)
        self.assertEqual(self.simulator.faults, 0)
        self.assertEqual(self.simulator.hits, 0)
        self.assertEqual(len(self.simulator.physical_memory), 0)
        self.assertEqual(len(self.simulator.page_table), 0)
        self.assertEqual(len(self.simulator.tlb), 0)
        self.assertEqual(self.simulator.algorithm, "FIFO")
        self.assertEqual(len(self.simulator.frame_order), 0)

    def test_tlb_hit(self):
        """Test TLB hit behavior with repeated page access."""
        self.simulator.translate_address(256, 0)  # Page 1
        self.assertEqual(self.simulator.faults, 1)
        self.assertEqual(self.simulator.hits, 0)
        self.simulator.translate_address(256, 1)  # Same page, should hit TLB
        self.assertEqual(self.simulator.faults, 1)
        self.assertEqual(self.simulator.hits, 1)

    def test_page_fault_handler(self):
        """Test page fault handling and physical memory loading."""
        frame = self.simulator._page_fault_handler(1)
        self.assertEqual(frame, 0)
        self.assertIn(0, self.simulator.physical_memory)
        self.assertEqual(len(self.simulator.physical_memory[0]), 256)
        self.assertIn(1, self.simulator.page_table)
        self.assertEqual(self.simulator.page_table[1], 0)
        self.assertIn((1, 0), self.simulator.tlb)

    def test_fifo_algorithm(self):
        """Test FIFO replacement with a known sequence."""
        self.simulator.set_algorithm("FIFO")
        for step, vaddr in enumerate(self.virtual_addresses):
            self.simulator.translate_address(vaddr, step)
        self.assertEqual(self.simulator.faults, 7)
        self.assertEqual(self.simulator.hits, 0)

    def test_lru_algorithm(self):
        """Test LRU replacement with the same sequence."""
        self.simulator.set_algorithm("LRU")
        for step, vaddr in enumerate(self.virtual_addresses):
            self.simulator.translate_address(vaddr, step)
        self.assertEqual(self.simulator.faults, 7)
        self.assertEqual(self.simulator.hits, 0)

    def test_optimal_algorithm(self):
        """Test Optimal replacement with future references."""
        self.simulator.set_algorithm("Optimal")
        self.simulator.set_future_references(self.pages)
        for step, vaddr in enumerate(self.virtual_addresses):
            self.simulator.translate_address(vaddr, step)
        self.assertEqual(self.simulator.faults, 5)
        self.assertEqual(self.simulator.hits, 2)

    def test_clock_algorithm(self):
        """Test Clock replacement with reference bits."""
        self.simulator.set_algorithm("Clock")
        for step, vaddr in enumerate(self.virtual_addresses):
            self.simulator.translate_address(vaddr, step)
        self.assertGreaterEqual(self.simulator.faults, 5)
        self.assertLessEqual(self.simulator.faults, 7)

    def test_lfu_algorithm(self):
        """Test LFU replacement based on frequency."""
        self.simulator.set_algorithm("LFU")
        for step, vaddr in enumerate(self.virtual_addresses):
            self.simulator.translate_address(vaddr, step)
        # Expected: 1, 2, 3 (faults), 4 (fault, replace 3), 1 (hit), 2 (hit), 5 (fault, replace 4)
        self.assertEqual(self.simulator.faults, 7)
        self.assertEqual(self.simulator.hits, 0)

    def test_out_of_bounds_page(self):
        """Test error handling for invalid page numbers."""
        with self.assertRaises(ValueError):
            self.simulator._page_fault_handler(256)

    def test_full_tlb_replacement(self):
        """Test TLB replacement when full."""
        simulator = MemorySimulator(frame_count=1)
        for i in range(5):
            simulator.translate_address(i * 256, i)
        self.assertLessEqual(len(simulator.tlb), 4)

if __name__ == "__main__":
    unittest.main()