import threading
import tkinter as tk
from tkinter import ttk, messagebox, font
import queue
import logging
from memory_simulator import MemorySimulator
from visualization import plot_memory, plot_faults_over_time, compare_algorithms, plot_fragmentation

class SimulatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Virtual Memory Simulator")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        

        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        
        self.simulator = MemorySimulator()
        self.logger = self._setup_logger("gui.log")
        
        self._create_widgets()
        
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        sim_control_frame = ttk.LabelFrame(left_panel, text="Simulation Configuration", padding=10)
        sim_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sim_control_frame, text="Page Sequence (comma-separated):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.page_entry = ttk.Entry(sim_control_frame)
        self.page_entry.grid(row=1, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(sim_control_frame, text="Number of Frames:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.frame_entry = ttk.Entry(sim_control_frame)
        self.frame_entry.grid(row=3, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(sim_control_frame, text="Algorithm:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.algo_var = tk.StringVar()
        algo_menu = ttk.Combobox(sim_control_frame, textvariable=self.algo_var,
                                values=["FIFO", "LRU", "Optimal", "Clock", "LFU"])
        algo_menu.grid(row=5, column=0, sticky=tk.EW, pady=2)
        algo_menu.current(0)
        

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Run Simulation", command=self.run).pack(side=tk.TOP, fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Compare Algorithms", command=self.compare).pack(side=tk.TOP, fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Optimization Tips", command=self.show_optimization_suggestions).pack(side=tk.TOP, fill=tk.X, pady=2)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        config_notebook = ttk.Notebook(right_panel)
        config_notebook.pack(fill=tk.BOTH, expand=True)
        
        process_tab = ttk.Frame(config_notebook)
        self._create_process_controls(process_tab)
        config_notebook.add(process_tab, text="Process Management")
        
        segment_tab = ttk.Frame(config_notebook)
        self._create_segment_controls(segment_tab)
        config_notebook.add(segment_tab, text="Segment Management")
        
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding=10)
        results_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(results_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self.queue = queue.Queue()
        self.all_results = {}

    def _create_process_controls(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Process ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.process_id_entry = ttk.Entry(frame)
        self.process_id_entry.grid(row=1, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(frame, text="Pages (comma-separated):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.process_pages_entry = ttk.Entry(frame)
        self.process_pages_entry.grid(row=3, column=0, sticky=tk.EW, pady=2)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, sticky=tk.EW, pady=10)
        ttk.Button(btn_frame, text="Add Process", command=self.add_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Allocate Memory", command=self.allocate_memory).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Deallocate Memory", command=self.deallocate_memory).pack(side=tk.LEFT, padx=2)
        
        frame.columnconfigure(0, weight=1)

    def _create_segment_controls(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Segment Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.segment_name_entry = ttk.Entry(frame)
        self.segment_name_entry.grid(row=1, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(frame, text="Base Address:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.segment_base_entry = ttk.Entry(frame)
        self.segment_base_entry.grid(row=3, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(frame, text="Segment Size:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.segment_size_entry = ttk.Entry(frame)
        self.segment_size_entry.grid(row=5, column=0, sticky=tk.EW, pady=2)
        
        ttk.Button(frame, text="Add Segment", command=self.add_segment).grid(row=6, column=0, sticky=tk.EW, pady=10)
        
        ttk.Label(frame, text="Address Translation", style='Header.TLabel').grid(row=7, column=0, sticky=tk.W, pady=10)
        
        ttk.Label(frame, text="Segment Name:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.translate_segment_name_entry = ttk.Entry(frame)
        self.translate_segment_name_entry.grid(row=9, column=0, sticky=tk.EW, pady=2)
        
        ttk.Label(frame, text="Offset:").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.translate_offset_entry = ttk.Entry(frame)
        self.translate_offset_entry.grid(row=11, column=0, sticky=tk.EW, pady=2)
        
        ttk.Button(frame, text="Translate Address", command=self.translate_segment_address).grid(row=12, column=0, sticky=tk.EW, pady=10)
        
        ttk.Button(frame, text="Show Fragmentation", command=self.show_fragmentation).grid(row=13, column=0, sticky=tk.EW, pady=10)
        
        frame.columnconfigure(0, weight=1)

    def _setup_logger(self, log_file: str) -> logging.Logger:
        """Configure logging for the GUI."""
        logger = logging.getLogger("SimulatorGUI")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def show_optimization_suggestions(self):
        if not hasattr(self, "simulator"):
            messagebox.showerror("Error", "No simulation data available. Run a simulation first.")
            return

        suggestions = self.simulator.get_optimization_suggestions()
        if not suggestions:
            messagebox.showinfo("Optimization Suggestions", "No optimization suggestions available.")
            return

        suggestions_str = "\n".join(suggestions)
        messagebox.showinfo("Optimization Suggestions", f"Suggestions:\n\n{suggestions_str}")

    def add_process(self):
        try:
            pid = int(self.process_id_entry.get().strip())
            pages = [int(p.strip()) for p in self.process_pages_entry.get().split(",")]
            self.simulator.add_process(pid, pages)
            messagebox.showinfo("Success", f"Process {pid} added successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def allocate_memory(self):
        try:
            pid = int(self.process_id_entry.get().strip())
            self.simulator.allocate_memory_for_process(pid)
            messagebox.showinfo("Success", f"Memory allocated for Process {pid}.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def deallocate_memory(self):
        try:
            pid = int(self.process_id_entry.get().strip())
            self.simulator.deallocate_memory_for_process(pid)
            messagebox.showinfo("Success", f"Memory deallocated for Process {pid}.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def add_segment(self):
        try:
            name = self.segment_name_entry.get().strip()
            base = int(self.segment_base_entry.get().strip())
            size = int(self.segment_size_entry.get().strip())
            self.simulator.add_segment(name, base, size)
            messagebox.showinfo("Success", f"Segment '{name}' added successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_fragmentation(self):
        if not hasattr(self, "simulator") or not self.simulator.fragmentation_history:
            messagebox.showerror("Error", "No fragmentation data available. Run a simulation first.")
            return
        plot_fragmentation(self.simulator.fragmentation_history, self.simulator.algorithm)

    def translate_segment_address(self):
        try:
            segment_name = self.translate_segment_name_entry.get().strip()
            offset = int(self.translate_offset_entry.get().strip())

            physical_address = self.simulator.translate_segment_address(segment_name, offset)

            messagebox.showinfo("Translation Result", f"Physical Address: {physical_address}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        try:
            pages = self._parse_page_sequence(self.page_entry.get().strip())
            frames = self._parse_frame_count(self.frame_entry.get().strip())
            algorithm = self.algo_var.get()

            self.logger.info(f"Starting simulation: Algorithm={algorithm}, Frames={frames}, Pages={pages}")
            simulation_thread = threading.Thread(
                target=self._run_simulation, args=(pages, frames, algorithm))
            simulation_thread.start()
            self.root.after(100, self.process_queue)

        except ValueError as e:
            self.logger.error(f"Input error: {str(e)}")
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def compare(self):
        try:
            pages = self._parse_page_sequence(self.page_entry.get().strip())
            frames = self._parse_frame_count(self.frame_entry.get().strip())

            self.logger.info(f"Comparing algorithms for Pages={pages}, Frames={frames}")
            self.all_results = {}
            for algorithm in ["FIFO", "LRU", "Optimal", "Clock", "LFU"]:
                simulator = MemorySimulator(frame_count=frames)
                simulator.set_algorithm(algorithm)
                if algorithm == "Optimal":
                    simulator.set_future_references(pages)

                for page in pages:
                    simulator.translate_address(page * 256)

                self.all_results[algorithm] = simulator.faults
                self.logger.info(f"{algorithm} Algorithm: Faults={simulator.faults}, Hits={simulator.hits}")

            compare_algorithms(self.all_results)

        except ValueError as e:
            self.logger.error(f"Input error: {str(e)}")
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _parse_page_sequence(self, pages_input):
        if not pages_input:
            self.logger.error("Page sequence cannot be empty.")
            raise ValueError("Page sequence cannot be empty.")
        try:
            pages = [int(page.strip()) for page in pages_input.split(",")]
            if not pages:
                self.logger.error("Page sequence must contain at least one page.")
                raise ValueError("Page sequence must contain at least one page.")
            return pages
        except ValueError:
            self.logger.error("Page sequence must be comma-separated integers (e.g., 1,2,3,4).")
            raise ValueError("Page sequence must be comma-separated integers (e.g., 1,2,3,4).")

    def _parse_frame_count(self, frames_input):
        if not frames_input:
            self.logger.error("Number of frames cannot be empty.")
            raise ValueError("Number of frames cannot be empty.")
        try:
            frames = int(frames_input)
            if frames <= 0:
                self.logger.error("Number of frames must be positive.")
                raise ValueError("Number of frames must be positive.")
            return frames
        except ValueError:
            self.logger.error("Number of frames must be a positive integer.")
            raise ValueError("Number of frames must be a positive integer.")

    def _run_simulation(self, pages, frames, algorithm):
        simulator = MemorySimulator(frame_count=frames)
        simulator.set_algorithm(algorithm)
        if algorithm == "Optimal":
            simulator.set_future_references(pages)

        virtual_addresses = [page * 256 for page in pages]
        result_lines = []
        for step, vaddr in enumerate(virtual_addresses):
            physical_addr, value = simulator.translate_address(vaddr, step)
            result_lines.append(f"Step {step}: Page {vaddr//256}, Physical Address: {physical_addr}, Value: {value}")

        result_lines.append(f"\n{algorithm} Algorithm:")
        result_lines.append(f"Total Page Faults: {simulator.faults}")
        result_lines.append(f"Total TLB Hits: {simulator.hits}")

        self.all_results[algorithm] = simulator.faults

        vis_data = {
            "result": "\n".join(result_lines),
            "memory": [simulator.physical_memory.get(i, None) for i in range(frames)],
            "faults": simulator.faults,
            "faults_history": simulator.faults_history,
            "fragmentation_history": simulator.fragmentation_history,
            "algorithm": algorithm,
            "step": len(pages),
            "compare_results": self.all_results.copy()
        }

        self.simulator.fragmentation_history = simulator.fragmentation_history

        self.logger.info(f"Simulation completed: {algorithm}, Faults={simulator.faults}, Hits={simulator.hits}")
        self.queue.put(vis_data)

    def process_queue(self):
        try:
            vis_data = self.queue.get_nowait()
            self.display_result(vis_data)
        except queue.Empty:
            self.root.after(100, self.process_queue)

    def display_result(self, vis_data):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, vis_data["result"])
        plot_memory(vis_data["memory"], vis_data["faults"], vis_data["algorithm"], vis_data["step"])
        plot_faults_over_time(vis_data["faults_history"], vis_data["algorithm"])
        if len(vis_data["compare_results"]) > 1:
            compare_algorithms(vis_data["compare_results"])

def start_gui():
    root = tk.Tk()
    app = SimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()