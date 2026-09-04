"""Notification system for index health status."""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from rag_kb.config import settings


class NotificationSystem:
    """Notification system for index health and system events."""
    
    def __init__(self):
        """Initialize notification system."""
        self.enabled = False
        self.webhook_url: Optional[str] = None
        self.email_config: Optional[Dict] = None
        self.notification_history = []
    
    def configure_webhook(self, webhook_url: str):
        """Configure webhook notification.
        
        Args:
            webhook_url: Webhook URL for notifications
        """
        self.webhook_url = webhook_url
        self.enabled = True
        print(f"Webhook notification configured: {webhook_url}")
    
    def configure_email(self, smtp_server: str, smtp_port: int, email: str, password: str):
        """Configure email notification.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            email: Sender email address
            password: Email password
        """
        self.email_config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'email': email,
            'password': password
        }
        self.enabled = True
        print(f"Email notification configured: {email}")
    
    async def send_notification(self, event_type: str, message: str, data: Dict = None):
        """Send notification.
        
        Args:
            event_type: Type of event (e.g., 'index_unhealthy', 'index_complete')
            message: Notification message
            data: Additional data
        """
        if not self.enabled:
            print(f"Notification disabled: {event_type} - {message}")
            return
        
        notification = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'data': data or {}
        }
        
        self.notification_history.append(notification)
        
        # Keep only last 100 notifications
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]
        
        # Send via webhook if configured
        if self.webhook_url:
            await self._send_webhook_notification(notification)
        
        # Send via email if configured
        if self.email_config:
            await self._send_email_notification(notification)
    
    async def _send_webhook_notification(self, notification: Dict):
        """Send webhook notification.
        
        Args:
            notification: Notification data
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=notification,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print(f"Webhook notification sent successfully: {notification['event_type']}")
                    else:
                        print(f"Webhook notification failed: {response.status}")
        except Exception as e:
            print(f"Error sending webhook notification: {e}")
    
    async def _send_email_notification(self, notification: Dict):
        """Send email notification.
        
        Args:
            notification: Notification data
        """
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['email']
            msg['Subject'] = f"RAG KB Notification: {notification['event_type']}"
            
            body = f"""
Event: {notification['event_type']}
Message: {notification['message']}
Timestamp: {notification['timestamp']}
Data: {notification['data']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            async with aiosmtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                await server.login(self.email_config['email'], self.email_config['password'])
                await server.send_message(msg)
            
            print(f"Email notification sent successfully: {notification['event_type']}")
        except Exception as e:
            print(f"Error sending email notification: {e}")
    
    async def notify_index_unhealthy(self, unindexed_count: int, total_count: int):
        """Notify when index is unhealthy.
        
        Args:
            unindexed_count: Number of unindexed documents
            total_count: Total number of documents
        """
        message = f"Index health is unhealthy: {unindexed_count}/{total_count} documents unindexed"
        await self.send_notification(
            'index_unhealthy',
            message,
            {
                'unindexed_count': unindexed_count,
                'total_count': total_count,
                'health_status': 'unhealthy'
            }
        )
    
    async def notify_index_complete(self, indexed_count: int, total_count: int):
        """Notify when indexing is complete.
        
        Args:
            indexed_count: Number of indexed documents
            total_count: Total number of documents
        """
        message = f"Indexing complete: {indexed_count}/{total_count} documents indexed"
        await self.send_notification(
            'index_complete',
            message,
            {
                'indexed_count': indexed_count,
                'total_count': total_count,
                'health_status': 'healthy'
            }
        )
    
    async def notify_index_partial(self, unindexed_count: int, total_count: int):
        """Notify when index is partial.
        
        Args:
            unindexed_count: Number of unindexed documents
            total_count: Total number of documents
        """
        message = f"Index health is partial: {unindexed_count}/{total_count} documents unindexed"
        await self.send_notification(
            'index_partial',
            message,
            {
                'unindexed_count': unindexed_count,
                'total_count': total_count,
                'health_status': 'partial'
            }
        )
    
    def get_notification_history(self, limit: int = 10) -> list:
        """Get notification history.
        
        Args:
            limit: Number of recent notifications to return
            
        Returns:
            List of recent notifications
        """
        return self.notification_history[-limit:]


# Global notification system instance
_notification_system: Optional[NotificationSystem] = None


def get_notification_system() -> NotificationSystem:
    """Get or create global notification system instance.
    
    Returns:
        NotificationSystem instance
    """
    global _notification_system
    if _notification_system is None:
        _notification_system = NotificationSystem()
    return _notification_system