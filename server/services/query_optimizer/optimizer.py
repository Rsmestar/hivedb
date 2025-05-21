import logging
import json
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import dask.dataframe as dd
from dask.distributed import Client as DaskClient

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Query optimizer for HiveDB to improve performance of complex queries."""
    
    def __init__(self):
        self.dask_client = None
        self.is_initialized = False
        self.query_cache = {}
        self.statistics = {}
    
    async def initialize(self):
        """Initialize the query optimizer."""
        try:
            # Initialize Dask client for parallel processing
            self.dask_client = DaskClient(processes=True, threads_per_worker=4, n_workers=2)
            self.is_initialized = True
            logger.info("Query optimizer initialized with Dask")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize query optimizer: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the query optimizer."""
        if self.dask_client:
            self.dask_client.close()
            self.is_initialized = False
            logger.info("Query optimizer shut down")
    
    def _convert_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert a list of dictionaries to a pandas DataFrame."""
        return pd.DataFrame(data)
    
    def _convert_to_dask_dataframe(self, df: pd.DataFrame) -> dd.DataFrame:
        """Convert a pandas DataFrame to a Dask DataFrame for parallel processing."""
        return dd.from_pandas(df, npartitions=max(1, len(df) // 10000))
    
    async def optimize_query(self, query: Dict[str, Any], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize and execute a query on the provided data."""
        if not self.is_initialized:
            logger.warning("Query optimizer not initialized, using standard processing")
            return self._execute_standard_query(query, data)
        
        try:
            # Generate a query hash for caching
            query_hash = json.dumps(query, sort_keys=True)
            
            # Check if we have a cached result
            if query_hash in self.query_cache:
                logger.info("Using cached query result")
                return self.query_cache[query_hash]
            
            # Convert data to DataFrame
            df = self._convert_to_dataframe(data)
            
            # For large datasets, use Dask for parallel processing
            if len(df) > 10000:
                result = await self._execute_parallel_query(query, df)
            else:
                result = self._execute_optimized_query(query, df)
            
            # Cache the result for future use
            self.query_cache[query_hash] = result
            
            # Update statistics
            self._update_statistics(query, len(data), len(result))
            
            return result
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            # Fallback to standard processing
            return self._execute_standard_query(query, data)
    
    def _execute_standard_query(self, query: Dict[str, Any], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a query using standard Python processing."""
        result = data
        
        # Filter data based on conditions
        if 'filter' in query:
            result = self._apply_filters(result, query['filter'])
        
        # Sort data
        if 'sort' in query:
            result = self._apply_sorting(result, query['sort'])
        
        # Limit results
        if 'limit' in query:
            limit = query['limit']
            result = result[:limit]
        
        return result
    
    def _execute_optimized_query(self, query: Dict[str, Any], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Execute a query using pandas optimizations."""
        # Apply filters
        if 'filter' in query:
            df = self._apply_pandas_filters(df, query['filter'])
        
        # Apply sorting
        if 'sort' in query:
            sort_fields = query['sort']
            ascending = [not field.startswith('-') for field in sort_fields]
            sort_fields = [field.lstrip('-+') for field in sort_fields]
            df = df.sort_values(sort_fields, ascending=ascending)
        
        # Apply limit
        if 'limit' in query:
            df = df.head(query['limit'])
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    async def _execute_parallel_query(self, query: Dict[str, Any], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Execute a query using Dask for parallel processing."""
        # Convert to Dask DataFrame
        ddf = self._convert_to_dask_dataframe(df)
        
        # Apply filters
        if 'filter' in query:
            ddf = self._apply_dask_filters(ddf, query['filter'])
        
        # Apply sorting (note: sorting in Dask is expensive)
        if 'sort' in query:
            sort_fields = query['sort']
            ascending = [not field.startswith('-') for field in sort_fields]
            sort_fields = [field.lstrip('-+') for field in sort_fields]
            ddf = ddf.sort_values(sort_fields, ascending=ascending)
        
        # Apply limit
        if 'limit' in query:
            # Convert back to pandas for limit operation
            df = ddf.compute()
            df = df.head(query['limit'])
        else:
            # Compute the full result
            df = ddf.compute()
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to a list of dictionaries."""
        result = []
        for item in data:
            if self._match_filters(item, filters):
                result.append(item)
        return result
    
    def _match_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if an item matches the specified filters."""
        for field, condition in filters.items():
            if field not in item:
                return False
            
            if isinstance(condition, dict):
                # Complex condition
                for op, value in condition.items():
                    if op == 'eq' and item[field] != value:
                        return False
                    elif op == 'ne' and item[field] == value:
                        return False
                    elif op == 'gt' and not (item[field] > value):
                        return False
                    elif op == 'gte' and not (item[field] >= value):
                        return False
                    elif op == 'lt' and not (item[field] < value):
                        return False
                    elif op == 'lte' and not (item[field] <= value):
                        return False
                    elif op == 'in' and item[field] not in value:
                        return False
                    elif op == 'nin' and item[field] in value:
                        return False
            else:
                # Simple equality condition
                if item[field] != condition:
                    return False
        
        return True
    
    def _apply_sorting(self, data: List[Dict[str, Any]], sort_fields: List[str]) -> List[Dict[str, Any]]:
        """Sort a list of dictionaries based on specified fields."""
        for field in reversed(sort_fields):
            reverse = False
            if field.startswith('-'):
                reverse = True
                field = field[1:]
            elif field.startswith('+'):
                field = field[1:]
            
            data = sorted(data, key=lambda x: x.get(field, None), reverse=reverse)
        
        return data
    
    def _apply_pandas_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to a pandas DataFrame."""
        mask = pd.Series(True, index=df.index)
        
        for field, condition in filters.items():
            if field not in df.columns:
                continue
            
            if isinstance(condition, dict):
                # Complex condition
                for op, value in condition.items():
                    if op == 'eq':
                        mask &= (df[field] == value)
                    elif op == 'ne':
                        mask &= (df[field] != value)
                    elif op == 'gt':
                        mask &= (df[field] > value)
                    elif op == 'gte':
                        mask &= (df[field] >= value)
                    elif op == 'lt':
                        mask &= (df[field] < value)
                    elif op == 'lte':
                        mask &= (df[field] <= value)
                    elif op == 'in':
                        mask &= df[field].isin(value)
                    elif op == 'nin':
                        mask &= ~df[field].isin(value)
            else:
                # Simple equality condition
                mask &= (df[field] == condition)
        
        return df[mask]
    
    def _apply_dask_filters(self, ddf: dd.DataFrame, filters: Dict[str, Any]) -> dd.DataFrame:
        """Apply filters to a Dask DataFrame."""
        mask = True
        
        for field, condition in filters.items():
            if field not in ddf.columns:
                continue
            
            if isinstance(condition, dict):
                # Complex condition
                for op, value in condition.items():
                    if op == 'eq':
                        mask = mask & (ddf[field] == value)
                    elif op == 'ne':
                        mask = mask & (ddf[field] != value)
                    elif op == 'gt':
                        mask = mask & (ddf[field] > value)
                    elif op == 'gte':
                        mask = mask & (ddf[field] >= value)
                    elif op == 'lt':
                        mask = mask & (ddf[field] < value)
                    elif op == 'lte':
                        mask = mask & (ddf[field] <= value)
                    elif op == 'in':
                        mask = mask & ddf[field].isin(value)
                    elif op == 'nin':
                        mask = mask & ~ddf[field].isin(value)
            else:
                # Simple equality condition
                mask = mask & (ddf[field] == condition)
        
        return ddf[mask]
    
    def _update_statistics(self, query: Dict[str, Any], input_size: int, output_size: int):
        """Update query statistics for performance monitoring."""
        query_type = self._get_query_type(query)
        
        if query_type not in self.statistics:
            self.statistics[query_type] = {
                'count': 0,
                'total_input_size': 0,
                'total_output_size': 0,
                'avg_selectivity': 0
            }
        
        stats = self.statistics[query_type]
        stats['count'] += 1
        stats['total_input_size'] += input_size
        stats['total_output_size'] += output_size
        
        # Calculate selectivity (ratio of output size to input size)
        selectivity = output_size / input_size if input_size > 0 else 0
        stats['avg_selectivity'] = (stats['avg_selectivity'] * (stats['count'] - 1) + selectivity) / stats['count']
    
    def _get_query_type(self, query: Dict[str, Any]) -> str:
        """Determine the type of query for statistics."""
        if 'filter' in query and 'sort' in query:
            return 'filter_sort'
        elif 'filter' in query:
            return 'filter'
        elif 'sort' in query:
            return 'sort'
        else:
            return 'simple'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get query optimizer statistics."""
        return {
            'query_types': self.statistics,
            'cache_size': len(self.query_cache),
            'is_initialized': self.is_initialized
        }
    
    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache = {}
        logger.info("Query cache cleared")

# Singleton instance
query_optimizer = QueryOptimizer()
