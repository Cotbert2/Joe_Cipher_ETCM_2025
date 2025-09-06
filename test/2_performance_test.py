import time
import psutil
import os
import sys
import tracemalloc
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

sys.path.append('your_local_path')

import Joe
import utils

class PerformanceTest:
    def __init__(self):
        self.p = 99999999991
        self.g = 3
        self.x = 30
        
    def generate_test_string(self, length):
        """Generates a test string of specific length"""
        base_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        repeated_text = (base_text * ((length // len(base_text)) + 1))[:length]
        return repeated_text
    
    def measure_encryption_performance(self, text):
        """Measures encryption performance for a given text"""
        tracemalloc.start()
        process = psutil.Process(os.getpid())
        
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        cpu_percent_before = process.cpu_percent()
        
        start_time = time.perf_counter()
        
        myJoeCypher = Joe.JoeCypher(p=self.p, g=self.g, x=self.x, show_plot=False)
        
        encrypted_list = [myJoeCypher.cypher(ord(char)) for char in text]
        encoded_string = utils.Utils.encode_encrypted_floats(encrypted_list)
        
        end_time = time.perf_counter()
        
        cpu_percent_after = process.cpu_percent()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = end_time - start_time
        memory_used = memory_after - memory_before
        peak_memory = peak / 1024 / 1024  # MB
        cpu_usage = max(cpu_percent_after, cpu_percent_before)
        
        return {
            'length': len(text),
            'execution_time': execution_time,
            'memory_used': memory_used,
            'peak_memory': peak_memory,
            'cpu_usage': cpu_usage,
            'encrypted_size': len(encoded_string)
        }
    
    def run_performance_tests(self):
        """Test with different length strings"""
        print("Test with different length strings")
        print("=" * 80)
        
        test_sizes = [10, 50, 100, 250, 500, 1000, 2000, 3000, 5000, 7500, 10000]
        results = []
        
        for size in test_sizes:
            print(f"Testing with {size} characters...", end=" ")
            
            test_text = self.generate_test_string(size)
            
            measurements = []
            for _ in range(3): 
                try:
                    result = self.measure_encryption_performance(test_text)
                    measurements.append(result)
                except Exception as e:
                    print(f"Error: {e}")
                    continue
            
            if measurements:
                avg_result = {
                    'length': size,
                    'execution_time': np.mean([m['execution_time'] for m in measurements]),
                    'memory_used': np.mean([m['memory_used'] for m in measurements]),
                    'peak_memory': np.mean([m['peak_memory'] for m in measurements]),
                    'cpu_usage': np.mean([m['cpu_usage'] for m in measurements]),
                    'encrypted_size': measurements[0]['encrypted_size']
                }
                results.append(avg_result)
                print("[+]")
            else:
                print("[-]")
        
        return results
    
    def analyze_results(self, results):
        """Analyze results"""
        if not results:
            print("There are no results to analyze")
            return
        
        lengths = [r['length'] for r in results]
        times = [r['execution_time'] for r in results]
        memories = [r['peak_memory'] for r in results]
        cpu_usages = [r['cpu_usage'] for r in results]
        
        print("\nResults Table")
        print("=" * 100)
        print(f"{'length':<10} {'time (s)':<12} {'memory (MB)':<14} {'CPU (%)':<10} {'ciphertext length':<15}")
        print("-" * 100)
        
        for result in results:
            print(f"{result['length']:<10} "
                  f"{result['execution_time']:<12.4f} "
                  f"{result['peak_memory']:<14.2f} "
                  f"{result['cpu_usage']:<10.1f} "
                  f"{result['encrypted_size']:<15}")
        
        print("\n📈 CORRELATION ANALYSIS")
        print("=" * 50)
        
        slope_time, intercept_time, r_value_time, p_value_time, std_err_time = stats.linregress(lengths, times)
        print(f"\n⏱️  Execution time vs Length:")
        print(f"   Linear equation: T(n) = {slope_time:.6f} * n + {intercept_time:.6f}")
        print(f"   Correlation coefficient R²: {r_value_time**2:.4f}")
        
        slope_mem, intercept_mem, r_value_mem, p_value_mem, std_err_mem = stats.linregress(lengths, memories)
        print(f"\n💾 Memory vs Length:")
        print(f"   Linear equation: M(n) = {slope_mem:.6f} * n + {intercept_mem:.6f}")
        print(f"   Correlation coefficient R²: {r_value_mem**2:.4f}")
        
        poly_coeffs_time = np.polyfit(lengths, times, 2)
        poly_r2_time = np.corrcoef(times, np.polyval(poly_coeffs_time, lengths))[0,1]**2
        print(f"\n⏱️  Execution time (quadratic analysis):")
        print(f"   Quadratic equation: T(n) = {poly_coeffs_time[0]:.2e} * n² + {poly_coeffs_time[1]:.6f} * n + {poly_coeffs_time[2]:.6f}")
        print(f"   Correlation coefficient R²: {poly_r2_time:.4f}")

        print(f"\n🔍 COMPLEXITY ANALYSIS:")
        print("=" * 30)
        
        if r_value_time**2 > 0.9:
            print("LINEAR complexity O(n) for execution time")
        elif poly_r2_time > r_value_time**2 and poly_r2_time > 0.9:
            print("QUADRATIC complexity O(n²) for execution time")
        else:
            print("Complexity not clearly determined")
        
        if r_value_mem**2 > 0.9:
            print("LINEAR complexity O(n) for memory usage")
        else:
            print("Memory usage does not correlate linearly")
        
        print(f"\n📋 ADDITIONAL STATISTICS:")
        print("=" * 30)
        print(f"Average time per character: {np.mean(times)/np.mean(lengths)*1000:.3f} ms/char")
        print(f"Average memory per character: {np.mean(memories)/np.mean(lengths):.3f} MB/char")
        print(f"Average CPU usage: {np.mean(cpu_usages):.1f}%")
        
        self.create_performance_plots(results)
    
    def create_performance_plots(self, results):
        """Creates performance plots"""
        lengths = [r['length'] for r in results]
        times = [r['execution_time'] for r in results]
        memories = [r['peak_memory'] for r in results]
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(lengths, times, 'bo-', linewidth=2, markersize=6)
        plt.xlabel('Text length (characters)')
        plt.ylabel('Execution time (seconds)')
        plt.title('Time vs Length')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 3, 2)
        plt.plot(lengths, memories, 'ro-', linewidth=2, markersize=6)
        plt.xlabel('Text length (characters)')
        plt.ylabel('Peak memory (MB)')
        plt.title('Memory vs Length')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 3, 3)
        times_norm = np.array(times) / max(times)
        memories_norm = np.array(memories) / max(memories)
        plt.plot(lengths, times_norm, 'bo-', label='Time (normalized)', linewidth=2)
        plt.plot(lengths, memories_norm, 'ro-', label='Memory (normalized)', linewidth=2)
        plt.xlabel('Text length (characters)')
        plt.ylabel('Normalized value')
        plt.title('Normalized Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/Users/mateo/Development/JoeCypherEDO/clean/test/performance_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n📈 Plots saved at: clean/test/performance_analysis.png")


def main():
    """Main function"""
    print("🔐 PERFORMANCE ANALYSIS - JOECYPHER ALGORITHM")
    print("=" * 60)
    print("This script analyzes the performance of the encryption algorithm")
    print("measuring execution time, memory usage, and CPU for different")
    print("input sizes.\n")
    
    perf_test = PerformanceTest()
    
    results = perf_test.run_performance_tests()
    
    if results:
        perf_test.analyze_results(results)
    else:
        print("[-] Could not obtain test results")
    
    print(f"\n[+] Analysis completed!")


if __name__ == "__main__":
    main()
