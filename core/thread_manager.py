"""
Thread Manager for centralized thread lifecycle management.

This module provides a centralized way to manage all application threads,
ensuring proper cleanup during application shutdown.
"""

import logging
import threading
from typing import List, Optional
from PyQt6.QtCore import QThread, QThreadPool

logger = logging.getLogger(__name__)


class ThreadManager:
    """
    Centralized manager for application threads.
    
    Provides thread registration, monitoring, and graceful shutdown capabilities.
    Now with improved thread safety and cleanup validation.
    """
    
    def __init__(self):
        """Initialize ThreadManager with empty thread registry and synchronization."""
        self.active_threads: List[QThread] = []
        self.thread_pools: List[QThreadPool] = []
        self._lock = threading.Lock()  # Thread safety for registry operations
        logger.debug("ThreadManager initialized with thread safety")
    
    def register_thread(self, thread: QThread, description: Optional[str] = None) -> None:
        """
        Register a thread for lifecycle management (thread-safe).
        
        Args:
            thread (QThread): Thread to register
            description (str, optional): Human-readable description for logging
        """
        if not thread:
            return
            
        with self._lock:
            if thread not in self.active_threads:
                self.active_threads.append(thread)
                desc = description or thread.__class__.__name__
                logger.debug(f"Registered thread: {desc} ({id(thread)})")
    
    def register_thread_pool(self, pool: QThreadPool, description: Optional[str] = None) -> None:
        """
        Register a thread pool for lifecycle management (thread-safe).
        
        Args:
            pool (QThreadPool): Thread pool to register  
            description (str, optional): Human-readable description for logging
        """
        if not pool:
            return
            
        with self._lock:
            if pool not in self.thread_pools:
                self.thread_pools.append(pool)
                desc = description or "QThreadPool"
                logger.debug(f"Registered thread pool: {desc} ({id(pool)})")
    
    def unregister_thread(self, thread: QThread) -> None:
        """
        Unregister a thread (called when thread finishes naturally) (thread-safe).
        
        Args:
            thread (QThread): Thread to unregister
        """
        if not thread:
            return
            
        with self._lock:
            if thread in self.active_threads:
                self.active_threads.remove(thread)
                logger.debug(f"Unregistered thread: {thread.__class__.__name__} ({id(thread)})")
    
    def get_active_thread_count(self) -> int:
        """
        Get count of currently active threads (thread-safe).
        
        Returns:
            int: Number of active threads
        """
        with self._lock:
            # Clean up finished threads
            self.active_threads = [t for t in self.active_threads if t.isRunning()]
            return len(self.active_threads)
    
    def stop_all_threads(self, timeout_ms: int = 5000) -> bool:
        """
        Stop all registered threads gracefully with improved cleanup validation.
        
        Args:
            timeout_ms (int): Timeout in milliseconds for each thread
            
        Returns:
            bool: True if all threads stopped gracefully, False if some were terminated
        """
        with self._lock:
            thread_count = len(self.active_threads)
            pool_count = len(self.thread_pools)
        
        logger.info(f"Stopping {thread_count} threads and {pool_count} thread pools...")
        
        all_stopped_gracefully = True
        
        # Stop thread pools first
        all_stopped_gracefully &= self._stop_all_thread_pools(timeout_ms)
        
        # Stop individual threads
        all_stopped_gracefully &= self._stop_all_individual_threads(timeout_ms)
        
        # CLEANUP VALIDATION: Verify threads actually stopped
        remaining_threads = self._validate_and_cleanup_registries()
        
        if remaining_threads > 0:
            logger.error(f"Cleanup validation failed: {remaining_threads} threads still running after stop")
            all_stopped_gracefully = False
        
        if all_stopped_gracefully:
            logger.info("All threads stopped gracefully")
        else:
            logger.warning("Some threads required forced termination or failed to stop")
            
        return all_stopped_gracefully
    
    def _stop_all_thread_pools(self, timeout_ms: int) -> bool:
        """Stop all thread pools with error handling"""
        all_pools_stopped = True
        
        with self._lock:
            pools_to_stop = self.thread_pools.copy()
        
        for pool in pools_to_stop:
            try:
                logger.debug(f"Stopping thread pool with {pool.activeThreadCount()} active threads")
                pool.clear()  # Remove pending tasks
                if not pool.waitForDone(timeout_ms):
                    logger.warning("Thread pool did not finish within timeout")
                    all_pools_stopped = False
            except Exception as e:
                logger.error(f"Error stopping thread pool: {e}")
                all_pools_stopped = False
        
        return all_pools_stopped
    
    def _stop_all_individual_threads(self, timeout_ms: int) -> bool:
        """Stop all individual threads with thread-safe iteration"""
        all_threads_stopped = True
        
        with self._lock:
            threads_to_stop = self.active_threads.copy()  # Thread-safe copy
        
        for thread in threads_to_stop:
            if not self._stop_single_thread(thread, timeout_ms):
                all_threads_stopped = False
        
        return all_threads_stopped
    
    def _validate_and_cleanup_registries(self) -> int:
        """
        Validate cleanup by checking remaining threads and clean registries.
        
        Returns:
            int: Number of threads still running after cleanup
        """
        with self._lock:
            # Check how many threads are still actually running
            still_running = [t for t in self.active_threads if t.isRunning()]
            running_count = len(still_running)
            
            if running_count > 0:
                logger.warning(f"Found {running_count} threads still running after stop:")
                for thread in still_running:
                    logger.warning(f"  - {thread.__class__.__name__} ({id(thread)})")
            
            # Clear registries regardless (for cleanup)
            self.active_threads.clear()
            self.thread_pools.clear()
            
            return running_count
    
    def _stop_single_thread(self, thread: QThread, timeout_ms: int) -> bool:
        """
        Stop a single thread with timeout and fallback to termination.
        
        Args:
            thread (QThread): Thread to stop
            timeout_ms (int): Timeout in milliseconds
            
        Returns:
            bool: True if stopped gracefully, False if terminated
        """
        if not thread or not thread.isRunning():
            return True
            
        thread_name = thread.__class__.__name__
        thread_id = id(thread)
        
        try:
            logger.debug(f"Stopping thread: {thread_name} ({thread_id})")
            
            # Try graceful stop first (new method)
            if hasattr(thread, 'stop'):
                thread.stop()
            else:
                # Fallback to quit for older threads
                thread.quit()
            
            # Wait for graceful shutdown
            if thread.wait(timeout_ms):
                logger.debug(f"Thread stopped gracefully: {thread_name}")
                return True
            else:
                # Force termination as last resort
                logger.warning(f"Forcing termination of thread: {thread_name}")
                thread.terminate()
                if thread.wait(2000):  # Give 2 seconds for termination
                    logger.debug(f"Thread terminated: {thread_name}")
                else:
                    logger.error(f"Thread failed to terminate: {thread_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping thread {thread_name}: {e}")
            return False
    
    def emergency_stop_all(self) -> None:
        """
        Emergency stop - immediately terminate all threads.
        
        This should only be used as a last resort when graceful shutdown fails.
        """
        logger.warning("Emergency stop - terminating all threads immediately")
        
        for thread in self.active_threads:
            if thread and thread.isRunning():
                try:
                    thread.terminate()
                    thread.wait(1000)  # Short wait
                except Exception as e:
                    logger.error(f"Error in emergency stop for {thread.__class__.__name__}: {e}")
        
        for pool in self.thread_pools:
            try:
                pool.clear()
                pool.waitForDone(1000)
            except Exception as e:
                logger.error(f"Error in emergency stop for thread pool: {e}")
        
        self.active_threads.clear()
        self.thread_pools.clear()
        logger.warning("Emergency stop completed")
    
    def get_status_report(self) -> str:
        """
        Get detailed status report of all managed threads.
        
        Returns:
            str: Human-readable status report
        """
        active_count = self.get_active_thread_count()
        pool_info = []
        
        for i, pool in enumerate(self.thread_pools):
            pool_info.append(f"Pool {i}: {pool.activeThreadCount()} active")
        
        pool_status = ", ".join(pool_info) if pool_info else "No pools"
        
        return f"ThreadManager: {active_count} active threads, {pool_status}" 