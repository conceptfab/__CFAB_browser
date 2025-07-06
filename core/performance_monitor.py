"""
Performance monitoring module for the CFAB Browser application.

Provides tools for measuring operation duration, monitoring memory usage,
and logging performance metrics in a structured way.
"""

import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - memory monitoring disabled")

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Class for storing performance metrics"""

    def __init__(self, operation_name: str, start_time: float):
        self.operation_name = operation_name
        self.start_time = start_time
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.memory_before: Optional[float] = None
        self.memory_after: Optional[float] = None
        self.memory_peak: Optional[float] = None
        self.success: bool = True
        self.error_message: Optional[str] = None
        self.additional_data: Dict[str, Any] = {}

    def finish(
        self,
        success: bool = True,
        error_message: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """Finalizes metric measurement"""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message

        if additional_data:
            self.additional_data.update(additional_data)

        # Pobierz końcowe zużycie pamięci
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                self.memory_after = process.memory_info().rss / 1024 / 1024  # MB
                self.memory_peak = process.memory_info().rss / 1024 / 1024  # MB
            except Exception as e:
                logger.debug(f"Could not get memory usage: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Converts metrics to a dictionary"""
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "memory_before_mb": self.memory_before,
            "memory_after_mb": self.memory_after,
            "memory_peak_mb": self.memory_peak,
            "success": self.success,
            "error_message": self.error_message,
            "additional_data": self.additional_data,
            "timestamp": datetime.now().isoformat(),
        }


class PerformanceMonitor:
    """Main class for performance monitoring"""

    def __init__(
        self, log_file: Optional[str] = None, enable_console_logging: bool = True
    ):
        """
        Initializes the performance monitor

        Args:
            log_file: Path to log file (optional)
            enable_console_logging: Whether to enable console logging
        """
        self.log_file = log_file
        self.enable_console_logging = enable_console_logging
        self.metrics_history: list[PerformanceMetrics] = []
        self._setup_logging()

    def _setup_logging(self):
        """Configures logging system"""
        if self.log_file:
            log_dir = Path(self.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)

    def _log_metrics(self, metrics: PerformanceMetrics):
        """Logs metrics to file and/or console"""
        metrics_dict = metrics.to_dict()

        # Logowanie do pliku
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(metrics_dict, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.error(f"Could not write to performance log file: {e}")

        # Logowanie do konsoli
        if self.enable_console_logging:
            duration_str = f"{metrics.duration:.3f}s" if metrics.duration else "N/A"
            memory_str = (
                f"{metrics.memory_after:.1f}MB" if metrics.memory_after else "N/A"
            )

            if metrics.success:
                logger.debug(
                    f"PERF: {metrics.operation_name} completed in {duration_str} "
                    f"(memory: {memory_str})"
                )
            else:
                logger.error(
                    f"PERF: {metrics.operation_name} failed after {duration_str} "
                    f"(memory: {memory_str}) - {metrics.error_message}"
                )

        # Dodaj do historii
        self.metrics_history.append(metrics)

        # Ogranicz historię do ostatnich 1000 wpisów
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

    def _get_memory_usage(self) -> Optional[float]:
        """Gets current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return None

        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except Exception as e:
            logger.debug(f"Could not get memory usage: {e}")
            return None

    @contextmanager
    def measure_operation(
        self, operation_name: str, additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for measuring operation performance

        Args:
            operation_name: Name of the operation to measure
            additional_data: Additional data to save in metrics

        Yields:
            PerformanceMetrics: Metrics object
        """
        start_time = time.perf_counter()
        memory_before = self._get_memory_usage()

        metrics = PerformanceMetrics(operation_name, start_time)
        metrics.memory_before = memory_before

        if additional_data:
            metrics.additional_data.update(additional_data)

        try:
            yield metrics
            metrics.finish(success=True)
        except Exception as e:
            metrics.finish(success=False, error_message=str(e))
            raise
        finally:
            self._log_metrics(metrics)

    def measure_function(
        self,
        operation_name: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Decorator for measuring function performance

        Args:
            operation_name: Operation name (if None, uses function name)
            additional_data: Additional data to save in metrics

        Returns:
            Callable: Decorated function
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                # Użyj nazwy funkcji jeśli nie podano operation_name
                op_name = operation_name or func.__name__

                start_time = time.perf_counter()
                memory_before = self._get_memory_usage()

                metrics = PerformanceMetrics(op_name, start_time)
                metrics.memory_before = memory_before

                if additional_data:
                    metrics.additional_data.update(additional_data)

                try:
                    result = func(*args, **kwargs)
                    metrics.finish(success=True)
                    return result
                except Exception as e:
                    metrics.finish(success=False, error_message=str(e))
                    raise
                finally:
                    self._log_metrics(metrics)

            return wrapper

        return decorator


# Globalna instancja monitora wydajności
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Gets the global performance monitor instance"""
    global _performance_monitor

    if _performance_monitor is None:
        # Create a default instance
        log_file = Path(__file__).parent.parent / "logs" / "performance.log"
        _performance_monitor = PerformanceMonitor(str(log_file))

    return _performance_monitor


def measure_operation(
    operation_name: str, additional_data: Optional[Dict[str, Any]] = None
):
    """Short function for measuring operation performance"""
    return get_performance_monitor().measure_operation(operation_name, additional_data)


def measure_function(
    operation_name: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None,
):
    """Short function for decorating functions"""
    return get_performance_monitor().measure_function(operation_name, additional_data)
