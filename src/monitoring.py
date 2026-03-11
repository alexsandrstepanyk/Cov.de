#!/usr/bin/env python3
"""
Monitoring Module for Gov.de
Health checks, metrics, and performance monitoring.
"""

import os
import sys
import time
import logging
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import threading
from collections import deque

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Збір та зберігання метрик продуктивності."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self._response_times: deque = deque(maxlen=max_samples)
        self._cache_hits: deque = deque(maxlen=max_samples)
        self._errors: deque = deque(maxlen=max_samples)
        self._requests: deque = deque(maxlen=max_samples)
        self._start_time = datetime.now()
        self._lock = threading.Lock()
    
    def record_response_time(self, endpoint: str, duration_ms: float):
        """Записує час відповіді."""
        with self._lock:
            self._response_times.append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'duration_ms': duration_ms
            })
    
    def record_cache_operation(self, hit: bool):
        """Записує операцію кешу."""
        with self._lock:
            self._cache_hits.append({
                'timestamp': datetime.now().isoformat(),
                'hit': hit
            })
    
    def record_error(self, endpoint: str, error: str):
        """Записує помилку."""
        with self._lock:
            self._errors.append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'error': error
            })
    
    def record_request(self, endpoint: str, status: int):
        """Записує запит."""
        with self._lock:
            self._requests.append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'status': status
            })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Повертає статистику продуктивності."""
        with self._lock:
            now = datetime.now()
            uptime = now - self._start_time
            
            # Останні 100 запитів для аналізу
            recent_requests = list(self._requests)[-100:]
            recent_errors = list(self._errors)[-100:]
            recent_cache = list(self._cache_hits)[-100:]
            recent_response = list(self._response_times)[-100:]
            
            # Обчислення метрик
            total_requests = len(self._requests)
            total_errors = len(self._errors)
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            cache_hits = sum(1 for op in self._cache_hits if op['hit'])
            cache_total = len(self._cache_hits)
            cache_hit_rate = (cache_hits / cache_total * 100) if cache_total > 0 else 0
            
            avg_response_time = 0
            if recent_response:
                avg_response_time = sum(r['duration_ms'] for r in recent_response) / len(recent_response)
            
            # Requests per minute (остання хвилина)
            one_minute_ago = now - timedelta(minutes=1)
            recent_rpm = sum(
                1 for r in self._requests
                if datetime.fromisoformat(r['timestamp']) > one_minute_ago
            )
            
            return {
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime),
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate_percent': round(error_rate, 2),
                'cache_hit_rate_percent': round(cache_hit_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'requests_per_minute': recent_rpm,
                'samples_collected': {
                    'response_times': len(self._response_times),
                    'cache_ops': len(self._cache_hits),
                    'errors': len(self._errors),
                    'requests': len(self._requests)
                }
            }


class HealthChecker:
    """Перевірка здоров'я системи."""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = None
    
    def register_check(self, name: str, check_func):
        """Реєструє функцію перевірки."""
        self.checks[name] = check_func
        logger.debug(f"Зареєстровано health check: {name}")
    
    async def run_all_checks(self) -> Dict[str, Dict]:
        """Виконує всі перевірки."""
        results = {}
        self.last_check_time = datetime.now()
        
        for name, check_func in self.checks.items():
            try:
                start = time.time()
                result = await check_func() if hasattr(check_func, '__await__') else check_func()
                duration = (time.time() - start) * 1000
                
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'duration_ms': round(duration, 2),
                    'message': 'OK' if result else 'Check failed'
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'duration_ms': 0,
                    'message': str(e)
                }
                logger.error(f"Health check '{name}' failed: {e}")
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Повертає підсумок здоров'я системи."""
        if not self.last_check_time:
            return {'status': 'unknown', 'message': 'No checks performed yet'}
        
        all_healthy = all(
            check['status'] == 'healthy'
            for check in self.checks.values()
        ) if self.checks else False
        
        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'last_check': self.last_check_time.isoformat(),
            'total_checks': len(self.checks),
            'healthy_checks': sum(1 for c in self.checks.values() if c['status'] == 'healthy'),
            'checks': self.checks
        }


# Глобальні екземпляри
_metrics = None
_health_checker = None


def get_metrics() -> PerformanceMetrics:
    """Отримує глобальний екземпляр метрик."""
    global _metrics
    if _metrics is None:
        _metrics = PerformanceMetrics()
        logger.info("PerformanceMetrics ініціалізовано")
    return _metrics


def get_health_checker() -> HealthChecker:
    """Отримує глобальний екземпляр health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
        logger.info("HealthChecker ініціалізовано")
    return _health_checker


# Стандартні перевірки здоров'я
def check_database() -> bool:
    """Перевірка бази даних."""
    try:
        from legal_database import DB_PATH
        if not DB_PATH.exists():
            logger.warning(f"База даних не знайдена: {DB_PATH}")
            return False
        
        # Перевірка розміру
        db_size = DB_PATH.stat().st_size
        if db_size < 1024:  # Менше 1KB
            logger.warning(f"База даних занадто мала: {db_size} bytes")
            return False
        
        logger.debug(f"База даних OK: {db_size} bytes")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки бази даних: {e}")
        return False


def check_disk_space() -> bool:
    """Перевірка вільного місця на диску."""
    try:
        project_root = Path(__file__).parent.parent
        usage = psutil.disk_usage(str(project_root))
        
        # Попередження якщо менше 10% вільно
        free_percent = (usage.free / usage.total) * 100
        if free_percent < 10:
            logger.warning(f"Мало вільного місця: {free_percent:.1f}%")
            return False
        
        logger.debug(f"Вільне місце: {free_percent:.1f}%")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки диску: {e}")
        return False


def check_memory() -> bool:
    """Перевірка використання пам'яті."""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Попередження якщо більше 80% пам'яті
        if memory_percent > 80:
            logger.warning(f"Високе використання пам'яті: {memory_percent:.1f}%")
            return False
        
        logger.debug(f"Використання пам'яті: {memory_percent:.1f}% ({memory_info.rss / 1024 / 1024:.1f} MB)")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки пам'яті: {e}")
        return False


def check_cpu() -> bool:
    """Перевірка завантаження CPU."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Попередження якщо CPU > 90%
        if cpu_percent > 90:
            logger.warning(f"Високе завантаження CPU: {cpu_percent:.1f}%")
            return False
        
        logger.debug(f"Завантаження CPU: {cpu_percent:.1f}%")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки CPU: {e}")
        return False


def check_logs() -> bool:
    """Перевірка лог файлів."""
    try:
        log_dir = Path(__file__).parent.parent / 'logs'
        if not log_dir.exists():
            log_dir.mkdir(exist_ok=True)
            logger.debug(f"Створено log директорію: {log_dir}")
            return True
        
        # Перевірка розміру логів
        total_log_size = sum(f.stat().st_size for f in log_dir.glob('*.log'))
        if total_log_size > 100 * 1024 * 1024:  # > 100MB
            logger.warning(f"Лог файли занадто великі: {total_log_size / 1024 / 1024:.1f} MB")
            return False
        
        logger.debug(f"Розмір логів: {total_log_size / 1024:.1f} KB")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки логів: {e}")
        return False


def check_env() -> bool:
    """Перевірка змінних оточення."""
    try:
        env_file = Path(__file__).parent.parent / '.env'
        if not env_file.exists():
            logger.warning(".env файл не знайдено")
            return False
        
        # Перевірка критичних змінних
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN'
        ]
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for var in required_vars:
            if var not in content:
                missing.append(var)
        
        if missing:
            logger.warning(f"Відсутні змінні оточення: {missing}")
            return False
        
        logger.debug("Всі змінні оточення наявні")
        return True
    except Exception as e:
        logger.error(f"Помилка перевірки змінних оточення: {e}")
        return False


def init_standard_checks():
    """Ініціалізує стандартні перевірки."""
    checker = get_health_checker()
    
    checker.register_check('database', check_database)
    checker.register_check('disk_space', check_disk_space)
    checker.register_check('memory', check_memory)
    checker.register_check('cpu', check_cpu)
    checker.register_check('logs', check_logs)
    checker.register_check('env', check_env)
    
    logger.info("Стандартні health checks ініціалізовано")


def get_system_info() -> Dict[str, Any]:
    """Повертає інформацію про систему."""
    try:
        process = psutil.Process(os.getpid())
        
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024,
            'memory_available': psutil.virtual_memory().available / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_total': psutil.disk_usage('/').total / 1024 / 1024 / 1024,
            'disk_used': psutil.disk_usage('/').used / 1024 / 1024 / 1024,
            'process_memory_mb': process.memory_info().rss / 1024 / 1024,
            'process_cpu_percent': process.cpu_percent(interval=0.1),
            'process_threads': process.num_threads(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка отримання інформації про систему: {e}")
        return {'error': str(e)}


# Декоратор для моніторингу продуктивності
def monitor_performance(endpoint_name: str):
    """
    Декоратор для моніторингу продуктивності функцій.
    
    Використання:
        @monitor_performance('search_laws')
        def search_laws(query):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_response_time(endpoint_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_response_time(endpoint_name, duration_ms)
                metrics.record_error(endpoint_name, str(e))
                raise
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# Приклад використання
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Ініціалізація
    init_standard_checks()
    
    # Запуск перевірок
    import asyncio
    
    async def test():
        print("\n🔍 Health Checks:")
        results = await get_health_checker().run_all_checks()
        for name, result in results.items():
            status = '✅' if result['status'] == 'healthy' else '❌'
            print(f"  {status} {name}: {result['message']} ({result['duration_ms']}ms)")
        
        print("\n📊 System Info:")
        info = get_system_info()
        print(f"  CPU: {info.get('cpu_percent', 'N/A')}%")
        print(f"  Memory: {info.get('memory_percent', 'N/A')}%")
        print(f"  Process Memory: {info.get('process_memory_mb', 'N/A'):.1f} MB")
        
        print("\n📈 Performance Metrics:")
        metrics = get_metrics().get_statistics()
        print(f"  Uptime: {metrics['uptime_formatted']}")
        print(f"  Cache Hit Rate: {metrics['cache_hit_rate_percent']}%")
        print(f"  Avg Response Time: {metrics['avg_response_time_ms']}ms")
    
    asyncio.run(test())
