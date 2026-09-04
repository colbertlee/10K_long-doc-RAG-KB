"""RAGAS evaluation framework for RAG quality assessment."""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_entity_recall,
        context_precision,
        context_recall,
        faithfulness,
    )
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("RAGAS not available. Install with: pip install ragas", flush=True)


@dataclass
class EvaluationCase:
    """Single evaluation case for RAGAS."""
    question: str
    contexts: list[str]
    answer: str
    ground_truth: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class EvaluationResult:
    """Evaluation result from RAGAS."""
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float | None = None
    context_entity_recall: float | None = None
    overall_score: float = 0.0


class RAGASEvaluator:
    """RAGAS-based RAG quality evaluator."""
    
    def __init__(self, use_ragas: bool = True):
        """Initialize RAGAS evaluator.
        
        Args:
            use_ragas: Whether to use RAGAS (requires installation)
        """
        self.use_ragas = use_ragas and RAGAS_AVAILABLE
        self.evaluation_cases: list[EvaluationCase] = []
        self._initialized = False
    
    async def initialize(self):
        """Initialize the evaluator."""
        if self._initialized:
            return
        
        if self.use_ragas:
            print("RAGAS evaluator initialized", flush=True)
        else:
            print("Using fallback evaluation (RAGAS not available)", flush=True)
        
        self._initialized = True
    
    def add_evaluation_case(
        self,
        question: str,
        contexts: list[str],
        answer: str,
        ground_truth: str | None = None,
        metadata: dict[str, Any] | None = None
    ):
        """Add an evaluation case.
        
        Args:
            question: User question
            contexts: Retrieved contexts
            answer: Generated answer
            ground_truth: Ground truth answer (optional)
            metadata: Additional metadata
        """
        case = EvaluationCase(
            question=question,
            contexts=contexts,
            answer=answer,
            ground_truth=ground_truth,
            metadata=metadata
        )
        self.evaluation_cases.append(case)
    
    async def evaluate(self) -> dict[str, Any]:
        """Run evaluation on all cases.
        
        Returns:
            Evaluation results dictionary
        """
        if not self.evaluation_cases:
            return {"error": "No evaluation cases provided"}
        
        if self.use_ragas:
            return await self._evaluate_with_ragas()
        else:
            return await self._evaluate_fallback()
    
    async def _evaluate_with_ragas(self) -> dict[str, Any]:
        """Evaluate using RAGAS framework."""
        try:
            # Convert evaluation cases to RAGAS format
            dataset = [
                {
                    "question": case.question,
                    "contexts": case.contexts,
                    "answer": case.answer,
                    "ground_truth": case.ground_truth or ""
                }
                for case in self.evaluation_cases
            ]
            
            # Run evaluation
            result = await evaluate(
                dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                    context_entity_recall
                ]
            )
            
            # Calculate overall score
            overall_score = (
                result['faithfulness'] * 0.3 +
                result['answer_relevancy'] * 0.3 +
                result['context_precision'] * 0.2 +
                result.get('context_recall', 0) * 0.1 +
                result.get('context_entity_recall', 0) * 0.1
            )
            
            return {
                "faithfulness": result['faithfulness'],
                "answer_relevancy": result['answer_relevancy'],
                "context_precision": result['context_precision'],
                "context_recall": result.get('context_recall'),
                "context_entity_recall": result.get('context_entity_recall'),
                "overall_score": overall_score,
                "method": "RAGAS"
            }
            
        except Exception as e:
            print(f"RAGAS evaluation error: {e}", flush=True)
            return await self._evaluate_fallback()
    
    async def _evaluate_fallback(self) -> dict[str, Any]:
        """Fallback evaluation using simple heuristics."""
        total_faithfulness = 0.0
        total_relevancy = 0.0
        total_precision = 0.0
        
        for case in self.evaluation_cases:
            # Simple faithfulness: check if answer contains terms from contexts
            context_terms = set()
            for context in case.contexts:
                context_terms.update(context.lower().split())
            
            answer_terms = set(case.answer.lower().split())
            faithfulness = len(answer_terms & context_terms) / len(answer_terms) if answer_terms else 0
            total_faithfulness += faithfulness
            
            # Simple relevancy: check if answer addresses question
            question_terms = set(case.question.lower().split())
            relevancy = len(answer_terms & question_terms) / len(question_terms) if question_terms else 0
            total_relevancy += relevancy
            
            # Simple precision: check if contexts are relevant to question
            context_relevance = 0
            for context in case.contexts:
                context_terms = set(context.lower().split())
                if len(context_terms & question_terms) > 0:
                    context_relevance += 1
            precision = context_relevance / len(case.contexts) if case.contexts else 0
            total_precision += precision
        
        # Calculate averages
        num_cases = len(self.evaluation_cases)
        avg_faithfulness = total_faithfulness / num_cases
        avg_relevancy = total_relevancy / num_cases
        avg_precision = total_precision / num_cases
        
        overall_score = (
            avg_faithfulness * 0.3 +
            avg_relevancy * 0.3 +
            avg_precision * 0.4
        )
        
        return {
            "faithfulness": avg_faithfulness,
            "answer_relevancy": avg_relevancy,
            "context_precision": avg_precision,
            "context_recall": None,
            "context_entity_recall": None,
            "overall_score": overall_score,
            "method": "fallback"
        }
    
    def clear_cases(self):
        """Clear all evaluation cases."""
        self.evaluation_cases.clear()
    
    def save_results(self, results: dict[str, Any], filepath: Path):
        """Save evaluation results to file.
        
        Args:
            results: Evaluation results
            filepath: Path to save results
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filepath}", flush=True)
    
    def get_evaluation_summary(self) -> dict[str, Any]:
        """Get summary of current evaluation cases."""
        return {
            "total_cases": len(self.evaluation_cases),
            "has_ground_truth": sum(1 for case in self.evaluation_cases if case.ground_truth),
            "avg_contexts_per_case": sum(len(case.contexts) for case in self.evaluation_cases) / len(self.evaluation_cases) if self.evaluation_cases else 0,
            "use_ragas": self.use_ragas
        }


class RAGQualityMonitor:
    """Continuous RAG quality monitoring system."""
    
    def __init__(self, evaluator: RAGASEvaluator):
        """Initialize quality monitor.
        
        Args:
            evaluator: RAGAS evaluator instance
        """
        self.evaluator = evaluator
        self.evaluation_history: list[dict[str, Any]] = []
        self.thresholds = {
            "faithfulness": 0.8,
            "answer_relevancy": 0.8,
            "context_precision": 0.7,
            "overall_score": 0.75
        }
    
    async def monitor_quality(
        self,
        question: str,
        contexts: list[str],
        answer: str,
        ground_truth: str | None = None
    ) -> dict[str, Any]:
        """Monitor quality of a single RAG interaction.
        
        Args:
            question: User question
            contexts: Retrieved contexts
            answer: Generated answer
            ground_truth: Ground truth answer (optional)
            
        Returns:
            Quality assessment with alerts
        """
        # Add evaluation case
        self.evaluator.add_evaluation_case(
            question=question,
            contexts=contexts,
            answer=answer,
            ground_truth=ground_truth
        )
        
        # Run evaluation
        results = await self.evaluator.evaluate()
        
        # Check for quality issues
        alerts = []
        for metric, threshold in self.thresholds.items():
            if metric in results and results[metric] < threshold:
                alerts.append({
                    "metric": metric,
                    "value": results[metric],
                    "threshold": threshold,
                    "message": f"{metric} below threshold: {results[metric]:.2f} < {threshold}"
                })
        
        # Store in history
        self.evaluation_history.append({
            "timestamp": str(asyncio.get_event_loop().time()),
            "results": results,
            "alerts": alerts
        })
        
        return {
            "quality_score": results.get("overall_score", 0),
            "metrics": results,
            "alerts": alerts,
            "status": "warning" if alerts else "good"
        }
    
    def get_quality_trends(self) -> dict[str, Any]:
        """Get quality trends over time."""
        if not self.evaluation_history:
            return {"error": "No evaluation history"}
        
        # Calculate trends
        recent_scores = [h["results"].get("overall_score", 0) for h in self.evaluation_history[-10:]]
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        # Count alerts
        total_alerts = sum(len(h["alerts"]) for h in self.evaluation_history)
        
        return {
            "recent_avg_score": avg_score,
            "total_evaluations": len(self.evaluation_history),
            "total_alerts": total_alerts,
            "alert_rate": total_alerts / len(self.evaluation_history) if self.evaluation_history else 0
        }