#!/usr/bin/env python3
"""
This module contains the AsyncQueue class, which is used to insert and get items with its index given
"""
import asyncio


class AsyncQueue:
    def __init__(self):
        self._queue = []
        self._lock = asyncio.Lock()

    async def insert_at(self, index, item):
        async with self._lock:
            self._queue.insert(index, item)

    async def get_at(self, index):
        async with self._lock:
            return self._queue[index]
