"""User feedback system for RAG quality improvement."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FeedbackType(Enum):
    """Types of user feedback."""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    REGENERATE = "regenerate"
    COPY = "copy"


class FeedbackReason(Enum):
    """Reasons for negative feedback."""
    HALLUCINATION = "hallucination"
    NO_RELEVANT_DOCS = "no_relevant_docs"
    INCORRECT_CITATION = "incorrect_citation"
    POOR_QUALITY = "poor_quality"
    OTHER = "other"


@dataclass
class UserFeedback:
    """User feedback data structure."""
    feedback_id: str
    user_id: str
    query: str
    answer: str
    feedback_type: FeedbackType
    feedback_reason: FeedbackReason | None = None
    feedback_comment: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'query': self.query,
            'answer': self.answer,
            'feedback_type': self.feedback_type.value,
            'feedback_reason': self.feedback_reason.value if self.feedback_reason else None,
            'feedback_comment': self.feedback_comment,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class FeedbackManager:
    """Manager for user feedback collection and analysis."""
    
    def __init__(self):
        """Initialize feedback manager."""
        from rag_kb.config import settings
        self.feedback_file = settings.data_dir / 'user_feedback.json'
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self) -> dict[str, Any]:
        """Load feedback data from file."""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'feedbacks': [],
            'statistics': {
                'total_feedbacks': 0,
                'thumbs_up': 0,
                'thumbs_down': 0,
                'regenerate': 0,
                'copy': 0
            }
        }
    
    def _save_feedback_data(self):
        """Save feedback data to file."""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
    
    def add_feedback(self, feedback: UserFeedback) -> dict[str, Any]:
        """Add user feedback.
        
        Args:
            feedback: User feedback object
            
        Returns:
            Feedback addition result
        """
        try:
            # Add feedback to data
            self.feedback_data['feedbacks'].append(feedback.to_dict())
            
            # Update statistics
            self.feedback_data['statistics']['total_feedbacks'] += 1
            
            if feedback.feedback_type == FeedbackType.THUMBS_UP:
                self.feedback_data['statistics']['thumbs_up'] += 1
            elif feedback.feedback_type == FeedbackType.THUMBS_DOWN:
                self.feedback_data['statistics']['thumbs_down'] += 1
            elif feedback.feedback_type == FeedbackType.REGENERATE:
                self.feedback_data['statistics']['regenerate'] += 1
            elif feedback.feedback_type == FeedbackType.COPY:
                self.feedback_data['statistics']['copy'] += 1
            
            self._save_feedback_data()
            
            return {
                'success': True,
                'feedback_id': feedback.feedback_id,
                'message': 'Feedback recorded successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to record feedback'
            }
    
    def get_feedback_statistics(self) -> dict[str, Any]:
        """Get feedback statistics.
        
        Returns:
            Feedback statistics
        """
        return self.feedback_data['statistics']
    
    def get_feedback_by_type(self, feedback_type: FeedbackType) -> list[dict[str, Any]]:
        """Get feedback by type.
        
        Args:
            feedback_type: Type of feedback
            
        Returns:
            List of feedback items
        """
        return [
            f for f in self.feedback_data['feedbacks']
            if f['feedback_type'] == feedback_type.value
        ]
    
    def get_negative_feedback_reasons(self) -> dict[str, int]:
        """Get statistics of negative feedback reasons.
        
        Returns:
            Dictionary of reason counts
        """
        reasons = {}
        
        for feedback in self.feedback_data['feedbacks']:
            if feedback['feedback_type'] == FeedbackType.THUMBS_DOWN.value:
                reason = feedback.get('feedback_reason', 'other')
                reasons[reason] = reasons.get(reason, 0) + 1
        
        return reasons
    
    def get_feedback_by_user(self, user_id: str) -> list[dict[str, Any]]:
        """Get feedback by user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of feedback items
        """
        return [
            f for f in self.feedback_data['feedbacks']
            if f['user_id'] == user_id
        ]
    
    def calculate_satisfaction_rate(self) -> float:
        """Calculate user satisfaction rate.
        
        Returns:
            Satisfaction rate (0-1)
        """
        stats = self.feedback_data['statistics']
        total = stats['thumbs_up'] + stats['thumbs_down']
        
        if total == 0:
            return 0.0
        
        return stats['thumbs_up'] / total
    
    def get_recent_feedback(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent feedback.
        
        Args:
            limit: Number of recent feedback items
            
        Returns:
            List of recent feedback items
        """
        sorted_feedbacks = sorted(
            self.feedback_data['feedbacks'],
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        return sorted_feedbacks[:limit]


# Global instance
feedback_manager = FeedbackManager()