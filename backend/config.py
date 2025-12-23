from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # TigerGraph Configuration
    tigergraph_host: str = "localhost"
    tigergraph_port: int = 9000
    tigergraph_username: str = "tigergraph"
    tigergraph_password: str = "tigergraph"
    tigergraph_graph_name: str = "K8sSecurityGraph"
    
    # K8s Configuration
    k8s_config_file: str = None
    k8s_in_cluster: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()