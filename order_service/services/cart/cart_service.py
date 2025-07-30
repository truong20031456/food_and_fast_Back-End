"""
Cart Service for Order Management
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.cart import Cart, CartItem
from schemas.cart_schemas import CartCreate, CartItemCreate


class CartService:
    """Service for managing shopping carts"""

    @staticmethod
    def get_or_create_cart(
        db: Session, user_id: Optional[int] = None, session_id: Optional[str] = None
    ) -> Cart:
        """Get existing cart or create new one"""
        if user_id:
            cart = (
                db.query(Cart)
                .filter(Cart.user_id == user_id, Cart.status == "active")
                .first()
            )
        elif session_id:
            cart = (
                db.query(Cart)
                .filter(Cart.session_id == session_id, Cart.status == "active")
                .first()
            )
        else:
            raise ValueError("Either user_id or session_id must be provided")

        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id, status="active")
            db.add(cart)
            db.commit()
            db.refresh(cart)

        return cart

    @staticmethod
    def add_item_to_cart(
        db: Session, cart_id: int, item_data: CartItemCreate
    ) -> CartItem:
        """Add item to cart"""
        # Check if item already exists in cart
        existing_item = (
            db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id, CartItem.product_id == item_data.product_id
            )
            .first()
        )

        if existing_item:
            # Update quantity
            existing_item.quantity += item_data.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                price=item_data.price,
                quantity=item_data.quantity,
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item

    @staticmethod
    def get_cart_items(db: Session, cart_id: int) -> List[CartItem]:
        """Get all items in cart"""
        return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    @staticmethod
    def remove_item_from_cart(db: Session, cart_item_id: int) -> bool:
        """Remove item from cart"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if not cart_item:
            return False

        db.delete(cart_item)
        db.commit()
        return True

    @staticmethod
    def update_item_quantity(
        db: Session, cart_item_id: int, quantity: int
    ) -> Optional[CartItem]:
        """Update cart item quantity"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if not cart_item:
            return None

        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def clear_cart(db: Session, cart_id: int) -> bool:
        """Remove all items from cart"""
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.commit()
        return True
