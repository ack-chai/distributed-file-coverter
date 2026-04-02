# Performance analysis module enhanced with logging and clarity 

import matplotlib.pyplot as plt
import time
import socket
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Adds parent folder so we can import project modules

from shared.config import HOST, SERVER_PORT
from shared.protocols import send_file, receive_file, send_message, receive_message


def generate_test_image(size_kb, path):
    """Generate a test image of approximately size_kb kilobytes."""
    from PIL import Image
    import random # random pixels are imported

    print(f"[ANALYSIS] Generating test image of size ~{size_kb} KB...")

    # Approximate: each pixel = 3 bytes (RGB)
    pixels_needed = (size_kb * 1024) // 3
    width = int(pixels_needed ** 0.5)
    height = width  # making square image

    img = Image.new('RGB', (width, height)) # creates blank image
    pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) # generates random colors
              for _ in range(width * height)]
    img.putdata(pixels) # put pixels in image
    img.save(path, 'JPEG')

    actual_size = os.path.getsize(path) / 1024
    print(f"[ANALYSIS] Generated test image: {path} (~{actual_size:.1f} KB)")
    return path


def measure_conversion_time(filepath, target_format):
    """Send file to server and measure round-trip conversion time."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates tcp socket    

    try:
        print(f"[ANALYSIS] Connecting to server at {HOST}:{SERVER_PORT}...")
        sock.connect((HOST, SERVER_PORT))

        send_message(sock, target_format)

        print("[ANALYSIS] Sending file for conversion...")
        start = time.time()
        send_file(sock, filepath)

        status = receive_message(sock)
        if status.startswith("ERROR"):
            print(f"[ANALYSIS] Server error: {status}")
            return None

        print("[ANALYSIS] Receiving converted file...")
        receive_file(sock, save_dir="analysis_outputs")

        elapsed = time.time() - start  # calculates total time 
        print(f"[ANALYSIS] Conversion completed in {elapsed:.3f} seconds")

        return elapsed

    except Exception as e:
        print(f"[ANALYSIS] Error during measurement: {e}")
        return None

    finally:
        sock.close()


def run_analysis():
    """Run conversions across different file sizes and plot results."""
    os.makedirs("test_files", exist_ok=True)  # Create folder for input
    os.makedirs("analysis_outputs", exist_ok=True)  # Create folder for output

    # File sizes to test (in KB)
    sizes_kb = [50, 100, 200, 500, 1000, 2000]
    times = [] # stores result

    print("[ANALYSIS] Starting performance analysis...")

    for size in sizes_kb:
        test_path = f"test_files/test_{size}kb.jpg"
        generate_test_image(size, test_path)

        print(f"[ANALYSIS] Testing {size} KB file...")
        elapsed = measure_conversion_time(test_path, "png") # converts image

        if elapsed is not None:
            times.append(elapsed) # stores time
            print(f"[ANALYSIS] {size} KB → {elapsed:.3f} seconds")
        else:
            times.append(0)

    print("[ANALYSIS] Generating performance graph...")

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(sizes_kb, times, marker='o', color='steelblue', linewidth=2, markersize=8)
    plt.fill_between(sizes_kb, times, alpha=0.15, color='steelblue')

    plt.title("Distributed File Conversion: File Size vs Conversion Time", fontsize=14, fontweight='bold')
    plt.xlabel("File Size (KB)", fontsize=12)
    plt.ylabel("Conversion Time (seconds)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(sizes_kb)

    # Annotate each point
    for x, y in zip(sizes_kb, times):
        plt.annotate(f"{y:.2f}s", (x, y), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9)

    plt.xscale('log')  # spreads out the x-axis nicely

    plt.tight_layout()
    plot_path = "analysis/performance_result.png"
    plt.savefig(plot_path, dpi=150)

    print(f"[ANALYSIS] Plot saved to {plot_path}")
    plt.show()


if __name__ == "__main__":
    run_analysis()  # runs program
