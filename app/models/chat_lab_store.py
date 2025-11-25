"""
Multi-Turn Chat Lab Store
Stores conversation trees with branching paths and state management.
"""

import json
import os
import time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass
from pathlib import Path


class ChatMessage(BaseModel):
    """A single message in a conversation."""
    id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # latency, tokens, model used, etc.


class ConversationNode(BaseModel):
    """A node in the conversation tree representing a state after a message."""
    id: str
    parent_id: Optional[str] = None  # None for root
    message: ChatMessage
    children: List[str] = Field(default_factory=list)  # IDs of child nodes
    is_active: bool = True  # Whether this is the currently active branch
    branch_name: Optional[str] = None  # Optional name for this branch


class ConversationTree(BaseModel):
    """A complete conversation tree with multiple branches."""
    id: int
    name: str
    description: str = ""
    model_name: str = ""
    system_prompt: str = ""
    root_node_id: Optional[str] = None
    nodes: Dict[str, ConversationNode] = Field(default_factory=dict)
    active_path: List[str] = Field(default_factory=list)  # IDs of nodes in current active path
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class ChatLabStore:
    """Persists conversation trees to JSON."""
    
    def __init__(self, data_dir: str = "app/data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._data_dir / "chat_lab.json"
        self._trees: Dict[int, ConversationTree] = {}
        self._next_id = 1
        self._load()
    
    def _load(self):
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                for item in data.get("trees", []):
                    tree = ConversationTree(**item)
                    self._trees[tree.id] = tree
                    if tree.id >= self._next_id:
                        self._next_id = tree.id + 1
            except Exception:
                pass
    
    def _save(self):
        data = {"trees": [t.model_dump() for t in self._trees.values()]}
        self._file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def list_trees(self) -> List[ConversationTree]:
        """List all conversation trees."""
        return list(self._trees.values())
    
    def get_tree(self, tree_id: int) -> Optional[ConversationTree]:
        """Get a specific conversation tree."""
        return self._trees.get(tree_id)
    
    def create_tree(self, name: str, description: str = "", 
                    model_name: str = "", system_prompt: str = "") -> ConversationTree:
        """Create a new conversation tree."""
        tree = ConversationTree(
            id=self._next_id,
            name=name,
            description=description,
            model_name=model_name,
            system_prompt=system_prompt
        )
        self._trees[tree.id] = tree
        self._next_id += 1
        self._save()
        return tree
    
    def update_tree(self, tree_id: int, **kwargs) -> Optional[ConversationTree]:
        """Update tree metadata."""
        tree = self._trees.get(tree_id)
        if not tree:
            return None
        
        for key, value in kwargs.items():
            if hasattr(tree, key) and key not in ("id", "nodes", "created_at"):
                setattr(tree, key, value)
        
        tree.updated_at = time.time()
        self._save()
        return tree
    
    def delete_tree(self, tree_id: int) -> bool:
        """Delete a conversation tree."""
        if tree_id in self._trees:
            del self._trees[tree_id]
            self._save()
            return True
        return False
    
    def add_message(self, tree_id: int, role: str, content: str, 
                    parent_node_id: Optional[str] = None,
                    metadata: Dict[str, Any] = None) -> Optional[ConversationNode]:
        """
        Add a message to the conversation tree.
        If parent_node_id is None and tree has nodes, uses the last node in active_path.
        """
        tree = self._trees.get(tree_id)
        if not tree:
            return None
        
        # Generate unique node ID
        node_id = f"node_{int(time.time() * 1000)}_{len(tree.nodes)}"
        
        # Create message
        message = ChatMessage(
            id=f"msg_{node_id}",
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        # Determine parent
        if parent_node_id is None and tree.active_path:
            parent_node_id = tree.active_path[-1]
        
        # Create node
        node = ConversationNode(
            id=node_id,
            parent_id=parent_node_id,
            message=message
        )
        
        # Update parent's children
        if parent_node_id and parent_node_id in tree.nodes:
            parent = tree.nodes[parent_node_id]
            if node_id not in parent.children:
                parent.children.append(node_id)
        
        # Add node to tree
        tree.nodes[node_id] = node
        
        # If this is the first node, set as root
        if tree.root_node_id is None:
            tree.root_node_id = node_id
        
        # Update active path
        tree.active_path.append(node_id)
        
        tree.updated_at = time.time()
        self._save()
        return node
    
    def create_branch(self, tree_id: int, from_node_id: str, 
                      branch_name: str = None) -> Optional[str]:
        """
        Create a new branch from a specific node.
        Returns the branch point node ID.
        """
        tree = self._trees.get(tree_id)
        if not tree or from_node_id not in tree.nodes:
            return None
        
        # Update active path to end at from_node_id
        new_active_path = []
        for nid in tree.active_path:
            new_active_path.append(nid)
            if nid == from_node_id:
                break
        
        tree.active_path = new_active_path
        tree.updated_at = time.time()
        self._save()
        return from_node_id
    
    def switch_branch(self, tree_id: int, to_node_id: str) -> bool:
        """
        Switch the active path to include a specific node.
        Rebuilds the active path from root to this node.
        """
        tree = self._trees.get(tree_id)
        if not tree or to_node_id not in tree.nodes:
            return False
        
        # Build path from root to target node
        path = []
        current_id = to_node_id
        while current_id:
            path.insert(0, current_id)
            node = tree.nodes.get(current_id)
            current_id = node.parent_id if node else None
        
        tree.active_path = path
        tree.updated_at = time.time()
        self._save()
        return True
    
    def get_conversation_history(self, tree_id: int, 
                                  node_id: str = None) -> List[ChatMessage]:
        """
        Get the conversation history up to a specific node.
        If node_id is None, uses the last node in active_path.
        """
        tree = self._trees.get(tree_id)
        if not tree:
            return []
        
        if node_id is None:
            if not tree.active_path:
                return []
            node_id = tree.active_path[-1]
        
        # Build path from root to node
        path = []
        current_id = node_id
        while current_id:
            path.insert(0, current_id)
            node = tree.nodes.get(current_id)
            current_id = node.parent_id if node else None
        
        # Extract messages
        messages = []
        for nid in path:
            node = tree.nodes.get(nid)
            if node:
                messages.append(node.message)
        
        return messages
    
    def get_tree_structure(self, tree_id: int) -> Dict:
        """
        Get the tree structure for visualization.
        Returns a nested dict representation.
        """
        tree = self._trees.get(tree_id)
        if not tree or not tree.root_node_id:
            return {}
        
        def build_subtree(node_id: str) -> Dict:
            node = tree.nodes.get(node_id)
            if not node:
                return {}
            
            return {
                "id": node.id,
                "role": node.message.role,
                "content_preview": node.message.content[:50] + "..." if len(node.message.content) > 50 else node.message.content,
                "is_active": node.id in tree.active_path,
                "branch_name": node.branch_name,
                "children": [build_subtree(cid) for cid in node.children]
            }
        
        return build_subtree(tree.root_node_id)
    
    def delete_node(self, tree_id: int, node_id: str) -> bool:
        """
        Delete a node and all its descendants.
        Cannot delete if node is in active path (switch first).
        """
        tree = self._trees.get(tree_id)
        if not tree or node_id not in tree.nodes:
            return False
        
        # Collect all nodes to delete (node + descendants)
        to_delete = set()
        queue = [node_id]
        while queue:
            nid = queue.pop(0)
            to_delete.add(nid)
            node = tree.nodes.get(nid)
            if node:
                queue.extend(node.children)
        
        # Remove from parent's children
        node = tree.nodes.get(node_id)
        if node and node.parent_id and node.parent_id in tree.nodes:
            parent = tree.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)
        
        # Delete nodes
        for nid in to_delete:
            if nid in tree.nodes:
                del tree.nodes[nid]
        
        # Update active path
        tree.active_path = [nid for nid in tree.active_path if nid not in to_delete]
        
        # Update root if needed
        if tree.root_node_id in to_delete:
            tree.root_node_id = None
        
        tree.updated_at = time.time()
        self._save()
        return True
