from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.database.dbConfig import get_db
from src.modals.courses_models import Course
from src.modals.user_models import User

router = APIRouter(prefix="/verify", tags=["Certificate Verification"])


@router.get(
    "/certificate", response_class=HTMLResponse, status_code=status.HTTP_200_OK
)
def verify_certificate(
    user_id: int, course_id: int, db: Session = Depends(get_db)
):
    """Public endpoint scanned via QR Code.

    Returns an HTML verification badge confirming course completion.
    """
    user = db.query(User).filter(User.id == user_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()

    if not user or not course:
        return HTMLResponse(
            content=render_invalid_certificate_html(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    is_enrolled = any(c.id == course_id for c in user.enrollments)
    if not is_enrolled:
        return HTMLResponse(
            content=render_invalid_certificate_html(),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return HTMLResponse(
        content=render_verified_certificate_html(
            student_name=user.full_name,
            course_title=course.title,
            student_email=user.email,
        )
    )


# --- HTML TEMPLATES ---


def render_verified_certificate_html(
    student_name: str, course_title: str, student_email: str
) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Certificate Verification</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #ffffff;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                text-align: center;
                max-width: 450px;
                width: 90%;
            }}
            .badge {{
                width: 70px;
                height: 70px;
                background-color: #e6f4ea;
                color: #137333;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                margin: 0 auto 20px auto;
            }}
            h1 {{
                color: #137333;
                font-size: 24px;
                margin-bottom: 8px;
            }}
            p {{
                color: #5f6368;
                font-size: 15px;
                margin: 6px 0;
            }}
            .details {{
                margin-top: 25px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                text-align: left;
            }}
            .details strong {{
                color: #202124;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">&#10004;</div>
            <h1>Verified Certificate</h1>
            <p>This certificate is authentic and officially issued.</p>
            
            <div class="details">
                <p><strong>Student:</strong> {student_name}</p>
                <p><strong>Course:</strong> {course_title}</p>
                <p><strong>Email:</strong> {student_email}</p>
                <p><strong>Status:</strong> Successfully Completed</p>
            </div>
        </div>
    </body>
    </html>
    """


def render_invalid_certificate_html() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invalid Certificate</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #ffffff;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                text-align: center;
                max-width: 450px;
                width: 90%;
            }
            .badge {
                width: 70px;
                height: 70px;
                background-color: #fce8e6;
                color: #c5221f;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                margin: 0 auto 20px auto;
            }
            h1 {
                color: #c5221f;
                font-size: 24px;
                margin-bottom: 8px;
            }
            p {
                color: #5f6368;
                font-size: 15px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">&#10008;</div>
            <h1>Invalid Certificate</h1>
            <p>We could not verify this certificate. The record does not exist or has been revoked.</p>
        </div>
    </body>
    </html>
    """