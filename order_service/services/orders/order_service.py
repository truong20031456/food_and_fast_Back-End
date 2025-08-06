from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime
import uuid
from models.order import Order, OrderItem
from schemas.order_schema import (
    OrderCreate,
    OrderUpdate,
    OrderStatusUpdate,
    PaymentStatusUpdate,
)


class OrderNotFoundException(Exception):
    """Exception raised when order is not found"""

    pass


class OrderService:
    """Service for managing orders with full business logic"""

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: OrderCreate) -> Order:
        """
        Tạo đơn hàng mới với validation và transaction safety.

        Args:
            order_data: Dữ liệu đơn hàng từ request

        Returns:
            Order: Đơn hàng đã tạo

        Raises:
            SQLAlchemyError: Lỗi database
        """
        try:
            # Generate unique order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

            # Calculate total amount from items
            total_amount = sum(item.price * item.quantity for item in order_data.items)

            # Create order
            order = Order(
                order_number=order_number,
                user_id=order_data.user_id,
                restaurant_id=order_data.restaurant_id,
                total_amount=total_amount,
                delivery_fee=order_data.delivery_fee or 0,
                tax_amount=order_data.tax_amount or 0,
                delivery_address=order_data.delivery_address,
                phone_number=order_data.phone_number,
                special_instructions=order_data.special_instructions,
                status="pending",
                payment_status="pending",
                created_at=datetime.now(),
            )

            self.db.add(order)
            self.db.flush()  # Get order ID before adding items

            # Create order items
            for item_data in order_data.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data.product_id,
                    product_name=item_data.product_name,
                    price=item_data.price,
                    quantity=item_data.quantity,
                )
                self.db.add(order_item)

            self.db.commit()
            self.db.refresh(order)
            return order

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_order(self, order_id: int) -> Optional[Order]:
        """
        Lấy thông tin đơn hàng theo ID.

        Args:
            order_id: ID của đơn hàng

        Returns:
            Optional[Order]: Đơn hàng nếu tìm thấy, None nếu không
        """
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """
        Lấy thông tin đơn hàng theo order number.

        Args:
            order_number: Số đơn hàng

        Returns:
            Optional[Order]: Đơn hàng nếu tìm thấy, None nếu không
        """
        return self.db.query(Order).filter(Order.order_number == order_number).first()

    def get_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Lấy danh sách đơn hàng có phân trang.

        Args:
            skip: Số record bỏ qua
            limit: Số record tối đa trả về

        Returns:
            List[Order]: Danh sách đơn hàng
        """
        return self.db.query(Order).offset(skip).limit(limit).all()

    def get_orders_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> List[Order]:
        """
        Lấy danh sách đơn hàng của user có phân trang.

        Args:
            user_id: ID của user
            skip: Số record bỏ qua
            limit: Số record tối đa trả về

        Returns:
            List[Order]: Danh sách đơn hàng của user
        """
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Lấy danh sách đơn hàng theo trạng thái.

        Args:
            status: Trạng thái đơn hàng
            skip: Số record bỏ qua
            limit: Số record tối đa trả về

        Returns:
            List[Order]: Danh sách đơn hàng theo trạng thái
        """
        return (
            self.db.query(Order)
            .filter(Order.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_order_status(
        self, order_id: int, status_data: OrderStatusUpdate
    ) -> Optional[Order]:
        """
        Cập nhật trạng thái đơn hàng.

        Args:
            order_id: ID của đơn hàng
            status_data: Dữ liệu cập nhật trạng thái

        Returns:
            Optional[Order]: Đơn hàng đã cập nhật, None nếu không tìm thấy

        Raises:
            OrderNotFoundException: Không tìm thấy đơn hàng
        """
        order = self.get_order(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")

        try:
            order.status = status_data.status

            # Update timestamp based on status
            if status_data.status == "confirmed":
                order.confirmed_at = datetime.now()
            elif status_data.status == "preparing":
                order.preparing_at = datetime.now()
            elif status_data.status == "out_for_delivery":
                order.out_for_delivery_at = datetime.now()
            elif status_data.status == "delivered":
                order.delivered_at = datetime.now()
            elif status_data.status == "cancelled":
                order.cancelled_at = datetime.now()

            order.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(order)
            return order

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update_payment_status(
        self, order_id: int, payment_data: PaymentStatusUpdate
    ) -> Optional[Order]:
        """
        Cập nhật trạng thái thanh toán đơn hàng.

        Args:
            order_id: ID của đơn hàng
            payment_data: Dữ liệu cập nhật trạng thái thanh toán

        Returns:
            Optional[Order]: Đơn hàng đã cập nhật, None nếu không tìm thấy
        """
        order = self.get_order(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")

        try:
            order.payment_status = payment_data.payment_status
            order.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(order)
            return order

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def cancel_order(self, order_id: int, user_id: int) -> Optional[Order]:
        """
        Hủy đơn hàng (chỉ cho phép chủ đơn hàng).

        Args:
            order_id: ID của đơn hàng
            user_id: ID của user (để kiểm tra quyền)

        Returns:
            Optional[Order]: Đơn hàng đã hủy, None nếu không thể hủy

        Raises:
            OrderNotFoundException: Không tìm thấy đơn hàng
            PermissionError: Không có quyền hủy đơn hàng
        """
        order = self.get_order(order_id)
        if not order:
            raise OrderNotFoundException(f"Order with ID {order_id} not found")

        # Check permission
        if order.user_id != user_id:
            raise PermissionError("You don't have permission to cancel this order")

        # Check if order can be cancelled
        if order.status in ["delivered", "cancelled"]:
            return None

        try:
            order.status = "cancelled"
            order.cancelled_at = datetime.now()
            order.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(order)
            return order

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete_order(self, order_id: int) -> bool:
        """
        Xóa đơn hàng (chỉ dành cho admin, không khuyến khích dùng).

        Args:
            order_id: ID của đơn hàng

        Returns:
            bool: True nếu xóa thành công, False nếu không tìm thấy
        """
        order = self.get_order(order_id)
        if not order:
            return False

        try:
            # Delete order items first (foreign key constraint)
            self.db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

            # Delete order
            self.db.delete(order)
            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
