"""
Component-level caching strategy.
Implements smart caching for Streamlit components.
"""

import logging
import hashlib
import json
from typing import Any, Callable, Optional
from functools import wraps

import streamlit as st
import pandas as pd

logger = logging.getLogger(__name__)


class CachingStrategy:
    """
    Smart caching strategy for Streamlit components.
    
    Implements multiple caching layers:
    1. @st.cache_data for data transformations
    2. @st.cache_resource for expensive objects
    3. Session state for user-specific data
    4. Custom TTL-based caching
    """
    
    @staticmethod
    def cache_dataframe_hash(df: pd.DataFrame) -> str:
        """
        Generate hash for dataframe caching.
        
        Args:
            df: DataFrame to hash
            
        Returns:
            Hash string
        """
        # Hash based on shape and column names
        hash_input = f"{df.shape}_{','.join(df.columns.tolist())}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    @staticmethod
    def cache_with_ttl(ttl_seconds: int = 3600):
        """
        Decorator for TTL-based caching.
        
        Args:
            ttl_seconds: Time to live in seconds
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func.__name__}_{args}_{kwargs}"
                cache_key_hash = hashlib.md5(cache_key.encode()).hexdigest()
                
                # Check session state cache
                if 'ttl_cache' not in st.session_state:
                    st.session_state.ttl_cache = {}
                
                cache_entry = st.session_state.ttl_cache.get(cache_key_hash)
                
                if cache_entry:
                    # Check TTL
                    import time
                    if time.time() - cache_entry['timestamp'] < ttl_seconds:
                        logger.debug(f"Cache HIT for {func.__name__}")
                        return cache_entry['value']
                
                # Cache miss - execute function
                logger.debug(f"Cache MISS for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache
                import time
                st.session_state.ttl_cache[cache_key_hash] = {
                    'value': result,
                    'timestamp': time.time()
                }
                
                return result
            
            return wrapper
        return decorator


# Pre-configured caching decorators for common use cases

@st.cache_data(ttl=3600, show_spinner="Loading data...")
def cache_dataframe_transform(df: pd.DataFrame, transform_func: Callable) -> pd.DataFrame:
    """
    Cache dataframe transformation.
    
    Args:
        df: Input dataframe
        transform_func: Transformation function
        
    Returns:
        Transformed dataframe
    """
    return transform_func(df)


@st.cache_data(ttl=1800, show_spinner="Calculating metrics...")
def cache_metrics_calculation(df: pd.DataFrame, metric_func: Callable) -> dict:
    """
    Cache metrics calculation.
    
    Args:
        df: Input dataframe
        metric_func: Metrics calculation function
        
    Returns:
        Metrics dictionary
    """
    return metric_func(df)


@st.cache_resource
def cache_expensive_object(create_func: Callable, *args, **kwargs) -> Any:
    """
    Cache expensive object creation.
    
    Args:
        create_func: Object creation function
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Created object
    """
    return create_func(*args, **kwargs)


@st.cache_data(ttl=7200, show_spinner="Processing analysis...")
def cache_analysis_results(df_hash: str, analysis_func: Callable, df: pd.DataFrame) -> dict:
    """
    Cache analysis results.
    
    Args:
        df_hash: Hash of input dataframe
        analysis_func: Analysis function
        df: Input dataframe
        
    Returns:
        Analysis results
    """
    return analysis_func(df)


class ComponentCache:
    """
    Component-specific caching manager.
    
    Provides caching for specific Streamlit components.
    """
    
    def __init__(self, component_name: str):
        """
        Initialize component cache.
        
        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.cache_key_prefix = f"component_cache_{component_name}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        full_key = f"{self.cache_key_prefix}_{key}"
        return st.session_state.get(full_key)
    
    def set(self, key: str, value: Any):
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        full_key = f"{self.cache_key_prefix}_{key}"
        st.session_state[full_key] = value
    
    def clear(self):
        """Clear all cache for this component."""
        keys_to_remove = [
            key for key in st.session_state.keys()
            if key.startswith(self.cache_key_prefix)
        ]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        logger.info(f"Cleared cache for component: {self.component_name}")


class CacheManager:
    """
    Global cache manager for the application.
    
    Provides centralized cache management and statistics.
    """
    
    @staticmethod
    def get_cache_stats() -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        stats = {
            'session_state_keys': len(st.session_state.keys()),
            'ttl_cache_entries': len(st.session_state.get('ttl_cache', {})),
            'cache_data_hits': 0,  # Streamlit doesn't expose this
            'cache_resource_hits': 0  # Streamlit doesn't expose this
        }
        
        return stats
    
    @staticmethod
    def clear_all_caches():
        """Clear all application caches."""
        # Clear Streamlit caches
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # Clear TTL cache
        if 'ttl_cache' in st.session_state:
            st.session_state.ttl_cache = {}
        
        # Clear component caches
        keys_to_remove = [
            key for key in st.session_state.keys()
            if key.startswith('component_cache_')
        ]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        logger.info("Cleared all application caches")
    
    @staticmethod
    def render_cache_controls():
        """Render cache control UI."""
        with st.expander("🗄️ Cache Management"):
            stats = CacheManager.get_cache_stats()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Session State Keys", stats['session_state_keys'])
                st.metric("TTL Cache Entries", stats['ttl_cache_entries'])
            
            with col2:
                if st.button("🗑️ Clear All Caches"):
                    CacheManager.clear_all_caches()
                    st.success("✅ All caches cleared")
                    st.rerun()
                
                if st.button("🔄 Clear Data Cache"):
                    st.cache_data.clear()
                    st.success("✅ Data cache cleared")


# Example usage decorators for common patterns

def cache_chart_generation(ttl: int = 1800):
    """
    Decorator for caching chart generation.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner="Generating chart...")(func)
    return decorator


def cache_llm_response(ttl: int = 3600):
    """
    Decorator for caching LLM responses.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner="Generating response...")(func)
    return decorator


def cache_database_query(ttl: int = 600):
    """
    Decorator for caching database queries.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner="Querying database...")(func)
    return decorator


# Caching best practices

CACHING_BEST_PRACTICES = """
# Caching Best Practices

## When to Use @st.cache_data
- Data transformations (filtering, aggregating)
- API calls that return data
- Database queries
- File I/O operations
- Expensive calculations

## When to Use @st.cache_resource
- ML models
- Database connections
- API clients
- Large objects that shouldn't be copied

## When to Use Session State
- User-specific data
- Form inputs
- Navigation state
- Temporary UI state

## TTL Guidelines
- Fast-changing data: 5-10 minutes
- Moderate data: 30-60 minutes
- Slow-changing data: 2-4 hours
- Static data: No TTL (cache indefinitely)

## Cache Invalidation
- Clear cache when data source changes
- Use hash-based keys for automatic invalidation
- Provide manual cache clear button for users
"""
