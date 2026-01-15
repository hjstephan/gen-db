import hashlib
import numpy as np
from typing import List, Dict, Optional
from backend.database import get_db_connection, get_db_cursor

# Import Subgraph Algorithmus aus dem hjstephan/subgraph Package
try:
    from subgraph import Subgraph
    SUBGRAPH_AVAILABLE = True
except ImportError:
    print("WARNING: Subgraph package not available. Install with: pip install git+https://github.com/hjstephan/subgraph.git")
    SUBGRAPH_AVAILABLE = False

# Initialisiere den Subgraph Algorithmus
if SUBGRAPH_AVAILABLE:
    comparator = Subgraph()

def compute_signatures(matrix: np.ndarray) -> List[int]:
    """Berechnet Spalten-Signaturen für Adjacency Matrix (wie im Subgraph Algorithmus)"""
    n = matrix.shape[0]
    signatures = []
    for col in range(n):
        row_sig = sum(2**i for i in range(n) if matrix[i, col] == 1)
        col_weight = col * (2**n)
        signatures.append(row_sig + col_weight)
    return signatures

def compute_signature_hash(signatures: List[int]) -> str:
    """Berechnet SHA-256 Hash der Signatur-Sequenz"""
    sig_str = str(signatures).encode()
    return hashlib.sha256(sig_str).hexdigest()

def create_network(name: str, network_type: str, organism: str, 
                   description: str, node_labels: List[str], 
                   adjacency_matrix: List[List[int]]) -> Dict:
    """Erstellt neues biologisches Netzwerk"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        # Berechne Metriken
        matrix_np = np.array(adjacency_matrix, dtype=int)
        node_count = len(node_labels)
        edge_count = int(np.sum(matrix_np))
        
        # Berechne Signaturen
        signatures = compute_signatures(matrix_np)
        sig_hash = compute_signature_hash(signatures)
        
        # Erstelle Netzwerk-Eintrag
        cursor.execute("""
            INSERT INTO biological_networks 
            (name, network_type, organism, description, node_count, edge_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING network_id
        """, (name, network_type, organism, description, node_count, edge_count))
        
        network_id = cursor.fetchone()['network_id']
        
        # Speichere Matrix und Signaturen
        cursor.execute("""
            INSERT INTO network_matrices 
            (network_id, node_labels, adjacency_matrix, signature_array, signature_hash)
            VALUES (%s, %s, %s, %s, %s)
        """, (network_id, node_labels, adjacency_matrix, signatures, sig_hash))
        
        return {
            'network_id': network_id,
            'name': name,
            'node_count': node_count,
            'edge_count': edge_count,
            'signature_hash': sig_hash
        }

def get_all_networks() -> List[Dict]:
    """Holt alle Netzwerke aus der DB"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        cursor.execute("""
            SELECT bn.*, nm.node_labels, nm.signature_hash
            FROM biological_networks bn
            LEFT JOIN network_matrices nm ON bn.network_id = nm.network_id
            ORDER BY bn.created_at DESC
        """)
        return cursor.fetchall()

def get_network_by_id(network_id: int) -> Optional[Dict]:
    """Holt spezifisches Netzwerk mit Matrix"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        cursor.execute("""
            SELECT bn.*, nm.node_labels, nm.adjacency_matrix, nm.signature_array
            FROM biological_networks bn
            JOIN network_matrices nm ON bn.network_id = nm.network_id
            WHERE bn.network_id = %s
        """, (network_id,))
        return cursor.fetchone()

def search_subgraph(query_matrix: List[List[int]], 
                    query_labels: List[str]) -> List[Dict]:
    """
    Sucht in DB nach Netzwerken die query_matrix enthalten könnten.
    Nutzt den echten SubgraphComparator aus hjstephan/subgraph!
    """
    if not SUBGRAPH_AVAILABLE:
        return [{
            'error': 'Subgraph package not installed',
            'message': 'Install with: pip install git+https://github.com/hjstephan/subgraph.git'
        }]
    
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        
        query_np = np.array(query_matrix, dtype=int)
        query_node_count = query_np.shape[0]
        query_edge_count = int(np.sum(query_np))
        
        # Pre-filtering: Nur Netzwerke >= Query-Größe
        cursor.execute("""
            SELECT bn.network_id, bn.name, bn.network_type, bn.organism,
                   bn.node_count, bn.edge_count,
                   nm.node_labels, nm.adjacency_matrix
            FROM biological_networks bn
            JOIN network_matrices nm ON bn.network_id = nm.network_id
            WHERE bn.node_count >= %s AND bn.edge_count >= %s
            ORDER BY bn.node_count ASC
        """, (query_node_count, query_edge_count))
        
        candidates = cursor.fetchall()
        
        print(f"🔍 Subgraph-Suche: {len(candidates)} Kandidaten für Query (n={query_node_count}, e={query_edge_count})")
        
        # Verwende Subgraph Algorithmus
        matches = []
        for candidate in candidates:
            candidate_matrix = np.array(candidate['adjacency_matrix'], dtype=int)
            
            # Vergleiche mit Subgraph Algorithmus
            # compare_graphs gibt Tuple zurück: (decision, matrix_A, matrix_B)
            result = comparator.compare_graphs(query_np, candidate_matrix)
            
            # Extrahiere Decision aus Tuple
            decision = result[0] if isinstance(result, tuple) else result
            
            # Tuple (Entscheidung, behaltene Matrix)
            # - ("keep_B", B) wenn B die Matrix A enthält (G' hat mehr Info)
            # - ("keep_A", A) wenn A die Matrix B enthält (G hat mehr Info)
            # - ("keep_both", None) wenn keiner den anderen enthält
            # - ("equal", A) wenn beide identisch sind
            
            if decision in ['keep_B', 'keep_A', 'equal_keep_A', 'equal_keep_B']:
                match_type = 'exact' if decision in ['equal_keep_A', 'equal_keep_B'] else 'subgraph'
                matches.append({
                    'network_id': candidate['network_id'],
                    'name': candidate['name'],
                    'network_type': candidate['network_type'],
                    'organism': candidate['organism'],
                    'node_labels': candidate['node_labels'],
                    'node_count': candidate['node_count'],
                    'edge_count': candidate['edge_count'],
                    'match_type': match_type,
                    'subgraph_result': decision
                })
                print(f"  ✅ Match: {candidate['name']} ({decision})")
            else:
                print(f"  ❌ No match: {candidate['name']} ({decision})")
        
        print(f"✨ Gefunden: {len(matches)} Matches")
        return matches

def delete_network(network_id: int) -> bool:
    """Löscht Netzwerk aus DB (CASCADE löscht auch Matrix)"""
    with get_db_connection() as conn:
        cursor = get_db_cursor(conn)
        cursor.execute("""
            DELETE FROM biological_networks WHERE network_id = %s
            RETURNING network_id
        """, (network_id,))
        return cursor.fetchone() is not None
