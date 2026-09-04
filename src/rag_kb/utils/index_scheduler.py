"""Background task scheduler for periodic index integrity checking."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from rag_kb.config import settings


class IndexIntegrityScheduler:
    """Scheduler for periodic index integrity checking."""
    
    def __init__(self, check_interval_minutes: int = 30, auto_index_enabled: bool = False):
        """Initialize index integrity scheduler.
        
        Args:
            check_interval_minutes: Interval between checks in minutes
            auto_index_enabled: Whether to auto-index unindexed documents
        """
        self.check_interval = timedelta(minutes=check_interval_minutes)
        self.auto_index_enabled = auto_index_enabled
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.last_check_time: Optional[datetime] = None
        self.last_check_result: Optional[dict] = None
        self.previous_health_status: Optional[str] = None
    
    async def check_index_integrity(self):
        """Check index integrity and log results."""
        try:
            from rag_kb.ingest.index_manager import get_index_manager
            from rag_kb.utils.notification_system import get_notification_system
            
            index_manager = get_index_manager()
            report = index_manager.get_index_integrity_report()
            
            self.last_check_time = datetime.now()
            self.last_check_result = report
            
            print(f"\n{'='*60}", flush=True)
            print(f"Index Integrity Check - {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            print(f"{'='*60}", flush=True)
            print(f"Total uploaded: {report['total_uploaded']}", flush=True)
            print(f"Total indexed: {report['total_indexed']}", flush=True)
            print(f"Unindexed: {report['unindexed_count']}", flush=True)
            print(f"Index health: {report['index_health']}", flush=True)
            
            # Send notification if health status changed
            current_health = report['index_health']
            if self.previous_health_status and current_health != self.previous_health_status:
                notification_system = get_notification_system()
                
                if current_health == 'unhealthy':
                    await notification_system.notify_index_unhealthy(
                        report['unindexed_count'],
                        report['total_uploaded']
                    )
                elif current_health == 'healthy':
                    await notification_system.notify_index_complete(
                        report['total_indexed'],
                        report['total_uploaded']
                    )
                elif current_health == 'partial':
                    await notification_system.notify_index_partial(
                        report['unindexed_count'],
                        report['total_uploaded']
                    )
            
            self.previous_health_status = current_health
            
            # Auto-index if unhealthy and auto-index is enabled
            if current_health == 'unhealthy' and report['unindexed_count'] > 0:
                if self.auto_index_enabled:
                    print(f"🔄 Auto-indexing {report['unindexed_count']} unindexed documents...", flush=True)
                    await self._auto_index_unindexed()
                else:
                    print(f"⚠️ Auto-index is disabled. {report['unindexed_count']} documents need indexing", flush=True)
                    print(f"   Run: curl -X POST http://localhost:8000/api/v1/index/all", flush=True)
            elif report['index_health'] == 'partial':
                print(f"⚠️ WARNING: Index health is partial", flush=True)
                print(f"   {report['unindexed_count']} documents need indexing", flush=True)
            else:
                print(f"✅ Index health is healthy", flush=True)
            
            print(f"{'='*60}\n", flush=True)
            
        except Exception as e:
            print(f"Error checking index integrity: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    async def _auto_index_unindexed(self):
        """Auto-index unindexed documents."""
        try:
            from rag_kb.ingest.index_manager import get_index_manager
            
            index_manager = get_index_manager()
            results = await index_manager.index_all_unindexed()
            
            print(f"Auto-indexing completed: {results['success_count']}/{results['total_unindexed']} successful", flush=True)
            
            # Send notification about auto-indexing result
            from rag_kb.utils.notification_system import get_notification_system
            notification_system = get_notification_system()
            
            if results['success_count'] > 0:
                await notification_system.send_notification(
                    'auto_index_complete',
                    f"Auto-indexing completed: {results['success_count']}/{results['total_unindexed']} successful",
                    results
                )
            
        except Exception as e:
            print(f"Error in auto-indexing: {e}", flush=True)
    
    async def run_periodic_checks(self):
        """Run periodic index integrity checks."""
        print(f"Starting periodic index integrity checks (interval: {self.check_interval})", flush=True)
        
        while self.running:
            try:
                await self.check_index_integrity()
            except Exception as e:
                print(f"Error in periodic check: {e}", flush=True)
            
            # Wait for next check
            await asyncio.sleep(self.check_interval.total_seconds())
    
    def start(self):
        """Start the periodic index integrity checker."""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.run_periodic_checks())
            print("Index integrity scheduler started", flush=True)
    
    def stop(self):
        """Stop the periodic index integrity checker."""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            print("Index integrity scheduler stopped", flush=True)
    
    def get_status(self) -> dict:
        """Get scheduler status.
        
        Returns:
            Dictionary with scheduler status
        """
        return {
            'running': self.running,
            'check_interval_minutes': self.check_interval.total_seconds() / 60,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'last_check_result': self.last_check_result,
            'previous_health_status': self.previous_health_status
        }
    
    def set_check_interval(self, minutes: int):
        """Set check interval.
        
        Args:
            minutes: Interval in minutes
        """
        self.check_interval = timedelta(minutes=minutes)
        print(f"Check interval updated to {minutes} minutes", flush=True)


# Global scheduler instance
_index_scheduler: Optional[IndexIntegrityScheduler] = None


def get_index_scheduler() -> IndexIntegrityScheduler:
    """Get or create global index scheduler instance.
    
    Returns:
        IndexIntegrityScheduler instance
    """
    global _index_scheduler
    if _index_scheduler is None:
        _index_scheduler = IndexIntegrityScheduler(check_interval_minutes=30)
    return _index_scheduler