"""
Voice Quality Assessment Module
Advanced audio and conversation quality analysis for PIPECAT voice calls
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AudioQualityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


class ConversationFlowPhase(Enum):
    GREETING = "greeting"
    INFORMATION_GATHERING = "information_gathering"
    PROBLEM_SOLVING = "problem_solving"
    CONCLUSION = "conclusion"
    EMERGENCY_HANDLING = "emergency_handling"


@dataclass
class AudioMetrics:
    """Comprehensive audio quality metrics"""
    signal_to_noise_ratio: float = 0.0
    volume_consistency: float = 0.0
    clarity_score: float = 0.0
    background_noise_level: float = 0.0
    echo_detection: float = 0.0
    distortion_level: float = 0.0
    frequency_balance: float = 0.0
    overall_quality: AudioQualityLevel = AudioQualityLevel.FAIR


@dataclass
class SpeechPatternMetrics:
    """Speech pattern and delivery analysis"""
    words_per_minute: float = 0.0
    pause_frequency: float = 0.0
    average_pause_duration: float = 0.0
    filler_word_count: int = 0
    interruption_rate: float = 0.0
    response_latency: float = 0.0
    speaking_time_ratio: float = 0.0
    articulation_clarity: float = 0.0


@dataclass
class ConversationFlowMetrics:
    """Conversation flow and structure analysis"""
    current_phase: ConversationFlowPhase = ConversationFlowPhase.GREETING
    phase_transitions: List[Dict[str, Any]] = field(default_factory=list)
    topic_coherence_score: float = 0.0
    natural_flow_score: float = 0.0
    goal_progression_score: float = 0.0
    efficiency_score: float = 0.0
    completion_score: float = 0.0


@dataclass
class AgentResponseMetrics:
    """Agent response effectiveness analysis"""
    relevance_score: float = 0.0
    helpfulness_score: float = 0.0
    professionalism_score: float = 0.0
    empathy_score: float = 0.0
    accuracy_score: float = 0.0
    response_appropriateness: float = 0.0
    problem_solving_effectiveness: float = 0.0


@dataclass
class OverallQualityAssessment:
    """Combined quality assessment"""
    audio_metrics: AudioMetrics = field(default_factory=AudioMetrics)
    speech_metrics: SpeechPatternMetrics = field(default_factory=SpeechPatternMetrics)
    flow_metrics: ConversationFlowMetrics = field(default_factory=ConversationFlowMetrics)
    agent_metrics: AgentResponseMetrics = field(default_factory=AgentResponseMetrics)
    
    overall_score: float = 0.0
    quality_grade: str = "C"
    improvement_suggestions: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)


class VoiceQualityAssessor:
    """
    Advanced voice quality assessment system for PIPECAT calls
    """
    
    def __init__(self, call_id: str):
        self.call_id = call_id
        self.assessment = OverallQualityAssessment()
        
        # Tracking data
        self.audio_samples: List[bytes] = []
        self.transcription_data: List[Dict[str, Any]] = []
        self.timing_data: List[Dict[str, Any]] = []
        self.response_data: List[Dict[str, Any]] = []
        
        # Real-time analysis buffers
        self.recent_audio_quality = []
        self.recent_speech_patterns = []
        self.conversation_timeline = []
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.75,
            'fair': 0.6,
            'poor': 0.4
        }
        
        logger.info(f"Voice Quality Assessor initialized for call: {call_id}")
    
    async def process_audio_sample(self, audio_data: bytes, timestamp: datetime) -> None:
        """Process audio sample for quality analysis"""
        try:
            self.audio_samples.append(audio_data)
            
            # Analyze audio quality metrics
            audio_quality = self._analyze_audio_quality(audio_data)
            self.recent_audio_quality.append(audio_quality)
            
            # Keep only recent samples for real-time analysis
            if len(self.recent_audio_quality) > 50:
                self.recent_audio_quality.pop(0)
            
            # Update audio metrics
            await self._update_audio_metrics()
            
        except Exception as e:
            logger.error(f"Error processing audio sample: {e}")
    
    async def process_transcription(self, text: str, speaker: str, timestamp: datetime) -> None:
        """Process transcription for speech pattern analysis"""
        try:
            transcription_entry = {
                'text': text,
                'speaker': speaker,
                'timestamp': timestamp,
                'word_count': len(text.split()),
                'duration': 0  # Would be calculated from audio timing
            }
            
            self.transcription_data.append(transcription_entry)
            
            # Analyze speech patterns
            speech_patterns = self._analyze_speech_patterns(text, speaker)
            self.recent_speech_patterns.append(speech_patterns)
            
            # Update speech metrics
            await self._update_speech_metrics()
            
            # Analyze conversation flow
            await self._analyze_conversation_flow(text, speaker, timestamp)
            
        except Exception as e:
            logger.error(f"Error processing transcription: {e}")
    
    async def process_agent_response(self, response_text: str, context: Dict[str, Any], timestamp: datetime) -> None:
        """Process agent response for effectiveness analysis"""
        try:
            response_entry = {
                'text': response_text,
                'context': context,
                'timestamp': timestamp,
                'relevance': self._assess_response_relevance(response_text, context),
                'helpfulness': self._assess_response_helpfulness(response_text),
                'professionalism': self._assess_professionalism(response_text)
            }
            
            self.response_data.append(response_entry)
            
            # Update agent metrics
            await self._update_agent_metrics()
            
        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
    
    def _analyze_audio_quality(self, audio_data: bytes) -> Dict[str, float]:
        """Analyze audio quality from raw audio data"""
        # Simplified audio analysis - would use advanced DSP in production
        
        # Simulate audio quality metrics
        data_length = len(audio_data)
        
        # Basic quality indicators based on data characteristics
        signal_quality = min(data_length / 4000, 1.0)  # Assume 4KB is good quality
        noise_level = 0.1 if data_length > 2000 else 0.3  # Higher noise for shorter samples
        clarity = signal_quality * (1 - noise_level)
        
        return {
            'signal_to_noise_ratio': signal_quality * 20,  # dB scale
            'volume_consistency': 0.8,  # Assume good consistency
            'clarity_score': clarity,
            'background_noise_level': noise_level,
            'echo_detection': 0.1,  # Low echo
            'distortion_level': 0.05,  # Low distortion
            'frequency_balance': 0.75  # Decent balance
        }
    
    def _analyze_speech_patterns(self, text: str, speaker: str) -> Dict[str, Any]:
        """Analyze speech patterns from transcription"""
        words = text.split()
        word_count = len(words)
        
        # Filler words detection
        filler_words = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well']
        filler_count = sum(1 for word in words if word.lower() in filler_words)
        
        # Estimate speaking rate (simplified)
        estimated_duration = word_count * 0.4  # Assume 0.4 seconds per word average
        words_per_minute = (word_count / estimated_duration) * 60 if estimated_duration > 0 else 0
        
        return {
            'speaker': speaker,
            'word_count': word_count,
            'filler_count': filler_count,
            'words_per_minute': words_per_minute,
            'text_length': len(text),
            'sentence_count': text.count('.') + text.count('!') + text.count('?')
        }
    
    async def _analyze_conversation_flow(self, text: str, speaker: str, timestamp: datetime) -> None:
        """Analyze conversation flow and phase transitions"""
        text_lower = text.lower()
        
        # Detect conversation phases
        new_phase = self._detect_conversation_phase(text_lower)
        
        if new_phase != self.assessment.flow_metrics.current_phase:
            transition = {
                'from_phase': self.assessment.flow_metrics.current_phase.value,
                'to_phase': new_phase.value,
                'timestamp': timestamp,
                'trigger_text': text[:100]  # First 100 chars
            }
            
            self.assessment.flow_metrics.phase_transitions.append(transition)
            self.assessment.flow_metrics.current_phase = new_phase
        
        # Add to conversation timeline
        self.conversation_timeline.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'text': text,
            'phase': new_phase.value
        })
    
    def _detect_conversation_phase(self, text: str) -> ConversationFlowPhase:
        """Detect current conversation phase based on text content"""
        # Emergency detection
        emergency_keywords = ['emergency', 'accident', 'help', 'urgent', 'breakdown', 'medical']
        if any(keyword in text for keyword in emergency_keywords):
            return ConversationFlowPhase.EMERGENCY_HANDLING
        
        # Greeting phase
        greeting_keywords = ['hello', 'hi', 'good morning', 'calling', 'this is']
        if any(keyword in text for keyword in greeting_keywords):
            return ConversationFlowPhase.GREETING
        
        # Information gathering
        info_keywords = ['where', 'when', 'what', 'how', 'status', 'location', 'eta']
        if any(keyword in text for keyword in info_keywords):
            return ConversationFlowPhase.INFORMATION_GATHERING
        
        # Problem solving
        problem_keywords = ['problem', 'issue', 'solution', 'help', 'fix', 'delayed']
        if any(keyword in text for keyword in problem_keywords):
            return ConversationFlowPhase.PROBLEM_SOLVING
        
        # Conclusion
        conclusion_keywords = ['thank', 'bye', 'goodbye', 'complete', 'done', 'finished']
        if any(keyword in text for keyword in conclusion_keywords):
            return ConversationFlowPhase.CONCLUSION
        
        return self.assessment.flow_metrics.current_phase  # Keep current phase
    
    def _assess_response_relevance(self, response: str, context: Dict[str, Any]) -> float:
        """Assess how relevant the agent response is to the context"""
        # Simplified relevance assessment
        response_lower = response.lower()
        
        # Check if response addresses common logistics topics
        logistics_terms = ['location', 'delivery', 'pickup', 'eta', 'status', 'highway', 'mile']
        relevance_score = sum(1 for term in logistics_terms if term in response_lower) / len(logistics_terms)
        
        return min(relevance_score + 0.5, 1.0)  # Baseline + relevance bonus
    
    def _assess_response_helpfulness(self, response: str) -> float:
        """Assess how helpful the agent response is"""
        response_lower = response.lower()
        
        helpful_indicators = [
            'understand', 'help', 'assist', 'thank you', 'please', 'let me',
            'can you', 'would you', 'i will', 'we can'
        ]
        
        helpfulness_score = sum(1 for indicator in helpful_indicators if indicator in response_lower)
        return min(helpfulness_score / 5, 1.0)
    
    def _assess_professionalism(self, response: str) -> float:
        """Assess professionalism of the response"""
        response_lower = response.lower()
        
        professional_indicators = ['please', 'thank you', 'certainly', 'understand', 'appreciate']
        unprofessional_indicators = ['yeah', 'ok', 'sure', 'whatever']
        
        positive_score = sum(1 for indicator in professional_indicators if indicator in response_lower)
        negative_score = sum(1 for indicator in unprofessional_indicators if indicator in response_lower)
        
        professionalism = (positive_score - negative_score * 0.5) / 3
        return max(min(professionalism + 0.6, 1.0), 0.0)  # Baseline + adjustment
    
    async def _update_audio_metrics(self) -> None:
        """Update audio quality metrics based on recent samples"""
        if not self.recent_audio_quality:
            return
        
        # Average recent audio quality metrics
        avg_metrics = {}
        for key in ['signal_to_noise_ratio', 'volume_consistency', 'clarity_score', 
                   'background_noise_level', 'echo_detection', 'distortion_level', 'frequency_balance']:
            values = [sample.get(key, 0) for sample in self.recent_audio_quality]
            avg_metrics[key] = sum(values) / len(values) if values else 0
        
        # Update audio metrics
        self.assessment.audio_metrics.signal_to_noise_ratio = avg_metrics['signal_to_noise_ratio']
        self.assessment.audio_metrics.volume_consistency = avg_metrics['volume_consistency']
        self.assessment.audio_metrics.clarity_score = avg_metrics['clarity_score']
        self.assessment.audio_metrics.background_noise_level = avg_metrics['background_noise_level']
        self.assessment.audio_metrics.echo_detection = avg_metrics['echo_detection']
        self.assessment.audio_metrics.distortion_level = avg_metrics['distortion_level']
        self.assessment.audio_metrics.frequency_balance = avg_metrics['frequency_balance']
        
        # Determine overall audio quality level
        overall_audio_score = (
            avg_metrics['clarity_score'] * 0.3 +
            (1 - avg_metrics['background_noise_level']) * 0.25 +
            avg_metrics['volume_consistency'] * 0.2 +
            (1 - avg_metrics['echo_detection']) * 0.15 +
            (1 - avg_metrics['distortion_level']) * 0.1
        )
        
        if overall_audio_score >= self.quality_thresholds['excellent']:
            self.assessment.audio_metrics.overall_quality = AudioQualityLevel.EXCELLENT
        elif overall_audio_score >= self.quality_thresholds['good']:
            self.assessment.audio_metrics.overall_quality = AudioQualityLevel.GOOD
        elif overall_audio_score >= self.quality_thresholds['fair']:
            self.assessment.audio_metrics.overall_quality = AudioQualityLevel.FAIR
        elif overall_audio_score >= self.quality_thresholds['poor']:
            self.assessment.audio_metrics.overall_quality = AudioQualityLevel.POOR
        else:
            self.assessment.audio_metrics.overall_quality = AudioQualityLevel.VERY_POOR
    
    async def _update_speech_metrics(self) -> None:
        """Update speech pattern metrics"""
        if not self.recent_speech_patterns:
            return
        
        # Calculate average speech metrics
        total_words = sum(pattern['word_count'] for pattern in self.recent_speech_patterns)
        total_fillers = sum(pattern['filler_count'] for pattern in self.recent_speech_patterns)
        
        if self.recent_speech_patterns:
            avg_wpm = sum(pattern['words_per_minute'] for pattern in self.recent_speech_patterns) / len(self.recent_speech_patterns)
            filler_rate = total_fillers / total_words if total_words > 0 else 0
            
            self.assessment.speech_metrics.words_per_minute = avg_wpm
            self.assessment.speech_metrics.filler_word_count = total_fillers
            self.assessment.speech_metrics.articulation_clarity = max(1 - filler_rate * 2, 0)
    
    async def _update_agent_metrics(self) -> None:
        """Update agent response effectiveness metrics"""
        if not self.response_data:
            return
        
        # Calculate averages
        relevance_scores = [resp['relevance'] for resp in self.response_data]
        helpfulness_scores = [resp['helpfulness'] for resp in self.response_data]
        professionalism_scores = [resp['professionalism'] for resp in self.response_data]
        
        self.assessment.agent_metrics.relevance_score = sum(relevance_scores) / len(relevance_scores)
        self.assessment.agent_metrics.helpfulness_score = sum(helpfulness_scores) / len(helpfulness_scores)
        self.assessment.agent_metrics.professionalism_score = sum(professionalism_scores) / len(professionalism_scores)
        
        # Calculate overall response appropriateness
        self.assessment.agent_metrics.response_appropriateness = (
            self.assessment.agent_metrics.relevance_score * 0.4 +
            self.assessment.agent_metrics.helpfulness_score * 0.3 +
            self.assessment.agent_metrics.professionalism_score * 0.3
        )
    
    async def generate_final_assessment(self) -> OverallQualityAssessment:
        """Generate comprehensive final quality assessment"""
        try:
            # Update all metrics
            await self._update_audio_metrics()
            await self._update_speech_metrics()
            await self._update_agent_metrics()
            
            # Calculate conversation flow metrics
            await self._calculate_flow_metrics()
            
            # Calculate overall score
            audio_score = self._calculate_audio_score()
            speech_score = self._calculate_speech_score()
            flow_score = self._calculate_flow_score()
            agent_score = self._calculate_agent_score()
            
            # Weighted overall score
            self.assessment.overall_score = (
                audio_score * 0.25 +
                speech_score * 0.20 +
                flow_score * 0.25 +
                agent_score * 0.30
            )
            
            # Assign quality grade
            self.assessment.quality_grade = self._assign_quality_grade(self.assessment.overall_score)
            
            # Generate improvement suggestions
            self.assessment.improvement_suggestions = self._generate_improvement_suggestions()
            
            # Identify critical issues
            self.assessment.critical_issues = self._identify_critical_issues()
            
            logger.info(f"Final quality assessment completed for call {self.call_id}: "
                       f"Score: {self.assessment.overall_score:.2f}, Grade: {self.assessment.quality_grade}")
            
            return self.assessment
            
        except Exception as e:
            logger.error(f"Error generating final assessment: {e}")
            return self.assessment
    
    async def _calculate_flow_metrics(self) -> None:
        """Calculate conversation flow quality metrics"""
        # Topic coherence (simplified)
        self.assessment.flow_metrics.topic_coherence_score = 0.8  # Would analyze topic consistency
        
        # Natural flow (based on phase transitions)
        expected_transitions = len(ConversationFlowPhase) - 1
        actual_transitions = len(self.assessment.flow_metrics.phase_transitions)
        self.assessment.flow_metrics.natural_flow_score = min(actual_transitions / expected_transitions, 1.0)
        
        # Goal progression
        has_info_gathering = any(t['to_phase'] == 'information_gathering' for t in self.assessment.flow_metrics.phase_transitions)
        has_conclusion = any(t['to_phase'] == 'conclusion' for t in self.assessment.flow_metrics.phase_transitions)
        self.assessment.flow_metrics.goal_progression_score = (has_info_gathering + has_conclusion) / 2
        
        # Efficiency (fewer unnecessary phase changes is better)
        efficiency = max(1 - (len(self.assessment.flow_metrics.phase_transitions) - 3) * 0.1, 0.3)
        self.assessment.flow_metrics.efficiency_score = efficiency
        
        # Completion
        self.assessment.flow_metrics.completion_score = 1.0 if has_conclusion else 0.6
    
    def _calculate_audio_score(self) -> float:
        """Calculate overall audio quality score"""
        audio = self.assessment.audio_metrics
        return (
            audio.clarity_score * 0.3 +
            (1 - audio.background_noise_level) * 0.25 +
            audio.volume_consistency * 0.2 +
            (1 - audio.echo_detection) * 0.15 +
            (1 - audio.distortion_level) * 0.1
        )
    
    def _calculate_speech_score(self) -> float:
        """Calculate speech pattern quality score"""
        speech = self.assessment.speech_metrics
        
        # Ideal WPM range is 140-180
        wpm_score = 1.0 if 140 <= speech.words_per_minute <= 180 else max(1 - abs(speech.words_per_minute - 160) / 100, 0.3)
        
        return (
            speech.articulation_clarity * 0.4 +
            wpm_score * 0.3 +
            (1 - min(speech.filler_word_count / 20, 1)) * 0.3
        )
    
    def _calculate_flow_score(self) -> float:
        """Calculate conversation flow quality score"""
        flow = self.assessment.flow_metrics
        return (
            flow.topic_coherence_score * 0.25 +
            flow.natural_flow_score * 0.25 +
            flow.goal_progression_score * 0.25 +
            flow.efficiency_score * 0.125 +
            flow.completion_score * 0.125
        )
    
    def _calculate_agent_score(self) -> float:
        """Calculate agent response quality score"""
        agent = self.assessment.agent_metrics
        return (
            agent.relevance_score * 0.3 +
            agent.helpfulness_score * 0.25 +
            agent.professionalism_score * 0.25 +
            agent.response_appropriateness * 0.2
        )
    
    def _assign_quality_grade(self, score: float) -> str:
        """Assign letter grade based on overall score"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.9:
            return "A"
        elif score >= 0.85:
            return "A-"
        elif score >= 0.8:
            return "B+"
        elif score >= 0.75:
            return "B"
        elif score >= 0.7:
            return "B-"
        elif score >= 0.65:
            return "C+"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "C-"
        elif score >= 0.4:
            return "D"
        else:
            return "F"
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Audio quality suggestions
        if self.assessment.audio_metrics.background_noise_level > 0.3:
            suggestions.append("Reduce background noise for clearer audio quality")
        
        if self.assessment.audio_metrics.volume_consistency < 0.7:
            suggestions.append("Maintain more consistent volume levels throughout the call")
        
        # Speech pattern suggestions
        if self.assessment.speech_metrics.words_per_minute > 200:
            suggestions.append("Slow down speaking rate for better comprehension")
        elif self.assessment.speech_metrics.words_per_minute < 120:
            suggestions.append("Increase speaking rate to maintain engagement")
        
        if self.assessment.speech_metrics.articulation_clarity < 0.7:
            suggestions.append("Reduce filler words and improve speech clarity")
        
        # Agent response suggestions
        if self.assessment.agent_metrics.relevance_score < 0.7:
            suggestions.append("Provide more relevant responses to driver questions")
        
        if self.assessment.agent_metrics.professionalism_score < 0.8:
            suggestions.append("Maintain more professional language and tone")
        
        # Flow suggestions
        if self.assessment.flow_metrics.efficiency_score < 0.6:
            suggestions.append("Streamline conversation flow to reduce unnecessary transitions")
        
        return suggestions
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify critical quality issues that need immediate attention"""
        issues = []
        
        # Critical audio issues
        if self.assessment.audio_metrics.overall_quality == AudioQualityLevel.VERY_POOR:
            issues.append("CRITICAL: Very poor audio quality affecting call comprehension")
        
        # Critical flow issues
        if self.assessment.flow_metrics.completion_score < 0.3:
            issues.append("CRITICAL: Call did not reach proper conclusion")
        
        # Critical agent issues
        if self.assessment.agent_metrics.response_appropriateness < 0.4:
            issues.append("CRITICAL: Agent responses are largely inappropriate or irrelevant")
        
        # Overall quality issues
        if self.assessment.overall_score < 0.4:
            issues.append("CRITICAL: Overall call quality is unacceptable and requires immediate attention")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary for storage/serialization"""
        return {
            'call_id': self.call_id,
            'overall_score': self.assessment.overall_score,
            'quality_grade': self.assessment.quality_grade,
            'audio_metrics': {
                'signal_to_noise_ratio': self.assessment.audio_metrics.signal_to_noise_ratio,
                'volume_consistency': self.assessment.audio_metrics.volume_consistency,
                'clarity_score': self.assessment.audio_metrics.clarity_score,
                'background_noise_level': self.assessment.audio_metrics.background_noise_level,
                'overall_quality': self.assessment.audio_metrics.overall_quality.value
            },
            'speech_metrics': {
                'words_per_minute': self.assessment.speech_metrics.words_per_minute,
                'filler_word_count': self.assessment.speech_metrics.filler_word_count,
                'articulation_clarity': self.assessment.speech_metrics.articulation_clarity
            },
            'flow_metrics': {
                'current_phase': self.assessment.flow_metrics.current_phase.value,
                'phase_transitions_count': len(self.assessment.flow_metrics.phase_transitions),
                'topic_coherence_score': self.assessment.flow_metrics.topic_coherence_score,
                'natural_flow_score': self.assessment.flow_metrics.natural_flow_score,
                'efficiency_score': self.assessment.flow_metrics.efficiency_score,
                'completion_score': self.assessment.flow_metrics.completion_score
            },
            'agent_metrics': {
                'relevance_score': self.assessment.agent_metrics.relevance_score,
                'helpfulness_score': self.assessment.agent_metrics.helpfulness_score,
                'professionalism_score': self.assessment.agent_metrics.professionalism_score,
                'response_appropriateness': self.assessment.agent_metrics.response_appropriateness
            },
            'improvement_suggestions': self.assessment.improvement_suggestions,
            'critical_issues': self.assessment.critical_issues,
            'timestamp': datetime.utcnow().isoformat()
        }