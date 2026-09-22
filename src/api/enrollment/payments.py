import os
import razorpay
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.utils.auth_deps import get_current_user
from src.schemas.payment_schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    PaymentResponse,
)
from src.database.dbConfig import get_db
from src.modals.courses_models import Course
from src.modals.user_models import User
from src.modals.payments_models import Payment  # Ensure your Payment model exists

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_payment_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Step 1: Create a Razorpay order for a specific course."""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check if already enrolled
    if any(c.id == course.id for c in current_user.enrollments):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course",
        )

    # Razorpay expects amount in paise (1 INR = 100 Paise)
    amount_in_paise = int(course.price * 100)

    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "notes": {
            "user_id": str(current_user.id),
            "course_id": str(course.id),
        },
    }

    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Razorpay order creation failed: {str(e)}",
        )

    # Optionally record pending payment in database
    payment = Payment(
        user_id=current_user.id,
        course_id=course.id,
        amount=course.price,
        razorpay_order_id=razorpay_order["id"],
        status="PENDING",
    )
    db.add(payment)
    db.commit()

    return CreateOrderResponse(
        order_id=razorpay_order["id"],
        amount=razorpay_order["amount"],
        currency=razorpay_order["currency"],
        key_id=RAZORPAY_KEY_ID,
        course_id=course.id,
    )


@router.post("/verify-payment", response_model=PaymentResponse)
def verify_payment(
    payload: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Step 2: Verify Razorpay payment signature & enroll user in course."""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # 1. Verify Razorpay Signature
    params_dict = {
        "razorpay_order_id": payload.razorpay_order_id,
        "razorpay_payment_id": payload.razorpay_payment_id,
        "razorpay_signature": payload.razorpay_signature,
    }

    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        # Mark payment as failed in DB if record exists
        payment = (
            db.query(Payment)
            .filter(Payment.razorpay_order_id == payload.razorpay_order_id)
            .first()
        )
        if payment:
            payment.status = "FAILED"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature",
        )

    # 2. Update payment record to SUCCESS
    payment = (
        db.query(Payment)
        .filter(Payment.razorpay_order_id == payload.razorpay_order_id)
        .first()
    )
    if not payment:
        payment = Payment(
            user_id=current_user.id,
            course_id=course.id,
            amount=course.price,
            razorpay_order_id=payload.razorpay_order_id,
        )
        db.add(payment)

    payment.razorpay_payment_id = payload.razorpay_payment_id
    payment.status = "SUCCESS"

    # 3. Enroll user in the course
    if course not in current_user.enrollments:
        current_user.enrollments.append(course)

    db.commit()
    db.refresh(payment)

    return payment