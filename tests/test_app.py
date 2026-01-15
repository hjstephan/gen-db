"""
Tests for app.py FastAPI application
Coverage: All API endpoints, request/response validation, error handling
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from backend.app import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test /api/health endpoint"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.integration
class TestNetworkEndpoints:
    """Test network CRUD endpoints"""
    
    def test_get_networks_empty(self, client, clean_database, monkeypatch):
        """Test GET /api/networks with empty database"""
        from backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        response = client.get("/api/networks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
    
    def test_create_network_valid(self, client, clean_database, sample_network_data, monkeypatch):
        """Test POST /api/networks with valid data"""
        from backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        response = client.post("/api/networks", json=sample_network_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "network_id" in data["data"]
    
    def test_create_network_invalid_data(self, client):
        """Test POST /api/networks with invalid data"""
        invalid_data = {
            "name": "Test",
            # Missing required fields
        }
        
        response = client.post("/api/networks", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_network_by_id_exists(self, client, clean_database, sample_network_data, monkeypatch):
        """Test GET /api/networks/{id} for existing network"""
        from backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        # Create network first
        create_response = client.post("/api/networks", json=sample_network_data)
        network_id = create_response.json()["data"]["network_id"]
        
        # Get network
        response = client.get(f"/api/networks/{network_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["network_id"] == network_id
    
    def test_get_network_by_id_not_exists(self, client):
        """Test GET /api/networks/{id} for non-existent network"""
        response = client.get("/api/networks/99999")
        assert response.status_code == 404
    
    def test_delete_network_success(self, client, clean_database, sample_network_data, monkeypatch):
        """Test DELETE /api/networks/{id}"""
        from backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        # Create network
        create_response = client.post("/api/networks", json=sample_network_data)
        network_id = create_response.json()["data"]["network_id"]
        
        # Delete network
        response = client.delete(f"/api/networks/{network_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_network_not_exists(self, client):
        """Test DELETE /api/networks/{id} for non-existent network"""
        response = client.delete("/api/networks/99999")
        assert response.status_code == 404

@pytest.mark.integration
class TestSearchEndpoint:
    """Test subgraph search endpoint"""
    
    def test_search_networks_valid(self, client, clean_database, sample_glycolysis, monkeypatch):
        """Test POST /api/networks/search with valid data"""
        from backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        # Create network first
        client.post("/api/networks", json=sample_glycolysis)
        
        # Search
        search_data = {
            "node_labels": ["Glucose", "G6P"],
            "adjacency_matrix": [[0, 1], [0, 0]]
        }
        
        response = client.post("/api/networks/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
    
    def test_search_networks_invalid_data(self, client):
        """Test POST /api/networks/search with invalid data"""
        invalid_data = {
            "node_labels": ["A", "B"],
            # Missing adjacency_matrix
        }
        
        response = client.post("/api/networks/search", json=invalid_data)
        assert response.status_code == 422