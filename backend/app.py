from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import crud

app = FastAPI(title="Gen - Biological Network Analysis API")

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class NetworkCreate(BaseModel):
    name: str
    network_type: str
    organism: str
    description: Optional[str] = ""
    node_labels: List[str]
    adjacency_matrix: List[List[int]]

class NetworkSearch(BaseModel):
    node_labels: List[str]
    adjacency_matrix: List[List[int]]

# API Endpoints
@app.get("/")
async def root():
    """Serve frontend"""
    return FileResponse("../frontend/index.html")

@app.get("/api/networks")
async def get_networks():
    """Hole alle Netzwerke"""
    try:
        networks = crud.get_all_networks()
        return {"success": True, "data": networks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/networks/{network_id}")
async def get_network(network_id: int):
    """Hole spezifisches Netzwerk"""
    try:
        network = crud.get_network_by_id(network_id)
        if not network:
            raise HTTPException(status_code=404, detail="Network not found")
        return {"success": True, "data": network}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/networks")
async def create_network(network: NetworkCreate):
    """Erstelle neues Netzwerk"""
    try:
        result = crud.create_network(
            name=network.name,
            network_type=network.network_type,
            organism=network.organism,
            description=network.description or "",
            node_labels=network.node_labels,
            adjacency_matrix=network.adjacency_matrix
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/networks/search")
async def search_networks(search: NetworkSearch):
    """Suche nach Subgraph-Matches"""
    try:
        matches = crud.search_subgraph(
            query_matrix=search.adjacency_matrix,
            query_labels=search.node_labels
        )
        return {"success": True, "data": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/networks/{network_id}")
async def delete_network(network_id: int):
    """Lösche Netzwerk"""
    try:
        deleted = crud.delete_network(network_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Network not found")
        return {"success": True, "message": "Network deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
