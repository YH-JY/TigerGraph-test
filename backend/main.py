from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from config import settings
from k8s_discovery import K8sAssetDiscovery
from tigergraph_manager import TigerGraphManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="K8s Native Security Platform",
    description="Platform for discovering K8s assets and analyzing attack paths",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
k8s_discovery = None
tg_manager = None

class DiscoveryResponse(BaseModel):
    status: str
    timestamp: datetime
    assets: Dict[str, List[Dict[str, Any]]]

class ImportResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime

class QueryRequest(BaseModel):
    source_type: Optional[str] = None
    target_type: Optional[str] = None
    max_depth: Optional[int] = 5

class QueryResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    global k8s_discovery, tg_manager
    
    try:
        k8s_discovery = K8sAssetDiscovery(
            config_file=settings.k8s_config_file,
            in_cluster=settings.k8s_in_cluster
        )
        logger.info("K8s discovery initialized")
    except Exception as e:
        logger.error(f"Failed to initialize K8s discovery: {e}")
    
    try:
        tg_manager = TigerGraphManager(
            host=settings.tigergraph_host,
            port=settings.tigergraph_port,
            username=settings.tigergraph_username,
            password=settings.tigergraph_password,
            graph_name=settings.tigergraph_graph_name
        )
        logger.info("TigerGraph manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize TigerGraph manager: {e}")

@app.get("/")
async def root():
    return {"message": "K8s Native Security Platform API"}

@app.get("/health")
async def health_check():
    status = {"status": "healthy", "timestamp": datetime.now()}
    
    # Check K8s connection
    try:
        if k8s_discovery:
            nodes = k8s_discovery.discover_nodes()
            status["k8s"] = "connected" if nodes else "no_data"
        else:
            status["k8s"] = "not_initialized"
    except Exception as e:
        status["k8s"] = f"error: {str(e)}"
    
    # Check TigerGraph connection
    try:
        if tg_manager:
            stats = tg_manager.get_graph_statistics()
            status["tigergraph"] = "connected" if stats else "no_data"
        else:
            status["tigergraph"] = "not_initialized"
    except Exception as e:
        status["tigergraph"] = f"error: {str(e)}"
    
    return status

@app.post("/api/discover", response_model=DiscoveryResponse)
async def discover_assets():
    """Discover K8s cluster assets"""
    if not k8s_discovery:
        raise HTTPException(status_code=500, detail="K8s discovery not initialized")
    
    try:
        assets = k8s_discovery.discover_all_assets()
        return DiscoveryResponse(
            status="success",
            timestamp=datetime.now(),
            assets=assets
        )
    except Exception as e:
        logger.error(f"Error during asset discovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import", response_model=ImportResponse)
async def import_to_tigergraph(background_tasks: BackgroundTasks):
    """Import discovered assets to TigerGraph"""
    if not k8s_discovery or not tg_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    
    async def import_task():
        try:
            # Discover assets
            assets = k8s_discovery.discover_all_assets()
            
            # Clear existing data
            tg_manager.clear_graph()
            
            # Import to TigerGraph
            tg_manager.import_k8s_assets(assets)
            
            logger.info("Assets imported successfully to TigerGraph")
        except Exception as e:
            logger.error(f"Error during import: {e}")
    
    background_tasks.add_task(import_task)
    
    return ImportResponse(
        status="accepted",
        message="Import job started in background",
        timestamp=datetime.now()
    )

@app.post("/api/query/attack-paths", response_model=QueryResponse)
async def query_attack_paths(request: QueryRequest):
    """Query potential attack paths in the graph"""
    if not tg_manager:
        raise HTTPException(status_code=500, detail="TigerGraph manager not initialized")
    
    try:
        result = tg_manager.query_attack_paths(
            source_type=request.source_type,
            target_type=request.target_type,
            max_depth=request.max_depth
        )
        
        return QueryResponse(
            status="success",
            data=result
        )
    except Exception as e:
        logger.error(f"Error querying attack paths: {e}")
        return QueryResponse(
            status="error",
            error=str(e)
        )

@app.get("/api/visualize/graph", response_model=QueryResponse)
async def get_graph_visualization():
    """Get graph data for visualization"""
    if not tg_manager:
        raise HTTPException(status_code=500, detail="TigerGraph manager not initialized")
    
    try:
        data = tg_manager.visual_graph_data()
        return QueryResponse(
            status="success",
            data=data
        )
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        return QueryResponse(
            status="error",
            error=str(e)
        )

@app.get("/api/statistics", response_model=QueryResponse)
async def get_statistics():
    """Get graph statistics"""
    if not tg_manager:
        raise HTTPException(status_code=500, detail="TigerGraph manager not initialized")
    
    try:
        stats = tg_manager.get_graph_statistics()
        return QueryResponse(
            status="success",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return QueryResponse(
            status="error",
            error=str(e)
        )

@app.get("/api/assets/types")
async def get_asset_types():
    """Get available asset types"""
    return {
        "types": [
            {"name": "K8sNode", "label": "Kubernetes Node"},
            {"name": "Pod", "label": "Pod"},
            {"name": "Service", "label": "Service"},
            {"name": "Deployment", "label": "Deployment"},
            {"name": "ConfigMap", "label": "ConfigMap"},
            {"name": "Secret", "label": "Secret"},
            {"name": "Namespace", "label": "Namespace"},
            {"name": "RBAC", "label": "RBAC"},
            {"name": "Container", "label": "Container"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )