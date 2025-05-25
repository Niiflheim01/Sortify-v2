"""
app.py - Flask backend for Sortify visual sorting visualizer
Provides API endpoints for generating arrays and visualizing sorting algorithms (Bubble, Merge, Quick, Insertion, Selection).
"""
from flask import Flask, render_template, jsonify, request
import random
import time
from typing import List, Dict

app = Flask(__name__)

class SortingVisualizer:
    """Handles array generation and sorting algorithm step tracking for visualization."""
    def __init__(self):
        self.array = []
        self.array_size = 20
        self.comparisons = 0
        self.swaps = 0
        self.start_time = 0
        self.steps = []

    def generate_new_array(self):
        """Generate a new random array and reset stats."""
        self.array = [random.randint(10, 100) for _ in range(self.array_size)]
        self.comparisons = 0
        self.swaps = 0
        self.steps = []
        return self.array

    def bubble_sort(self, arr):
        """Bubble Sort: Simple comparison-based sort."""
        self.steps = []
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                self.comparisons += 1
                if arr[j] > arr[j + 1]:
                    self.swaps += 1
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.steps.append({
                        'array': arr.copy(),
                        'comparing': [j, j + 1],
                        'sorted': list(range(n - i, n)),
                        'comparisons': self.comparisons,
                        'swaps': self.swaps
                    })
        return self.steps

    def merge_sort(self, arr):
        """Merge Sort: Divide and conquer sort."""
        self.steps = []
        self._merge_sort_helper(arr, 0)
        return self.steps

    def _merge_sort_helper(self, arr, start_idx):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = self._merge_sort_helper(arr[:mid], start_idx)
        right = self._merge_sort_helper(arr[mid:], start_idx + mid)
        return self._merge(left, right, start_idx)

    def _merge(self, left, right, start_idx):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            self.comparisons += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
                self.swaps += 1
            self.steps.append({
                'array': result.copy(),
                'comparing': [start_idx + i, start_idx + j],
                'sorted': [],
                'comparisons': self.comparisons,
                'swaps': self.swaps
            })
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def quick_sort(self, arr):
        """Quick Sort: Partition-based sort."""
        self.steps = []
        self._quick_sort_helper(arr, 0, len(arr) - 1)
        return self.steps

    def _quick_sort_helper(self, arr, low, high):
        if low < high:
            pivot_idx = self._partition(arr, low, high)
            self._quick_sort_helper(arr, low, pivot_idx - 1)
            self._quick_sort_helper(arr, pivot_idx + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            self.comparisons += 1
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                self.swaps += 1
                self.steps.append({
                    'array': arr.copy(),
                    'comparing': [i, j, high],
                    'sorted': [],
                    'comparisons': self.comparisons,
                    'swaps': self.swaps
                })
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.swaps += 1
        self.steps.append({
            'array': arr.copy(),
            'comparing': [i + 1, high],
            'sorted': [],
            'comparisons': self.comparisons,
            'swaps': self.swaps
        })
        return i + 1

    def insertion_sort(self, arr):
        """Insertion Sort: Builds sorted array one item at a time."""
        self.steps = []
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                self.comparisons += 1
                arr[j + 1] = arr[j]
                self.swaps += 1
                self.steps.append({
                    'array': arr.copy(),
                    'comparing': [j, j + 1],
                    'sorted': list(range(i)),
                    'comparisons': self.comparisons,
                    'swaps': self.swaps
                })
                j -= 1
            arr[j + 1] = key
            self.steps.append({
                'array': arr.copy(),
                'comparing': [j + 1],
                'sorted': list(range(i + 1)),
                'comparisons': self.comparisons,
                'swaps': self.swaps
            })
        return self.steps

    def selection_sort(self, arr):
        """Selection Sort: Repeatedly finds the minimum and puts it in place."""
        self.steps = []
        for i in range(len(arr)):
            min_idx = i
            for j in range(i + 1, len(arr)):
                self.comparisons += 1
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.swaps += 1
            self.steps.append({
                'array': arr.copy(),
                'comparing': [i, min_idx],
                'sorted': list(range(i)),
                'comparisons': self.comparisons,
                'swaps': self.swaps
            })
        return self.steps

visualizer = SortingVisualizer()

@app.route('/')
def index():
    """Serve the main SPA page."""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """API endpoint to generate a new random array."""
    array = visualizer.generate_new_array()
    return jsonify({'array': array})

@app.route('/api/sort', methods=['POST'])
def sort():
    """API endpoint to perform a sort and return all steps and stats."""
    data = request.get_json()
    array = data.get('array', [])
    algorithm = data.get('algorithm', 'bubble')
    visualizer.comparisons = 0
    visualizer.swaps = 0
    visualizer.start_time = time.time()
    if algorithm == 'bubble':
        steps = visualizer.bubble_sort(array.copy())
    elif algorithm == 'merge':
        steps = visualizer.merge_sort(array.copy())
    elif algorithm == 'quick':
        steps = visualizer.quick_sort(array.copy())
    elif algorithm == 'insertion':
        steps = visualizer.insertion_sort(array.copy())
    elif algorithm == 'selection':
        steps = visualizer.selection_sort(array.copy())
    else:
        return jsonify({'error': 'Invalid algorithm'}), 400
    return jsonify({
        'steps': steps,
        'stats': {
            'comparisons': visualizer.comparisons,
            'swaps': visualizer.swaps,
            'time': time.time() - visualizer.start_time
        }
    })

if __name__ == '__main__':
    app.run(debug=True) 