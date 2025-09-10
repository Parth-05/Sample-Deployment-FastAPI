# Ensure these import so metadata is ready (for create_all or reflection)
from .profile import Profile
from .trainer import Trainer
from .client import Client

__all__ = ["Profile", "Trainer", "Client"]
