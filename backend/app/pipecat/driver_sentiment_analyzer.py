import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import re
from collections import defaultdict, deque
import math


logger = logging.getLogger(__name__)


class PredictionConfidence(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CallOutcomePrediction(Enum):
    SUCCESSFUL_DELIVERY = "successful_delivery"
    DELAYED_DELIVERY = "delayed_delivery"
    DELIVERY_ISSUE = "delivery_issue"
    ROUTE_CHANGE_NEEDED = "route_change_needed"
    EMERGENCY_SITUATION = "emergency_situation"
    DRIVER_ASSISTANCE_REQUIRED = "driver_assistance_required"
    CUSTOMER_COMPLAINT = "customer_complaint"
    EARLY_DELIVERY = "early_delivery"


class DriverMoodState(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    STRESSED = "stressed"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    CONFUSED = "confused"
    TIRED = "tired"
    URGENT = "urgent"


class RiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SentimentMetrics:
    dominant_sentiment: DriverMoodState
    sentiment_score: float  
    emotional_intensity: float  
    sentiment_stability: float  
    mood_indicators: List[str]
    stress_level: float 
    urgency_level: float 
    confidence: PredictionConfidence


@dataclass
class CallOutcomePredictionResult:
    predicted_outcome: CallOutcomePrediction
    confidence: PredictionConfidence
    probability_score: float
    contributing_factors: List[str]
    risk_assessment: RiskLevel
    recommended_actions: List[str]
    alternative_outcomes: List[Tuple[CallOutcomePrediction, float]]
    prediction_reasoning: List[str]


@dataclass
class DriverProfile:
    driver_id: str
    historical_sentiment_patterns: Dict[str, float]
    typical_call_outcomes: Dict[str, int]
    stress_triggers: List[str]
    communication_preferences: Dict[str, Any]
    performance_metrics: Dict[str, float]
    recent_interactions: List[Dict[str, Any]]
    risk_factors: List[str]
    last_updated: datetime


@dataclass
class PredictionFeatures:
    call_duration_so_far: float
    time_of_day: int 
    day_of_week: int 
    driver_historical_pattern: Dict[str, float]
    current_sentiment_score: float
    urgency_keywords_count: int
    negative_keywords_count: int
    positive_keywords_count: int
    interruption_count: int
    speech_pace: float
    silence_duration: float
    route_complexity: float
    weather_conditions: Optional[str]
    traffic_conditions: Optional[str]


class DriverSentimentAnalyzer:
    """
    Advanced driver sentiment analysis and call outcome prediction system
    """
    
    def __init__(self):
        self.sentiment_patterns = self._initialize_sentiment_patterns()
        self.outcome_predictors = self._initialize_outcome_predictors()
        self.driver_profiles: Dict[str, DriverProfile] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        self.model_weights = self._initialize_model_weights()
    
    def _initialize_sentiment_patterns(self) -> Dict[DriverMoodState, Dict[str, Any]]:
        """Initialize sentiment analysis patterns"""
        return {
            DriverMoodState.EXCELLENT: {
                'keywords': ['excellent', 'perfect', 'amazing', 'fantastic', 'great job', 'smooth', 'easy'],
                'tone_indicators': ['enthusiastic', 'upbeat', 'cheerful'],
                'speech_patterns': ['fast_pace', 'clear_articulation'],
                'base_score': 0.9
            },
            DriverMoodState.GOOD: {
                'keywords': ['good', 'fine', 'okay', 'satisfied', 'no problem', 'all set'],
                'tone_indicators': ['calm', 'steady', 'cooperative'],
                'speech_patterns': ['normal_pace', 'clear_speech'],
                'base_score': 0.6
            },
            DriverMoodState.NEUTRAL: {
                'keywords': ['understand', 'yes', 'okay', 'got it', 'received'],
                'tone_indicators': ['neutral', 'matter_of_fact'],
                'speech_patterns': ['steady_pace'],
                'base_score': 0.0
            },
            DriverMoodState.STRESSED: {
                'keywords': ['stressed', 'pressure', 'tight schedule', 'running late', 'behind'],
                'tone_indicators': ['tense', 'hurried', 'clipped'],
                'speech_patterns': ['fast_pace', 'short_responses'],
                'base_score': -0.4
            },
            DriverMoodState.FRUSTRATED: {
                'keywords': ['frustrated', 'annoying', 'ridiculous', 'fed up', 'sick of this'],
                'tone_indicators': ['irritated', 'impatient', 'sharp'],
                'speech_patterns': ['irregular_pace', 'interrupted_speech'],
                'base_score': -0.6
            },
            DriverMoodState.ANGRY: {
                'keywords': ['angry', 'furious', 'unacceptable', 'outrageous', 'demand', 'supervisor'],
                'tone_indicators': ['hostile', 'aggressive', 'loud'],
                'speech_patterns': ['raised_voice', 'rapid_speech'],
                'base_score': -0.8
            },
            DriverMoodState.CONFUSED: {
                'keywords': ['confused', 'dont understand', 'what do you mean', 'unclear', 'makes no sense'],
                'tone_indicators': ['uncertain', 'questioning', 'hesitant'],
                'speech_patterns': ['slow_pace', 'frequent_pauses'],
                'base_score': -0.2
            },
            DriverMoodState.TIRED: {
                'keywords': ['tired', 'exhausted', 'long day', 'worn out', 'need rest'],
                'tone_indicators': ['weary', 'low_energy', 'monotone'],
                'speech_patterns': ['slow_pace', 'long_pauses'],
                'base_score': -0.3
            },
            DriverMoodState.URGENT: {
                'keywords': ['urgent', 'emergency', 'asap', 'immediately', 'right now', 'critical'],
                'tone_indicators': ['pressing', 'intense', 'focused'],
                'speech_patterns': ['fast_pace', 'direct_communication'],
                'base_score': 0.1
            }
        }
    
    def _initialize_outcome_predictors(self) -> Dict[CallOutcomePrediction, Dict[str, Any]]:
        """Initialize outcome prediction patterns"""
        return {
            CallOutcomePrediction.SUCCESSFUL_DELIVERY: {
                'sentiment_indicators': [DriverMoodState.EXCELLENT, DriverMoodState.GOOD, DriverMoodState.NEUTRAL],
                'keywords': ['delivered', 'completed', 'finished', 'all set', 'confirmed'],
                'risk_factors': [],
                'base_probability': 0.7
            },
            CallOutcomePrediction.DELAYED_DELIVERY: {
                'sentiment_indicators': [DriverMoodState.STRESSED, DriverMoodState.FRUSTRATED],
                'keywords': ['delayed', 'late', 'traffic', 'behind schedule', 'running late'],
                'risk_factors': ['traffic_issues', 'weather_conditions'],
                'base_probability': 0.2
            },
            CallOutcomePrediction.DELIVERY_ISSUE: {
                'sentiment_indicators': [DriverMoodState.FRUSTRATED, DriverMoodState.CONFUSED],
                'keywords': ['issue', 'problem', 'wrong address', 'cant find', 'damaged'],
                'risk_factors': ['location_issues', 'cargo_problems'],
                'base_probability': 0.15
            },
            CallOutcomePrediction.ROUTE_CHANGE_NEEDED: {
                'sentiment_indicators': [DriverMoodState.CONFUSED, DriverMoodState.STRESSED],
                'keywords': ['lost', 'wrong way', 'directions', 'route', 'gps'],
                'risk_factors': ['navigation_issues', 'road_closures'],
                'base_probability': 0.1
            },
            CallOutcomePrediction.EMERGENCY_SITUATION: {
                'sentiment_indicators': [DriverMoodState.URGENT, DriverMoodState.STRESSED],
                'keywords': ['emergency', 'accident', 'breakdown', 'help', 'stuck'],
                'risk_factors': ['vehicle_issues', 'safety_concerns'],
                'base_probability': 0.05
            },
            CallOutcomePrediction.DRIVER_ASSISTANCE_REQUIRED: {
                'sentiment_indicators': [DriverMoodState.CONFUSED, DriverMoodState.TIRED],
                'keywords': ['help', 'assistance', 'dont know', 'unclear', 'guidance'],
                'risk_factors': ['experience_level', 'complex_delivery'],
                'base_probability': 0.1
            },
            CallOutcomePrediction.CUSTOMER_COMPLAINT: {
                'sentiment_indicators': [DriverMoodState.ANGRY, DriverMoodState.FRUSTRATED],
                'keywords': ['complaint', 'unhappy', 'unacceptable', 'supervisor', 'manager'],
                'risk_factors': ['service_issues', 'communication_problems'],
                'base_probability': 0.08
            },
            CallOutcomePrediction.EARLY_DELIVERY: {
                'sentiment_indicators': [DriverMoodState.EXCELLENT, DriverMoodState.GOOD],
                'keywords': ['early', 'ahead of schedule', 'ready now', 'faster than expected'],
                'risk_factors': [],
                'base_probability': 0.12
            }
        }
    
    def _initialize_model_weights(self) -> Dict[str, float]:
        """Initialize machine learning model weights"""
        return {
            'sentiment_score': 0.25,
            'keyword_match': 0.20,
            'historical_pattern': 0.15,
            'time_context': 0.10,
            'speech_patterns': 0.10,
            'driver_profile': 0.10,
            'external_factors': 0.10
        }
    
    async def analyze_driver_sentiment(self, call_id: str, conversation_segments: List[Dict[str, Any]], driver_id: str) -> SentimentMetrics:
        """
        Perform comprehensive driver sentiment analysis
        """
        try:
            features = await self._extract_sentiment_features(conversation_segments)
            
            driver_profile = await self._get_driver_profile(driver_id)
            
            sentiment_scores = await self._calculate_sentiment_scores(features, driver_profile)
            
            dominant_sentiment = await self._determine_dominant_sentiment(sentiment_scores)
            
            sentiment_score = sentiment_scores.get(dominant_sentiment, 0.0)
            emotional_intensity = await self._calculate_emotional_intensity(features)
            sentiment_stability = await self._calculate_sentiment_stability(sentiment_scores)
            stress_level = await self._calculate_stress_level(features, sentiment_scores)
            urgency_level = await self._calculate_urgency_level(features)
            
            mood_indicators = await self._extract_mood_indicators(features, dominant_sentiment)
            
            confidence = await self._calculate_sentiment_confidence(features, sentiment_scores)
            
            sentiment_metrics = SentimentMetrics(
                dominant_sentiment=dominant_sentiment,
                sentiment_score=sentiment_score,
                emotional_intensity=emotional_intensity,
                sentiment_stability=sentiment_stability,
                mood_indicators=mood_indicators,
                stress_level=stress_level,
                urgency_level=urgency_level,
                confidence=confidence
            )
            
            await self._update_driver_profile(driver_id, sentiment_metrics, features)
            
            logger.info(f"Sentiment analysis completed for driver {driver_id} in call {call_id}")
            return sentiment_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing driver sentiment: {e}")
            return await self._create_fallback_sentiment(driver_id)
    
    async def predict_call_outcome(self, call_id: str, sentiment_metrics: SentimentMetrics, call_context: Dict[str, Any]) -> CallOutcomePredictionResult:
        """
        Predict the likely outcome of the call based on sentiment and context
        """
        try:
            features = await self._extract_prediction_features(sentiment_metrics, call_context)
            
            outcome_probabilities = await self._calculate_outcome_probabilities(features, sentiment_metrics)
            
            predicted_outcome, probability = max(outcome_probabilities.items(), key=lambda x: x[1])
            
            confidence = await self._determine_prediction_confidence(probability, features)
            
            risk_level = await self._assess_risk_level(predicted_outcome, sentiment_metrics, features)
            
            recommended_actions = await self._generate_recommendations(predicted_outcome, sentiment_metrics, risk_level)
            
            alternative_outcomes = await self._get_alternative_outcomes(outcome_probabilities, predicted_outcome)
            
            reasoning = await self._generate_prediction_reasoning(predicted_outcome, sentiment_metrics, features)
            
            contributing_factors = await self._identify_contributing_factors(predicted_outcome, sentiment_metrics, features)
            
            prediction_result = CallOutcomePredictionResult(
                predicted_outcome=predicted_outcome,
                confidence=confidence,
                probability_score=probability,
                contributing_factors=contributing_factors,
                risk_assessment=risk_level,
                recommended_actions=recommended_actions,
                alternative_outcomes=alternative_outcomes,
                prediction_reasoning=reasoning
            )
            
            await self._record_prediction(call_id, prediction_result, sentiment_metrics, features)
            
            logger.info(f"Call outcome predicted for {call_id}: {predicted_outcome.value} (confidence: {confidence.value})")
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error predicting call outcome: {e}")
            return await self._create_fallback_prediction()
    
    async def _extract_sentiment_features(self, conversation_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features for sentiment analysis"""
        features = {
            'total_segments': len(conversation_segments),
            'total_duration': sum(seg.get('duration', 3.0) for seg in conversation_segments),
            'keyword_counts': defaultdict(int),
            'tone_indicators': [],
            'speech_patterns': [],
            'driver_segments': [seg for seg in conversation_segments if not seg.get('is_agent', False)]
        }
        
        for segment in features['driver_segments']:
            text = segment.get('text', '').lower()
            
            for sentiment_state, patterns in self.sentiment_patterns.items():
                for keyword in patterns['keywords']:
                    if keyword in text:
                        features['keyword_counts'][sentiment_state] += 1
        
        if features['driver_segments']:
            avg_segment_duration = sum(seg.get('duration', 3.0) for seg in features['driver_segments']) / len(features['driver_segments'])
            features['avg_speech_pace'] = avg_segment_duration
            features['interruption_count'] = sum(1 for seg in features['driver_segments'] if seg.get('interrupted', False))
        
        return features
    
    async def _get_driver_profile(self, driver_id: str) -> DriverProfile:
        """Get or create driver profile"""
        if driver_id not in self.driver_profiles:
            self.driver_profiles[driver_id] = DriverProfile(
                driver_id=driver_id,
                historical_sentiment_patterns={},
                typical_call_outcomes={},
                stress_triggers=[],
                communication_preferences={},
                performance_metrics={},
                recent_interactions=[],
                risk_factors=[],
                last_updated=datetime.utcnow()
            )
        
        return self.driver_profiles[driver_id]
    
    async def _calculate_sentiment_scores(self, features: Dict[str, Any], driver_profile: DriverProfile) -> Dict[DriverMoodState, float]:
        """Calculate sentiment scores for each mood state"""
        scores = {}
        
        for sentiment_state, patterns in self.sentiment_patterns.items():
            score = patterns['base_score']
            
            keyword_count = features['keyword_counts'].get(sentiment_state, 0)
            if keyword_count > 0:
                score += keyword_count * 0.2
            
            historical_score = driver_profile.historical_sentiment_patterns.get(sentiment_state.value, 0.0)
            score += historical_score * 0.1
            
            if features.get('avg_speech_pace', 3.0) > 5.0 and sentiment_state in [DriverMoodState.STRESSED, DriverMoodState.ANGRY]:
                score += 0.1
            elif features.get('avg_speech_pace', 3.0) < 2.0 and sentiment_state in [DriverMoodState.TIRED, DriverMoodState.CONFUSED]:
                score += 0.1
            
            scores[sentiment_state] = max(-1.0, min(1.0, score))
        
        return scores
    
    async def _determine_dominant_sentiment(self, sentiment_scores: Dict[DriverMoodState, float]) -> DriverMoodState:
        """Determine the dominant sentiment from scores"""
        if not sentiment_scores:
            return DriverMoodState.NEUTRAL
        
        return max(sentiment_scores.items(), key=lambda x: x[1])[0]
    
    async def _calculate_emotional_intensity(self, features: Dict[str, Any]) -> float:
        """Calculate emotional intensity (0.0 to 1.0)"""
        intensity = 0.0
        
        total_keywords = sum(features['keyword_counts'].values())
        if total_keywords > 0:
            intensity += min(0.5, total_keywords * 0.1)
        
        if features.get('interruption_count', 0) > 0:
            intensity += min(0.3, features['interruption_count'] * 0.1)
        
        normal_pace = 3.0
        pace_deviation = abs(features.get('avg_speech_pace', normal_pace) - normal_pace)
        intensity += min(0.2, pace_deviation * 0.05)
        
        return min(1.0, intensity)
    
    async def _calculate_sentiment_stability(self, sentiment_scores: Dict[DriverMoodState, float]) -> float:
        """Calculate how stable/consistent the sentiment is"""
        if not sentiment_scores:
            return 0.5
        
        scores = list(sentiment_scores.values())
        if len(scores) < 2:
            return 1.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        stability = 1.0 - min(1.0, variance)
        return stability
    
    async def _calculate_stress_level(self, features: Dict[str, Any], sentiment_scores: Dict[DriverMoodState, float]) -> float:
        """Calculate stress level (0.0 to 1.0)"""
        stress_indicators = [DriverMoodState.STRESSED, DriverMoodState.FRUSTRATED, DriverMoodState.ANGRY]
        stress_score = sum(sentiment_scores.get(state, 0.0) for state in stress_indicators)
        
        normalized_stress = (stress_score + 3.0) / 6.0
        
        if features.get('interruption_count', 0) > 2:
            normalized_stress += 0.1
        
        if features.get('avg_speech_pace', 3.0) > 4.0:
            normalized_stress += 0.1
        
        return min(1.0, max(0.0, normalized_stress))
    
    async def _calculate_urgency_level(self, features: Dict[str, Any]) -> float:
        """Calculate urgency level (0.0 to 1.0)"""
        urgency_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'right now']
        urgency_count = 0
        
        for segment in features['driver_segments']:
            text = segment.get('text', '').lower()
            urgency_count += sum(1 for keyword in urgency_keywords if keyword in text)
        
        urgency_level = min(1.0, urgency_count * 0.3)
        
        return urgency_level
    
    async def _extract_mood_indicators(self, features: Dict[str, Any], dominant_sentiment: DriverMoodState) -> List[str]:
        """Extract specific mood indicators"""
        indicators = []
        
        if dominant_sentiment in self.sentiment_patterns:
            patterns = self.sentiment_patterns[dominant_sentiment]
            
            for keyword in patterns['keywords']:
                for segment in features['driver_segments']:
                    if keyword in segment.get('text', '').lower():
                        indicators.append(f"keyword: {keyword}")
                        break
        
        if features.get('avg_speech_pace', 3.0) > 4.0:
            indicators.append("rapid speech")
        elif features.get('avg_speech_pace', 3.0) < 2.0:
            indicators.append("slow speech")
        
        if features.get('interruption_count', 0) > 0:
            indicators.append("frequent interruptions")
        
        return list(set(indicators)) 
    
    async def _calculate_sentiment_confidence(self, features: Dict[str, Any], sentiment_scores: Dict[DriverMoodState, float]) -> PredictionConfidence:
        """Calculate confidence in sentiment analysis"""
        if not sentiment_scores:
            return PredictionConfidence.VERY_LOW
        
        sorted_scores = sorted(sentiment_scores.values(), reverse=True)
        
        if len(sorted_scores) < 2:
            return PredictionConfidence.MEDIUM
        
        score_separation = sorted_scores[0] - sorted_scores[1]
        
        feature_quality = min(1.0, len(features['driver_segments']) / 5.0)  # 5 segments = good quality
        
        confidence_score = (score_separation + feature_quality) / 2.0
        
        if confidence_score >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.6:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.4:
            return PredictionConfidence.MEDIUM
        elif confidence_score >= 0.2:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def _extract_prediction_features(self, sentiment_metrics: SentimentMetrics, call_context: Dict[str, Any]) -> PredictionFeatures:
        """Extract features for outcome prediction"""
        current_time = datetime.utcnow()
        
        return PredictionFeatures(
            call_duration_so_far=call_context.get('duration', 0.0),
            time_of_day=current_time.hour,
            day_of_week=current_time.weekday(),
            driver_historical_pattern={}, 
            current_sentiment_score=sentiment_metrics.sentiment_score,
            urgency_keywords_count=int(sentiment_metrics.urgency_level * 10),
            negative_keywords_count=len([ind for ind in sentiment_metrics.mood_indicators if 'negative' in ind]),
            positive_keywords_count=len([ind for ind in sentiment_metrics.mood_indicators if 'positive' in ind]),
            interruption_count=0,
            speech_pace=1.0, 
            silence_duration=0.0,
            route_complexity=call_context.get('route_complexity', 0.5),
            weather_conditions=call_context.get('weather'),
            traffic_conditions=call_context.get('traffic')
        )
    
    async def _calculate_outcome_probabilities(self, features: PredictionFeatures, sentiment_metrics: SentimentMetrics) -> Dict[CallOutcomePrediction, float]:
        """Calculate probabilities for each outcome"""
        probabilities = {}
        
        for outcome, patterns in self.outcome_predictors.items():
            probability = patterns['base_probability']
            
            if sentiment_metrics.dominant_sentiment in patterns['sentiment_indicators']:
                probability += 0.2
            
            if outcome in [CallOutcomePrediction.DELIVERY_ISSUE, CallOutcomePrediction.EMERGENCY_SITUATION]:
                probability += sentiment_metrics.stress_level * 0.15
            
            if outcome == CallOutcomePrediction.EMERGENCY_SITUATION:
                probability += sentiment_metrics.urgency_level * 0.2
            
            if features.time_of_day >= 17 or features.time_of_day <= 6:  # Evening/night
                if outcome == CallOutcomePrediction.DELAYED_DELIVERY:
                    probability += 0.1
            
            probabilities[outcome] = min(1.0, max(0.0, probability))
        
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {outcome: prob / total_prob for outcome, prob in probabilities.items()}
        
        return probabilities
    
    async def _determine_prediction_confidence(self, probability: float, features: PredictionFeatures) -> PredictionConfidence:
        """Determine confidence in outcome prediction"""
        base_confidence = probability
        
        feature_quality = 0.5  
        
        combined_confidence = (base_confidence + feature_quality) / 2.0
        
        if combined_confidence >= 0.8:
            return PredictionConfidence.VERY_HIGH
        elif combined_confidence >= 0.6:
            return PredictionConfidence.HIGH
        elif combined_confidence >= 0.4:
            return PredictionConfidence.MEDIUM
        elif combined_confidence >= 0.2:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def _assess_risk_level(self, predicted_outcome: CallOutcomePrediction, sentiment_metrics: SentimentMetrics, features: PredictionFeatures) -> RiskLevel:
        """Assess risk level based on prediction and sentiment"""
        risk_score = 0.0
        
        high_risk_outcomes = [
            CallOutcomePrediction.EMERGENCY_SITUATION,
            CallOutcomePrediction.CUSTOMER_COMPLAINT,
            CallOutcomePrediction.DELIVERY_ISSUE
        ]
        
        if predicted_outcome in high_risk_outcomes:
            risk_score += 0.4
        
        if sentiment_metrics.dominant_sentiment in [DriverMoodState.ANGRY, DriverMoodState.FRUSTRATED]:
            risk_score += 0.3
        
        risk_score += sentiment_metrics.stress_level * 0.2
        
        risk_score += sentiment_metrics.urgency_level * 0.1
        
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        elif risk_score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    async def _generate_recommendations(self, predicted_outcome: CallOutcomePrediction, sentiment_metrics: SentimentMetrics, risk_level: RiskLevel) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        outcome_recommendations = {
            CallOutcomePrediction.EMERGENCY_SITUATION: [
                "Immediate escalation to emergency protocols",
                "Verify driver location and safety",
                "Prepare emergency response team"
            ],
            CallOutcomePrediction.DELIVERY_ISSUE: [
                "Proactively contact customer",
                "Prepare alternative delivery options",
                "Have supervisor on standby"
            ],
            CallOutcomePrediction.DELAYED_DELIVERY: [
                "Update customer with realistic ETA",
                "Consider route optimization",
                "Monitor traffic conditions"
            ]
        }
        
        recommendations.extend(outcome_recommendations.get(predicted_outcome, []))
        
        if sentiment_metrics.dominant_sentiment in [DriverMoodState.FRUSTRATED, DriverMoodState.ANGRY]:
            recommendations.extend([
                "Use empathetic communication approach",
                "Allow driver to express concerns",
                "Offer concrete solutions"
            ])
        
        # Risk-specific recommendations
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "Escalate to supervisor immediately",
                "Document all interactions",
                "Prepare incident report"
            ])
        
        return recommendations
    
    async def _get_alternative_outcomes(self, outcome_probabilities: Dict[CallOutcomePrediction, float], predicted_outcome: CallOutcomePrediction) -> List[Tuple[CallOutcomePrediction, float]]:
        """Get alternative outcomes with their probabilities"""
        alternatives = [
            (outcome, prob) for outcome, prob in outcome_probabilities.items()
            if outcome != predicted_outcome
        ]
        
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives[:3]
    
    async def _generate_prediction_reasoning(self, predicted_outcome: CallOutcomePrediction, sentiment_metrics: SentimentMetrics, features: PredictionFeatures) -> List[str]:
        """Generate human-readable reasoning for the prediction"""
        reasoning = []
        
        reasoning.append(f"Dominant sentiment: {sentiment_metrics.dominant_sentiment.value}")
        reasoning.append(f"Sentiment score: {sentiment_metrics.sentiment_score:.2f}")
        
        if sentiment_metrics.stress_level > 0.6:
            reasoning.append(f"High stress level detected: {sentiment_metrics.stress_level:.2f}")
        
        if sentiment_metrics.urgency_level > 0.5:
            reasoning.append(f"Urgency indicators present: {sentiment_metrics.urgency_level:.2f}")
        
        reasoning.append(f"Call duration: {features.call_duration_so_far:.1f} seconds")
        
        if features.time_of_day < 6 or features.time_of_day > 18:
            reasoning.append("Outside normal business hours")
        
        return reasoning
    
    async def _identify_contributing_factors(self, predicted_outcome: CallOutcomePrediction, sentiment_metrics: SentimentMetrics, features: PredictionFeatures) -> List[str]:
        """Identify factors contributing to the prediction"""
        factors = []
        
        if sentiment_metrics.sentiment_score < -0.3:
            factors.append("Negative sentiment detected")
        
        if sentiment_metrics.stress_level > 0.5:
            factors.append("Elevated stress level")
        
        if sentiment_metrics.urgency_level > 0.4:
            factors.append("Urgency indicators present")
        
        for indicator in sentiment_metrics.mood_indicators:
            factors.append(f"Mood indicator: {indicator}")
        
        if features.weather_conditions:
            factors.append(f"Weather conditions: {features.weather_conditions}")
        
        if features.traffic_conditions:
            factors.append(f"Traffic conditions: {features.traffic_conditions}")
        
        return factors
    
    async def _record_prediction(self, call_id: str, prediction: CallOutcomePredictionResult, sentiment: SentimentMetrics, features: PredictionFeatures):
        """Record prediction for learning and analytics"""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'call_id': call_id,
            'predicted_outcome': prediction.predicted_outcome.value,
            'confidence': prediction.confidence.value,
            'probability_score': prediction.probability_score,
            'sentiment_score': sentiment.sentiment_score,
            'stress_level': sentiment.stress_level,
            'urgency_level': sentiment.urgency_level,
            'risk_level': prediction.risk_assessment.value
        }
        
        self.prediction_history.append(record)
        
        # Keep only recent history
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]
    
    async def _update_driver_profile(self, driver_id: str, sentiment_metrics: SentimentMetrics, features: Dict[str, Any]):
        """Update driver profile with new interaction data"""
        if driver_id not in self.driver_profiles:
            return
        
        profile = self.driver_profiles[driver_id]
        
        sentiment_key = sentiment_metrics.dominant_sentiment.value
        if sentiment_key not in profile.historical_sentiment_patterns:
            profile.historical_sentiment_patterns[sentiment_key] = 0.0
        
        profile.historical_sentiment_patterns[sentiment_key] = (
            profile.historical_sentiment_patterns[sentiment_key] * 0.8 + 
            sentiment_metrics.sentiment_score * 0.2
        )
        
        interaction_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'sentiment': sentiment_metrics.dominant_sentiment.value,
            'stress_level': sentiment_metrics.stress_level,
            'urgency_level': sentiment_metrics.urgency_level
        }
        
        profile.recent_interactions.append(interaction_record)
        
        if len(profile.recent_interactions) > 10:
            profile.recent_interactions = profile.recent_interactions[-10:]
        
        profile.last_updated = datetime.utcnow()
    
    async def _create_fallback_sentiment(self, driver_id: str) -> SentimentMetrics:
        """Create fallback sentiment analysis when analysis fails"""
        return SentimentMetrics(
            dominant_sentiment=DriverMoodState.NEUTRAL,
            sentiment_score=0.0,
            emotional_intensity=0.0,
            sentiment_stability=0.5,
            mood_indicators=[],
            stress_level=0.0,
            urgency_level=0.0,
            confidence=PredictionConfidence.VERY_LOW
        )
    
    async def _create_fallback_prediction(self) -> CallOutcomePredictionResult:
        """Create fallback prediction when prediction fails"""
        return CallOutcomePredictionResult(
            predicted_outcome=CallOutcomePrediction.SUCCESSFUL_DELIVERY,
            confidence=PredictionConfidence.VERY_LOW,
            probability_score=0.5,
            contributing_factors=['Insufficient data'],
            risk_assessment=RiskLevel.MEDIUM,
            recommended_actions=['Monitor call closely'],
            alternative_outcomes=[],
            prediction_reasoning=['Fallback prediction due to analysis error']
        )
    
    async def get_driver_profile(self, driver_id: str) -> Optional[DriverProfile]:
        """Get driver profile"""
        return self.driver_profiles.get(driver_id)
    
    async def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for sentiment analysis and predictions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_predictions = [
            record for record in self.prediction_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
        
        if not recent_predictions:
            return {'total_predictions': 0, 'message': 'No recent prediction data'}
        
        total_predictions = len(recent_predictions)
        avg_confidence = len([p for p in recent_predictions if p['confidence'] in ['high', 'very_high']]) / total_predictions
        avg_sentiment = sum(p['sentiment_score'] for p in recent_predictions) / total_predictions
        avg_stress = sum(p['stress_level'] for p in recent_predictions) / total_predictions
        
        outcome_distribution = defaultdict(int)
        risk_distribution = defaultdict(int)
        
        for prediction in recent_predictions:
            outcome_distribution[prediction['predicted_outcome']] += 1
            risk_distribution[prediction['risk_level']] += 1
        
        return {
            'total_predictions': total_predictions,
            'high_confidence_predictions': avg_confidence,
            'average_sentiment_score': avg_sentiment,
            'average_stress_level': avg_stress,
            'outcome_distribution': dict(outcome_distribution),
            'risk_distribution': dict(risk_distribution),
            'total_driver_profiles': len(self.driver_profiles)
        }


_sentiment_analyzer: Optional[DriverSentimentAnalyzer] = None


def get_sentiment_analyzer() -> Optional[DriverSentimentAnalyzer]:
    """Get the global sentiment analyzer instance"""
    global _sentiment_analyzer
    return _sentiment_analyzer


async def initialize_sentiment_analyzer():
    """Initialize the global sentiment analyzer"""
    global _sentiment_analyzer
    
    if _sentiment_analyzer is None:
        _sentiment_analyzer = DriverSentimentAnalyzer()
        logger.info("Driver sentiment analyzer initialized")
    
    return _sentiment_analyzer