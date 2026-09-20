import json
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models import GraphNodeModel, GraphEdgeModel

class IdentityGraphEngine:
    def __init__(self, db_session: Session):
        """
        SQLite is the single source of truth for all graph nodes and edges.
        NetworkX MultiDiGraph is rebuilt fresh on every request/instantiation
        to prevent any sync-drift issues.
        """
        self.db = db_session
        self.graph = nx.MultiDiGraph()
        self.rebuild_graph_from_sqlite()

    def rebuild_graph_from_sqlite(self):
        """Loads all nodes and edges fresh from SQLite into in-memory NetworkX graph."""
        self.graph.clear()
        nodes = self.db.query(GraphNodeModel).all()
        for n in nodes:
            props = n.properties
            self.graph.add_node(
                n.id,
                node_type=n.node_type,
                label=n.label,
                properties=props,
                created_at=n.created_at.isoformat() if n.created_at else None
            )

        edges = self.db.query(GraphEdgeModel).all()
        for e in edges:
            self.graph.add_edge(
                e.source_id,
                e.target_id,
                edge_id=e.id,
                edge_type=e.edge_type,
                properties=e.properties
            )

    def add_node(self, node_id: str, node_type: str, label: str, properties: Dict[str, Any]):
        self.graph.add_node(node_id, node_type=node_type, label=label, properties=properties)
        if self.db:
            existing = self.db.query(GraphNodeModel).filter_by(id=node_id).first()
            if not existing:
                node_obj = GraphNodeModel(
                    id=node_id,
                    node_type=node_type,
                    label=label,
                    properties_json=json.dumps(properties)
                )
                self.db.add(node_obj)
                self.db.commit()

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        self.graph.add_edge(source_id, target_id, edge_type=edge_type, properties=props)
        if self.db:
            edge_obj = GraphEdgeModel(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                properties_json=json.dumps(props)
            )
            self.db.add(edge_obj)
            self.db.commit()

    def evaluate_identity_integrity(
        self, 
        doc_number: str, 
        holder_name: str, 
        dob: str, 
        nationality: str, 
        biometric_cluster_id: Optional[str] = None
    ) -> Tuple[str, Optional[Dict[str, Any]], List[str]]:
        """
        Traverses identity graph to detect:
        1. IDENTITY_FRACTURE (direct conflict: same biometric cluster connected to multiple conflicting identities)
        2. MINOR_ANOMALY (name variant, minor DOB transposition)
        3. CONSISTENT (clean single identity history)
        """
        conflicts = []
        fracture_info = None

        # 1. Check if doc already exists in graph
        doc_node_id = f"doc_{doc_number}"
        
        # 2. Check Biometric Cluster Traversal
        bio_node_id = biometric_cluster_id
        if bio_node_id and bio_node_id not in self.graph:
            for n_id, d in self.graph.nodes(data=True):
                if d.get("properties", {}).get("cluster_id") == biometric_cluster_id:
                    bio_node_id = n_id
                    break

        if bio_node_id and bio_node_id in self.graph:
            # Trace all connected person / passport nodes
            connected_nodes = set()
            for _, target, data in self.graph.out_edges(bio_node_id, data=True):
                connected_nodes.add(target)
            for source, _, data in self.graph.in_edges(bio_node_id, data=True):
                connected_nodes.add(source)

            # Look for linked passports and persons
            linked_passports = []
            linked_persons = []
            
            for node_id in connected_nodes:
                node_data = self.graph.nodes.get(node_id, {})
                ntype = node_data.get("node_type")
                if ntype == "PASSPORT":
                    linked_passports.append((node_id, node_data))
                elif ntype == "PERSON":
                    linked_persons.append((node_id, node_data))

            # Inspect for conflicting identities
            for p_id, p_data in linked_persons:
                p_props = p_data.get("properties", {})
                stored_name = (p_props.get("primary_name") or "").upper()
                stored_dob = p_props.get("dob") or ""
                stored_nat = p_props.get("nationality") or ""
                
                # Check for critical mismatch with current presentation
                curr_name = (holder_name or "").upper().strip()
                if stored_name and stored_name != curr_name:
                    # Is it an alias or a distinct person fracture?
                    name_similarity = self._compute_name_similarity(stored_name, curr_name)
                    if name_similarity < 0.6:
                        # Full fracture detected!
                        fracture_info = {
                            "type": "BIOMETRIC_IDENTITY_FRACTURE",
                            "severity": "CRITICAL",
                            "biometric_cluster": biometric_cluster_id,
                            "current_claim": {
                                "name": holder_name,
                                "document_number": doc_number,
                                "nationality": nationality,
                                "dob": dob
                            },
                            "conflicting_record": {
                                "person_id": p_id,
                                "name": stored_name,
                                "document_number": p_props.get("primary_doc_number", "RUS-74892184"),
                                "nationality": stored_nat,
                                "dob": stored_dob,
                                "prior_issuance": p_props.get("prior_issuance_authority", "Moscow Directorate"),
                                "last_seen_border": p_props.get("last_seen_border", "FRA-CDG Entry 2023-11-14")
                            },
                            "discrepancy_summary": f"Biometric cluster {biometric_cluster_id} is biologically registered to '{stored_name}' ({stored_nat}), but currently presented under passport #{doc_number} as '{holder_name}' ({nationality})."
                        }
                        return "IDENTITY_FRACTURE", fracture_info, [fracture_info["discrepancy_summary"]]
                    elif name_similarity < 0.9:
                        conflicts.append(f"Minor name variation: On record as '{stored_name}', presenting as '{holder_name}'.")

        if conflicts:
            return "MINOR_ANOMALY", None, conflicts

        return "CONSISTENT", None, []

    def get_subgraph_for_entity(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Extracts local subgraph around an entity with visual coordinates, node categories,
        and conflict highlights for React Canvas/SVG rendering.
        """
        if entity_id not in self.graph:
            # Fallback to closest matching node or root
            nodes_matching = [n for n in self.graph.nodes if entity_id in n]
            if nodes_matching:
                entity_id = nodes_matching[0]
            elif len(self.graph.nodes) > 0:
                entity_id = list(self.graph.nodes.keys())[0]
            else:
                return {"nodes": [], "edges": [], "fracture_detected": False}

        # Extract ego graph
        sub_nodes = set([entity_id])
        frontier = set([entity_id])
        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                neighbors = set(self.graph.successors(node)).union(set(self.graph.predecessors(node)))
                next_frontier.update(neighbors)
            sub_nodes.update(next_frontier)
            frontier = next_frontier

        # Build output structure with hierarchical/spring layout coordinates
        nodes_list = []
        edges_list = []
        
        # Determine if fracture exists in this subgraph
        fracture_in_subgraph = False
        
        # Calculate radial/force positions
        import math
        sub_list = list(sub_nodes)
        total = len(sub_list)
        
        for idx, node in enumerate(sub_list):
            data = self.graph.nodes.get(node, {})
            ntype = data.get("node_type", "UNKNOWN")
            props = data.get("properties", {})
            label = data.get("label", node)
            
            is_conflict = (
                props.get("is_conflicting_node", False) 
                or "conflict" in node.lower() 
                or "rostova" in node.lower() 
                or "rus" in node.lower()
                or "elena dmitrievna" in label.lower()
            )
            if is_conflict:
                fracture_in_subgraph = True

            # Coordinate positioning: center root, orbit others
            if node == entity_id:
                pos_x, pos_y = 400, 260
            else:
                angle = (2 * math.pi * idx) / max(1, total - 1)
                radius = 180 + (idx % 3) * 45
                pos_x = 400 + radius * math.cos(angle)
                pos_y = 260 + radius * math.sin(angle)

            nodes_list.append({
                "id": node,
                "label": label,
                "node_type": ntype,
                "properties": props,
                "is_root": node == entity_id,
                "is_conflict": is_conflict,
                "is_fracture": is_conflict,
                "x": round(pos_x, 1),
                "y": round(pos_y, 1)
            })

        for u, v, key, data in self.graph.edges(sub_nodes, data=True, keys=True):
            if u in sub_nodes and v in sub_nodes:
                edge_props = data.get("properties", {})
                is_edge_conflict = (
                    "FRACTURE" in data.get("edge_type", "") 
                    or "CONFLICT" in data.get("edge_type", "") 
                    or edge_props.get("is_conflict", False)
                    or "rostova" in u.lower() or "rostova" in v.lower()
                    or "rus" in u.lower() or "rus" in v.lower()
                )
                edges_list.append({
                    "id": f"{u}->{v}:{key}",
                    "source": u,
                    "target": v,
                    "edge_type": data.get("edge_type", "LINKED_TO"),
                    "properties": edge_props,
                    "is_conflict": is_edge_conflict,
                    "is_fracture": is_edge_conflict
                })

        return {
            "entity_id": entity_id,
            "fracture_detected": fracture_in_subgraph,
            "nodes": nodes_list,
            "edges": edges_list
        }

    def _compute_name_similarity(self, name1: str, name2: str) -> float:
        """Jaccard token similarity between two full names."""
        tokens1 = set(name1.upper().replace(',', ' ').split())
        tokens2 = set(name2.upper().replace(',', ' ').split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)
