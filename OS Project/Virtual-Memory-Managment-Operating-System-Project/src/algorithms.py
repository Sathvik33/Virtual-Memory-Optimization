# src/algorithms.py
from typing import List, Optional, Tuple, Dict

def fifo_replace(new_page: List[str], memory: List[Optional[List[str]]], max_frames: int, page_order: List[int]) -> List[Optional[List[str]]]:
    if len([x for x in memory if x is not None]) < max_frames:
        for i in range(len(memory)):
            if memory[i] is None:
                memory[i] = new_page
                page_order.append(len(page_order))  # Track page insertion order
                break
    else:
        # Find the index of the oldest page
        oldest_idx = page_order.index(min(page_order))
        memory[oldest_idx] = new_page
        page_order[oldest_idx] = len(page_order)  # Update insertion order
    return memory

def lru_replace(page_number: int, memory: List[Optional[List[str]]], access_history: List[int], max_frames: int, new_page: List[str], page_numbers: List[Optional[int]]) -> List[Optional[List[str]]]:
    if len([x for x in memory if x is not None]) < max_frames:
        for i in range(len(memory)):
            if memory[i] is None:
                memory[i] = new_page
                break
    else:
        lru_index = None
        earliest_access = float('inf')
        for i in range(len(memory)):
            if memory[i] is not None and page_numbers[i] is not None:
                page_num = page_numbers[i]
                accesses = [j for j, p in enumerate(access_history) if p == page_num]
                if accesses:
                    last_access = max(accesses)
                    if last_access < earliest_access:
                        earliest_access = last_access
                        lru_index = i
                else:
                    lru_index = i
                    break
        if lru_index is None:
            lru_index = 0
        memory[lru_index] = new_page
    return memory

def optimal_replace(page_number: int, memory: List[Optional[List[str]]], future_references: List[int], max_frames: int, new_page: List[str], page_numbers: List[Optional[int]]) -> List[Optional[List[str]]]:
    if len([x for x in memory if x is not None]) < max_frames:
        for i in range(len(memory)):
            if memory[i] is None:
                memory[i] = new_page
                break
    else:
        farthest = -1
        replace_idx = 0
        for i in range(len(memory)):
            if memory[i] is None:
                replace_idx = i
                break
            page_num = page_numbers[i]
            if page_num is None:
                replace_idx = i
                break
            try:
                next_use = future_references.index(page_num)
                if next_use > farthest:
                    farthest = next_use
                    replace_idx = i
            except ValueError:
                replace_idx = i
                break
        memory[replace_idx] = new_page
    return memory

def clock_replace(new_page: List[str], memory: List[Optional[List[str]]], clock_pointer: int, reference_bits: List[int], max_frames: int) -> Tuple[List[Optional[List[str]]], int, List[int]]:
    if len([x for x in memory if x is not None]) < max_frames:
        for i in range(len(memory)):
            if memory[i] is None:
                memory[i] = new_page
                reference_bits[i] = 1
                clock_pointer = (i + 1) % max_frames
                break
    else:
        while True:
            if reference_bits[clock_pointer] == 0:
                memory[clock_pointer] = new_page
                reference_bits[clock_pointer] = 1
                clock_pointer = (clock_pointer + 1) % max_frames
                break
            else:
                reference_bits[clock_pointer] = 0
                clock_pointer = (clock_pointer + 1) % max_frames
    return memory, clock_pointer, reference_bits

def lfu_replace(page_number: int, memory: List[Optional[List[str]]], frequency: Dict[int, int], max_frames: int, new_page: List[str], page_numbers: List[Optional[int]]) -> Tuple[List[Optional[List[str]]], Dict[int, int]]:
    if len([x for x in memory if x is not None]) < max_frames:
        for i in range(len(memory)):
            if memory[i] is None:
                memory[i] = new_page
                break
    else:
        min_freq = float('inf')
        lfu_idx = 0
        for i in range(len(memory)):
            if memory[i] is None:
                lfu_idx = i
                break
            if page_numbers[i] is not None:
                freq = frequency.get(page_numbers[i], 0)
                if freq < min_freq:
                    min_freq = freq
                    lfu_idx = i
        if page_numbers[lfu_idx] is not None:
            del frequency[page_numbers[lfu_idx]]
        memory[lfu_idx] = new_page
    return memory, frequency