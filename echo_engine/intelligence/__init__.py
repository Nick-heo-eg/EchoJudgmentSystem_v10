"""
Echo Intelligence System - Thin Adapters
========================================

Thin intelligence adapters that enhance existing Echo components:
- IntelligenceEvaluator: Standardizes intelligence metrics over ResultVerifier
- EvolutionAdapter: Provides learning hints over PatternMemory
"""

from .intelligence_evaluator import MultiDimensionalIntelligenceEvaluator
from .evolution_adapter import EvolutionAdapter
from .adaptive_memory import AdaptiveLearningMemory  
from .cognitive_evolution import CognitiveEvolutionTracker
from .meta_reasoning import MetaReasoningEngine
from .strategic_cognition import AdvancedStrategicPlanner

__all__ = ["MultiDimensionalIntelligenceEvaluator", "EvolutionAdapter", 
           "AdaptiveLearningMemory", "CognitiveEvolutionTracker", 
           "MetaReasoningEngine", "AdvancedStrategicPlanner"]

__version__ = "1.0.0-thin"
