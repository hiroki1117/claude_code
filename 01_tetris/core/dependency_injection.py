"""Dependency injection container for managing component dependencies."""

from typing import Dict, Type, TypeVar, Any, Callable, Optional
from abc import ABC, abstractmethod
import inspect


T = TypeVar('T')


class Injectable(ABC):
    """Base class for injectable components."""
    
    @abstractmethod
    def initialize(self, container: 'Container') -> None:
        """Initialize the component with dependencies from container."""
        pass


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._initialized: bool = False
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service."""
        if self._initialized:
            raise ContainerError("Cannot register services after container initialization")
        
        if not issubclass(implementation, interface):
            raise ContainerError(f"{implementation} does not implement {interface}")
        
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating instances."""
        if self._initialized:
            raise ContainerError("Cannot register services after container initialization")
        
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance."""
        if self._initialized:
            raise ContainerError("Cannot register services after container initialization")
        
        if not isinstance(instance, interface):
            raise ContainerError(f"Instance does not implement {interface}")
        
        self._singletons[interface] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Get an instance of the requested interface."""
        if not self._initialized:
            self.initialize()
        
        # Check for pre-registered instances
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check for factory functions
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check for singleton services
        if interface in self._services:
            if interface not in self._singletons:
                implementation = self._services[interface]
                instance = self._create_instance(implementation)
                self._singletons[interface] = instance
            return self._singletons[interface]
        
        raise ContainerError(f"No registration found for {interface}")
    
    def initialize(self) -> None:
        """Initialize all registered services."""
        if self._initialized:
            return
        
        # Initialize all singleton services
        for interface, implementation in self._services.items():
            if interface not in self._singletons:
                instance = self._create_instance(implementation)
                self._singletons[interface] = instance
        
        # Initialize injectable components
        for instance in self._singletons.values():
            if isinstance(instance, Injectable):
                instance.initialize(self)
        
        self._initialized = True
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create an instance with dependency injection."""
        # Get constructor parameters
        sig = inspect.signature(implementation.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    params[param_name] = self.get(param.annotation)
                except ContainerError:
                    if param.default == inspect.Parameter.empty:
                        raise ContainerError(
                            f"Cannot resolve dependency {param.annotation} for {implementation}"
                        )
                    # Use default value if dependency cannot be resolved
            elif param.default == inspect.Parameter.empty:
                raise ContainerError(
                    f"Parameter {param_name} in {implementation} has no type annotation"
                )
        
        return implementation(**params)
    
    def reset(self) -> None:
        """Reset the container to uninitialized state."""
        self._singletons.clear()
        self._initialized = False


class ContainerError(Exception):
    """Raised when dependency injection operations fail."""
    pass