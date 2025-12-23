from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class K8sAssetDiscovery:
    def __init__(self, config_file: str = None, in_cluster: bool = False):
        try:
            if in_cluster:
                config.load_incluster_config()
            elif config_file:
                config.load_kube_config(config_file=config_file)
            else:
                config.load_kube_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            logger.info("Kubernetes client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise

    def discover_namespaces(self) -> List[Dict[str, Any]]:
        try:
            namespaces = self.v1.list_namespace()
            return [{
                "id": ns.metadata.name,
                "name": ns.metadata.name,
                "status": ns.status.phase,
                "creation_time": ns.metadata.creation_timestamp.isoformat() if ns.metadata.creation_timestamp else None
            } for ns in namespaces.items]
        except ApiException as e:
            logger.error(f"Error fetching namespaces: {e}")
            return []

    def discover_nodes(self) -> List[Dict[str, Any]]:
        try:
            nodes = self.v1.list_node()
            node_list = []
            for node in nodes.items:
                labels = dict(node.metadata.labels) if node.metadata.labels else {}
                node_list.append({
                    "id": node.metadata.name,
                    "name": node.metadata.name,
                    "labels": str(labels),
                    "status": node.status.conditions[-1].type if node.status.conditions else "Unknown",
                    "creation_time": node.metadata.creation_timestamp.isoformat() if node.metadata.creation_timestamp else None
                })
            return node_list
        except ApiException as e:
            logger.error(f"Error fetching nodes: {e}")
            return []

    def discover_pods(self) -> List[Dict[str, Any]]:
        try:
            pods = self.v1.list_pod_for_all_namespaces()
            pod_list = []
            for pod in pods.items:
                containers = []
                if pod.spec.containers:
                    for container in pod.spec.containers:
                        ports = [str(port.container_port) for port in (container.ports or [])]
                        containers.append({
                            "id": f"{pod.metadata.name}-{container.name}",
                            "name": container.name,
                            "image": container.image,
                            "ports": ",".join(ports) if ports else ""
                        })
                
                pod_list.append({
                    "id": pod.metadata.uid,
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "creation_time": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None,
                    "containers": containers
                })
            return pod_list
        except ApiException as e:
            logger.error(f"Error fetching pods: {e}")
            return []

    def discover_services(self) -> List[Dict[str, Any]]:
        try:
            services = self.v1.list_service_for_all_namespaces()
            return [{
                "id": svc.metadata.uid,
                "name": svc.metadata.name,
                "namespace": svc.metadata.namespace,
                "type": svc.spec.type,
                "cluster_ip": svc.spec.cluster_ip,
                "creation_time": svc.metadata.creation_timestamp.isoformat() if svc.metadata.creation_timestamp else None
            } for svc in services.items]
        except ApiException as e:
            logger.error(f"Error fetching services: {e}")
            return []

    def discover_deployments(self) -> List[Dict[str, Any]]:
        try:
            deployments = self.apps_v1.list_deployment_for_all_namespaces()
            return [{
                "id": deploy.metadata.uid,
                "name": deploy.metadata.name,
                "namespace": deploy.metadata.namespace,
                "replicas": deploy.spec.replicas,
                "creation_time": deploy.metadata.creation_timestamp.isoformat() if deploy.metadata.creation_timestamp else None
            } for deploy in deployments.items]
        except ApiException as e:
            logger.error(f"Error fetching deployments: {e}")
            return []

    def discover_configmaps(self) -> List[Dict[str, Any]]:
        try:
            configmaps = self.v1.list_config_map_for_all_namespaces()
            return [{
                "id": cm.metadata.uid,
                "name": cm.metadata.name,
                "namespace": cm.metadata.namespace,
                "creation_time": cm.metadata.creation_timestamp.isoformat() if cm.metadata.creation_timestamp else None
            } for cm in configmaps.items]
        except ApiException as e:
            logger.error(f"Error fetching configmaps: {e}")
            return []

    def discover_secrets(self) -> List[Dict[str, Any]]:
        try:
            secrets = self.v1.list_secret_for_all_namespaces()
            return [{
                "id": sec.metadata.uid,
                "name": sec.metadata.name,
                "namespace": sec.metadata.namespace,
                "type": sec.type,
                "creation_time": sec.metadata.creation_timestamp.isoformat() if sec.metadata.creation_timestamp else None
            } for sec in secrets.items]
        except ApiException as e:
            logger.error(f"Error fetching secrets: {e}")
            return []

    def discover_rbac(self) -> List[Dict[str, Any]]:
        rbac_list = []
        try:
            roles = self.rbac_v1.list_role_for_all_namespaces()
            for role in roles.items:
                rbac_list.append({
                    "id": role.metadata.uid,
                    "name": role.metadata.name,
                    "namespace": role.metadata.namespace,
                    "type": "Role",
                    "rules": str([rule.to_dict() for rule in role.rules]) if role.rules else "",
                    "creation_time": role.metadata.creation_timestamp.isoformat() if role.metadata.creation_timestamp else None
                })
        except ApiException as e:
            logger.error(f"Error fetching roles: {e}")
        
        try:
            cluster_roles = self.rbac_v1.list_cluster_role()
            for cr in cluster_roles.items:
                rbac_list.append({
                    "id": cr.metadata.uid,
                    "name": cr.metadata.name,
                    "namespace": "cluster",
                    "type": "ClusterRole",
                    "rules": str([rule.to_dict() for rule in cr.rules]) if cr.rules else "",
                    "creation_time": cr.metadata.creation_timestamp.isoformat() if cr.metadata.creation_timestamp else None
                })
        except ApiException as e:
            logger.error(f"Error fetching cluster roles: {e}")
        
        return rbac_list

    def discover_all_assets(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "namespaces": self.discover_namespaces(),
            "nodes": self.discover_nodes(),
            "pods": self.discover_pods(),
            "services": self.discover_services(),
            "deployments": self.discover_deployments(),
            "configmaps": self.discover_configmaps(),
            "secrets": self.discover_secrets(),
            "rbac": self.discover_rbac()
        }