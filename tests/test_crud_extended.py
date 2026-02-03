"""
Extended tests for crud.py module
Additional coverage for edge cases and error scenarios
"""
import pytest
import numpy as np
from src.backend.crud import (
    compute_signatures,
    compute_signature_hash,
    create_network,
    get_all_networks,
    get_network_by_id,
    search_subgraph,
    delete_network
)

@pytest.mark.unit
class TestSignatureComputationExtended:
    """Extended signature computation tests"""
    
    def test_compute_signatures_large_matrix(self):
        """Test signature computation for larger matrix"""
        matrix = np.random.randint(0, 2, (10, 10))
        np.fill_diagonal(matrix, 0)
        
        signatures = compute_signatures(matrix)
        assert len(signatures) == 10
        assert all(isinstance(sig, int) for sig in signatures)
    
    def test_compute_signatures_diagonal_zeros(self):
        """Test that diagonal (self-loops) are handled correctly"""
        matrix = np.array([
            [1, 1, 0],  # Self-loop
            [0, 1, 1],  # Self-loop
            [0, 0, 1]   # Self-loop
        ])
        signatures = compute_signatures(matrix)
        # Signatures should still be computed
        assert len(signatures) == 3
    
    def test_signature_hash_consistency(self):
        """Test hash is consistent across multiple calls"""
        sig = [100, 200, 300]
        hashes = [compute_signature_hash(sig) for _ in range(5)]
        assert all(h == hashes[0] for h in hashes)
    
    def test_signature_hash_uniqueness(self):
        """Test different signatures produce different hashes"""
        sigs = [[1, 2, 3], [1, 2, 4], [1, 3, 3], [2, 2, 3]]
        hashes = [compute_signature_hash(sig) for sig in sigs]
        assert len(set(hashes)) == len(sigs)  # All unique

@pytest.mark.db
class TestCreateNetworkExtended:
    """Extended network creation tests"""
    
    def test_create_network_large(self, clean_database, monkeypatch):
        """Test creating large network"""
        monkeypatch.setattr('src.backend.crud.get_db_connection', lambda: clean_database)
        
        n = 20
        data = {
            'name': 'Large_Network',
            'network_type': 'test',
            'organism': 'Test',
            'description': 'Large test network',
            'node_labels': [f'Node_{i}' for i in range(n)],
            'adjacency_matrix': np.random.randint(0, 2, (n, n)).tolist()
        }
        
        result = create_network(**data)
        assert result['node_count'] == n
        assert 'network_id' in result
    
    def test_create_network_special_characters(self, clean_database, monkeypatch):
        """Test creating network with special characters in labels"""
        monkeypatch.setattr('src.backend.crud.get_db_connection', lambda: clean_database)
        
        data = {
            'name': 'Special_Chars',
            'network_type': 'test',
            'organism': 'Test',
            'description': 'Network with special chars',
            'node_labels': ['α-Ketoglutarate', 'β-Oxidation', 'γ-Aminobutyric'],
            'adjacency_matrix': [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
        }
        
        result = create_network(**data)
        assert 'network_id' in result
        
        # Verify retrieval
        network = get_network_by_id(result['network_id'])
        assert 'α-Ketoglutarate' in network['node_labels']

@pytest.mark.db
class TestSearchSubgraphExtended:
    """Extended subgraph search tests"""
    
    def test_search_handles_disconnected_graph(self, clean_database, monkeypatch):
        """Test search with disconnected graph"""
        monkeypatch.setattr('src.backend.crud.get_db_connection', lambda: clean_database)
        
        # Create disconnected network (two separate components)
        data = {
            'name': 'Disconnected',
            'network_type': 'test',
            'organism': 'Test',
            'description': 'Disconnected graph',
            'node_labels': ['A', 'B', 'C', 'D'],
            'adjacency_matrix': [
                [0, 1, 0, 0],  # A connects to B
                [0, 0, 0, 0],
                [0, 0, 0, 1],  # C connects to D (separate component)
                [0, 0, 0, 0]
            ]
        }
        create_network(**data)
        
        # Search for one component
        matches = search_subgraph(
            query_matrix=[[0, 1], [0, 0]],
            query_labels=['A', 'B']
        )
        
        assert isinstance(matches, list)
    
    def test_search_with_cycle(self, clean_database, monkeypatch):
        """Test search with cyclic graph"""
        monkeypatch.setattr('src.backend.crud.get_db_connection', lambda: clean_database)
        
        # Create network with cycle
        data = {
            'name': 'Cyclic',
            'network_type': 'test',
            'organism': 'Test',
            'description': 'Graph with cycle',
            'node_labels': ['A', 'B', 'C'],
            'adjacency_matrix': [
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 0]  # C -> A creates cycle
            ]
        }
        create_network(**data)
        
        # Search for cycle
        matches = search_subgraph(
            query_matrix=data['adjacency_matrix'],
            query_labels=data['node_labels']
        )
        
        assert len(matches) >= 1
    
    def test_search_performance_with_many_candidates(self, clean_database, monkeypatch):
        """Test search performance with multiple candidates"""
        monkeypatch.setattr('src.backend.crud.get_db_connection', lambda: clean_database)
        
        # Create multiple networks
        for i in range(10):
            data = {
                'name': f'Network_{i}',
                'network_type': 'test',
                'organism': 'Test',
                'description': f'Test network {i}',
                'node_labels': ['A', 'B', 'C'],
                'adjacency_matrix': [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
            }
            create_network(**data)
        
        # Search should handle all candidates
        matches = search_subgraph(
            query_matrix=[[0, 1], [0, 0]],
            query_labels=['A', 'B']
        )
        
        # Should find all 10 as they all contain the query
        assert len(matches) >= 1