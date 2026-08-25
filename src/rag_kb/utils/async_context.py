"""Async context manager for event loop management and graceful shutdown."""

import asyncio
import atexit
import signal
import sys
from typing import Set, Optional


class AsyncContextManager:
    """Manages async context with proper event loop cleanup and graceful shutdown."""
    
    def __init__(self):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.tasks: Set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()
        self._initialized = False
    
    async def initialize(self):
        """Initialize the async context manager."""
        if self._initialized:
            return
        
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # Register signal handlers for graceful shutdown
        if sys.platform != 'win32':
            for sig in (signal.SIGINT, signal.SIGTERM):
                self.loop.add_signal_handler(sig, self._signal_handler)
        
        # Register cleanup on exit
        atexit.register(self.sync_cleanup)
        
        self._initialized = True
        print("Async context manager initialized", file=sys.stderr, flush=True)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"Received signal {signum}, initiating graceful shutdown...", file=sys.stderr, flush=True)
        self._shutdown_event.set()
    
    def track_task(self, task: asyncio.Task):
        """Track a task for cleanup."""
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
    
    async def cleanup(self):
        """Gracefully cleanup all pending tasks."""
        if not self._initialized:
            return
        
        print("Starting graceful shutdown...", file=sys.stderr, flush=True)
        
        # Cancel all pending tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        # Wait for all tasks to complete
        if self.tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.tasks, return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                print("Some tasks did not complete in time", file=sys.stderr, flush=True)
        
        # Only close the loop if we created it and it's not running
        if self.loop and not self.loop.is_closed() and not self.loop.is_running():
            self.loop.close()
        
        self._initialized = False
        print("Graceful shutdown completed", file=sys.stderr, flush=True)
    
    def sync_cleanup(self):
        """Synchronous cleanup for atexit."""
        if self.loop and not self.loop.is_closed():
            try:
                # Try to run the async cleanup
                if self.loop.is_running():
                    # Loop is running, schedule cleanup
                    asyncio.create_task(self.cleanup())
                else:
                    # Loop is not running, run cleanup directly
                    self.loop.run_until_complete(self.cleanup())
            except Exception as e:
                print(f"Error during sync cleanup: {e}", file=sys.stderr, flush=True)
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()
        await self.cleanup()


# Global instance
_global_async_context: Optional[AsyncContextManager] = None


def get_async_context() -> AsyncContextManager:
    """Get the global async context manager instance."""
    global _global_async_context
    if _global_async_context is None:
        _global_async_context = AsyncContextManager()
    return _global_async_context