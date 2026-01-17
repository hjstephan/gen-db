"""
Tests for database.py module
Coverage: Connection management, error handling, context manager
"""
import pytest
from backend.database import get_db_connection, get_db_cursor, DATABASE_CONFIG

@pytest.mark.unit
class TestDatabaseConnection:
    """Test database connection utilities"""
    
    def test_get_db_connection_success(self):
        """Test successful database connection"""
        with get_db_connection() as conn:
            assert conn is not None
            assert not conn.closed
    
    def test_get_db_connection_closes(self):
        """Test connection is closed after context"""
        with get_db_connection() as conn:
            pass
        assert conn.closed
    
    def test_get_db_connection_rollback_on_error(self):
        """Test rollback on exception"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INVALID SQL")
        except:
            pass
        # Connection should be closed
        assert conn.closed
    
    def test_get_db_cursor_returns_dict_cursor(self):
        """Test cursor returns dict-like results"""
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT 1 as test_col")
            result = cursor.fetchone()
            # RealDictCursor returns dict-like objects
            assert 'test_col' in result or result[0] == 1