"""User feedback collection and analysis system."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class FeedbackCollector:
    """Collect and manage user feedback for RAG system."""
    
    def __init__(self, feedback_dir: Path):
        """Initialize feedback collector.
        
        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback.json"
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> dict[str, Any]:
        """Load feedback data from file.
        
        Returns:
            Dictionary containing feedback data
        """
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading feedback data: {e}")
                return self._init_feedback_data()
        else:
            return self._init_feedback_data()
    
    def _init_feedback_data(self) -> dict[str, Any]:
        """Initialize empty feedback data structure.
        
        Returns:
            Empty feedback data structure
        """
        return {
            "feedbacks": [],
            "statistics": {
                "total_feedbacks": 0,
                "positive_count": 0,
                "negative_count": 0,
                "average_rating": 0.0
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_feedback(self):
        """Save feedback data to file."""
        try:
            self.feedback_data["last_updated"] = datetime.now().isoformat()
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving feedback data: {e}")
    
    def add_feedback(self, feedback: dict[str, Any]) -> bool:
        """Add user feedback.
        
        Args:
            feedback: Dictionary containing feedback data
                - user_id: User identifier
                - query: User query
                - answer: System answer
                - rating: User rating (positive/negative or 1-5)
                - comment: Optional user comment
                - timestamp: Feedback timestamp
                
        Returns:
            True if feedback was added successfully
        """
        try:
            feedback_id = f"feedback_{datetime.now().timestamp()}"
            feedback_entry = {
                "id": feedback_id,
                "user_id": feedback.get("user_id", "anonymous"),
                "query": feedback.get("query", ""),
                "answer": feedback.get("answer", ""),
                "rating": feedback.get("rating", "neutral"),
                "comment": feedback.get("comment", ""),
                "timestamp": feedback.get("timestamp", datetime.now().isoformat()),
                "sources": feedback.get("sources", []),
                "search_mode": feedback.get("search_mode", "hybrid")
            }
            
            self.feedback_data["feedbacks"].append(feedback_entry)
            self._update_statistics()
            self._save_feedback()
            
            return True
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return False
    
    def _update_statistics(self):
        """Update feedback statistics."""
        feedbacks = self.feedback_data["feedbacks"]
        total = len(feedbacks)
        
        positive_count = sum(1 for f in feedbacks if f["rating"] in ["positive", 4, 5])
        negative_count = sum(1 for f in feedbacks if f["rating"] in ["negative", 1, 2])
        
        # Calculate average rating (convert ratings to numeric)
        numeric_ratings = []
        for f in feedbacks:
            rating = f["rating"]
            if isinstance(rating, (int, float)):
                numeric_ratings.append(rating)
            elif rating == "positive":
                numeric_ratings.append(5)
            elif rating == "negative":
                numeric_ratings.append(1)
            elif rating == "neutral":
                numeric_ratings.append(3)
        
        average_rating = sum(numeric_ratings) / len(numeric_ratings) if numeric_ratings else 0.0
        
        self.feedback_data["statistics"] = {
            "total_feedbacks": total,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "average_rating": average_rating,
            "positive_rate": positive_count / total if total > 0 else 0.0
        }
    
    def get_feedback(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Get feedback entries.
        
        Args:
            limit: Maximum number of feedback entries to return
            offset: Number of entries to skip
            
        Returns:
            List of feedback entries
        """
        feedbacks = self.feedback_data["feedbacks"]
        # Return most recent first
        feedbacks_sorted = sorted(feedbacks, key=lambda x: x["timestamp"], reverse=True)
        return feedbacks_sorted[offset:offset + limit]
    
    def get_statistics(self) -> dict[str, Any]:
        """Get feedback statistics.
        
        Returns:
            Dictionary containing feedback statistics
        """
        return self.feedback_data["statistics"]
    
    def get_feedback_by_query(self, query: str) -> list[dict[str, Any]]:
        """Get feedback for specific query patterns.
        
        Args:
            query: Query pattern to search for
            
        Returns:
            List of matching feedback entries
        """
        feedbacks = self.feedback_data["feedbacks"]
        query_lower = query.lower()
        
        matching = []
        for feedback in feedbacks:
            if query_lower in feedback["query"].lower():
                matching.append(feedback)
        
        return matching
    
    def get_low_quality_queries(self, threshold: float = 2.0) -> list[dict[str, Any]]:
        """Get queries with low user ratings.
        
        Args:
            threshold: Rating threshold below which queries are considered low quality
            
        Returns:
            List of low-quality query feedback entries
        """
        feedbacks = self.feedback_data["feedbacks"]
        low_quality = []
        
        for feedback in feedbacks:
            rating = feedback["rating"]
            numeric_rating = rating if isinstance(rating, (int, float)) else (
                1 if rating == "negative" else 5 if rating == "positive" else 3
            )
            
            if numeric_rating < threshold:
                low_quality.append(feedback)
        
        return sorted(low_quality, key=lambda x: x["timestamp"], reverse=True)
    
    def analyze_feedback_trends(self, days: int = 7) -> dict[str, Any]:
        """Analyze feedback trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        feedbacks = self.feedback_data["feedbacks"]
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        recent_feedbacks = [
            f for f in feedbacks 
            if datetime.fromisoformat(f["timestamp"]).timestamp() > cutoff_date
        ]
        
        if not recent_feedbacks:
            return {"message": "No recent feedback available"}
        
        # Calculate daily trends
        daily_trends = {}
        for feedback in recent_feedbacks:
            date = feedback["timestamp"][:10]  # YYYY-MM-DD
            if date not in daily_trends:
                daily_trends[date] = {"positive": 0, "negative": 0, "total": 0}
            
            daily_trends[date]["total"] += 1
            if feedback["rating"] in ["positive", 4, 5]:
                daily_trends[date]["positive"] += 1
            elif feedback["rating"] in ["negative", 1, 2]:
                daily_trends[date]["negative"] += 1
        
        return {
            "period_days": days,
            "total_feedbacks": len(recent_feedbacks),
            "daily_trends": daily_trends,
            "average_daily_rating": sum(
                daily_trends[date]["positive"] / daily_trends[date]["total"] 
                for date in daily_trends
            ) / len(daily_trends) if daily_trends else 0.0
        }


class FeedbackAnalyzer:
    """Analyze user feedback to improve RAG system."""
    
    def __init__(self, feedback_collector: FeedbackCollector):
        """Initialize feedback analyzer.
        
        Args:
            feedback_collector: FeedbackCollector instance
        """
        self.collector = feedback_collector
    
    def identify_common_issues(self) -> list[dict[str, Any]]:
        """Identify common issues from negative feedback.
        
        Returns:
            List of common issues with frequency
        """
        low_quality = self.collector.get_low_quality_queries()
        
        # Analyze common patterns in negative feedback
        issue_patterns = {}
        
        for feedback in low_quality:
            query = feedback["query"].lower()
            answer = feedback["answer"].lower()
            comment = feedback.get("comment", "").lower()
            
            # Check for common issue patterns
            if "not relevant" in comment or "irrelevant" in comment:
                issue_patterns["relevance"] = issue_patterns.get("relevance", 0) + 1
            if "incomplete" in comment or "missing" in comment:
                issue_patterns["completeness"] = issue_patterns.get("completeness", 0) + 1
            if "inaccurate" in comment or "wrong" in comment:
                issue_patterns["accuracy"] = issue_patterns.get("accuracy", 0) + 1
            if "slow" in comment or "timeout" in comment:
                issue_patterns["performance"] = issue_patterns.get("performance", 0) + 1
        
        # Sort by frequency
        sorted_issues = sorted(
            issue_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [{"issue": issue, "frequency": freq} for issue, freq in sorted_issues]
    
    def suggest_improvements(self) -> list[str]:
        """Suggest system improvements based on feedback.
        
        Returns:
            List of improvement suggestions
        """
        common_issues = self.identify_common_issues()
        suggestions = []
        
        for issue in common_issues:
            if issue["issue"] == "relevance":
                suggestions.append("Improve retrieval precision with better ranking")
            elif issue["issue"] == "completeness":
                suggestions.append("Increase context window or improve chunking strategy")
            elif issue["issue"] == "accuracy":
                suggestions.append("Enhance answer generation with fact-checking")
            elif issue["issue"] == "performance":
                suggestions.append("Optimize query processing and caching")
        
        # Add general suggestions based on overall statistics
        stats = self.collector.get_statistics()
        if stats["positive_rate"] < 0.7:
            suggestions.append("Overall satisfaction is low - consider reviewing retrieval quality")
        
        return suggestions