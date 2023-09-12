#!/usr/bin/env python3
"""
This test aims to perform the performance test for face detection.
All the values are tested locally and tested.
"""

# TODO: performance test should be implemented on pipeline, check if required?
import matplotlib.pyplot as plt

# Performance data
concurrent_futures = {"6 seconds": {"memory": 648.14, "cpu": 33.86}, "16 seconds": {"memory": 1570.86, "cpu": 31.45}}

asyncio_and_cpu = {"6 seconds": {"memory": 643.96, "cpu": 22.99}, "16 seconds": {"memory": 1588.00, "cpu": 41.65}}

async_task = {"6 seconds": {"memory": 639.89, "cpu": 20.18}, "16 seconds": {"memory": 1445.79, "cpu": 20.62}}

without_async = {"6 seconds": {"memory": 700.83, "cpu": 39.94}, "16 seconds": {"memory": 1474.86, "cpu": 19.52}}

# Plotting memory usage
plt.bar(
    ["Concurrent Futures", "AsyncIO and CPU", "Async Task", "Without Async"],
    [
        concurrent_futures["6 seconds"]["memory"],
        asyncio_and_cpu["6 seconds"]["memory"],
        async_task["6 seconds"]["memory"],
        without_async["6 seconds"]["memory"],
    ],
    color="blue",
    label="6 seconds",
)

plt.bar(
    ["Concurrent Futures", "AsyncIO and CPU", "Async Task", "Without Async"],
    [
        concurrent_futures["16 seconds"]["memory"],
        asyncio_and_cpu["16 seconds"]["memory"],
        async_task["16 seconds"]["memory"],
        without_async["16 seconds"]["memory"],
    ],
    color="red",
    label="16 seconds",
    alpha=0.5,
)

plt.legend()
plt.xlabel("Approach")
plt.ylabel("Memory Usage (MB)")
plt.title("Memory Usage Comparison")
plt.show()

# Plotting CPU usage
plt.bar(
    ["Concurrent Futures", "AsyncIO and CPU", "Async Task", "Without Async"],
    [
        concurrent_futures["6 seconds"]["cpu"],
        asyncio_and_cpu["6 seconds"]["cpu"],
        async_task["6 seconds"]["cpu"],
        without_async["6 seconds"]["cpu"],
    ],
    color="blue",
    label="6 seconds",
)

plt.bar(
    ["Concurrent Futures", "AsyncIO and CPU", "Async Task", "Without Async"],
    [
        concurrent_futures["16 seconds"]["cpu"],
        asyncio_and_cpu["16 seconds"]["cpu"],
        async_task["16 seconds"]["cpu"],
        without_async["16 seconds"]["cpu"],
    ],
    color="red",
    label="16 seconds",
    alpha=0.5,
)

plt.legend()
plt.xlabel("Approach")
plt.ylabel("CPU Usage (%)")
plt.title("CPU Usage Comparison")
plt.show()

# Execution time statistics

# Data for comparison
approaches = ["ConcurrentFutures", "AsyncIOAndCPU", "AsyncTask", "Without Async"]
execution_time_6s = [85.58, 116.27, 93.81, 79.56]
execution_time_16s = [269.26, 225.08, 346.64, 367.57]

# Plotting bar graph
fig, ax = plt.subplots()
ax.plot(approaches, execution_time_6s, label="6 seconds")
ax.plot(approaches, execution_time_16s, label="16 seconds")

ax.set_xlabel("Approaches")
ax.set_ylabel("Execution Time (in seconds)")
ax.set_title("Execution Time of Different Approaches for Face Detection")
ax.legend()

plt.show()
