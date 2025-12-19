"""
Safe Query Executor - SQL Injection Prevention
Provides parameterized query execution with validation
"""
from sqlalchemy import text
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class SQLInjectionError(Exception):
    """Raised when dangerous SQL patterns are detected"""
    pass


class SafeQueryExecutor:
    """Secure SQL query execution with parameterization"""
    
    # Dangerous SQL patterns to block
    DANGEROUS_PATTERNS = [
        r';\s*DROP',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE.*WHERE\s+1\s*=\s*1',
        r';\s*TRUNCATE',
        r'EXEC\s*\(',
        r'xp_cmdshell',
        r'--\s*$',  # SQL comments at end
        r'/\*.*\*/',  # Block comments
        r'UNION\s+SELECT',  # Union-based injection
        r'OR\s+1\s*=\s*1',  # Always true conditions
        r'OR\s+\'1\'\s*=\s*\'1\'',
    ]
    
    @staticmethod
    def validate_sql(sql: str) -> bool:
        """
        Validate SQL doesn't contain dangerous patterns
        
        Args:
            sql: SQL query to validate
            
        Returns:
            True if safe
            
        Raises:
            SQLInjectionError: If dangerous pattern detected
        """
        for pattern in SafeQueryExecutor.DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                logger.error(f"Dangerous SQL pattern detected: {pattern}")
                raise SQLInjectionError(f"Dangerous SQL pattern detected: {pattern}")
        return True
    
    @staticmethod
    def execute_safe(conn, sql: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute SQL with parameters (prevents SQL injection)
        
        Args:
            conn: Database connection
            sql: SQL query with named parameters (:param_name)
            params: Dictionary of parameter values
            
        Returns:
            Query result
            
        Example:
            result = SafeQueryExecutor.execute_safe(
                conn,
                "SELECT * FROM campaigns WHERE platform = :platform",
                {"platform": "facebook"}
            )
        """
        # Validate SQL
        SafeQueryExecutor.validate_sql(sql)
        
        # Convert to parameterized query
        query = text(sql)
        
        # Execute with parameters
        try:
            result = conn.execute(query, params or {})
            logger.info(f"Executed safe query: {sql[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    @staticmethod
    def sanitize_identifier(identifier: str) -> str:
        """
        Sanitize table/column names (identifiers)
        Only allows alphanumeric and underscore
        
        Args:
            identifier: Table or column name
            
        Returns:
            Sanitized identifier
            
        Raises:
            ValueError: If identifier contains invalid characters
        """
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError(f"Invalid identifier: {identifier}")
        return identifier
    
    @staticmethod
    def build_safe_query(
        table: str,
        columns: list = None,
        where_conditions: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Build a safe SELECT query with parameters
        
        Args:
            table: Table name
            columns: List of column names (default: *)
            where_conditions: Dictionary of column: value conditions
            order_by: Column to order by
            limit: Maximum rows to return
            
        Returns:
            Tuple of (sql_query, parameters)
        """
        # Sanitize identifiers
        table = SafeQueryExecutor.sanitize_identifier(table)
        
        # Build SELECT clause
        if columns:
            cols = ", ".join([SafeQueryExecutor.sanitize_identifier(c) for c in columns])
        else:
            cols = "*"
        
        sql = f"SELECT {cols} FROM {table}"
        params = {}
        
        # Build WHERE clause
        if where_conditions:
            where_parts = []
            for i, (col, val) in enumerate(where_conditions.items()):
                col = SafeQueryExecutor.sanitize_identifier(col)
                param_name = f"param_{i}"
                where_parts.append(f"{col} = :{param_name}")
                params[param_name] = val
            sql += " WHERE " + " AND ".join(where_parts)
        
        # Add ORDER BY
        if order_by:
            order_by = SafeQueryExecutor.sanitize_identifier(order_by)
            sql += f" ORDER BY {order_by}"
        
        # Add LIMIT
        if limit:
            sql += f" LIMIT {int(limit)}"
        
        return sql, params
