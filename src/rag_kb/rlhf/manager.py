"""Basic RLHF (Reinforcement Learning from Human Feedback) system."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class FeedbackLabel(Enum):
    """Feedback labels for RLHF training."""
    POSITIVE = "positive"      # Good response
    NEGATIVE = "negative"      # Bad response
    NEUTRAL = "neutral"        # Average response


@dataclass
class RLHFTrainingExample:
    """Training example for RLHF."""
    example_id: str
    query: str
    response: str
    label: FeedbackLabel
    feedback_reason: Optional[str] = None
    user_id: str = "anonymous"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'example_id': self.example_id,
            'query': self.query,
            'response': self.response,
            'label': self.label.value,
            'feedback_reason': self.feedback_reason,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class RewardModel:
    """Simple reward model for response quality scoring."""
    
    def __init__(self):
        """Initialize reward model."""
        self.weights = {
            'relevance': 0.4,
            'accuracy': 0.3,
            'completeness': 0.2,
            'clarity': 0.1
        }
    
    def calculate_reward(self, query: str, response: str, 
                        context: Dict[str, Any] = None) -> float:
        """Calculate reward score for a response.
        
        Args:
            query: User query
            response: Model response
            context: Additional context
            
        Returns:
            Reward score (0-1)
        """
        if context is None:
            context = {}
        
        # Calculate individual scores
        relevance_score = self._calculate_relevance(query, response)
        accuracy_score = self._calculate_accuracy(response, context)
        completeness_score = self._calculate_completeness(query, response)
        clarity_score = self._calculate_clarity(response)
        
        # Weighted combination
        reward = (
            relevance_score * self.weights['relevance'] +
            accuracy_score * self.weights['accuracy'] +
            completeness_score * self.weights['completeness'] +
            clarity_score * self.weights['clarity']
        )
        
        return min(reward, 1.0)
    
    def _calculate_relevance(self, query: str, response: str) -> float:
        """Calculate relevance score.
        
        Args:
            query: User query
            response: Model response
            
        Returns:
            Relevance score (0-1)
        """
        query_terms = set(query.lower().split())
        response_terms = set(response.lower().split())
        
        if not query_terms:
            return 0.5
        
        overlap = len(query_terms & response_terms)
        return overlap / len(query_terms)
    
    def _calculate_accuracy(self, response: str, context: Dict[str, Any]) -> float:
        """Calculate accuracy score based on context.
        
        Args:
            response: Model response
            context: Context information
            
        Returns:
            Accuracy score (0-1)
        """
        # Check if response contains factual information
        if context.get('has_citations'):
            return 0.8  # Responses with citations are more likely accurate
        
        # Check response length (very short responses may be inaccurate)
        if len(response) < 50:
            return 0.3
        
        return 0.6  # Default moderate score
    
    def _calculate_completeness(self, query: str, response: str) -> float:
        """Calculate completeness score.
        
        Args:
            query: User query
            response: Model response
            
        Returns:
            Completeness score (0-1)
        """
        # Check if response addresses the query
        if not response:
            return 0.0
        
        # Check response length relative to query complexity
        query_complexity = len(query.split())
        response_length = len(response.split())
        
        if response_length < query_complexity * 2:
            return 0.4  # Response might be too short
        
        return 0.8  # Good completeness
    
    def _calculate_clarity(self, response: str) -> float:
        """Calculate clarity score.
        
        Args:
            response: Model response
            
        Returns:
            Clarity score (0-1)
        """
        if not response:
            return 0.0
        
        # Check for clear structure
        has_structure = any(char in response for char in ['\n', '。', '？', '！', '.', '?', '!'])
        
        if has_structure:
            return 0.8
        
        return 0.5


class RLHFManager:
    """Manager for RLHF system operations."""
    
    def __init__(self):
        """Initialize RLHF manager."""
        from rag_kb.config import settings
        self.dataset_file = settings.data_dir / 'rlhf_dataset.json'
        self.reward_model = RewardModel()
        self.training_examples: List[RLHFTrainingExample] = []
        self._load_dataset()
    
    def _load_dataset(self):
        """Load training dataset from file."""
        if self.dataset_file.exists():
            try:
                with open(self.dataset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for example_data in data.get('examples', []):
                        self.training_examples.append(self._dict_to_example(example_data))
            except Exception as e:
                print(f"Error loading RLHF dataset: {e}")
    
    def _save_dataset(self):
        """Save training dataset to file."""
        try:
            data = {
                'examples': [example.to_dict() for example in self.training_examples],
                'total_examples': len(self.training_examples),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.dataset_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving RLHF dataset: {e}")
    
    def _dict_to_example(self, data: Dict[str, Any]) -> RLHFTrainingExample:
        """Convert dictionary to training example."""
        return RLHFTrainingExample(
            example_id=data['example_id'],
            query=data['query'],
            response=data['response'],
            label=FeedbackLabel(data['label']),
            feedback_reason=data.get('feedback_reason'),
            user_id=data.get('user_id', 'anonymous'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )
    
    def add_training_example(self, query: str, response: str, 
                           label: FeedbackLabel, feedback_reason: str = None,
                           user_id: str = "anonymous") -> Dict[str, Any]:
        """Add a training example from user feedback.
        
        Args:
            query: User query
            response: Model response
            label: Feedback label
            feedback_reason: Reason for feedback
            user_id: User ID
            
        Returns:
            Addition result
        """
        import uuid
        
        example = RLHFTrainingExample(
            example_id=f"example_{uuid.uuid4().hex[:8]}",
            query=query,
            response=response,
            label=label,
            feedback_reason=feedback_reason,
            user_id=user_id,
            metadata={
                'reward_score': self.reward_model.calculate_reward(query, response)
            }
        )
        
        self.training_examples.append(example)
        self._save_dataset()
        
        return {
            'success': True,
            'example_id': example.example_id,
            'reward_score': example.metadata['reward_score'],
            'message': 'Training example added successfully'
        }
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics.
        
        Returns:
            Dataset statistics
        """
        if not self.training_examples:
            return {
                'total_examples': 0,
                'positive_examples': 0,
                'negative_examples': 0,
                'neutral_examples': 0,
                'average_reward': 0.0
            }
        
        positive_count = sum(1 for e in self.training_examples if e.label == FeedbackLabel.POSITIVE)
        negative_count = sum(1 for e in self.training_examples if e.label == FeedbackLabel.NEGATIVE)
        neutral_count = sum(1 for e in self.training_examples if e.label == FeedbackLabel.NEUTRAL)
        
        average_reward = sum(e.metadata.get('reward_score', 0.0) for e in self.training_examples) / len(self.training_examples)
        
        return {
            'total_examples': len(self.training_examples),
            'positive_examples': positive_count,
            'negative_examples': negative_count,
            'neutral_examples': neutral_count,
            'average_reward': average_reward,
            'positive_rate': positive_count / len(self.training_examples) if self.training_examples else 0.0
        }
    
    def calculate_response_reward(self, query: str, response: str, 
                                 context: Dict[str, Any] = None) -> float:
        """Calculate reward score for a response.
        
        Args:
            query: User query
            response: Model response
            context: Additional context
            
        Returns:
            Reward score (0-1)
        """
        return self.reward_model.calculate_reward(query, response, context)
    
    def get_training_batch(self, batch_size: int = 10) -> List[Dict[str, Any]]:
        """Get a batch of training examples.
        
        Args:
            batch_size: Number of examples to return
            
        Returns:
            Batch of training examples
        """
        if not self.training_examples:
            return []
        
        # Return most recent examples
        recent_examples = self.training_examples[-batch_size:]
        
        return [example.to_dict() for example in recent_examples]
    
    def filter_by_label(self, label: FeedbackLabel) -> List[Dict[str, Any]]:
        """Filter training examples by label.
        
        Args:
            label: Feedback label to filter by
            
        Returns:
            Filtered examples
        """
        return [
            example.to_dict()
            for example in self.training_examples
            if example.label == label
        ]


# Global instance
rlhf_manager = RLHFManager()