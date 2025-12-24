from pyTigerGraph import TigerGraphConnection
from typing import List, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TigerGraphManager:
    def __init__(self, host: str, port: int, username: str, password: str, graph_name: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.graph_name = graph_name
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = TigerGraphConnection(
                host=self.host,
                username=self.username,
                password=self.password
            )
            
            # Connect first
            self.conn.connect()
            
            # Set the graph
            self.conn.graphname = self.graph_name
            
            version = self.conn.getVersion()
            logger.info(f"Connected to TigerGraph version: {version}")
        except Exception as e:
            logger.error(f"Failed to connect to TigerGraph: {e}")
            raise

    def clear_graph(self):
        try:
            # Delete all vertices to clear the graph
            result = self.conn.runInterpretedQuery("DELETE FROM K8sNode")
            result = self.conn.runInterpretedQuery("DELETE FROM Pod")
            result = self.conn.runInterpretedQuery("DELETE FROM Service")
            result = self.conn.runInterpretedQuery("DELETE FROM Deployment")
            result = self.conn.runInterpretedQuery("DELETE FROM ConfigMap")
            result = self.conn.runInterpretedQuery("DELETE FROM Secret")
            result = self.conn.runInterpretedQuery("DELETE FROM Namespace")
            result = self.conn.runInterpretedQuery("DELETE FROM RBAC")
            result = self.conn.runInterpretedQuery("DELETE FROM Container")
            logger.info("Graph cleared successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            return None

    def insert_vertices(self, vertex_type: str, vertices: List[Dict[str, Any]]):
        try:
            for vertex in vertices:
                attributes = {k: v for k, v in vertex.items() if k != 'id'}
                # Use upsertVertexData instead of upsertVertex
                result = self.conn.upsertVertexData(
                    vertexType=vertex_type,
                    vertexId=vertex['id'],
                    attributes=attributes
                )
            logger.info(f"Inserted {len(vertices)} {vertex_type} vertices")
            return True
        except Exception as e:
            logger.error(f"Failed to insert {vertex_type} vertices: {e}")
            return False

    def insert_edges(self, edge_type: str, edges: List[Dict[str, Any]]):
        try:
            for edge in edges:
                result = self.conn.upsertEdgeData(
                    sourceVertexType=edge['from_type'],
                    sourceVertexId=edge['from_id'],
                    edgeType=edge_type,
                    targetVertexType=edge['to_type'],
                    targetVertexId=edge['to_id'],
                    attributes=edge.get('attributes', {})
                )
            logger.info(f"Inserted {len(edges)} {edge_type} edges")
            return True
        except Exception as e:
            logger.error(f"Failed to insert {edge_type} edges: {e}")
            return False

    def import_k8s_assets(self, assets: Dict[str, List[Dict[str, Any]]]):
        logger.info("Starting to import K8s assets into TigerGraph")
        
        # Insert vertices
        self.insert_vertices("Namespace", assets.get('namespaces', []))
        self.insert_vertices("K8sNode", assets.get('nodes', []))
        self.insert_vertices("Pod", assets.get('pods', []))
        self.insert_vertices("Service", assets.get('services', []))
        self.insert_vertices("Deployment", assets.get('deployments', []))
        self.insert_vertices("ConfigMap", assets.get('configmaps', []))
        self.insert_vertices("Secret", assets.get('secrets', []))
        self.insert_vertices("RBAC", assets.get('rbac', []))
        
        # Insert containers
        containers = []
        for pod in assets.get('pods', []):
            for container in pod.get('containers', []):
                containers.append(container)
        self.insert_vertices("Container", containers)
        
        # Insert edges
        self._create_relationships(assets)
        
        logger.info("Completed importing K8s assets into TigerGraph")

    def _create_relationships(self, assets: Dict[str, List[Dict[str, Any]]]):
        edges = []
        
        # Pod -> Node (runs_on)
        for pod in assets.get('pods', []):
            if pod.get('node'):
                edges.append({
                    'from_type': 'Pod',
                    'from_id': pod['id'],
                    'to_type': 'K8sNode',
                    'to_id': pod['node']
                })
        
        # Service -> Pod (exposes)
        for service in assets.get('services', []):
            service_pods = self._get_pods_for_service(service, assets.get('pods', []))
            for pod in service_pods:
                edges.append({
                    'from_type': 'Service',
                    'from_id': service['id'],
                    'to_type': 'Pod',
                    'to_id': pod['id']
                })
        
        # Deployment -> Pod (manages)
        for deployment in assets.get('deployments', []):
            deployment_pods = self._get_pods_for_deployment(deployment, assets.get('pods', []))
            for pod in deployment_pods:
                edges.append({
                    'from_type': 'Deployment',
                    'from_id': deployment['id'],
                    'to_type': 'Pod',
                    'to_id': pod['id']
                })
        
        # Namespace -> Pod (contains)
        for pod in assets.get('pods', []):
            if pod.get('namespace'):
                edges.append({
                    'from_type': 'Namespace',
                    'from_id': pod['namespace'],
                    'to_type': 'Pod',
                    'to_id': pod['id']
                })
        
        # Pod -> ConfigMap (uses_config)
        for pod in assets.get('pods', []):
            if pod.get('namespace'):
                configmaps = self._get_configmaps_for_pod(pod, assets.get('configmaps', []))
                for cm in configmaps:
                    edges.append({
                        'from_type': 'Pod',
                        'from_id': pod['id'],
                        'to_type': 'ConfigMap',
                        'to_id': cm['id']
                    })
        
        # Pod -> Secret (uses_secret)
        for pod in assets.get('pods', []):
            if pod.get('namespace'):
                secrets = self._get_secrets_for_pod(pod, assets.get('secrets', []))
                for secret in secrets:
                    edges.append({
                        'from_type': 'Pod',
                        'from_id': pod['id'],
                        'to_type': 'Secret',
                        'to_id': secret['id']
                    })
        
        # Pod -> Container (has_container)
        for pod in assets.get('pods', []):
            for container in pod.get('containers', []):
                edges.append({
                    'from_type': 'Pod',
                    'from_id': pod['id'],
                    'to_type': 'Container',
                    'to_id': container['id']
                })
        
        # Insert all edges
        self.insert_edges("runs_on", edges[:len([e for e in edges if 'runs_on' in e])])
        self.insert_edges("exposes", [e for e in edges if e['from_type'] == 'Service'])
        self.insert_edges("manages", [e for e in edges if e['from_type'] == 'Deployment'])
        self.insert_edges("contains", [e for e in edges if e['from_type'] == 'Namespace'])
        self.insert_edges("uses_config", [e for e in edges if e['to_type'] == 'ConfigMap'])
        self.insert_edges("uses_secret", [e for e in edges if e['to_type'] == 'Secret'])
        self.insert_edges("has_container", [e for e in edges if e['to_type'] == 'Container'])

    def _get_pods_for_service(self, service: Dict, pods: List[Dict]) -> List[Dict]:
        matching_pods = []
        service_labels = service.get('selector', {})
        for pod in pods:
            if pod['namespace'] == service['namespace']:
                pod_labels = pod.get('labels', {})
                if all(pod_labels.get(k) == v for k, v in service_labels.items()):
                    matching_pods.append(pod)
        return matching_pods

    def _get_pods_for_deployment(self, deployment: Dict, pods: List[Dict]) -> List[Dict]:
        matching_pods = []
        for pod in pods:
            if pod['namespace'] == deployment['namespace']:
                if deployment['name'] in pod['name']:
                    matching_pods.append(pod)
        return matching_pods

    def _get_configmaps_for_pod(self, pod: Dict, configmaps: List[Dict]) -> List[Dict]:
        matching_configmaps = []
        for cm in configmaps:
            if cm['namespace'] == pod['namespace']:
                matching_configmaps.append(cm)
        return matching_configmaps

    def _get_secrets_for_pod(self, pod: Dict, secrets: List[Dict]) -> List[Dict]:
        matching_secrets = []
        for secret in secrets:
            if secret['namespace'] == pod['namespace']:
                matching_secrets.append(secret)
        return matching_secrets

    def query_attack_paths(self, source_type: str = None, target_type: str = None, max_depth: int = 5):
        try:
            query = """
            INTERPRET QUERY () FOR GRAPH K8sSecurityGraph {
                // Find potential attack paths
                SetAccum<STRING> @paths;
                
                // If source and target specified, find path between them
                IF @@source_type != "" AND @@target_type != "" THEN
                    @paths = SELECT t FROM Start:s - (ANY:e) - :t
                    WHERE s.type == @@source_type AND t.type == @@target_type
                    ACCUM CASE WHEN e.type == "uses_secret" OR e.type == "has_permission" THEN
                        @paths += s.type + " -> " + t.type + " (RISK: HIGH)"
                    ELSE
                        @paths += s.type + " -> " + t.type + " (RISK: MEDIUM)"
                    END;
                END;
                
                RETURN @paths;
            }
            """
            
            params = {
                "source_type": source_type or "",
                "target_type": target_type or ""
            }
            
            result = self.conn.runInterpretedQuery(query, params=params)
            return result
        except Exception as e:
            logger.error(f"Failed to query attack paths: {e}")
            return None

    def get_graph_statistics(self):
        try:
            # Use getEdgeStatistics and getVertexStatistics instead
            vertex_stats = self.conn.getVertexStatistics()
            edge_stats = self.conn.getEdgeStatistics()
            return {
                'vertexCount': sum(vertex_stats.values()) if vertex_stats else 0,
                'edgeCount': sum(edge_stats.values()) if edge_stats else 0,
                'vertexTypes': vertex_stats,
                'edgeTypes': edge_stats
            }
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return None

    def visual_graph_data(self):
        try:
            # Get all vertices and edges for visualization
            vertices_query = "SELECT v FROM K8sNode:v"
            edges_query = "SELECT e FROM ANY:e"
            
            vertices = self.conn.runInterpretedQuery(vertices_query)
            edges = self.conn.runInterpretedQuery(edges_query)
            
            return {
                "vertices": vertices,
                "edges": edges
            }
        except Exception as e:
            logger.error(f"Failed to get visualization data: {e}")
            return None