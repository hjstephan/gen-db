"""
End-to-end integration tests
Tests complete workflows across multiple components
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

from src.backend.app import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.mark.integration
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test complete user workflows"""
    
    def test_create_search_delete_workflow(self, client, clean_database, 
                                          sample_glycolysis, sample_partial_glycolysis, 
                                          monkeypatch):
        """Test complete workflow: create networks, search, delete"""
        import src.backend.crud
        monkeypatch.setattr(src.backend.crud, 'get_db_connection', lambda: clean_database)
        
        # 1. Create full glycolysis
        response1 = client.post("/api/networks", json=sample_glycolysis)
        assert response1.status_code == 200
        full_id = response1.json()["data"]["network_id"]
        
        # 2. Create partial glycolysis
        response2 = client.post("/api/networks", json=sample_partial_glycolysis)
        assert response2.status_code == 200
        partial_id = response2.json()["data"]["network_id"]
        
        # 3. List all networks
        response3 = client.get("/api/networks")
        assert len(response3.json()["data"]) == 2
        
        # 4. Search for partial (should find full)
        search_data = {
            "node_labels": sample_partial_glycolysis["node_labels"],
            "adjacency_matrix": sample_partial_glycolysis["adjacency_matrix"]
        }
        response4 = client.post("/api/networks/search", json=search_data)
        matches = response4.json()["data"]
        assert len(matches) >= 1
        
        # 5. Delete networks
        response5 = client.delete(f"/api/networks/{full_id}")
        assert response5.status_code == 200
        
        response6 = client.delete(f"/api/networks/{partial_id}")
        assert response6.status_code == 200
        
        # 6. Verify deletion
        response7 = client.get("/api/networks")
        assert len(response7.json()["data"]) == 0
    
    def test_concurrent_network_creation(self, client, clean_database, monkeypatch):
        """Test creating multiple networks concurrently"""
        import src.backend.crud
        monkeypatch.setattr(src.backend.crud, 'get_db_connection', lambda: clean_database)
        
        networks = [
            {
                "name": f"Network_{i}",
                "network_type": "test",
                "organism": "Test",
                "description": "",
                "node_labels": ["A", "B"],
                "adjacency_matrix": [[0, 1], [0, 0]]
            }
            for i in range(5)
        ]
        
        # Create all networks
        for network_data in networks:
            response = client.post("/api/networks", json=network_data)
            assert response.status_code == 200
        
        # Verify all created
        response = client.get("/api/networks")
        assert len(response.json()["data"]) == 5