import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import asyncpg
import json
from collections import defaultdict


logger = logging.getLogger(__name__)


class PerformanceStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


class OptimizationType(Enum):
    INDEX_OPTIMIZATION = "index_optimization"
    QUERY_OPTIMIZATION = "query_optimization"
    TABLE_MAINTENANCE = "table_maintenance"
    CONNECTION_MANAGEMENT = "connection_management"
    DATA_ARCHIVING = "data_archiving"


@dataclass
class DatabaseMetric:
    metric_name: str
    current_value: float
    threshold_warning: float
    threshold_critical: float
    unit: str
    status: PerformanceStatus
    recommendation: Optional[str] = None


@dataclass
class QueryPerformanceInfo:
    query_hash: str
    query_text: str
    execution_count: int
    total_time_ms: float
    mean_time_ms: float
    max_time_ms: float
    rows_affected: int
    performance_impact: float


@dataclass
class IndexAnalysis:
    index_name: str
    table_name: str
    index_size: int
    usage_count: int
    last_used: Optional[datetime]
    efficiency_score: float
    recommendation: str


@dataclass
class OptimizationRecommendation:
    optimization_type: OptimizationType
    priority: str
    description: str
    estimated_impact: str
    implementation_steps: List[str]
    estimated_time_savings: Optional[float] = None


class DatabasePerformanceMonitor:
    """
    Advanced database performance monitoring and optimization system
    """
    
    def __init__(self):
        self.connection_pool: Optional[asyncpg.Pool] = None
        self.monitoring_active = False
        self.performance_history: List[Dict[str, Any]] = []
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        self.last_analysis_time: Optional[datetime] = None
    
    async def initialize(self, database_url: str):
        """Initialize database connection pool and monitoring"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            
            await self._ensure_monitoring_extensions()
            
            logger.info("Database performance monitor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database performance monitor: {e}")
            raise
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("Database performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.connection_pool:
            await self.connection_pool.close()
        logger.info("Database performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._collect_performance_metrics()
                await self._analyze_query_performance()
                await self._check_index_usage()
                await self._update_recommendations()
                
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _ensure_monitoring_extensions(self):
        """Ensure required extensions are available"""
        if not self.connection_pool:
            return
        
        async with self.connection_pool.acquire() as conn:
            try:
                result = await conn.fetchval(
                    "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
                )
                if not result:
                    logger.warning("pg_stat_statements extension not available - query analysis will be limited")
                
            except Exception as e:
                logger.warning(f"Error checking extensions: {e}")
    
    async def _collect_performance_metrics(self) -> Dict[str, DatabaseMetric]:
        """Collect current database performance metrics"""
        if not self.connection_pool:
            return {}
        
        metrics = {}
        
        async with self.connection_pool.acquire() as conn:
            try:
                db_size = await conn.fetchval(
                    "SELECT pg_database_size(current_database())"
                )
                metrics['database_size'] = DatabaseMetric(
                    metric_name='Database Size',
                    current_value=db_size / (1024**3),  # Convert to GB
                    threshold_warning=10.0,
                    threshold_critical=50.0,
                    unit='GB',
                    status=self._determine_status(db_size / (1024**3), 10.0, 50.0)
                )
                
                active_connections = await conn.fetchval(
                    "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                max_connections = await conn.fetchval(
                    "SELECT current_setting('max_connections')::INTEGER"
                )
                connection_usage = (active_connections / max_connections) * 100
                
                metrics['connection_usage'] = DatabaseMetric(
                    metric_name='Connection Usage',
                    current_value=connection_usage,
                    threshold_warning=70.0,
                    threshold_critical=90.0,
                    unit='%',
                    status=self._determine_status(connection_usage, 70.0, 90.0)
                )
                
                cache_hit_ratio = await conn.fetchval("""
                    SELECT 
                        (sum(heap_blks_hit) / GREATEST(sum(heap_blks_hit + heap_blks_read), 1)) * 100
                    FROM pg_statio_user_tables
                """)
                if cache_hit_ratio:
                    metrics['cache_hit_ratio'] = DatabaseMetric(
                        metric_name='Cache Hit Ratio',
                        current_value=cache_hit_ratio,
                        threshold_warning=95.0,
                        threshold_critical=90.0,
                        unit='%',
                        status=self._determine_status(cache_hit_ratio, 95.0, 90.0, reverse=True)
                    )
                
                index_hit_ratio = await conn.fetchval("""
                    SELECT 
                        (sum(idx_blks_hit) / GREATEST(sum(idx_blks_hit + idx_blks_read), 1)) * 100
                    FROM pg_statio_user_indexes
                """)
                if index_hit_ratio:
                    metrics['index_hit_ratio'] = DatabaseMetric(
                        metric_name='Index Hit Ratio',
                        current_value=index_hit_ratio,
                        threshold_warning=95.0,
                        threshold_critical=90.0,
                        unit='%',
                        status=self._determine_status(index_hit_ratio, 95.0, 90.0, reverse=True)
                    )
                
                deadlocks = await conn.fetchval(
                    "SELECT deadlocks FROM pg_stat_database WHERE datname = current_database()"
                )
                if deadlocks is not None:
                    metrics['deadlocks'] = DatabaseMetric(
                        metric_name='Deadlock Count',
                        current_value=deadlocks,
                        threshold_warning=10,
                        threshold_critical=50,
                        unit='count',
                        status=self._determine_status(deadlocks, 10, 50)
                    )
                
                bloat_info = await conn.fetch("""
                    SELECT 
                        tablename,
                        CASE 
                            WHEN n_tup_ins + n_tup_upd + n_tup_del = 0 THEN 0
                            ELSE (n_dead_tup::FLOAT / (n_tup_ins + n_tup_upd + n_tup_del)) * 100
                        END as bloat_percentage
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                    ORDER BY bloat_percentage DESC
                    LIMIT 5
                """)
                
                max_bloat = max([row['bloat_percentage'] for row in bloat_info], default=0)
                metrics['table_bloat'] = DatabaseMetric(
                    metric_name='Maximum Table Bloat',
                    current_value=max_bloat,
                    threshold_warning=15.0,
                    threshold_critical=25.0,
                    unit='%',
                    status=self._determine_status(max_bloat, 15.0, 25.0)
                )
                
            except Exception as e:
                logger.error(f"Error collecting performance metrics: {e}")
        
        metric_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {name: {
                'value': metric.current_value,
                'status': metric.status.value
            } for name, metric in metrics.items()}
        }
        self.performance_history.append(metric_record)
        
        if len(self.performance_history) > 288:
            self.performance_history = self.performance_history[-288:]
        
        return metrics
    
    def _determine_status(self, value: float, warning_threshold: float, critical_threshold: float, reverse: bool = False) -> PerformanceStatus:
        """Determine performance status based on thresholds"""
        if reverse:  
            if value >= warning_threshold:
                return PerformanceStatus.EXCELLENT
            elif value >= critical_threshold:
                return PerformanceStatus.GOOD
            else:
                return PerformanceStatus.CRITICAL
        else:  
            if value >= critical_threshold:
                return PerformanceStatus.CRITICAL
            elif value >= warning_threshold:
                return PerformanceStatus.WARNING
            elif value < warning_threshold * 0.5:
                return PerformanceStatus.EXCELLENT
            else:
                return PerformanceStatus.GOOD
    
    async def _analyze_query_performance(self) -> List[QueryPerformanceInfo]:
        """Analyze query performance using pg_stat_statements"""
        if not self.connection_pool:
            return []
        
        queries = []
        
        async with self.connection_pool.acquire() as conn:
            try:
                has_pg_stat_statements = await conn.fetchval(
                    "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
                )
                
                if not has_pg_stat_statements:
                    return queries
                
                query_stats = await conn.fetch("""
                    SELECT 
                        queryid::TEXT as query_hash,
                        query,
                        calls,
                        total_time,
                        mean_time,
                        max_time,
                        rows
                    FROM pg_stat_statements
                    WHERE mean_time > 100  -- Queries taking more than 100ms
                    ORDER BY total_time DESC
                    LIMIT 20
                """)
                
                for row in query_stats:
                    impact = (row['total_time'] / 1000) * (row['calls'] / 100)  # Simplified impact score
                    
                    query_info = QueryPerformanceInfo(
                        query_hash=row['query_hash'],
                        query_text=row['query'][:200] + '...' if len(row['query']) > 200 else row['query'],
                        execution_count=row['calls'],
                        total_time_ms=row['total_time'],
                        mean_time_ms=row['mean_time'],
                        max_time_ms=row['max_time'],
                        rows_affected=row['rows'],
                        performance_impact=impact
                    )
                    queries.append(query_info)
                
            except Exception as e:
                logger.error(f"Error analyzing query performance: {e}")
        
        return queries
    
    async def _check_index_usage(self) -> List[IndexAnalysis]:
        """Analyze index usage and effectiveness"""
        if not self.connection_pool:
            return []
        
        indexes = []
        
        async with self.connection_pool.acquire() as conn:
            try:
                index_stats = await conn.fetch("""
                    SELECT 
                        i.indexrelname as index_name,
                        i.relname as table_name,
                        pg_relation_size(i.indexrelid) as index_size,
                        i.idx_scan as usage_count,
                        s.last_idx_scan as last_used
                    FROM pg_stat_user_indexes i
                    LEFT JOIN pg_stat_user_tables s ON i.relid = s.relid
                    WHERE i.schemaname = 'public'
                    ORDER BY i.idx_scan DESC
                """)
                
                for row in index_stats:
                    size_penalty = min(1.0, row['index_size'] / (1024 * 1024))  # Size in MB
                    usage_score = min(1.0, row['usage_count'] / 1000)  # Normalize usage
                    efficiency = usage_score - (size_penalty * 0.1)
                    
                    if row['usage_count'] == 0:
                        recommendation = "Consider dropping - never used"
                    elif row['usage_count'] < 10:
                        recommendation = "Low usage - review necessity"
                    elif efficiency > 0.8:
                        recommendation = "Well optimized"
                    else:
                        recommendation = "Monitor usage patterns"
                    
                    index_analysis = IndexAnalysis(
                        index_name=row['index_name'],
                        table_name=row['table_name'],
                        index_size=row['index_size'],
                        usage_count=row['usage_count'],
                        last_used=row['last_used'],
                        efficiency_score=efficiency,
                        recommendation=recommendation
                    )
                    indexes.append(index_analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing index usage: {e}")
        
        return indexes
    
    async def _update_recommendations(self):
        """Update optimization recommendations based on current metrics"""
        recommendations = []
        
        current_metrics = await self._collect_performance_metrics()
        
        if 'connection_usage' in current_metrics:
            usage = current_metrics['connection_usage']
            if usage.status in [PerformanceStatus.WARNING, PerformanceStatus.CRITICAL]:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.CONNECTION_MANAGEMENT,
                    priority='High' if usage.status == PerformanceStatus.CRITICAL else 'Medium',
                    description=f"Connection usage at {usage.current_value:.1f}% - optimize connection pooling",
                    estimated_impact="20-30% improvement in concurrent performance",
                    implementation_steps=[
                        "Review application connection pooling configuration",
                        "Implement connection timeout policies",
                        "Monitor connection lifecycle",
                        "Consider read replica for read-heavy operations"
                    ]
                ))
        
        if 'table_bloat' in current_metrics:
            bloat = current_metrics['table_bloat']
            if bloat.status in [PerformanceStatus.WARNING, PerformanceStatus.CRITICAL]:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.TABLE_MAINTENANCE,
                    priority='High' if bloat.status == PerformanceStatus.CRITICAL else 'Medium',
                    description=f"Table bloat at {bloat.current_value:.1f}% - requires maintenance",
                    estimated_impact="10-25% improvement in query performance",
                    implementation_steps=[
                        "Schedule VACUUM ANALYZE on high-bloat tables",
                        "Consider VACUUM FULL for severely bloated tables",
                        "Implement automated maintenance scheduling",
                        "Review update/delete patterns"
                    ]
                ))
        
        if 'cache_hit_ratio' in current_metrics:
            cache = current_metrics['cache_hit_ratio']
            if cache.status in [PerformanceStatus.WARNING, PerformanceStatus.CRITICAL]:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.QUERY_OPTIMIZATION,
                    priority='High',
                    description=f"Cache hit ratio at {cache.current_value:.1f}% - below optimal",
                    estimated_impact="15-40% improvement in query response time",
                    implementation_steps=[
                        "Increase shared_buffers configuration",
                        "Optimize query patterns to improve cache locality",
                        "Review and optimize frequently accessed queries",
                        "Consider read-only replicas for reporting queries"
                    ]
                ))
        
        index_analysis = await self._check_index_usage()
        unused_indexes = [idx for idx in index_analysis if idx.usage_count == 0]
        
        if unused_indexes:
            recommendations.append(OptimizationRecommendation(
                optimization_type=OptimizationType.INDEX_OPTIMIZATION,
                priority='Medium',
                description=f"Found {len(unused_indexes)} unused indexes consuming storage",
                estimated_impact="Reduced storage and faster write operations",
                implementation_steps=[
                    "Review unused indexes for removal",
                    "Analyze query patterns for missing beneficial indexes",
                    "Implement index usage monitoring",
                    "Schedule regular index maintenance"
                ]
            ))
        
        if 'database_size' in current_metrics:
            size = current_metrics['database_size']
            if size.status in [PerformanceStatus.WARNING, PerformanceStatus.CRITICAL]:
                recommendations.append(OptimizationRecommendation(
                    optimization_type=OptimizationType.DATA_ARCHIVING,
                    priority='Medium',
                    description=f"Database size at {size.current_value:.1f}GB - consider archiving",
                    estimated_impact="Improved backup/restore times and query performance",
                    implementation_steps=[
                        "Implement automated data archiving for old records",
                        "Set up compressed archive storage",
                        "Create data retention policies",
                        "Schedule regular archiving jobs"
                    ]
                ))
        
        self.optimization_recommendations = recommendations
        self.last_analysis_time = datetime.utcnow()
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        current_metrics = await self._collect_performance_metrics()
        query_performance = await self._analyze_query_performance()
        index_analysis = await self._check_index_usage()
        
        return {
            'current_metrics': {
                name: {
                    'value': metric.current_value,
                    'unit': metric.unit,
                    'status': metric.status.value,
                    'recommendation': metric.recommendation
                } for name, metric in current_metrics.items()
            },
            'slow_queries': [
                {
                    'query_text': query.query_text,
                    'execution_count': query.execution_count,
                    'mean_time_ms': query.mean_time_ms,
                    'performance_impact': query.performance_impact
                } for query in query_performance[:10]
            ],
            'index_efficiency': [
                {
                    'index_name': idx.index_name,
                    'table_name': idx.table_name,
                    'usage_count': idx.usage_count,
                    'efficiency_score': idx.efficiency_score,
                    'recommendation': idx.recommendation
                } for idx in index_analysis[:10]
            ],
            'optimization_recommendations': [
                {
                    'type': rec.optimization_type.value,
                    'priority': rec.priority,
                    'description': rec.description,
                    'estimated_impact': rec.estimated_impact,
                    'implementation_steps': rec.implementation_steps
                } for rec in self.optimization_recommendations
            ],
            'performance_trends': self.performance_history[-48:] if self.performance_history else [],  # Last 4 hours
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None
        }
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        dashboard_data = await self.get_performance_dashboard()
        
        metric_scores = []
        for metric_data in dashboard_data['current_metrics'].values():
            status = metric_data['status']
            if status == 'excellent':
                metric_scores.append(100)
            elif status == 'good':
                metric_scores.append(80)
            elif status == 'warning':
                metric_scores.append(60)
            else:  # critical
                metric_scores.append(30)
        
        overall_health = sum(metric_scores) / len(metric_scores) if metric_scores else 50
        
        priority_counts = defaultdict(int)
        for rec in self.optimization_recommendations:
            priority_counts[rec.priority.lower()] += 1
        
        return {
            'overall_health_score': overall_health,
            'health_status': self._get_health_status(overall_health),
            'total_recommendations': len(self.optimization_recommendations),
            'recommendations_by_priority': dict(priority_counts),
            'critical_issues': len([rec for rec in self.optimization_recommendations if rec.priority == 'High']),
            'performance_trends_summary': {
                'metrics_tracked': len(dashboard_data['current_metrics']),
                'data_points': len(dashboard_data['performance_trends']),
                'monitoring_duration_hours': len(dashboard_data['performance_trends']) * 5 / 60  # 5-minute intervals
            },
            'optimization_opportunities': {
                'slow_queries_found': len(dashboard_data['slow_queries']),
                'unused_indexes': len([idx for idx in dashboard_data['index_efficiency'] if idx['usage_count'] == 0]),
                'low_efficiency_indexes': len([idx for idx in dashboard_data['index_efficiency'] if idx['efficiency_score'] < 0.5])
            },
            'recommendations': dashboard_data['optimization_recommendations']
        }
    
    def _get_health_status(self, score: float) -> str:
        """Convert health score to status"""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'warning'
        else:
            return 'critical'
    
    async def execute_optimization(self, optimization_type: str) -> Dict[str, Any]:
        """Execute specific optimization recommendations"""
        if not self.connection_pool:
            return {'success': False, 'error': 'No database connection'}
        
        results = {'success': False, 'actions_taken': [], 'error': None}
        
        try:
            async with self.connection_pool.acquire() as conn:
                if optimization_type == 'table_maintenance':
                    bloated_tables = await conn.fetch("""
                        SELECT tablename
                        FROM pg_stat_user_tables
                        WHERE schemaname = 'public'
                        AND (
                            CASE 
                                WHEN n_tup_ins + n_tup_upd + n_tup_del = 0 THEN 0
                                ELSE (n_dead_tup::FLOAT / (n_tup_ins + n_tup_upd + n_tup_del)) * 100
                            END
                        ) > 15
                        LIMIT 5
                    """)
                    
                    for table in bloated_tables:
                        await conn.execute(f'VACUUM ANALYZE {table["tablename"]}')
                        results['actions_taken'].append(f'Vacuumed table {table["tablename"]}')
                
                elif optimization_type == 'index_cleanup':
                    unused_indexes = await conn.fetch("""
                        SELECT indexname, tablename
                        FROM pg_stat_user_indexes
                        WHERE schemaname = 'public'
                        AND idx_scan = 0
                        AND indexname NOT LIKE '%_pkey'
                        LIMIT 3
                    """)
                    
                    for index in unused_indexes:
                        # For safety, just log what would be dropped
                        results['actions_taken'].append(f'Identified unused index {index["indexname"]} for potential removal')
                
                results['success'] = True
                
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Error executing optimization {optimization_type}: {e}")
        
        return results


_performance_monitor: Optional[DatabasePerformanceMonitor] = None


def get_performance_monitor() -> Optional[DatabasePerformanceMonitor]:
    """Get the global performance monitor instance"""
    global _performance_monitor
    return _performance_monitor


async def initialize_performance_monitor(database_url: str):
    """Initialize the global performance monitor"""
    global _performance_monitor
    
    if _performance_monitor is None:
        _performance_monitor = DatabasePerformanceMonitor()
        await _performance_monitor.initialize(database_url)
        await _performance_monitor.start_monitoring()
        logger.info("Database performance monitor initialized")
    
    return _performance_monitor


async def shutdown_performance_monitor():
    """Shutdown the global performance monitor"""
    global _performance_monitor
    
    if _performance_monitor:
        await _performance_monitor.stop_monitoring()
        _performance_monitor = None
        logger.info("Database performance monitor shutdown")