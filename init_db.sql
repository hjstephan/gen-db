-- Gen Database Schema

-- Tabelle für biologische Netzwerke
CREATE TABLE IF NOT EXISTS biological_networks (
    network_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    network_type VARCHAR(50), -- 'metabolic', 'protein', 'gene_regulation'
    organism VARCHAR(100),
    description TEXT,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabelle für Adjacency Matrices mit Signaturen
CREATE TABLE IF NOT EXISTS network_matrices (
    network_id INTEGER PRIMARY KEY REFERENCES biological_networks(network_id) ON DELETE CASCADE,
    node_labels TEXT[] NOT NULL, -- Array der Knotennamen
    adjacency_matrix INTEGER[][] NOT NULL, -- 2D-Array
    signature_array BIGINT[] NOT NULL, -- Vorberechnete Signaturen
    signature_hash VARCHAR(64) -- SHA-256 Hash für schnellen Lookup
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_networks_type ON biological_networks(network_type);
CREATE INDEX IF NOT EXISTS idx_networks_organism ON biological_networks(organism);
CREATE INDEX IF NOT EXISTS idx_networks_node_count ON biological_networks(node_count);
CREATE INDEX IF NOT EXISTS idx_matrices_hash ON network_matrices(signature_hash);

-- Beispiel-Daten einfügen
INSERT INTO biological_networks (name, network_type, organism, description, node_count, edge_count)
VALUES 
    ('Glycolysis', 'metabolic', 'Homo sapiens', 'Glucose breakdown pathway', 7, 6),
    ('DNA_Damage_Response', 'protein', 'Homo sapiens', 'p53-centered protein interactions', 5, 6)
ON CONFLICT DO NOTHING;

-- Beispiel Glykolyse-Matrix
INSERT INTO network_matrices (network_id, node_labels, adjacency_matrix, signature_array, signature_hash)
VALUES (
    1,
    ARRAY['Glucose', 'G6P', 'F6P', 'FBP', 'DHAP', 'G3P', 'Pyruvate'],
    ARRAY[
        ARRAY[0,1,0,0,0,0,0],
        ARRAY[0,0,1,0,0,0,0],
        ARRAY[0,0,0,1,0,0,0],
        ARRAY[0,0,0,0,1,1,0],
        ARRAY[0,0,0,0,0,1,0],
        ARRAY[0,0,0,0,0,0,1],
        ARRAY[0,0,0,0,0,0,0]
    ]::INTEGER[][],
    ARRAY[1, 130, 260, 392, 528, 672, 768]::BIGINT[],
    'abc123def456'
)
ON CONFLICT DO NOTHING;

-- Beispiel DNA-Damage-Response-Matrix
INSERT INTO network_matrices (network_id, node_labels, adjacency_matrix, signature_array, signature_hash)
VALUES (
    2,
    ARRAY['p53', 'MDM2', 'ATM', 'DNA-PK', 'CHK2'],
    ARRAY[
        ARRAY[0,1,0,0,0],
        ARRAY[1,0,0,0,0],
        ARRAY[1,0,0,0,1],
        ARRAY[0,0,1,0,0],
        ARRAY[1,0,0,0,0]
    ]::INTEGER[][],
    ARRAY[10, 33, 68, 96, 144]::BIGINT[],
    'xyz789abc012'
)
ON CONFLICT DO NOTHING;
