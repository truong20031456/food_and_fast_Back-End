"""
Cart Service for Order Management
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from models.cart import Cart, CartItem
from schemas.cart_schemas import CartCreate, CartItemCreate


class CartNotFoundException(Exception):
    """Exception raised when cart is not found"""

    pass


class CartItemNotFoundException(Exception):
    """Exception raised when cart item is not found"""

    pass


class CartService:
    """Service for managing shopping carts with full error handling"""

    @staticmethod
    def get_or_create_cart(
        db: Session, user_id: Optional[int] = None, session_id: Optional[str] = None
    ) -> Cart:
        """
        Get existing cart or create new one.

        Args:
            db: Database session
            user_id: User ID (for authenticated users)
            session_id: Session ID (for guest users)

        Returns:
            Cart: Active cart for user/session

        Raises:
            ValueError: If neither user_id nor session_id provided
            SQLAlchemyError: Database error
        """
        if not user_id and not session_id:
            raise ValueError("Either user_id or session_id must be provided")

        try:
            if user_id:
                cart = (
                    db.query(Cart)
                    .filter(Cart.user_id == user_id, Cart.status == "active")
                    .first()
                )
            else:
                cart = (
                    db.query(Cart)
                    .filter(Cart.session_id == session_id, Cart.status == "active")
                    .first()
                )

            if not cart:
                cart = Cart(user_id=user_id, session_id=session_id, status="active")
                db.add(cart)
                db.commit()
                db.refresh(cart)

            return cart

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def add_item_to_cart(
        db: Session, cart_id: int, item_data: CartItemCreate
    ) -> CartItem:
        """
        Add item to cart or update quantity if exists.

        Args:
            db: Database session
            cart_id: Cart ID
            item_data: Item data to add

        Returns:
            CartItem: Added or updated cart item

        Raises:
            CartNotFoundException: If cart not found
            SQLAlchemyError: Database error
        """
        try:
            # Verify cart exists
            cart = db.query(Cart).filter(Cart.id == cart_id).first()
            if not cart:
                raise CartNotFoundException(f"Cart with ID {cart_id} not found")

            # Check if item already exists in cart
            existing_item = (
                db.query(CartItem)
                .filter(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == item_data.product_id,
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

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_cart_items(db: Session, cart_id: int) -> List[CartItem]:
        """
        Get all items in cart.

        Args:
            db: Database session
            cart_id: Cart ID

        Returns:
            List[CartItem]: List of cart items

        Raises:
            CartNotFoundException: If cart not found
        """
        # Verify cart exists
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise CartNotFoundException(f"Cart with ID {cart_id} not found")

        return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    @staticmethod
    def remove_item_from_cart(db: Session, cart_item_id: int) -> bool:
        """
        Remove item from cart.

        Args:
            db: Database session
            cart_item_id: Cart item ID

        Returns:
            bool: True if removed successfully

        Raises:
            CartItemNotFoundException: If cart item not found
            SQLAlchemyError: Database error
        """
        try:
            cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
            if not cart_item:
                raise CartItemNotFoundException(
                    f"Cart item with ID {cart_item_id} not found"
                )

            db.delete(cart_item)
            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def update_item_quantity(
        db: Session, cart_item_id: int, quantity: int
    ) -> Optional[CartItem]:
        """
        Update cart item quantity.

        Args:
            db: Database session
            cart_item_id: Cart item ID
            quantity: New quantity (must be > 0)

        Returns:
            Optional[CartItem]: Updated cart item

        Raises:
            CartItemNotFoundException: If cart item not found
            ValueError: If quantity <= 0
            SQLAlchemyError: Database error
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        try:
            cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
            if not cart_item:
                raise CartItemNotFoundException(
                    f"Cart item with ID {cart_item_id} not found"
                )

            cart_item.quantity = quantity
            db.commit()
            db.refresh(cart_item)
            return cart_item

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def clear_cart(db: Session, cart_id: int) -> bool:
        """
        Remove all items from cart.

        Args:
            db: Database session
            cart_id: Cart ID

        Returns:
            bool: True if cleared successfully

        Raises:
            CartNotFoundException: If cart not found
            SQLAlchemyError: Database error
        """
        try:
            # Verify cart exists
            cart = db.query(Cart).filter(Cart.id == cart_id).first()
            if not cart:
                raise CartNotFoundException(f"Cart with ID {cart_id} not found")

            db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_cart_total(db: Session, cart_id: int) -> float:
        """
        Calculate total amount for cart.

        Args:
            db: Database session
            cart_id: Cart ID

        Returns:
            float: Total amount

        Raises:
            CartNotFoundException: If cart not found
        """
        items = CartService.get_cart_items(db, cart_id)
        return sum(item.price * item.quantity for item in items)

    @staticmethod
    def merge_carts(db: Session, source_cart_id: int, target_cart_id: int) -> bool:
        """
        Merge items from source cart to target cart (useful when user logs in).

        Args:
            db: Database session
            source_cart_id: Source cart ID (e.g., guest cart)
            target_cart_id: Target cart ID (e.g., user cart)

        Returns:
            bool: True if merged successfully

        Raises:
            CartNotFoundException: If either cart not found
            SQLAlchemyError: Database error
        """
        try:
            source_items = CartService.get_cart_items(db, source_cart_id)

            for item in source_items:
                # Try to add to target cart (will merge if product exists)
                item_data = CartItemCreate(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=item.price,
                    quantity=item.quantity,
                )
                CartService.add_item_to_cart(db, target_cart_id, item_data)

            # Clear source cart after merge
            CartService.clear_cart(db, source_cart_id)

            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e
