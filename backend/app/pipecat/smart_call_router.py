import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
from collections import defaultdict, deque


logger = logging.getLogger(__name__)


class CallPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class CallOutcome(Enum):
    IN_TRANSIT_UPDATE = "in_transit_update"
    ARRIVAL_CONFIRMATION = "arrival_confirmation"
    EMERGENCY_ESCALATION = "emergency_escalation"
    DELIVERY_ISSUE = "delivery_issue"
    SCHEDULE_CHANGE = "schedule_change"
    DRIVER_ASSISTANCE = "driver_assistance"
    ROUTE_OPTIMIZATION = "route_optimization"


class DriverState(Enum):
    AVAILABLE = "available"
    ON_ROUTE = "on_route"
    AT_PICKUP = "at_pickup"
    AT_DELIVERY = "at_delivery"
    BREAK = "break"
    OFFLINE = "offline"
    EMERGENCY = "emergency"


@dataclass
class CallContext:
    call_id: str
    driver_name: str
    phone_number: str
    load_number: str
    priority: CallPriority
    predicted_outcome: Optional[CallOutcome]
    driver_state: DriverState
    location: Optional[Dict[str, float]]
    route_info: Dict[str, Any]
    historical_patterns: Dict[str, Any]
    sentiment_indicators: List[str]
    urgency_keywords: List[str]
    estimated_duration: Optional[int]
    created_at: datetime


@dataclass
class AgentCapability:
    agent_id: str
    specializations: List[str]
    current_load: int
    max_concurrent_calls: int
    average_call_duration: float
    success_rate: float
    language_skills: List[str]
    availability_schedule: Dict[str, Any]
    performance_score: float


@dataclass
class RoutingDecision:
    recommended_agent: str
    confidence_score: float
    routing_strategy: str
    estimated_wait_time: int
    alternative_agents: List[str]
    reasoning: List[str]
    predicted_outcome: CallOutcome
    predicted_duration: int


class SmartCallRouter:
    """
    Intelligent call routing system that uses ML-driven insights to optimize call assignments
    """
    
    def __init__(self):
        self.available_agents: Dict[str, AgentCapability] = {}
        self.call_queue: deque = deque()
        self.active_calls: Dict[str, CallContext] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.emergency_escalation_threshold = 3
        self.load_balancing_weights = {
            'current_load': 0.3,
            'success_rate': 0.25,
            'specialization_match': 0.2,
            'average_duration': 0.15,
            'performance_score': 0.1
        }
    
    async def initialize(self):
        """Initialize the routing system with default agents"""
        default_agents = [
            {
                'agent_id': 'general_agent_1',
                'specializations': ['general_inquiry', 'status_update', 'delivery_confirmation'],
                'max_concurrent_calls': 3,
                'success_rate': 0.85,
                'language_skills': ['en'],
                'performance_score': 0.82
            },
            {
                'agent_id': 'emergency_agent_1',
                'specializations': ['emergency_escalation', 'driver_assistance', 'urgent_issues'],
                'max_concurrent_calls': 2,
                'success_rate': 0.92,
                'language_skills': ['en', 'es'],
                'performance_score': 0.91
            },
            {
                'agent_id': 'logistics_agent_1',
                'specializations': ['route_optimization', 'schedule_change', 'delivery_issue'],
                'max_concurrent_calls': 4,
                'success_rate': 0.88,
                'language_skills': ['en'],
                'performance_score': 0.86
            }
        ]
        
        for agent_config in default_agents:
            agent = AgentCapability(
                agent_id=agent_config['agent_id'],
                specializations=agent_config['specializations'],
                current_load=0,
                max_concurrent_calls=agent_config['max_concurrent_calls'],
                average_call_duration=180.0, 
                success_rate=agent_config['success_rate'],
                language_skills=agent_config['language_skills'],
                availability_schedule={},
                performance_score=agent_config['performance_score']
            )
            self.available_agents[agent.agent_id] = agent
        
        logger.info(f"Smart call router initialized with {len(self.available_agents)} agents")
    
    async def route_call(self, call_context: CallContext) -> RoutingDecision:
        """
        Route a call to the most appropriate agent using intelligent decision making
        """
        try:
            predicted_outcome = await self._predict_call_outcome(call_context)
            call_context.predicted_outcome = predicted_outcome
            
            if call_context.priority == CallPriority.EMERGENCY:
                return await self._route_emergency_call(call_context)
            
            available_agents = self._get_available_agents()
            if not available_agents:
                return await self._handle_no_agents_available(call_context)
            
            agent_scores = await self._score_agents_for_call(call_context, available_agents)
            
            best_agent_id, confidence = self._select_best_agent(agent_scores)
            
            decision = RoutingDecision(
                recommended_agent=best_agent_id,
                confidence_score=confidence,
                routing_strategy=self._determine_routing_strategy(call_context),
                estimated_wait_time=await self._estimate_wait_time(best_agent_id),
                alternative_agents=self._get_alternative_agents(agent_scores, best_agent_id),
                reasoning=self._generate_routing_reasoning(call_context, agent_scores, best_agent_id),
                predicted_outcome=predicted_outcome,
                predicted_duration=await self._predict_call_duration(call_context)
            )
            
            if best_agent_id in self.available_agents:
                self.available_agents[best_agent_id].current_load += 1
            
            await self._record_routing_decision(call_context, decision)
            
            logger.info(f"Routed call {call_context.call_id} to {best_agent_id} with confidence {confidence:.2f}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error routing call {call_context.call_id}: {e}")
            return await self._fallback_routing(call_context)
    
    async def _predict_call_outcome(self, call_context: CallContext) -> CallOutcome:
        """Predict the likely outcome of a call based on context"""
        try:
            emergency_keywords = ['emergency', 'accident', 'urgent', 'help', 'stuck', 'breakdown']
            delivery_keywords = ['delivered', 'arrived', 'complete', 'finished']
            route_keywords = ['route', 'directions', 'lost', 'location', 'gps']
            schedule_keywords = ['delay', 'schedule', 'time', 'late', 'early']
            
            urgency_score = sum(1 for keyword in emergency_keywords if keyword in call_context.urgency_keywords)
            
            if urgency_score >= 2:
                return CallOutcome.EMERGENCY_ESCALATION
            
            # Check driver state
            if call_context.driver_state == DriverState.EMERGENCY:
                return CallOutcome.EMERGENCY_ESCALATION
            elif call_context.driver_state == DriverState.AT_DELIVERY:
                return CallOutcome.ARRIVAL_CONFIRMATION
            elif call_context.driver_state == DriverState.ON_ROUTE:
                return CallOutcome.IN_TRANSIT_UPDATE
            
            if call_context.historical_patterns.get('frequent_route_issues', False):
                return CallOutcome.ROUTE_OPTIMIZATION
            
            if any(keyword in call_context.urgency_keywords for keyword in delivery_keywords):
                return CallOutcome.ARRIVAL_CONFIRMATION
            elif any(keyword in call_context.urgency_keywords for keyword in route_keywords):
                return CallOutcome.ROUTE_OPTIMIZATION
            elif any(keyword in call_context.urgency_keywords for keyword in schedule_keywords):
                return CallOutcome.SCHEDULE_CHANGE
            
            return CallOutcome.IN_TRANSIT_UPDATE
            
        except Exception as e:
            logger.error(f"Error predicting call outcome: {e}")
            return CallOutcome.IN_TRANSIT_UPDATE
    
    async def _route_emergency_call(self, call_context: CallContext) -> RoutingDecision:
        """Handle emergency call routing with highest priority"""
        emergency_agents = [
            agent for agent in self.available_agents.values()
            if 'emergency_escalation' in agent.specializations and agent.current_load < agent.max_concurrent_calls
        ]
        
        if emergency_agents:
            best_agent = max(emergency_agents, key=lambda a: a.performance_score)
            return RoutingDecision(
                recommended_agent=best_agent.agent_id,
                confidence_score=0.95,
                routing_strategy="emergency_priority",
                estimated_wait_time=0,
                alternative_agents=[a.agent_id for a in emergency_agents[:3] if a.agent_id != best_agent.agent_id],
                reasoning=[
                    "Emergency call detected",
                    f"Routed to emergency specialist {best_agent.agent_id}",
                    f"Agent performance score: {best_agent.performance_score:.2f}"
                ],
                predicted_outcome=CallOutcome.EMERGENCY_ESCALATION,
                predicted_duration=300  
            )
        else:
            available = self._get_available_agents()
            if available:
                best_agent = max(available, key=lambda a: a.performance_score)
                return RoutingDecision(
                    recommended_agent=best_agent.agent_id,
                    confidence_score=0.7,
                    routing_strategy="emergency_fallback",
                    estimated_wait_time=0,
                    alternative_agents=[],
                    reasoning=[
                        "Emergency call - no emergency specialists available",
                        f"Fallback to best available agent {best_agent.agent_id}",
                        "Manual escalation may be required"
                    ],
                    predicted_outcome=CallOutcome.EMERGENCY_ESCALATION,
                    predicted_duration=300
                )
            else:
                return await self._handle_emergency_no_agents(call_context)
    
    def _get_available_agents(self) -> List[AgentCapability]:
        """Get list of currently available agents"""
        return [
            agent for agent in self.available_agents.values()
            if agent.current_load < agent.max_concurrent_calls
        ]
    
    async def _score_agents_for_call(self, call_context: CallContext, available_agents: List[AgentCapability]) -> Dict[str, float]:
        """Score each available agent for the specific call"""
        scores = {}
        
        for agent in available_agents:
            score = 0.0
            
            load_score = 1.0 - (agent.current_load / agent.max_concurrent_calls)
            score += load_score * self.load_balancing_weights['current_load']
            
            score += agent.success_rate * self.load_balancing_weights['success_rate']
            
            specialization_score = await self._calculate_specialization_match(call_context, agent)
            score += specialization_score * self.load_balancing_weights['specialization_match']
            
            duration_score = max(0, 1.0 - (agent.average_call_duration / 600))  # Normalize against 10 minutes
            score += duration_score * self.load_balancing_weights['average_duration']
            
            score += agent.performance_score * self.load_balancing_weights['performance_score']
            
            scores[agent.agent_id] = score
        
        return scores
    
    async def _calculate_specialization_match(self, call_context: CallContext, agent: AgentCapability) -> float:
        """Calculate how well an agent's specializations match the call context"""
        if not call_context.predicted_outcome:
            return 0.5 
        
        outcome_specializations = {
            CallOutcome.EMERGENCY_ESCALATION: ['emergency_escalation', 'driver_assistance'],
            CallOutcome.ARRIVAL_CONFIRMATION: ['delivery_confirmation', 'status_update'],
            CallOutcome.IN_TRANSIT_UPDATE: ['status_update', 'general_inquiry'],
            CallOutcome.DELIVERY_ISSUE: ['delivery_issue', 'driver_assistance'],
            CallOutcome.SCHEDULE_CHANGE: ['schedule_change', 'logistics_coordination'],
            CallOutcome.DRIVER_ASSISTANCE: ['driver_assistance', 'emergency_escalation'],
            CallOutcome.ROUTE_OPTIMIZATION: ['route_optimization', 'logistics_coordination']
        }
        
        required_specs = outcome_specializations.get(call_context.predicted_outcome, ['general_inquiry'])
        
        match_count = sum(1 for spec in required_specs if spec in agent.specializations)
        return match_count / len(required_specs) if required_specs else 0.0
    
    def _select_best_agent(self, agent_scores: Dict[str, float]) -> Tuple[str, float]:
        """Select the agent with the highest score"""
        if not agent_scores:
            raise ValueError("No agents available for scoring")
        
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        return best_agent[0], best_agent[1]
    
    def _determine_routing_strategy(self, call_context: CallContext) -> str:
        """Determine the routing strategy used"""
        if call_context.priority == CallPriority.EMERGENCY:
            return "emergency_priority"
        elif call_context.priority in [CallPriority.HIGH, CallPriority.URGENT]:
            return "priority_based"
        else:
            return "skill_based_load_balanced"
    
    async def _estimate_wait_time(self, agent_id: str) -> int:
        """Estimate wait time for an agent in seconds"""
        if agent_id not in self.available_agents:
            return 300  # 5 minutes default
        
        agent = self.available_agents[agent_id]
        if agent.current_load == 0:
            return 0 
        
        estimated_wait = (agent.current_load * agent.average_call_duration) / agent.max_concurrent_calls
        return int(min(estimated_wait, 600))  
    
    def _get_alternative_agents(self, agent_scores: Dict[str, float], selected_agent: str) -> List[str]:
        """Get list of alternative agents sorted by score"""
        alternatives = [
            agent_id for agent_id, score in sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
            if agent_id != selected_agent
        ]
        return alternatives[:3]  # Return top 3 alternatives
    
    def _generate_routing_reasoning(self, call_context: CallContext, agent_scores: Dict[str, float], selected_agent: str) -> List[str]:
        """Generate human-readable reasoning for the routing decision"""
        reasoning = []
        
        reasoning.append(f"Call priority: {call_context.priority.value}")
        reasoning.append(f"Predicted outcome: {call_context.predicted_outcome.value if call_context.predicted_outcome else 'unknown'}")
        reasoning.append(f"Driver state: {call_context.driver_state.value}")
        
        if selected_agent in self.available_agents:
            agent = self.available_agents[selected_agent]
            reasoning.append(f"Selected agent specializations: {', '.join(agent.specializations)}")
            reasoning.append(f"Agent performance score: {agent.performance_score:.2f}")
            reasoning.append(f"Current load: {agent.current_load}/{agent.max_concurrent_calls}")
        
        reasoning.append(f"Overall routing score: {agent_scores.get(selected_agent, 0):.2f}")
        
        return reasoning
    
    async def _predict_call_duration(self, call_context: CallContext) -> int:
        """Predict call duration in seconds based on context"""
        base_duration = 180  
        
        outcome_adjustments = {
            CallOutcome.EMERGENCY_ESCALATION: 300,  
            CallOutcome.ARRIVAL_CONFIRMATION: 120, 
            CallOutcome.IN_TRANSIT_UPDATE: 180,    
            CallOutcome.DELIVERY_ISSUE: 360,        
            CallOutcome.SCHEDULE_CHANGE: 240,      
            CallOutcome.DRIVER_ASSISTANCE: 300,    
            CallOutcome.ROUTE_OPTIMIZATION: 420   
        }
        
        if call_context.predicted_outcome:
            base_duration = outcome_adjustments.get(call_context.predicted_outcome, base_duration)
        
        if call_context.priority in [CallPriority.HIGH, CallPriority.URGENT]:
            base_duration = int(base_duration * 1.2)
        elif call_context.priority == CallPriority.EMERGENCY:
            base_duration = int(base_duration * 1.5)
        
        return base_duration
    
    async def _record_routing_decision(self, call_context: CallContext, decision: RoutingDecision):
        """Record the routing decision for analytics and learning"""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'call_id': call_context.call_id,
            'driver_name': call_context.driver_name,
            'priority': call_context.priority.value,
            'predicted_outcome': decision.predicted_outcome.value,
            'selected_agent': decision.recommended_agent,
            'confidence_score': decision.confidence_score,
            'routing_strategy': decision.routing_strategy,
            'estimated_wait_time': decision.estimated_wait_time,
            'predicted_duration': decision.predicted_duration,
            'reasoning': decision.reasoning
        }
        
        self.routing_history.append(record)
        
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
    
    async def _handle_no_agents_available(self, call_context: CallContext) -> RoutingDecision:
        """Handle case when no agents are available"""
        return RoutingDecision(
            recommended_agent="queue",
            confidence_score=0.0,
            routing_strategy="queue_until_available",
            estimated_wait_time=300,  # 5 minutes default
            alternative_agents=[],
            reasoning=[
                "No agents currently available",
                "Call queued for next available agent",
                "Estimated wait time: 5 minutes"
            ],
            predicted_outcome=call_context.predicted_outcome or CallOutcome.IN_TRANSIT_UPDATE,
            predicted_duration=await self._predict_call_duration(call_context)
        )
    
    async def _handle_emergency_no_agents(self, call_context: CallContext) -> RoutingDecision:
        """Handle emergency case when no agents are available"""
        return RoutingDecision(
            recommended_agent="emergency_queue",
            confidence_score=0.0,
            routing_strategy="emergency_escalation",
            estimated_wait_time=0,  # Immediate escalation
            alternative_agents=[],
            reasoning=[
                "EMERGENCY: No agents available",
                "Immediate manual escalation required",
                "Alerting supervisors"
            ],
            predicted_outcome=CallOutcome.EMERGENCY_ESCALATION,
            predicted_duration=300
        )
    
    async def _fallback_routing(self, call_context: CallContext) -> RoutingDecision:
        """Fallback routing when main routing fails"""
        available = self._get_available_agents()
        if available:
            selected_agent = available[0]
            return RoutingDecision(
                recommended_agent=selected_agent.agent_id,
                confidence_score=0.5,
                routing_strategy="fallback_round_robin",
                estimated_wait_time=await self._estimate_wait_time(selected_agent.agent_id),
                alternative_agents=[],
                reasoning=[
                    "Fallback routing due to system error",
                    f"Selected first available agent: {selected_agent.agent_id}"
                ],
                predicted_outcome=CallOutcome.IN_TRANSIT_UPDATE,
                predicted_duration=180
            )
        else:
            return await self._handle_no_agents_available(call_context)
    
    async def update_agent_performance(self, agent_id: str, call_outcome: str, call_duration: int, success: bool):
        """Update agent performance metrics after call completion"""
        if agent_id not in self.available_agents:
            return
        
        agent = self.available_agents[agent_id]
        
        agent.current_load = max(0, agent.current_load - 1)
        
        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = {
                'total_calls': 0,
                'successful_calls': 0,
                'total_duration': 0,
                'average_duration': 0,
                'success_rate': 0
            }
        
        metrics = self.performance_metrics[agent_id]
        metrics['total_calls'] += 1
        metrics['total_duration'] += call_duration
        metrics['average_duration'] = metrics['total_duration'] / metrics['total_calls']
        
        if success:
            metrics['successful_calls'] += 1
        
        metrics['success_rate'] = metrics['successful_calls'] / metrics['total_calls']
        
        # Update agent object
        agent.average_call_duration = metrics['average_duration']
        agent.success_rate = metrics['success_rate']
        
        logger.info(f"Updated performance for agent {agent_id}: success_rate={agent.success_rate:.2f}, avg_duration={agent.average_call_duration:.1f}s")
    
    async def get_routing_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get routing analytics for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_routes = [
            route for route in self.routing_history
            if datetime.fromisoformat(route['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_routes:
            return {'total_routes': 0, 'message': 'No recent routing data'}
        
        # Calculate analytics
        total_routes = len(recent_routes)
        avg_confidence = sum(route['confidence_score'] for route in recent_routes) / total_routes
        
        strategy_distribution = defaultdict(int)
        outcome_distribution = defaultdict(int)
        agent_utilization = defaultdict(int)
        
        for route in recent_routes:
            strategy_distribution[route['routing_strategy']] += 1
            outcome_distribution[route['predicted_outcome']] += 1
            agent_utilization[route['selected_agent']] += 1
        
        return {
            'total_routes': total_routes,
            'average_confidence': avg_confidence,
            'strategy_distribution': dict(strategy_distribution),
            'outcome_distribution': dict(outcome_distribution),
            'agent_utilization': dict(agent_utilization),
            'available_agents': len(self._get_available_agents()),
            'total_agents': len(self.available_agents)
        }


_smart_router: Optional[SmartCallRouter] = None


def get_smart_router() -> Optional[SmartCallRouter]:
    """Get the global smart router instance"""
    global _smart_router
    return _smart_router


async def initialize_smart_router():
    """Initialize the global smart router"""
    global _smart_router
    
    if _smart_router is None:
        _smart_router = SmartCallRouter()
        await _smart_router.initialize()
        logger.info("Smart call router initialized")
    
    return _smart_router