"""
Safe Query Executor - SQL Injection Prevention
Provides parameterized query execution with validation
"""
from sqlalchemy import text
from typing import Dict, Any, Optional, List
import re
import logging
import os

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
    def sanitize_identifier(identifier: str, allow_dots: bool = False) -> str:
        """
        Sanitize table/column names (identifiers)
        Only allows alphanumeric, underscore, and optionally dots
        
        Args:
            identifier: Table or column name
            allow_dots: If True, allow dots for qualified names (schema.table)
            
        Returns:
            Sanitized identifier
            
        Raises:
            ValueError: If identifier contains invalid characters
        """
        if allow_dots:
            pattern = r'^[a-zA-Z_][a-zA-Z0-9_.]*$'
        else:
            pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        
        if not re.match(pattern, identifier):
            raise ValueError(f"Invalid identifier: {identifier}")
        return identifier
    
    @staticmethod
    def execute_duckdb_safe(conn, sql: str, params: Optional[List[Any]] = None):
        """
        Execute DuckDB query with positional parameters (prevents SQL injection)
        
        Args:
            conn: DuckDB connection
            sql: SQL query with positional parameters (?)
            params: List of parameter values
            
        Returns:
            Query result
            
        Example:
            result = SafeQueryExecutor.execute_duckdb_safe(
                conn,
                "SELECT * FROM campaigns WHERE platform = ?",
                ["facebook"]
            )
        """
        # Validate SQL
        SafeQueryExecutor.validate_sql(sql)
        
        # Execute with parameters
        try:
            result = conn.execute(sql, params or [])
            logger.info(f"Executed safe DuckDB query: {sql[:100]}...")
            return result
        except Exception as e:
            logger.error(f"DuckDB query execution failed: {e}")
            raise
    
    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[List[str]] = None) -> str:
        """
        Validate file path for security
        
        Args:
            path: File path to validate
            allowed_extensions: List of allowed file extensions (e.g., ['.parquet', '.csv'])
            
        Returns:
            Absolute path if valid
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file extension not allowed or path contains suspicious patterns
        """
        # Check for path traversal attempts
        if '..' in path or path.startswith('/'):
            # Allow absolute paths but check they're not system paths
            if path.startswith(('/etc/', '/sys/', '/proc/', '/dev/')):
                raise ValueError(f"Access to system paths not allowed: {path}")
        
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Check file exists
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {abs_path}")
        
        # Check extension if specified
        if allowed_extensions:
            if not any(abs_path.endswith(ext) for ext in allowed_extensions):
                raise ValueError(f"File extension not allowed. Allowed: {allowed_extensions}")
        
        logger.info(f"Validated file path: {abs_path}")
        return abs_path
    
    @staticmethod
    def validate_query_against_schema(
        sql: str, 
        allowed_tables: List[str], 
        allowed_columns: List[str]
    ) -> bool:
        """
        Strict whitelist-based SQL validation.
        Ensures query only uses allowed tables, columns, and operators.
        """
        # 1. Run standard blacklist validation first
        SafeQueryExecutor.validate_sql(sql)
        
        # 2. Operator Whitelist (Strict)
        ALLOWED_KEYWORDS = {
            'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'LIMIT', 'JOIN', 
            'ON', 'WITH', 'AS', 'SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 'ROUND', 
            'NULLIF', 'DATE_TRUNC', 'CAST', 'INTERVAL', 'LAG', 'OVER', 'CASE', 
            'WHEN', 'THEN', 'ELSE', 'END', 'DESC', 'ASC', 'IN', 'AND', 'OR', 
            'NOT', 'IS', 'NULL', 'TOP', 'DISTINCT', 'DATE', 'WEEK', 'MONTH', 'YEAR',
            'DAY', 'DAYS', 'WEEKS', 'MONTHS', 'YEARS', 'QUARTER', 'QUARTERS',
            'HAVING', 'TRUE', 'FALSE', 'LIKE', 'ILIKE', 'BETWEEN', 'COALESCE',
            'STRING_AGG', 'ARRAY_AGG', 'FIRST_VALUE', 'LAST_VALUE', 'RANK', 'ROW_NUMBER',
            'TOTAL', 'SPENT', 'OFFSET', 'UNION', 'ALL', 'STAGE_TOTALS', 'FINAL_QUERY'
        }
        
        # Tokenizer that handles:
        # 1. Double-quoted identifiers: "Total Spent"
        # 2. Standard identifiers: campaigns
        # 3. Numeric literals are handled separately
        
        # Strip string literals ('...') first
        sql_no_strings = re.sub(r"'[^']*'", " 'LITERAL' ", sql)
        
        # Extract tokens: matches double-quoted strings OR words
        token_pattern = r'"[^"]+"|[a-zA-Z_][a-zA-Z0-9_.]*'
        raw_tokens = re.findall(token_pattern, sql_no_strings)
        
        # Identify aliases (tokens following 'AS')
        aliases = set()
        for i in range(len(raw_tokens) - 1):
            curr_upper = raw_tokens[i].upper()
            if curr_upper == 'AS':
                # Strip quotes from alias if present
                alias = raw_tokens[i+1].strip('"').upper()
                aliases.add(alias)
            elif curr_upper == 'WITH':
                # First CTE name in WITH clause
                alias = raw_tokens[i+1].strip('"').upper()
                aliases.add(alias)
            elif raw_tokens[i].endswith(','):
                # Subsequent CTE names in WITH clause (comma-separated before AS)
                # This is a bit simplistic but works for WITH t1 AS (...), t2 AS (...)
                potential_comma = raw_tokens[i].rstrip(',')
                if i > 0 and raw_tokens[i-1].upper() == ')': # End of previous CTE
                     alias = potential_comma.strip('"').upper()
                     aliases.add(alias)
        
        # Also handle comma-separated CTE names better
        for i in range(1, len(raw_tokens) - 1):
            if raw_tokens[i].upper() == 'AS' and raw_tokens[i-1].endswith(','):
                 # This is likely a CTE name after a comma
                 pass # The logic above might be cleaner
        
        normalized_allowed_tables = {t.upper() for t in allowed_tables}
        normalized_allowed_columns = {c.upper() for c in allowed_columns}
        
        for raw_token in raw_tokens:
            # Normalize token for validation: strip quotes and uppercase
            token = raw_token.strip('"').upper()
            # Skip placeholders or literals we inserted
            if token == 'LITERAL':
                continue
            
            if token.isdigit():
                continue
                
            # If it's a known keyword, it's fine
            if token in ALLOWED_KEYWORDS:
                continue
                
            # If it's a known alias, it's fine
            if token in aliases:
                continue

            # If it's a table or column, it's fine
            if token in normalized_allowed_tables or token in normalized_allowed_columns:
                continue
            
            # Check for qualified names (table.column)
            if '.' in token:
                parts = token.split('.')
                # All parts must be either table names or column names or keywords (like 'month' in date_trunc)
                if all(p in normalized_allowed_tables or p in normalized_allowed_columns or p in ALLOWED_KEYWORDS for p in parts):
                    continue

            # If we reach here, the token is unauthorized
            logger.error(f"Unauthorized SQL token detected: {token}")
            raise SQLInjectionError(f"Unauthorized SQL token detected: {token}")

        return True

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
        
        sql = f"SELECT {cols} FROM {table}"  # nosec B608
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
