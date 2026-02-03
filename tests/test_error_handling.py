"""
Tests for error handling and edge cases
"""
import pytest
from fastapi.testclient import TestClient
from src.backend.app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across the application"""
    
    def test_invalid_endpoint(self, client):
        """Test 404 for invalid endpoint"""
        response = client.get("/api/invalid_endpoint")
        assert response.status_code == 404
    
    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/networks",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_invalid_network_id_type(self, client):
        """Test invalid network ID type"""
        response = client.get("/api/networks/abc")
        assert response.status_code == 422
    
    def test_negative_network_id(self, client, clean_database, monkeypatch):
        """Test negative network ID"""
        from src.backend import crud
        monkeypatch.setattr(crud, 'get_db_connection', lambda: clean_database)
        
        response = client.get("/api/networks/-1")
        # Should either reject or return 404
        assert response.status_code in [404, 422]
    
    def test_matrix_size_mismatch(self, client):
        """Test matrix size doesn't match node count"""
        invalid_data = {
            "name": "Invalid",
            "network_type": "test",
            "organism": "Test",
            "description": "",
            "node_labels": ["A", "B"],  # 2 nodes
            "adjacency_matrix": [[0, 1, 0], [0, 0, 1], [0, 0, 0]]  # 3x3 matrix
        }
        response = client.post("/api/networks", json=invalid_data)
        # Should fail - either at validation or execution
        assert response.status_code in [422, 500]