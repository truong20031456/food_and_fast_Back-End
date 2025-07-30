from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from services.cart.cart_service import CartService
from schemas.cart_schemas import (
    CartResponse, CartCreate, CartItemCreate, 
    CartItemUpdate, CartItemResponse, CartSummary
)

router = APIRouter()

@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(cart_data: CartCreate, db: Session = Depends(get_db)):
    """Create a new cart or get existing active cart"""
    try:
        cart = CartService.get_or_create_cart(
            db=db, 
            user_id=cart_data.user_id, 
            session_id=cart_data.session_id
        )
        return cart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cart: {str(e)}"
        )

@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: int, db: Session = Depends(get_db)):
    """Get cart by ID"""
    cart = CartService.get_cart_by_id(db=db, cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart

@router.get("/user/{user_id}", response_model=CartResponse)
async def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    """Get or create active cart for user"""
    try:
        cart = CartService.get_or_create_cart(db=db, user_id=user_id)
        return cart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user cart: {str(e)}"
        )

@router.post("/{cart_id}/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_id: int, 
    item_data: CartItemCreate, 
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Verify cart exists
    cart = CartService.get_cart_by_id(db=db, cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    try:
        cart_item = CartService.add_item_to_cart(
            db=db, 
            cart_id=cart_id, 
            item_data=item_data
        )
        return cart_item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding item to cart: {str(e)}"
        )

@router.get("/{cart_id}/items", response_model=List[CartItemResponse])
async def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    """Get all items in cart"""
    # Verify cart exists
    cart = CartService.get_cart_by_id(db=db, cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    items = CartService.get_cart_items(db=db, cart_id=cart_id)
    return items

@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int, 
    item_data: CartItemUpdate, 
    db: Session = Depends(get_db)
):
    """Update cart item"""
    cart_item = CartService.update_cart_item(
        db=db, 
        item_id=item_id, 
        item_data=item_data
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return cart_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(item_id: int, db: Session = Depends(get_db)):
    """Remove item from cart"""
    success = CartService.remove_cart_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

@router.delete("/{cart_id}/items", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(cart_id: int, db: Session = Depends(get_db)):
    """Clear all items from cart"""
    # Verify cart exists
    cart = CartService.get_cart_by_id(db=db, cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    CartService.clear_cart(db=db, cart_id=cart_id)

@router.get("/{cart_id}/summary", response_model=CartSummary)
async def get_cart_summary(cart_id: int, db: Session = Depends(get_db)):
    """Get cart summary"""
    cart = CartService.get_cart_by_id(db=db, cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart