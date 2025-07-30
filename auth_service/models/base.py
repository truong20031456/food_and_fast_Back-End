# Legacy base model - now using shared base models
# This file is kept for backward compatibility

import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from shared.models.base import Base, BaseDBModel, TimestampMixin, UUIDMixin
from sqlalchemy import Column, Integer, Boolean


# Legacy BaseModel for backward compatibility
class BaseModel(BaseDBModel):
    """Legacy base model - extends shared BaseDBModel"""

    __abstract__ = True

    # Add legacy integer ID alongside UUID for backward compatibility
    legacy_id = Column(Integer, unique=True, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate legacy_id if not provided
        if not self.legacy_id:
            import time

            self.legacy_id = (
                int(time.time() * 1000000) % 2147483647
            )  # Keep within int range
