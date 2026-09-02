import asyncio
from typing import Callable, Any, Coroutine

class VoiceNoteQueue:
    """
    FIFO Queue to handle incoming voice intents so the LLM doesn't get jammed.
    """
    def __init__(self, maxsize: int = 10):
        self._queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, intent: str):
        await self._queue.put(intent)

    async def get(self) -> str:
        return await self._queue.get()
        
    def qsize(self) -> int:
        return self._queue.qsize()

class QueueProcessor:
    """
    Background worker that continuously pulls from the queue and routes to the LLM/MCP.
    """
    def __init__(self, queue: VoiceNoteQueue, process_callback: Callable[[str], Coroutine[Any, Any, None]]):
        self.queue = queue
        self.process_callback = process_callback
        self.is_running = False

    async def start(self):
        self.is_running = True
        while self.is_running:
            intent = await self.queue.get()
            try:
                # Route the intent to the processing callback (LLM/MCP)
                await self.process_callback(intent)
            except Exception as e:
                print(f"[QueueProcessor Error] Failed to process intent: {e}")
            finally:
                self.queue._queue.task_done()
                
    def stop(self):
        self.is_running = False
