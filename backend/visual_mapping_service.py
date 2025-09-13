from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import networkx as nx
from datetime import datetime

class NodeType(str, Enum):
    CORE_IDEA = "core_idea"
    SUB_CONCEPT = "sub_concept"
    FEATURE = "feature"
    STAKEHOLDER = "stakeholder"
    CHALLENGE = "challenge"
    OPPORTUNITY = "opportunity"
    TECHNOLOGY = "technology"
    MARKET_SEGMENT = "market_segment"

class EdgeType(str, Enum):
    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    ENABLES = "enables"
    COMPETES_WITH = "competes_with"
    SERVES = "serves"
    SOLVES = "solves"
    IMPLEMENTS = "implements"

@dataclass
class IdeaNode:
    id: str
    label: str
    type: NodeType
    description: str
    importance: float  # 0-1 scale
    feasibility: float  # 0-1 scale
    x: Optional[float] = None
    y: Optional[float] = None
    color: Optional[str] = None
    size: Optional[float] = None

@dataclass
class IdeaEdge:
    source: str
    target: str
    type: EdgeType
    weight: float  # 0-1 scale
    description: Optional[str] = None

@dataclass
class IdeaMap:
    central_idea: str
    nodes: List[IdeaNode]
    edges: List[IdeaEdge]
    clusters: Dict[str, List[str]]  # cluster_name -> node_ids
    created_at: str
    updated_at: str

class VisualMappingService:
    def __init__(self):
        self.node_colors = {
            NodeType.CORE_IDEA: "#FF6B6B",
            NodeType.SUB_CONCEPT: "#4ECDC4", 
            NodeType.FEATURE: "#45B7D1",
            NodeType.STAKEHOLDER: "#96CEB4",
            NodeType.CHALLENGE: "#FFEAA7",
            NodeType.OPPORTUNITY: "#DDA0DD",
            NodeType.TECHNOLOGY: "#98D8C8",
            NodeType.MARKET_SEGMENT: "#F7DC6F"
        }
        print("Visual Mapping Service initialized")
    
    def create_idea_map(self, 
                       central_idea: str, 
                       conversation_messages: List[Dict[str, str]] = None,
                       market_research_data: Dict = None) -> IdeaMap:
        """
        Create a visual idea map from conversation and research data
        """
        try:
            # Extract concepts from conversation
            concepts = self._extract_concepts_from_conversation(conversation_messages or [])
            
            # Create nodes
            nodes = [
                IdeaNode(
                    id="core",
                    label=central_idea,
                    type=NodeType.CORE_IDEA,
                    description=f"The central idea: {central_idea}",
                    importance=1.0,
                    feasibility=0.8,
                    x=0.5,
                    y=0.5,
                    color=self.node_colors[NodeType.CORE_IDEA],
                    size=1.0
                )
            ]
            
            # Add concept nodes
            for i, concept in enumerate(concepts):
                node_id = f"concept_{i}"
                node_type = self._classify_concept(concept)
                
                nodes.append(IdeaNode(
                    id=node_id,
                    label=concept["label"],
                    type=node_type,
                    description=concept["description"],
                    importance=concept.get("importance", 0.5),
                    feasibility=concept.get("feasibility", 0.5),
                    color=self.node_colors.get(node_type, "#95A5A6"),
                    size=0.6
                ))
            
            # Add market research nodes if available
            if market_research_data:
                nodes.extend(self._create_market_nodes(market_research_data))
            
            # Create edges (relationships)
            edges = self._create_relationships(nodes)
            
            # Position nodes using force-directed layout
            positioned_nodes = self._position_nodes(nodes, edges)
            
            # Create clusters
            clusters = self._create_clusters(positioned_nodes)
            
            return IdeaMap(
                central_idea=central_idea,
                nodes=positioned_nodes,
                edges=edges,
                clusters=clusters,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Error creating idea map: {e}")
            # Return minimal map on error
            return IdeaMap(
                central_idea=central_idea,
                nodes=[IdeaNode(
                    id="core",
                    label=central_idea,
                    type=NodeType.CORE_IDEA,
                    description=central_idea,
                    importance=1.0,
                    feasibility=0.8,
                    x=0.5,
                    y=0.5,
                    color=self.node_colors[NodeType.CORE_IDEA],
                    size=1.0
                )],
                edges=[],
                clusters={},
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
    
    def _extract_concepts_from_conversation(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """Extract key concepts from conversation messages"""
        concepts = []
        
        # Keywords that indicate different concept types
        feature_keywords = ["feature", "functionality", "capability", "tool", "interface"]
        challenge_keywords = ["problem", "challenge", "issue", "difficulty", "obstacle"]
        opportunity_keywords = ["opportunity", "potential", "market", "advantage", "benefit"]
        stakeholder_keywords = ["user", "customer", "client", "stakeholder", "target", "audience"]
        technology_keywords = ["technology", "platform", "framework", "api", "database", "algorithm"]
        
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Simple concept extraction (in production, use NLP)
            if any(keyword in content for keyword in feature_keywords):
                concepts.append({
                    "label": "Key Feature",
                    "description": msg.get("content", "")[:100],
                    "type": "feature",
                    "importance": 0.7,
                    "feasibility": 0.6
                })
            
            if any(keyword in content for keyword in challenge_keywords):
                concepts.append({
                    "label": "Challenge",
                    "description": msg.get("content", "")[:100],
                    "type": "challenge",
                    "importance": 0.8,
                    "feasibility": 0.4
                })
            
            if any(keyword in content for keyword in opportunity_keywords):
                concepts.append({
                    "label": "Opportunity",
                    "description": msg.get("content", "")[:100],
                    "type": "opportunity",
                    "importance": 0.9,
                    "feasibility": 0.7
                })
        
        # Limit to avoid overcrowding
        return concepts[:8]
    
    def _classify_concept(self, concept: Dict) -> NodeType:
        """Classify a concept into a node type"""
        concept_type = concept.get("type", "").lower()
        
        type_mapping = {
            "feature": NodeType.FEATURE,
            "challenge": NodeType.CHALLENGE,
            "opportunity": NodeType.OPPORTUNITY,
            "stakeholder": NodeType.STAKEHOLDER,
            "technology": NodeType.TECHNOLOGY,
            "market": NodeType.MARKET_SEGMENT
        }
        
        return type_mapping.get(concept_type, NodeType.SUB_CONCEPT)
    
    def _create_market_nodes(self, market_data: Dict) -> List[IdeaNode]:
        """Create nodes from market research data"""
        nodes = []
        
        # Add competitor nodes
        competitors = market_data.get("competitors", [])
        for i, competitor in enumerate(competitors[:3]):  # Limit to 3 competitors
            nodes.append(IdeaNode(
                id=f"competitor_{i}",
                label=competitor.get("name", f"Competitor {i+1}"),
                type=NodeType.SUB_CONCEPT,
                description=competitor.get("description", ""),
                importance=0.6,
                feasibility=0.8,
                color="#E74C3C",
                size=0.5
            ))
        
        # Add opportunity nodes from industry insights
        industry = market_data.get("industry_insights", {})
        opportunities = industry.get("opportunities", [])
        for i, opp in enumerate(opportunities[:2]):  # Limit to 2 opportunities
            nodes.append(IdeaNode(
                id=f"market_opp_{i}",
                label=opp,
                type=NodeType.OPPORTUNITY,
                description=f"Market opportunity: {opp}",
                importance=0.8,
                feasibility=0.6,
                color=self.node_colors[NodeType.OPPORTUNITY],
                size=0.6
            ))
        
        return nodes
    
    def _create_relationships(self, nodes: List[IdeaNode]) -> List[IdeaEdge]:
        """Create edges between nodes based on their types and content"""
        edges = []
        core_node = next((n for n in nodes if n.type == NodeType.CORE_IDEA), None)
        
        if not core_node:
            return edges
        
        # Connect all nodes to the core idea
        for node in nodes:
            if node.id != core_node.id:
                edge_type = self._determine_edge_type(core_node, node)
                edges.append(IdeaEdge(
                    source=core_node.id,
                    target=node.id,
                    type=edge_type,
                    weight=0.8,
                    description=f"{core_node.label} {edge_type.value} {node.label}"
                ))
        
        # Create some inter-node relationships
        feature_nodes = [n for n in nodes if n.type == NodeType.FEATURE]
        challenge_nodes = [n for n in nodes if n.type == NodeType.CHALLENGE]
        
        # Features can solve challenges
        for feature in feature_nodes:
            for challenge in challenge_nodes:
                if len(edges) < 20:  # Limit total edges
                    edges.append(IdeaEdge(
                        source=feature.id,
                        target=challenge.id,
                        type=EdgeType.SOLVES,
                        weight=0.6
                    ))
        
        return edges
    
    def _determine_edge_type(self, source: IdeaNode, target: IdeaNode) -> EdgeType:
        """Determine the relationship type between two nodes"""
        if source.type == NodeType.CORE_IDEA:
            if target.type == NodeType.FEATURE:
                return EdgeType.IMPLEMENTS
            elif target.type == NodeType.STAKEHOLDER:
                return EdgeType.SERVES
            elif target.type in [NodeType.CHALLENGE, NodeType.OPPORTUNITY]:
                return EdgeType.RELATES_TO
            else:
                return EdgeType.RELATES_TO
        
        return EdgeType.RELATES_TO
    
    def _position_nodes(self, nodes: List[IdeaNode], edges: List[IdeaEdge]) -> List[IdeaNode]:
        """Position nodes using a simple circular layout"""
        import math
        
        positioned_nodes = []
        
        # Find core node
        core_node = next((n for n in nodes if n.type == NodeType.CORE_IDEA), None)
        if core_node:
            core_node.x = 0.5
            core_node.y = 0.5
            positioned_nodes.append(core_node)
        
        # Position other nodes in circles around the core
        other_nodes = [n for n in nodes if n.type != NodeType.CORE_IDEA]
        
        if other_nodes:
            angle_step = 2 * math.pi / len(other_nodes)
            radius = 0.3
            
            for i, node in enumerate(other_nodes):
                angle = i * angle_step
                node.x = 0.5 + radius * math.cos(angle)
                node.y = 0.5 + radius * math.sin(angle)
                positioned_nodes.append(node)
        
        return positioned_nodes
    
    def _create_clusters(self, nodes: List[IdeaNode]) -> Dict[str, List[str]]:
        """Group nodes into logical clusters"""
        clusters = {}
        
        # Group by node type
        for node in nodes:
            cluster_name = node.type.value.replace("_", " ").title()
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(node.id)
        
        return clusters
    
    def update_node_position(self, idea_map: IdeaMap, node_id: str, x: float, y: float) -> IdeaMap:
        """Update the position of a specific node"""
        for node in idea_map.nodes:
            if node.id == node_id:
                node.x = x
                node.y = y
                break
        
        idea_map.updated_at = datetime.now().isoformat()
        return idea_map
    
    def add_node_to_map(self, idea_map: IdeaMap, node: IdeaNode) -> IdeaMap:
        """Add a new node to an existing idea map"""
        idea_map.nodes.append(node)
        
        # Connect to core node
        core_node = next((n for n in idea_map.nodes if n.type == NodeType.CORE_IDEA), None)
        if core_node:
            idea_map.edges.append(IdeaEdge(
                source=core_node.id,
                target=node.id,
                type=EdgeType.RELATES_TO,
                weight=0.7
            ))
        
        idea_map.updated_at = datetime.now().isoformat()
        return idea_map
    
    def to_json(self, idea_map: IdeaMap) -> str:
        """Convert idea map to JSON for frontend consumption"""
        return json.dumps({
            "central_idea": idea_map.central_idea,
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type.value,
                    "description": node.description,
                    "importance": node.importance,
                    "feasibility": node.feasibility,
                    "x": node.x,
                    "y": node.y,
                    "color": node.color,
                    "size": node.size
                } for node in idea_map.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type.value,
                    "weight": edge.weight,
                    "description": edge.description
                } for edge in idea_map.edges
            ],
            "clusters": idea_map.clusters,
            "created_at": idea_map.created_at,
            "updated_at": idea_map.updated_at
        }, indent=2)