import pytest
import asyncio
from core.async_queue import VoiceNoteQueue, QueueProcessor

@pytest.mark.asyncio
async def test_voice_note_queue():
    queue = VoiceNoteQueue(maxsize=5)
    
    # Test pushing to queue
    await queue.put("intent_1")
    await queue.put("intent_2")
    assert queue.qsize() == 2
    
    # Test getting from queue
    item = await queue.get()
    assert item == "intent_1"
    assert queue.qsize() == 1

@pytest.mark.asyncio
async def test_queue_processor():
    queue = VoiceNoteQueue()
    processed_items = []
    
    # Mock processing callback
    async def mock_process(item):
        processed_items.append(item)
        await asyncio.sleep(0.01) # Simulate LLM thinking
        
    processor = QueueProcessor(queue, process_callback=mock_process)
    
    # Start processor task
    task = asyncio.create_task(processor.start())
    
    # Queue up intents
    await queue.put("turn off wifi")
    await queue.put("what time is it")
    
    # Wait for queue to process
    await asyncio.sleep(0.05)
    
    assert len(processed_items) == 2
    assert processed_items[0] == "turn off wifi"
    assert processed_items[1] == "what time is it"
    
    # Clean up
    task.cancel()
