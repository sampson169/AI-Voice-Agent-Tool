import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import re
from collections import defaultdict


logger = logging.getLogger(__name__)


class SentimentType(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    CONFUSED = "confused"
    URGENT = "urgent"


class ConversationPhase(Enum):
    GREETING = "greeting"
    INFORMATION_GATHERING = "information_gathering"
    PROBLEM_SOLVING = "problem_solving"
    CONFIRMATION = "confirmation"
    CLOSING = "closing"
    ESCALATION = "escalation"


class KeywordCategory(Enum):
    EMERGENCY = "emergency"
    LOCATION = "location"
    TIME = "time"
    DELIVERY = "delivery"
    ISSUE = "issue"
    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass
class ConversationSegment:
    timestamp: datetime
    speaker: str  # 'agent' or 'driver'
    text: str
    duration: float
    confidence: float
    sentiment: SentimentType
    keywords: List[str]
    phase: ConversationPhase


@dataclass
class ConversationInsight:
    insight_type: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    actionable: bool
    priority: str


@dataclass
class ConversationSummary:
    call_id: str
    total_duration: float
    participant_talk_time: Dict[str, float]
    dominant_sentiment: SentimentType
    sentiment_progression: List[Tuple[datetime, SentimentType]]
    key_topics: List[str]
    main_issues: List[str]
    resolution_status: str
    action_items: List[str]
    insights: List[ConversationInsight]
    conversation_flow: List[ConversationPhase]
    effectiveness_score: float
    driver_satisfaction_score: float
    created_at: datetime


class ConversationAnalyzer:
    """
    Advanced conversation analysis and summarization system for driver interactions
    """
    
    def __init__(self):
        self.keyword_patterns = self._initialize_keyword_patterns()
        self.sentiment_indicators = self._initialize_sentiment_indicators()
        self.conversation_templates = self._initialize_conversation_templates()
        self.analysis_cache: Dict[str, ConversationSummary] = {}
    
    def _initialize_keyword_patterns(self) -> Dict[KeywordCategory, List[str]]:
        """Initialize keyword patterns for conversation analysis"""
        return {
            KeywordCategory.EMERGENCY: [
                'emergency', 'urgent', 'help', 'accident', 'stuck', 'breakdown',
                'medical', 'police', 'fire', 'dangerous', 'immediate', 'critical'
            ],
            KeywordCategory.LOCATION: [
                'location', 'address', 'where', 'gps', 'coordinates', 'mile marker',
                'exit', 'highway', 'street', 'building', 'warehouse', 'facility'
            ],
            KeywordCategory.TIME: [
                'time', 'when', 'schedule', 'appointment', 'delay', 'late', 'early',
                'eta', 'arrival', 'departure', 'deadline', 'urgent', 'asap'
            ],
            KeywordCategory.DELIVERY: [
                'delivery', 'pickup', 'load', 'cargo', 'freight', 'shipment',
                'package', 'container', 'trailer', 'dock', 'unload', 'complete'
            ],
            KeywordCategory.ISSUE: [
                'problem', 'issue', 'trouble', 'error', 'wrong', 'mistake',
                'damaged', 'missing', 'lost', 'broken', 'complaint', 'concern'
            ],
            KeywordCategory.POSITIVE: [
                'good', 'great', 'excellent', 'perfect', 'satisfied', 'happy',
                'pleased', 'smooth', 'easy', 'helpful', 'thanks', 'appreciate'
            ],
            KeywordCategory.NEGATIVE: [
                'bad', 'terrible', 'awful', 'frustrated', 'angry', 'upset',
                'disappointed', 'difficult', 'confusing', 'useless', 'waste'
            ]
        }
    
    def _initialize_sentiment_indicators(self) -> Dict[SentimentType, List[str]]:
        """Initialize sentiment indicators for advanced analysis"""
        return {
            SentimentType.VERY_POSITIVE: [
                'excellent', 'amazing', 'perfect', 'outstanding', 'fantastic',
                'wonderful', 'brilliant', 'exceptional', 'superb'
            ],
            SentimentType.POSITIVE: [
                'good', 'great', 'nice', 'satisfied', 'happy', 'pleased',
                'helpful', 'smooth', 'easy', 'thanks', 'appreciate'
            ],
            SentimentType.NEUTRAL: [
                'okay', 'fine', 'normal', 'standard', 'regular', 'typical',
                'average', 'usual', 'understand', 'confirm'
            ],
            SentimentType.NEGATIVE: [
                'bad', 'not good', 'disappointed', 'difficult', 'confusing',
                'slow', 'delayed', 'issue', 'problem', 'concern'
            ],
            SentimentType.VERY_NEGATIVE: [
                'terrible', 'awful', 'horrible', 'disgusting', 'unacceptable',
                'worst', 'hate', 'furious', 'outrageous'
            ],
            SentimentType.FRUSTRATED: [
                'frustrated', 'annoyed', 'irritated', 'fed up', 'tired of',
                'sick of', 'had enough', 'cant believe', 'ridiculous'
            ],
            SentimentType.ANGRY: [
                'angry', 'mad', 'furious', 'livid', 'pissed', 'outraged',
                'demanding', 'unacceptable', 'supervisor', 'manager'
            ],
            SentimentType.CONFUSED: [
                'confused', 'dont understand', 'unclear', 'what do you mean',
                'can you explain', 'i dont get it', 'makes no sense'
            ],
            SentimentType.URGENT: [
                'urgent', 'emergency', 'asap', 'immediately', 'right now',
                'cant wait', 'time sensitive', 'critical', 'rush'
            ]
        }
    
    def _initialize_conversation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conversation flow templates"""
        return {
            'standard_inquiry': {
                'phases': [
                    ConversationPhase.GREETING,
                    ConversationPhase.INFORMATION_GATHERING,
                    ConversationPhase.CONFIRMATION,
                    ConversationPhase.CLOSING
                ],
                'expected_duration': 180,
                'key_elements': ['greeting', 'load_identification', 'status_update', 'confirmation']
            },
            'problem_resolution': {
                'phases': [
                    ConversationPhase.GREETING,
                    ConversationPhase.INFORMATION_GATHERING,
                    ConversationPhase.PROBLEM_SOLVING,
                    ConversationPhase.CONFIRMATION,
                    ConversationPhase.CLOSING
                ],
                'expected_duration': 300,
                'key_elements': ['problem_identification', 'solution_proposal', 'implementation', 'verification']
            },
            'emergency_escalation': {
                'phases': [
                    ConversationPhase.INFORMATION_GATHERING,
                    ConversationPhase.ESCALATION
                ],
                'expected_duration': 120,
                'key_elements': ['emergency_assessment', 'immediate_action', 'escalation_protocol']
            }
        }
    
    async def analyze_conversation(self, call_id: str, conversation_data: List[Dict[str, Any]]) -> ConversationSummary:
        """
        Perform comprehensive conversation analysis and generate insights
        """
        try:
            segments = await self._parse_conversation_segments(conversation_data)
            
            conversation_flow = await self._analyze_conversation_flow(segments)
            
            sentiment_analysis = await self._analyze_sentiment_progression(segments)
            
            topics_and_issues = await self._extract_topics_and_issues(segments)
            
            talk_time = await self._calculate_talk_time(segments)
            
            insights = await self._generate_insights(segments, conversation_flow, sentiment_analysis)
            
            effectiveness_score = await self._calculate_effectiveness_score(segments, conversation_flow)
            satisfaction_score = await self._calculate_satisfaction_score(sentiment_analysis)
            
            summary = ConversationSummary(
                call_id=call_id,
                total_duration=sum(segment.duration for segment in segments),
                participant_talk_time=talk_time,
                dominant_sentiment=sentiment_analysis['dominant_sentiment'],
                sentiment_progression=sentiment_analysis['progression'],
                key_topics=topics_and_issues['topics'],
                main_issues=topics_and_issues['issues'],
                resolution_status=await self._determine_resolution_status(segments, insights),
                action_items=await self._extract_action_items(segments, insights),
                insights=insights,
                conversation_flow=conversation_flow,
                effectiveness_score=effectiveness_score,
                driver_satisfaction_score=satisfaction_score,
                created_at=datetime.utcnow()
            )
            
            self.analysis_cache[call_id] = summary
            
            logger.info(f"Conversation analysis completed for call {call_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing conversation {call_id}: {e}")
            return await self._create_fallback_summary(call_id, conversation_data)
    
    async def _parse_conversation_segments(self, conversation_data: List[Dict[str, Any]]) -> List[ConversationSegment]:
        """Parse raw conversation data into structured segments"""
        segments = []
        
        for item in conversation_data:
            try:
                speaker = 'agent' if item.get('is_agent', False) else 'driver'
                
                text = item.get('text', '').strip()
                if not text:
                    continue
                
                segment_sentiment = await self._analyze_segment_sentiment(text)
                
                keywords = await self._extract_keywords(text)
                
                phase = await self._determine_conversation_phase(text, len(segments))
                
                segment = ConversationSegment(
                    timestamp=datetime.fromisoformat(item.get('timestamp', datetime.utcnow().isoformat())),
                    speaker=speaker,
                    text=text,
                    duration=item.get('duration', 3.0),
                    confidence=item.get('confidence', 0.9),
                    sentiment=segment_sentiment,
                    keywords=keywords,
                    phase=phase
                )
                
                segments.append(segment)
                
            except Exception as e:
                logger.warning(f"Error parsing conversation segment: {e}")
                continue
        
        return segments
    
    async def _analyze_segment_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of a conversation segment"""
        text_lower = text.lower()
        
        sentiment_scores = {}
        
        for sentiment_type, indicators in self.sentiment_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                sentiment_scores[sentiment_type] = score
        
        if sentiment_scores:
            return max(sentiment_scores.items(), key=lambda x: x[1])[0]
        
        positive_count = sum(1 for word in self.keyword_patterns[KeywordCategory.POSITIVE] if word in text_lower)
        negative_count = sum(1 for word in self.keyword_patterns[KeywordCategory.NEGATIVE] if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        for category, keywords in self.keyword_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
        
        return list(set(found_keywords))  
    
    async def _determine_conversation_phase(self, text: str, segment_index: int) -> ConversationPhase:
        """Determine conversation phase based on content and position"""
        text_lower = text.lower()
        
        greeting_patterns = ['hello', 'hi', 'good morning', 'good afternoon', 'this is', 'calling about']
        if any(pattern in text_lower for pattern in greeting_patterns) and segment_index < 3:
            return ConversationPhase.GREETING
        
        closing_patterns = ['thank you', 'thanks', 'have a good', 'goodbye', 'take care', 'anything else']
        if any(pattern in text_lower for pattern in closing_patterns):
            return ConversationPhase.CLOSING
        
        emergency_patterns = ['emergency', 'urgent', 'supervisor', 'manager', 'escalate']
        if any(pattern in text_lower for pattern in emergency_patterns):
            return ConversationPhase.ESCALATION
        
        problem_patterns = ['fix', 'solve', 'help', 'solution', 'resolve', 'what can we do']
        if any(pattern in text_lower for pattern in problem_patterns):
            return ConversationPhase.PROBLEM_SOLVING
        
        confirmation_patterns = ['confirm', 'correct', 'verify', 'is that right', 'understand']
        if any(pattern in text_lower for pattern in confirmation_patterns):
            return ConversationPhase.CONFIRMATION
        
        return ConversationPhase.INFORMATION_GATHERING
    
    async def _analyze_conversation_flow(self, segments: List[ConversationSegment]) -> List[ConversationPhase]:
        """Analyze the flow of conversation phases"""
        if not segments:
            return []
        
        flow = []
        current_phase = None
        
        for segment in segments:
            if segment.phase != current_phase:
                flow.append(segment.phase)
                current_phase = segment.phase
        
        return flow
    
    async def _analyze_sentiment_progression(self, segments: List[ConversationSegment]) -> Dict[str, Any]:
        """Analyze how sentiment changes throughout the conversation"""
        if not segments:
            return {'dominant_sentiment': SentimentType.NEUTRAL, 'progression': []}
        
        progression = [(segment.timestamp, segment.sentiment) for segment in segments]
        
        sentiment_counts = defaultdict(int)
        for segment in segments:
            sentiment_counts[segment.sentiment] += 1
        
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'dominant_sentiment': dominant_sentiment,
            'progression': progression,
            'sentiment_distribution': dict(sentiment_counts)
        }
    
    async def _extract_topics_and_issues(self, segments: List[ConversationSegment]) -> Dict[str, List[str]]:
        """Extract key topics and issues from the conversation"""
        topics = set()
        issues = set()
        
        for segment in segments:
            for keyword in segment.keywords:
                if keyword in self.keyword_patterns[KeywordCategory.DELIVERY]:
                    topics.add('delivery_status')
                elif keyword in self.keyword_patterns[KeywordCategory.LOCATION]:
                    topics.add('location_information')
                elif keyword in self.keyword_patterns[KeywordCategory.TIME]:
                    topics.add('scheduling')
                elif keyword in self.keyword_patterns[KeywordCategory.EMERGENCY]:
                    topics.add('emergency_situation')
            
            if segment.sentiment in [SentimentType.NEGATIVE, SentimentType.VERY_NEGATIVE, SentimentType.FRUSTRATED, SentimentType.ANGRY]:
                for keyword in segment.keywords:
                    if keyword in self.keyword_patterns[KeywordCategory.ISSUE]:
                        issues.add(f'reported_{keyword}')
        
        return {
            'topics': list(topics),
            'issues': list(issues)
        }
    
    async def _calculate_talk_time(self, segments: List[ConversationSegment]) -> Dict[str, float]:
        """Calculate talk time for each participant"""
        talk_time = {'agent': 0.0, 'driver': 0.0}
        
        for segment in segments:
            talk_time[segment.speaker] += segment.duration
        
        return talk_time
    
    async def _generate_insights(self, segments: List[ConversationSegment], flow: List[ConversationPhase], sentiment_analysis: Dict[str, Any]) -> List[ConversationInsight]:
        """Generate actionable insights from conversation analysis"""
        insights = []
        
        dominant_sentiment = sentiment_analysis['dominant_sentiment']
        if dominant_sentiment in [SentimentType.NEGATIVE, SentimentType.VERY_NEGATIVE, SentimentType.FRUSTRATED, SentimentType.ANGRY]:
            insights.append(ConversationInsight(
                insight_type='sentiment_concern',
                description=f'Driver expressed {dominant_sentiment.value} sentiment during the call',
                confidence=0.8,
                supporting_evidence=[f'Dominant sentiment: {dominant_sentiment.value}'],
                actionable=True,
                priority='high'
            ))
        
        if ConversationPhase.ESCALATION in flow:
            insights.append(ConversationInsight(
                insight_type='escalation_occurred',
                description='Call required escalation - investigate root cause',
                confidence=0.9,
                supporting_evidence=['Escalation phase detected in conversation flow'],
                actionable=True,
                priority='high'
            ))
        
        total_duration = sum(segment.duration for segment in segments)
        if total_duration > 600:
            insights.append(ConversationInsight(
                insight_type='long_call_duration',
                description=f'Call duration ({total_duration:.1f}s) exceeds normal range - efficiency opportunity',
                confidence=0.7,
                supporting_evidence=[f'Total duration: {total_duration:.1f} seconds'],
                actionable=True,
                priority='medium'
            ))
        
        talk_time = await self._calculate_talk_time(segments)
        if talk_time['agent'] > talk_time['driver'] * 2:
            insights.append(ConversationInsight(
                insight_type='agent_dominated_conversation',
                description='Agent dominated conversation - consider more listening',
                confidence=0.6,
                supporting_evidence=[f'Agent talk time: {talk_time["agent"]:.1f}s, Driver: {talk_time["driver"]:.1f}s'],
                actionable=True,
                priority='low'
            ))
        
        emergency_keywords = sum(1 for segment in segments for keyword in segment.keywords if keyword in self.keyword_patterns[KeywordCategory.EMERGENCY])
        if emergency_keywords > 0:
            insights.append(ConversationInsight(
                insight_type='emergency_indicators',
                description=f'Emergency keywords detected ({emergency_keywords} instances)',
                confidence=0.8,
                supporting_evidence=[f'Emergency keyword count: {emergency_keywords}'],
                actionable=True,
                priority='critical'
            ))
        
        return insights
    
    async def _calculate_effectiveness_score(self, segments: List[ConversationSegment], flow: List[ConversationPhase]) -> float:
        """Calculate conversation effectiveness score (0.0 to 1.0)"""
        score = 0.5
        
        if ConversationPhase.GREETING in flow:
            score += 0.1
        if ConversationPhase.CONFIRMATION in flow:
            score += 0.1
        if ConversationPhase.CLOSING in flow:
            score += 0.1
        
        total_duration = sum(segment.duration for segment in segments)
        if 60 <= total_duration <= 300:
            score += 0.2
        elif total_duration > 600:
            score -= 0.2
        
        if ConversationPhase.ESCALATION in flow:
            score -= 0.3
        
        positive_segments = sum(1 for segment in segments if segment.sentiment in [SentimentType.POSITIVE, SentimentType.VERY_POSITIVE])
        total_segments = len(segments)
        if total_segments > 0:
            sentiment_ratio = positive_segments / total_segments
            score += sentiment_ratio * 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_satisfaction_score(self, sentiment_analysis: Dict[str, Any]) -> float:
        """Calculate driver satisfaction score based on sentiment analysis"""
        sentiment_weights = {
            SentimentType.VERY_POSITIVE: 1.0,
            SentimentType.POSITIVE: 0.8,
            SentimentType.NEUTRAL: 0.5,
            SentimentType.NEGATIVE: 0.2,
            SentimentType.VERY_NEGATIVE: 0.0,
            SentimentType.FRUSTRATED: 0.1,
            SentimentType.ANGRY: 0.0,
            SentimentType.CONFUSED: 0.3,
            SentimentType.URGENT: 0.4
        }
        
        sentiment_distribution = sentiment_analysis.get('sentiment_distribution', {})
        total_segments = sum(sentiment_distribution.values())
        
        if total_segments == 0:
            return 0.5
        
        weighted_score = sum(
            sentiment_weights.get(sentiment, 0.5) * count
            for sentiment, count in sentiment_distribution.items()
        ) / total_segments
        
        return weighted_score
    
    async def _determine_resolution_status(self, segments: List[ConversationSegment], insights: List[ConversationInsight]) -> str:
        """Determine if the conversation resulted in resolution"""
        resolution_keywords = ['resolved', 'solved', 'fixed', 'completed', 'confirmed', 'understood']
        escalation_keywords = ['escalate', 'supervisor', 'manager', 'unresolved']
        
        resolution_count = 0
        escalation_count = 0
        
        for segment in segments:
            text_lower = segment.text.lower()
            resolution_count += sum(1 for keyword in resolution_keywords if keyword in text_lower)
            escalation_count += sum(1 for keyword in escalation_keywords if keyword in text_lower)
        
        has_escalation_insight = any(insight.insight_type == 'escalation_occurred' for insight in insights)
        
        if has_escalation_insight or escalation_count > 0:
            return 'escalated'
        elif resolution_count > 0:
            return 'resolved'
        else:
            return 'information_provided'
    
    async def _extract_action_items(self, segments: List[ConversationSegment], insights: List[ConversationInsight]) -> List[str]:
        """Extract action items from conversation and insights"""
        action_items = []
        
        for insight in insights:
            if insight.actionable and insight.priority in ['high', 'critical']:
                action_items.append(f"Address {insight.insight_type}: {insight.description}")
        
        action_keywords = ['will call', 'will update', 'will send', 'will check', 'need to', 'should', 'must']
        
        for segment in segments:
            text_lower = segment.text.lower()
            for keyword in action_keywords:
                if keyword in text_lower:
                    sentences = segment.text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            action_items.append(sentence.strip())
                            break
        
        return list(set(action_items))
    
    async def _create_fallback_summary(self, call_id: str, conversation_data: List[Dict[str, Any]]) -> ConversationSummary:
        """Create a basic summary when analysis fails"""
        return ConversationSummary(
            call_id=call_id,
            total_duration=sum(item.get('duration', 3.0) for item in conversation_data),
            participant_talk_time={'agent': 0.0, 'driver': 0.0},
            dominant_sentiment=SentimentType.NEUTRAL,
            sentiment_progression=[],
            key_topics=['general_inquiry'],
            main_issues=[],
            resolution_status='unknown',
            action_items=[],
            insights=[],
            conversation_flow=[ConversationPhase.INFORMATION_GATHERING],
            effectiveness_score=0.5,
            driver_satisfaction_score=0.5,
            created_at=datetime.utcnow()
        )
    
    async def get_conversation_summary(self, call_id: str) -> Optional[ConversationSummary]:
        """Get cached conversation summary"""
        return self.analysis_cache.get(call_id)
    
    async def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for conversation analysis"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_summaries = [
            summary for summary in self.analysis_cache.values()
            if summary.created_at > cutoff_time
        ]
        
        if not recent_summaries:
            return {'total_conversations': 0, 'message': 'No recent conversation data'}
        
        total_conversations = len(recent_summaries)
        avg_effectiveness = sum(s.effectiveness_score for s in recent_summaries) / total_conversations
        avg_satisfaction = sum(s.driver_satisfaction_score for s in recent_summaries) / total_conversations
        
        sentiment_distribution = defaultdict(int)
        resolution_distribution = defaultdict(int)
        
        for summary in recent_summaries:
            sentiment_distribution[summary.dominant_sentiment.value] += 1
            resolution_distribution[summary.resolution_status] += 1
        
        return {
            'total_conversations': total_conversations,
            'average_effectiveness_score': avg_effectiveness,
            'average_satisfaction_score': avg_satisfaction,
            'sentiment_distribution': dict(sentiment_distribution),
            'resolution_distribution': dict(resolution_distribution),
            'total_insights': sum(len(s.insights) for s in recent_summaries),
            'actionable_insights': sum(len([i for i in s.insights if i.actionable]) for s in recent_summaries)
        }


_conversation_analyzer: Optional[ConversationAnalyzer] = None


def get_conversation_analyzer() -> Optional[ConversationAnalyzer]:
    """Get the global conversation analyzer instance"""
    global _conversation_analyzer
    return _conversation_analyzer


async def initialize_conversation_analyzer():
    """Initialize the global conversation analyzer"""
    global _conversation_analyzer
    
    if _conversation_analyzer is None:
        _conversation_analyzer = ConversationAnalyzer()
        logger.info("Conversation analyzer initialized")
    
    return _conversation_analyzer