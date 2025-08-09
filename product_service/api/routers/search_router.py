"""
Search Router - Handles product search functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from core.database import get_db
from schemas.product import ProductRead
from schemas.search import SearchResponse, SearchFilters
from services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])


async def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    """Get SearchService instance"""
    return SearchService(db)


@router.get("/products", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, price_asc, price_desc, rating, newest"),
    search_service: SearchService = Depends(get_search_service),
):
    """Search products with advanced filtering"""
    try:
        filters = SearchFilters(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock=in_stock,
        )
        
        results = await search_service.search_products(
            query=q,
            page=page,
            size=size,
            filters=filters,
            sort_by=sort_by,
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search products")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions"),
    search_service: SearchService = Depends(get_search_service),
):
    """Get search suggestions based on partial query"""
    try:
        suggestions = await search_service.get_suggestions(query=q, limit=limit)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get suggestions")


@router.get("/popular")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=20, description="Number of popular searches"),
    search_service: SearchService = Depends(get_search_service),
):
    """Get popular search terms"""
    try:
        popular = await search_service.get_popular_searches(limit=limit)
        return {"popular_searches": popular}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get popular searches")


@router.get("/categories")
async def search_categories(
    q: str = Query(..., min_length=2, description="Search query"),
    search_service: SearchService = Depends(get_search_service),
):
    """Search categories"""
    try:
        categories = await search_service.search_categories(query=q)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search categories")


@router.get("/filters")
async def get_search_filters(
    category_id: Optional[int] = Query(None, description="Category ID for context"),
    search_service: SearchService = Depends(get_search_service),
):
    """Get available search filters"""
    try:
        filters = await search_service.get_available_filters(category_id=category_id)
        return {"filters": filters}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get search filters")


@router.post("/track")
async def track_search(
    query: str,
    results_count: int = 0,
    search_service: SearchService = Depends(get_search_service),
):
    """Track search query for analytics"""
    try:
        await search_service.track_search(query=query, results_count=results_count)
        return {"message": "Search tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to track search")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product_service", "component": "search"}
