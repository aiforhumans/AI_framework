"""
Base Store Module.

Provides a generic base class for JSON file-based persistence,
eliminating duplicate CRUD boilerplate across all store classes.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Generic, TypeVar, List, Optional, Dict, Any, Type

from pydantic import BaseModel


# Type variable for the model class
T = TypeVar("T", bound=BaseModel)


class BaseStore(ABC, Generic[T]):
    """
    Abstract base class for JSON file-based data stores.
    
    Provides common CRUD operations and file persistence logic.
    Subclasses must define the model_class and file_path.
    
    Usage:
        class MyStore(BaseStore[MyModel]):
            model_class = MyModel
            file_path = Path("app/data/my_data.json")
    
    Attributes:
        model_class: The Pydantic model class for items in this store
        file_path: Path to the JSON file for persistence
    """
    
    # Subclasses must override these
    model_class: Type[T]
    file_path: Path
    
    # Optional: key for items in JSON (default: "items")
    json_key: str = "items"
    
    def __init__(self, file_path: Optional[Path] = None) -> None:
        """
        Initialize the store.
        
        Args:
            file_path: Optional override for the default file path
        """
        if file_path:
            self.file_path = file_path
        
        self._items: List[T] = []
        self._next_id: int = 1
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self) -> None:
        """Ensure the parent directory exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        """Load items from the JSON file."""
        if not self.file_path.exists():
            self._items = []
            self._next_id = 1
            return
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle both list format and dict format with key
            if isinstance(data, list):
                raw_items = data
                self._next_id = 1
            else:
                raw_items = data.get(self.json_key, [])
                self._next_id = data.get("next_id", 1)
            
            self._items = [self.model_class(**item) for item in raw_items]
            
            # Update next_id based on existing items
            if self._items:
                max_id = max(getattr(item, "id", 0) for item in self._items)
                self._next_id = max(self._next_id, max_id + 1)
                
        except Exception as e:
            print(f"Warning: Failed to load {self.file_path}: {e}")
            self._items = []
            self._next_id = 1
    
    def _save(self) -> None:
        """Save items to the JSON file."""
        self._ensure_directory()
        
        data = {
            self.json_key: [item.model_dump() for item in self._items],
            "next_id": self._next_id,
        }
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def _get_next_id(self) -> int:
        """Get and increment the next available ID."""
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    # =========================================================================
    # CRUD Operations
    # =========================================================================
    
    def list_all(self) -> List[T]:
        """
        List all items in the store.
        
        Returns:
            List of all items
        """
        return self._items.copy()
    
    def get(self, item_id: int) -> Optional[T]:
        """
        Get an item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        for item in self._items:
            if getattr(item, "id", None) == item_id:
                return item
        return None
    
    def create(self, item: T) -> T:
        """
        Create a new item.
        
        Args:
            item: The item to create (id will be auto-assigned)
            
        Returns:
            The created item with assigned ID
        """
        # Create a copy with the new ID
        item_data = item.model_dump()
        item_data["id"] = self._get_next_id()
        
        # Add timestamps if the model supports them
        now = datetime.now().isoformat()
        if "created_at" in item_data and not item_data.get("created_at"):
            item_data["created_at"] = now
        if "updated_at" in item_data:
            item_data["updated_at"] = now
        
        new_item = self.model_class(**item_data)
        self._items.append(new_item)
        self._save()
        return new_item
    
    def update(self, item_id: int, **updates) -> Optional[T]:
        """
        Update an existing item.
        
        Args:
            item_id: The ID of the item to update
            **updates: Field updates to apply
            
        Returns:
            The updated item if found, None otherwise
        """
        for i, item in enumerate(self._items):
            if getattr(item, "id", None) == item_id:
                item_data = item.model_dump()
                
                # Apply updates (skip None values)
                for key, value in updates.items():
                    if value is not None:
                        item_data[key] = value
                
                # Update timestamp if supported
                if "updated_at" in item_data:
                    item_data["updated_at"] = datetime.now().isoformat()
                
                self._items[i] = self.model_class(**item_data)
                self._save()
                return self._items[i]
        return None
    
    def delete(self, item_id: int) -> bool:
        """
        Delete an item by ID.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, item in enumerate(self._items):
            if getattr(item, "id", None) == item_id:
                del self._items[i]
                self._save()
                return True
        return False
    
    def count(self) -> int:
        """
        Get the total number of items.
        
        Returns:
            Number of items in the store
        """
        return len(self._items)
    
    def clear(self) -> int:
        """
        Delete all items.
        
        Returns:
            Number of items deleted
        """
        count = len(self._items)
        self._items = []
        self._save()
        return count
    
    # =========================================================================
    # Query Helpers
    # =========================================================================
    
    def find_by(self, **criteria) -> List[T]:
        """
        Find items matching the given criteria.
        
        Args:
            **criteria: Field=value pairs to match
            
        Returns:
            List of matching items
        """
        results = []
        for item in self._items:
            match = True
            for key, value in criteria.items():
                if getattr(item, key, None) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results
    
    def find_one_by(self, **criteria) -> Optional[T]:
        """
        Find the first item matching the given criteria.
        
        Args:
            **criteria: Field=value pairs to match
            
        Returns:
            First matching item or None
        """
        results = self.find_by(**criteria)
        return results[0] if results else None
    
    def exists(self, item_id: int) -> bool:
        """
        Check if an item exists.
        
        Args:
            item_id: The ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.get(item_id) is not None


class SimpleListStore(Generic[T]):
    """
    A simpler store variant for list-based JSON files.
    
    Used when the JSON file is just a list without additional metadata.
    """
    
    model_class: Type[T]
    file_path: Path
    
    def __init__(self, file_path: Optional[Path] = None) -> None:
        if file_path:
            self.file_path = file_path
        
        self._items: List[T] = []
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        if not self.file_path.exists():
            self._items = []
            return
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._items = [self.model_class(**item) for item in data]
        except Exception:
            self._items = []
    
    def _save(self) -> None:
        self._ensure_directory()
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([item.model_dump() for item in self._items], f, indent=2)
    
    def _next_id(self) -> int:
        if not self._items:
            return 1
        return max(getattr(item, "id", 0) for item in self._items) + 1
    
    def list_all(self) -> List[T]:
        return self._items.copy()
    
    def get(self, item_id: int) -> Optional[T]:
        for item in self._items:
            if getattr(item, "id", None) == item_id:
                return item
        return None
    
    def create(self, item: T) -> T:
        item_data = item.model_dump()
        item_data["id"] = self._next_id()
        new_item = self.model_class(**item_data)
        self._items.append(new_item)
        self._save()
        return new_item
    
    def update(self, item_id: int, updates: dict) -> Optional[T]:
        for i, item in enumerate(self._items):
            if getattr(item, "id", None) == item_id:
                item_data = item.model_dump()
                item_data.update({k: v for k, v in updates.items() if v is not None})
                self._items[i] = self.model_class(**item_data)
                self._save()
                return self._items[i]
        return None
    
    def delete(self, item_id: int) -> bool:
        for i, item in enumerate(self._items):
            if getattr(item, "id", None) == item_id:
                del self._items[i]
                self._save()
                return True
        return False
