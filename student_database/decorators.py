"""Custom decorators used by the student database system."""

from __future__ import annotations

import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable


def log_action(action_name: str) -> Callable:
    """Write a simple audit line after a manager action succeeds."""

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = function(*args, **kwargs)
            owner = args[0] if args else None
            log_path = getattr(owner, "log_path", None)
            if log_path:
                folder = os.path.dirname(os.path.abspath(log_path))
                os.makedirs(folder, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"[{timestamp}] {action_name}\n")
            return result

        return wrapper

    return decorator
