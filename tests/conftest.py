"""
Pytest configuration and shared fixtures
Provides database setup, teardown, and test data
"""
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import sys
import os
from typing import Generator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from backend import database
from backend import crud

# Override database config for tests
TEST_DB_CONFIG = {
    'dbname': 'gen_test',
    'user': 'dbuser',
    'password': 'dbpassword',
    'host': 'localhost',
    'port': 5432
}

@pytest.fixture(scope='session')
def test_db_config():
    """Provide test database configuration"""
    return TEST_DB_CONFIG.copy()

@pytest.fixture(scope='session', autouse=True)
def setup_test_database(test_db_config):
    """Setup test database schema (once per test session)"""
    # Connect to postgres to create test DB
    conn = psycopg2.connect(
        dbname='postgres',
        user=test_db_config['user'],
        password=test_db_config['password'],
        host=test_db_config['host'],
        port=test_db_config['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Recreate test database
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['dbname']}")
    cursor.execute(f"CREATE DATABASE {test_db_config['dbname']}")
    cursor.close()
    conn.close()
    
    # Create schema
    conn = psycopg2.connect(**test_db_config)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biological_networks (
            network_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            network_type VARCHAR(50),
            organism VARCHAR(100),
            description TEXT,
            node_count INTEGER NOT NULL,
            edge_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS network_matrices (
            network_id INTEGER PRIMARY KEY REFERENCES biological_networks(network_id) ON DELETE CASCADE,
            node_labels TEXT[] NOT NULL,
            adjacency_matrix INTEGER[][] NOT NULL,
            signature_array BIGINT[] NOT NULL,
            signature_hash VARCHAR(64)
        );
        
        CREATE INDEX IF NOT EXISTS idx_networks_type ON biological_networks(network_type);
        CREATE INDEX IF NOT EXISTS idx_networks_node_count ON biological_networks(node_count);
        CREATE INDEX IF NOT EXISTS idx_matrices_hash ON network_matrices(signature_hash);
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    yield
    
    # Cleanup after all tests
    conn = psycopg2.connect(
        dbname='postgres',
        user=test_db_config['user'],
        password=test_db_config['password'],
        host=test_db_config['host'],
        port=test_db_config['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['dbname']}")
    cursor.close()
    conn.close()

@pytest.fixture
def db_connection(test_db_config, monkeypatch):
    """Provide database connection for tests"""
    # Monkey-patch database config
    monkeypatch.setattr(database, 'DATABASE_CONFIG', test_db_config)
    
    with database.get_db_connection() as conn:
        yield conn
        conn.rollback()  # Rollback after each test

@pytest.fixture
def clean_database(db_connection):
    """Clean database before each test"""
    cursor = db_connection.cursor()
    cursor.execute("TRUNCATE biological_networks CASCADE")
    db_connection.commit()
    yield db_connection

@pytest.fixture
def sample_network_data():
    """Provide sample network data for testing"""
    return {
        'name': 'Test_Network',
        'network_type': 'metabolic',
        'organism': 'Test organism',
        'description': 'Test description',
        'node_labels': ['A', 'B', 'C'],
        'adjacency_matrix': [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
    }

@pytest.fixture
def sample_glycolysis():
    """Provide glycolysis pathway data"""
    return {
        'name': 'Glycolysis',
        'network_type': 'metabolic',
        'organism': 'Homo sapiens',
        'description': 'Glucose breakdown pathway',
        'node_labels': ['Glucose', 'G6P', 'F6P', 'FBP', 'DHAP', 'G3P', 'Pyruvate'],
        'adjacency_matrix': [
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0]
        ]
    }

@pytest.fixture
def sample_partial_glycolysis():
    """Provide partial glycolysis for subgraph testing"""
    return {
        'name': 'Partial_Glycolysis',
        'network_type': 'metabolic',
        'organism': 'Homo sapiens',
        'description': 'Partial glucose pathway',
        'node_labels': ['Glucose', 'G6P', 'F6P'],
        'adjacency_matrix': [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
    }

# ============================================================================
# FILE: tests/test_database.py
# ============================================================================
"""
Tests for database.py module
Coverage: Connection management, context managers, error handling
"""
import pytest
import psycopg2
from backend.database import get_db_connection, get_db_cursor, DATABASE_CONFIG

@pytest.mark.db
class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_get_db_connection_success(self, test_db_config, monkeypatch):
        """Test successful database connection"""
        monkeypatch.setattr('database.DATABASE_CONFIG', test_db_config)
        
        with get_db_connection() as conn:
            assert conn is not None
            assert not conn.closed
    
    def test_get_db_connection_commit(self, clean_database):
        """Test connection commits on success"""
        cursor = clean_database.cursor()
        cursor.execute("""
            INSERT INTO biological_networks 
            (name, network_type, organism, description, node_count, edge_count)
            VALUES ('Test', 'metabolic', 'Test', 'Test', 3, 2)
        """)
        clean_database.commit()
        
        cursor.execute("SELECT COUNT(*) FROM biological_networks")
        count = cursor.fetchone()[0]
        assert count == 1
    
    def test_get_db_connection_rollback_on_error(self, test_db_config, monkeypatch):
        """Test connection rolls back on error"""
        monkeypatch.setattr('database.DATABASE_CONFIG', test_db_config)
        
        with pytest.raises(psycopg2.Error):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO biological_networks (invalid_column) VALUES ('test')")
    
    def test_get_db_connection_closes_after_context(self, test_db_config, monkeypatch):
        """Test connection is closed after context manager exits"""
        monkeypatch.setattr('database.DATABASE_CONFIG', test_db_config)
        
        with get_db_connection() as conn:
            pass
        
        assert conn.closed
    
    def test_get_db_cursor_returns_dict_cursor(self, db_connection):
        """Test get_db_cursor returns RealDictCursor"""
        cursor = get_db_cursor(db_connection)
        assert cursor is not None
        assert cursor.connection == db_connection