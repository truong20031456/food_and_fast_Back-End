from .product_controller import router as product_router
from .category_controller import router as category_router
from .inventory_controller import router as inventory_router
from .review_controller import router as review_router
from .search_controller import router as search_router

__all__ = [
    "product_router",
    "category_router", 
    "inventory_router",
    "review_router",
    "search_router"
] 