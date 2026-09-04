"""RAG evaluation module for quality assessment and regression testing."""

from .rag_judge import RAGExpertJudge, JudgeEvaluation, evaluate_rag_quality
from .eval_sets import (
    EvaluationSet,
    EvaluationSetManager,
    EvaluationTestCase,
    EvaluationSetCategory,
    EvaluationSetStatus,
    EvaluationSetFactory
)
from .regression_tester import (
    RegressionTester,
    RegressionTestResult,
    RegressionTestReport,
    RegressionTestStatus,
    RegressionSeverity,
    RegressionTestScheduler
)
from .eval_runner import (
    EvaluationSetExecutor,
    ExecutionConfig,
    ExecutionMode,
    ExecutionResult,
    ReportGenerator,
    ReportFormat
)

__all__ = [
    # Expert judge
    'RAGExpertJudge',
    'JudgeEvaluation', 
    'evaluate_rag_quality',
    # Evaluation sets
    'EvaluationSet',
    'EvaluationSetManager',
    'EvaluationTestCase',
    'EvaluationSetCategory',
    'EvaluationSetStatus',
    'EvaluationSetFactory',
    # Regression testing
    'RegressionTester',
    'RegressionTestResult',
    'RegressionTestReport',
    'RegressionTestStatus',
    'RegressionSeverity',
    'RegressionTestScheduler',
    # Execution and reporting
    'EvaluationSetExecutor',
    'ExecutionConfig',
    'ExecutionMode',
    'ExecutionResult',
    'ReportGenerator',
    'ReportFormat'
]