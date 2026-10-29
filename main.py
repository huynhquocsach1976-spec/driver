import os
from google import genai

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =========================================================
# CẤU HÌNH
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Không tìm thấy DATABASE_URL trong file .env")


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="AI Driving Center Pro",
    description="Backend quản lý trung tâm đào tạo lái xe",
    version="1.0.0"
)

# ===== CORS: cho phep frontend Streamlit goi API tu moi domain =====
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sau nay thay bang domain Streamlit cu the de tang bao mat
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# =========================================================
# KẾT NỐI DATABASE
# =========================================================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


# =========================================================
# API TRANG CHỦ
# =========================================================

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "AI Driving Center Pro Backend đang chạy!"
    }


# =========================================================
# TEST DATABASE
# =========================================================

@app.get("/db-test")
def db_test():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "database": "Supabase PostgreSQL",
            "version": result[0]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DANH SÁCH HỌC VIÊN
# =========================================================

@app.get("/students")
def get_students():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                student_code,
                full_name,
                phone,
                date_of_birth,
                address,
                license_class,
                enrollment_date,
                tuition_fee,
                status,
                teacher_id,
                created_at
            FROM students
            ORDER BY id;
        """)

        students = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(students),
            "data": students
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DANH SÁCH GIÁO VIÊN
# =========================================================

@app.get("/teachers")
def get_teachers():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                teacher_code,
                full_name,
                phone,
                license_number,
                status,
                created_at
            FROM teachers
            ORDER BY id;
        """)

        teachers = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(teachers),
            "data": teachers
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# THÊM GIÁO VIÊN
# =========================================================

from pydantic import BaseModel
from typing import Optional


class TeacherCreate(BaseModel):
    teacher_code: str
    full_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    status: str = "active"


@app.post("/teachers")
def create_teacher(teacher: TeacherCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra mã giáo viên đã tồn tại chưa
        cursor.execute(
            """
            SELECT id
            FROM teachers
            WHERE teacher_code = %s
            """,
            (teacher.teacher_code,)
        )

        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Mã giáo viên đã tồn tại"
            )

        # Thêm giáo viên
        cursor.execute(
            """
            INSERT INTO teachers
            (
                teacher_code,
                full_name,
                phone,
                license_number,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                id,
                teacher_code,
                full_name,
                phone,
                license_number,
                status,
                created_at
            """,
            (
                teacher.teacher_code,
                teacher.full_name,
                teacher.phone,
                teacher.license_number,
                teacher.status
            )
        )

        new_teacher = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Thêm giáo viên thành công",
            "data": new_teacher
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# SỬA GIÁO VIÊN
# =========================================================

@app.put("/teachers/{teacher_id}")
def update_teacher(teacher_id: int, teacher: TeacherCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra giáo viên có tồn tại không
        cursor.execute(
            """
            SELECT id
            FROM teachers
            WHERE id = %s
            """,
            (teacher_id,)
        )

        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giáo viên"
            )

        # Kiểm tra mã giáo viên có bị trùng với giáo viên khác không
        cursor.execute(
            """
            SELECT id
            FROM teachers
            WHERE teacher_code = %s
              AND id <> %s
            """,
            (
                teacher.teacher_code,
                teacher_id
            )
        )

        duplicate = cursor.fetchone()

        if duplicate:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Mã giáo viên đã tồn tại"
            )

        # Cập nhật
        cursor.execute(
            """
            UPDATE teachers
            SET
                teacher_code = %s,
                full_name = %s,
                phone = %s,
                license_number = %s,
                status = %s
            WHERE id = %s
            RETURNING
                id,
                teacher_code,
                full_name,
                phone,
                license_number,
                status,
                created_at
            """,
            (
                teacher.teacher_code,
                teacher.full_name,
                teacher.phone,
                teacher.license_number,
                teacher.status,
                teacher_id
            )
        )

        updated_teacher = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật giáo viên thành công",
            "data": updated_teacher
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# XÓA GIÁO VIÊN
# =========================================================

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra giáo viên
        cursor.execute(
            """
            SELECT id, teacher_code, full_name
            FROM teachers
            WHERE id = %s
            """,
            (teacher_id,)
        )

        teacher = cursor.fetchone()

        if not teacher:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giáo viên"
            )

        # Kiểm tra giáo viên đang được sử dụng bởi học viên
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM students
            WHERE teacher_id = %s
            """,
            (teacher_id,)
        )

        student_count = cursor.fetchone()["total"]

        if student_count > 0:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa giáo viên vì đang phụ trách {student_count} học viên"
            )

        # Xóa giáo viên
        cursor.execute(
            """
            DELETE FROM teachers
            WHERE id = %s
            """,
            (teacher_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa giáo viên thành công",
            "data": teacher
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# THÊM XE
# =========================================================

class VehicleCreate(BaseModel):
    plate_number: str
    brand: Optional[str] = None
    model: Optional[str] = None
    license_class: Optional[str] = None
    year: Optional[int] = None
    status: str = "active"


@app.post("/vehicles")
def create_vehicle(vehicle: VehicleCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra biển số đã tồn tại chưa
        cursor.execute(
            """
            SELECT id
            FROM vehicles
            WHERE plate_number = %s
            """,
            (vehicle.plate_number,)
        )

        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Biển số xe đã tồn tại"
            )

        # Thêm xe
        cursor.execute(
            """
            INSERT INTO vehicles
            (
                plate_number,
                brand,
                model,
                license_class,
                year,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                plate_number,
                brand,
                model,
                license_class,
                year,
                status,
                created_at
            """,
            (
                vehicle.plate_number,
                vehicle.brand,
                vehicle.model,
                vehicle.license_class,
                vehicle.year,
                vehicle.status
            )
        )

        new_vehicle = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Thêm xe thành công",
            "data": new_vehicle
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# SỬA XE
# =========================================================

@app.put("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, vehicle: VehicleCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra xe có tồn tại không
        cursor.execute(
            """
            SELECT id
            FROM vehicles
            WHERE id = %s
            """,
            (vehicle_id,)
        )

        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy xe"
            )

        # Kiểm tra biển số có bị trùng với xe khác không
        cursor.execute(
            """
            SELECT id
            FROM vehicles
            WHERE plate_number = %s
              AND id <> %s
            """,
            (
                vehicle.plate_number,
                vehicle_id
            )
        )

        duplicate = cursor.fetchone()

        if duplicate:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Biển số xe đã tồn tại"
            )

        # Cập nhật xe
        cursor.execute(
            """
            UPDATE vehicles
            SET
                plate_number = %s,
                brand = %s,
                model = %s,
                license_class = %s,
                year = %s,
                status = %s
            WHERE id = %s
            RETURNING
                id,
                plate_number,
                brand,
                model,
                license_class,
                year,
                status,
                created_at
            """,
            (
                vehicle.plate_number,
                vehicle.brand,
                vehicle.model,
                vehicle.license_class,
                vehicle.year,
                vehicle.status,
                vehicle_id
            )
        )

        updated_vehicle = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật xe thành công",
            "data": updated_vehicle
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# XÓA XE
# =========================================================

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra xe có tồn tại không
        cursor.execute(
            """
            SELECT id, plate_number, brand, model
            FROM vehicles
            WHERE id = %s
            """,
            (vehicle_id,)
        )

        vehicle = cursor.fetchone()

        if not vehicle:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy xe"
            )

        # Kiểm tra xe có đang được sử dụng trong buổi học không
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM lessons
            WHERE vehicle_id = %s
            """,
            (vehicle_id,)
        )

        lesson_count = cursor.fetchone()["total"]

        if lesson_count > 0:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa xe vì xe đang được sử dụng trong {lesson_count} buổi học"
            )

        # Xóa xe
        cursor.execute(
            """
            DELETE FROM vehicles
            WHERE id = %s
            """,
            (vehicle_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa xe thành công",
            "data": vehicle
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# THÊM BUỔI HỌC
# =========================================================

class LessonCreate(BaseModel):
    student_id: int
    teacher_id: int
    vehicle_id: Optional[int] = None
    lesson_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: float = 0
    lesson_type: Optional[str] = None
    content: Optional[str] = None
    notes: Optional[str] = None


@app.post("/lessons")
def create_lesson(lesson: LessonCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra học viên
        cursor.execute(
            """
            SELECT id, full_name
            FROM students
            WHERE id = %s
            """,
            (lesson.student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # Kiểm tra giáo viên
        cursor.execute(
            """
            SELECT id, full_name
            FROM teachers
            WHERE id = %s
            """,
            (lesson.teacher_id,)
        )

        teacher = cursor.fetchone()

        if not teacher:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giáo viên"
            )

        # Kiểm tra xe nếu có chọn xe
        if lesson.vehicle_id is not None:

            cursor.execute(
                """
                SELECT id, plate_number
                FROM vehicles
                WHERE id = %s
                """,
                (lesson.vehicle_id,)
            )

            vehicle = cursor.fetchone()

            if not vehicle:
                cursor.close()
                conn.close()

                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy xe"
                )

        # Thêm buổi học
        cursor.execute(
            """
            INSERT INTO lessons
            (
                student_id,
                teacher_id,
                vehicle_id,
                lesson_date,
                start_time,
                end_time,
                duration,
                lesson_type,
                content,
                notes
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            RETURNING
                id,
                student_id,
                teacher_id,
                vehicle_id,
                lesson_date,
                start_time,
                end_time,
                duration,
                lesson_type,
                content,
                notes,
                created_at
            """,
            (
                lesson.student_id,
                lesson.teacher_id,
                lesson.vehicle_id,
                lesson.lesson_date,
                lesson.start_time,
                lesson.end_time,
                lesson.duration,
                lesson.lesson_type,
                lesson.content,
                lesson.notes
            )
        )

        new_lesson = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Thêm buổi học thành công",
            "data": new_lesson
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# SỬA BUỔI HỌC
# =========================================================

@app.put("/lessons/{lesson_id}")
def update_lesson(lesson_id: int, lesson: LessonCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra buổi học
        cursor.execute(
            """
            SELECT id
            FROM lessons
            WHERE id = %s
            """,
            (lesson_id,)
        )

        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy buổi học"
            )

        # Kiểm tra học viên
        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
            """,
            (lesson.student_id,)
        )

        if not cursor.fetchone():
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # Kiểm tra giáo viên
        cursor.execute(
            """
            SELECT id
            FROM teachers
            WHERE id = %s
            """,
            (lesson.teacher_id,)
        )

        if not cursor.fetchone():
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giáo viên"
            )

        # Kiểm tra xe nếu có
        if lesson.vehicle_id is not None:

            cursor.execute(
                """
                SELECT id
                FROM vehicles
                WHERE id = %s
                """,
                (lesson.vehicle_id,)
            )

            if not cursor.fetchone():
                cursor.close()
                conn.close()

                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy xe"
                )

        # Cập nhật buổi học
        cursor.execute(
            """
            UPDATE lessons
            SET
                student_id = %s,
                teacher_id = %s,
                vehicle_id = %s,
                lesson_date = %s,
                start_time = %s,
                end_time = %s,
                duration = %s,
                lesson_type = %s,
                content = %s,
                notes = %s
            WHERE id = %s
            RETURNING
                id,
                student_id,
                teacher_id,
                vehicle_id,
                lesson_date,
                start_time,
                end_time,
                duration,
                lesson_type,
                content,
                notes,
                created_at
            """,
            (
                lesson.student_id,
                lesson.teacher_id,
                lesson.vehicle_id,
                lesson.lesson_date,
                lesson.start_time,
                lesson.end_time,
                lesson.duration,
                lesson.lesson_type,
                lesson.content,
                lesson.notes,
                lesson_id
            )
        )

        updated_lesson = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật buổi học thành công",
            "data": updated_lesson
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# XÓA BUỔI HỌC
# =========================================================

@app.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra buổi học
        cursor.execute(
            """
            SELECT
                id,
                student_id,
                teacher_id,
                vehicle_id,
                lesson_date,
                lesson_type
            FROM lessons
            WHERE id = %s
            """,
            (lesson_id,)
        )

        lesson = cursor.fetchone()

        if not lesson:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy buổi học"
            )

        # Xóa đánh giá liên quan nếu có
        cursor.execute(
            """
            DELETE FROM evaluations
            WHERE lesson_id = %s
            """,
            (lesson_id,)
        )

        # Xóa buổi học
        cursor.execute(
            """
            DELETE FROM lessons
            WHERE id = %s
            """,
            (lesson_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa buổi học thành công",
            "data": lesson
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# THÊM ĐÁNH GIÁ HỌC VIÊN
# =========================================================

class EvaluationCreate(BaseModel):
    lesson_id: int
    student_id: int
    teacher_id: Optional[int] = None

    vehicle_control: Optional[float] = None
    braking: Optional[float] = None
    lane_change: Optional[float] = None
    observation: Optional[float] = None
    parking: Optional[float] = None
    traffic_rules: Optional[float] = None

    score: Optional[float] = None
    comment: Optional[str] = None
    ai_comment: Optional[str] = None


@app.post("/evaluations")
def create_evaluation(evaluation: EvaluationCreate):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra buổi học
        cursor.execute(
            """
            SELECT id
            FROM lessons
            WHERE id = %s
            """,
            (evaluation.lesson_id,)
        )

        lesson = cursor.fetchone()

        if not lesson:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy buổi học"
            )

        # Kiểm tra học viên
        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
            """,
            (evaluation.student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # Kiểm tra giáo viên nếu có
        if evaluation.teacher_id is not None:

            cursor.execute(
                """
                SELECT id
                FROM teachers
                WHERE id = %s
                """,
                (evaluation.teacher_id,)
            )

            teacher = cursor.fetchone()

            if not teacher:
                cursor.close()
                conn.close()

                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy giáo viên"
                )

        # Kiểm tra buổi học đã có đánh giá chưa
        cursor.execute(
            """
            SELECT id
            FROM evaluations
            WHERE lesson_id = %s
            """,
            (evaluation.lesson_id,)
        )

        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Buổi học này đã có đánh giá"
            )

        # Thêm đánh giá
        cursor.execute(
            """
            INSERT INTO evaluations
            (
                lesson_id,
                student_id,
                teacher_id,
                vehicle_control,
                braking,
                lane_change,
                observation,
                parking,
                traffic_rules,
                score,
                comment,
                ai_comment
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            RETURNING
                id,
                lesson_id,
                student_id,
                teacher_id,
                vehicle_control,
                braking,
                lane_change,
                observation,
                parking,
                traffic_rules,
                score,
                comment,
                ai_comment,
                created_at
            """,
            (
                evaluation.lesson_id,
                evaluation.student_id,
                evaluation.teacher_id,
                evaluation.vehicle_control,
                evaluation.braking,
                evaluation.lane_change,
                evaluation.observation,
                evaluation.parking,
                evaluation.traffic_rules,
                evaluation.score,
                evaluation.comment,
                evaluation.ai_comment
            )
        )

        new_evaluation = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Thêm đánh giá thành công",
            "data": new_evaluation
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DANH SÁCH XE
# =========================================================

@app.get("/vehicles")
def get_vehicles():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                id,
                plate_number,
                brand,
                model,
                license_class,
                year,
                status,
                created_at
            FROM vehicles
            ORDER BY id;
        """)

        vehicles = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(vehicles),
            "data": vehicles
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# DANH SÁCH BUỔI HỌC
# =========================================================

@app.get("/lessons")
def get_lessons():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                l.id,
                l.student_id,
                s.student_code,
                s.full_name AS student_name,
                l.teacher_id,
                t.teacher_code,
                t.full_name AS teacher_name,
                l.vehicle_id,
                v.plate_number,
                l.lesson_date,
                l.start_time,
                l.end_time,
                l.duration,
                l.lesson_type,
                l.content,
                l.notes
            FROM lessons l
            JOIN students s ON l.student_id = s.id
            JOIN teachers t ON l.teacher_id = t.id
            LEFT JOIN vehicles v ON l.vehicle_id = v.id
            ORDER BY l.lesson_date, l.id;
        """)

        lessons = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(lessons),
            "data": lessons
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DANH SÁCH ĐÁNH GIÁ
# =========================================================

@app.get("/evaluations")
def get_evaluations():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                e.id,
                e.lesson_id,
                e.student_id,
                s.student_code,
                s.full_name AS student_name,
                e.teacher_id,
                e.vehicle_control,
                e.braking,
                e.lane_change,
                e.observation,
                e.parking,
                e.traffic_rules,
                e.score,
                e.comment,
                e.ai_comment,
                e.created_at
            FROM evaluations e
            JOIN students s ON e.student_id = s.id
            ORDER BY e.id;
        """)

        evaluations = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(evaluations),
            "data": evaluations
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# CẬP NHẬT ĐÁNH GIÁ HỌC VIÊN
# =========================================================

@app.put("/evaluations/{evaluation_id}")
def update_evaluation(
    evaluation_id: int,
    evaluation: EvaluationCreate
):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra đánh giá
        cursor.execute(
            """
            SELECT id
            FROM evaluations
            WHERE id = %s
            """,
            (evaluation_id,)
        )

        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đánh giá"
            )

        # Kiểm tra buổi học
        cursor.execute(
            """
            SELECT id
            FROM lessons
            WHERE id = %s
            """,
            (evaluation.lesson_id,)
        )

        lesson = cursor.fetchone()

        if not lesson:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy buổi học"
            )

        # Kiểm tra học viên
        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
            """,
            (evaluation.student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # Kiểm tra giáo viên nếu có
        if evaluation.teacher_id is not None:

            cursor.execute(
                """
                SELECT id
                FROM teachers
                WHERE id = %s
                """,
                (evaluation.teacher_id,)
            )

            teacher = cursor.fetchone()

            if not teacher:
                cursor.close()
                conn.close()

                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy giáo viên"
                )

        # Kiểm tra lesson đã thuộc đánh giá khác chưa
        cursor.execute(
            """
            SELECT id
            FROM evaluations
            WHERE lesson_id = %s
            AND id <> %s
            """,
            (
                evaluation.lesson_id,
                evaluation_id
            )
        )

        duplicate = cursor.fetchone()

        if duplicate:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Buổi học này đã có đánh giá khác"
            )

        # Cập nhật đánh giá
        cursor.execute(
            """
            UPDATE evaluations
            SET
                lesson_id = %s,
                student_id = %s,
                teacher_id = %s,
                vehicle_control = %s,
                braking = %s,
                lane_change = %s,
                observation = %s,
                parking = %s,
                traffic_rules = %s,
                score = %s,
                comment = %s,
                ai_comment = %s
            WHERE id = %s
            RETURNING
                id,
                lesson_id,
                student_id,
                teacher_id,
                vehicle_control,
                braking,
                lane_change,
                observation,
                parking,
                traffic_rules,
                score,
                comment,
                ai_comment,
                created_at
            """,
            (
                evaluation.lesson_id,
                evaluation.student_id,
                evaluation.teacher_id,
                evaluation.vehicle_control,
                evaluation.braking,
                evaluation.lane_change,
                evaluation.observation,
                evaluation.parking,
                evaluation.traffic_rules,
                evaluation.score,
                evaluation.comment,
                evaluation.ai_comment,
                evaluation_id
            )
        )

        updated_evaluation = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật đánh giá thành công",
            "data": updated_evaluation
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# XÓA ĐÁNH GIÁ HỌC VIÊN
# =========================================================

@app.delete("/evaluations/{evaluation_id}")
def delete_evaluation(evaluation_id: int):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra đánh giá
        cursor.execute(
            """
            SELECT
                id,
                lesson_id,
                student_id,
                teacher_id,
                score,
                comment
            FROM evaluations
            WHERE id = %s
            """,
            (evaluation_id,)
        )

        evaluation = cursor.fetchone()

        if not evaluation:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đánh giá"
            )

        # Xóa đánh giá
        cursor.execute(
            """
            DELETE FROM evaluations
            WHERE id = %s
            """,
            (evaluation_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa đánh giá thành công",
            "data": evaluation
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DANH SÁCH THANH TOÁN
# =========================================================

@app.get("/payments")
def get_payments():

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                p.id,
                p.student_id,
                s.student_code,
                s.full_name AS student_name,
                s.tuition_fee,
                p.amount,
                p.payment_date,
                p.payment_method,
                p.note,
                p.created_at
            FROM payments p
            JOIN students s ON p.student_id = s.id
            ORDER BY p.payment_date, p.id;
        """)

        payments = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(payments),
            "data": payments
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# THÊM HỌC VIÊN
# =========================================================

from pydantic import BaseModel
from typing import Optional
from datetime import date


class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    license_class: str
    enrollment_date: Optional[date] = None
    tuition_fee: float = 0
    status: str = "Đang học"
    teacher_id: Optional[int] = None


@app.post("/students")
def create_student(student: StudentCreate):

    try:

        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # Kiểm tra mã học viên đã tồn tại chưa
        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE student_code = %s
            """,
            (student.student_code,)
        )

        existing_student = cursor.fetchone()

        if existing_student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Mã học viên đã tồn tại"
            )

        # Thêm học viên
        cursor.execute(
            """
            INSERT INTO students (
                student_code,
                full_name,
                phone,
                date_of_birth,
                address,
                license_class,
                enrollment_date,
                tuition_fee,
                status,
                teacher_id
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, COALESCE(%s, CURRENT_DATE),
                %s, %s, %s
            )
            RETURNING
                id,
                student_code,
                full_name,
                phone,
                date_of_birth,
                address,
                license_class,
                enrollment_date,
                tuition_fee,
                status,
                teacher_id,
                created_at
            """,
            (
                student.student_code,
                student.full_name,
                student.phone,
                student.date_of_birth,
                student.address,
                student.license_class,
                student.enrollment_date,
                student.tuition_fee,
                student.status,
                student.teacher_id
            )
        )

        new_student = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Thêm học viên thành công",
            "data": new_student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# SỬA THÔNG TIN HỌC VIÊN
# =========================================================

@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        existing_student = cursor.fetchone()

        if not existing_student:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        cursor.execute(
            """
            UPDATE students
            SET
                student_code = %s,
                full_name = %s,
                phone = %s,
                date_of_birth = %s,
                address = %s,
                license_class = %s,
                enrollment_date = COALESCE(%s, enrollment_date),
                tuition_fee = %s,
                status = %s,
                teacher_id = %s
            WHERE id = %s
            RETURNING
                id,
                student_code,
                full_name,
                phone,
                date_of_birth,
                address,
                license_class,
                enrollment_date,
                tuition_fee,
                status,
                teacher_id,
                created_at
            """,
            (
                student.student_code,
                student.full_name,
                student.phone,
                student.date_of_birth,
                student.address,
                student.license_class,
                student.enrollment_date,
                student.tuition_fee,
                student.status,
                student.teacher_id,
                student_id
            )
        )

        updated_student = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật học viên thành công",
            "data": updated_student
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# XÓA HỌC VIÊN
# =========================================================

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra học viên có tồn tại không
        cursor.execute(
            """
            SELECT id, student_code, full_name
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # Xóa học viên
        cursor.execute(
            """
            DELETE FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa học viên thành công",
            "data": student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# TÌM KIẾM HỌC VIÊN
# =========================================================

@app.get("/students/search")
def search_students(keyword: str):

    try:
        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        search = f"%{keyword}%"

        cursor.execute(
            """
            SELECT
                id,
                student_code,
                full_name,
                phone,
                date_of_birth,
                address,
                license_class,
                enrollment_date,
                tuition_fee,
                status,
                teacher_id,
                created_at
            FROM students
            WHERE
                student_code ILIKE %s
                OR full_name ILIKE %s
                OR phone ILIKE %s
            ORDER BY id
            """,
            (
                search,
                search,
                search
            )
        )

        students = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "keyword": keyword,
            "count": len(students),
            "data": students
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# LỌC HỌC VIÊN
# =========================================================

@app.get("/students/filter")
def filter_students(
    license_class: Optional[str] = None,
    status: Optional[str] = None,
    teacher_id: Optional[int] = None
):

    try:
        conn = get_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        query = """
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.phone,
                s.date_of_birth,
                s.address,
                s.license_class,
                s.enrollment_date,
                s.tuition_fee,
                s.status,
                s.teacher_id,
                t.teacher_code,
                t.full_name AS teacher_name,
                s.created_at
            FROM students s
            LEFT JOIN teachers t
                ON s.teacher_id = t.id
            WHERE 1=1
        """

        params = []

        # Lọc theo lớp bằng lái
        if license_class:
            query += """
                AND s.license_class = %s
            """
            params.append(license_class)

        # Lọc theo trạng thái
        if status:
            query += """
                AND s.status = %s
            """
            params.append(status)

        # Lọc theo giáo viên
        if teacher_id:
            query += """
                AND s.teacher_id = %s
            """
            params.append(teacher_id)

        query += """
            ORDER BY s.id
        """

        cursor.execute(
            query,
            tuple(params)
        )

        students = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "count": len(students),
            "data": students
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =========================================================
# DASHBOARD NÂNG CAO
# =========================================================

@app.get("/dashboard")
def dashboard():

    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # -------------------------------------------------
        # 1. Tổng quan
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_students
            FROM students
        """)
        total_students = cursor.fetchone()["total_students"]

        cursor.execute("""
            SELECT COUNT(*) AS total_teachers
            FROM teachers
        """)
        total_teachers = cursor.fetchone()["total_teachers"]

        cursor.execute("""
            SELECT COUNT(*) AS total_vehicles
            FROM vehicles
        """)
        total_vehicles = cursor.fetchone()["total_vehicles"]

        cursor.execute("""
            SELECT
                COUNT(*) AS total_lessons,
                COALESCE(SUM(duration), 0) AS total_hours
            FROM lessons
        """)
        lesson_data = cursor.fetchone()

        total_lessons = lesson_data["total_lessons"]
        total_hours = lesson_data["total_hours"]

        # -------------------------------------------------
        # 2. Học phí
        # -------------------------------------------------

        cursor.execute("""
            SELECT COALESCE(SUM(tuition_fee), 0) AS total_tuition
            FROM students
        """)
        total_tuition = cursor.fetchone()["total_tuition"]

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total_paid
            FROM payments
        """)
        total_paid = cursor.fetchone()["total_paid"]

        total_remaining = total_tuition - total_paid

        # -------------------------------------------------
        # 3. Học viên theo giáo viên
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                t.id AS teacher_id,
                t.teacher_code,
                t.full_name,
                COUNT(s.id) AS total_students
            FROM teachers t
            LEFT JOIN students s
                ON s.teacher_id = t.id
            GROUP BY
                t.id,
                t.teacher_code,
                t.full_name
            ORDER BY t.id
        """)

        students_by_teacher = cursor.fetchall()

        # -------------------------------------------------
        # 4. Điểm đánh giá trung bình
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*) AS total_evaluations,
                COALESCE(AVG(score), 0) AS average_score
            FROM evaluations
        """)

        evaluation_data = cursor.fetchone()

        total_evaluations = evaluation_data["total_evaluations"]
        average_score = evaluation_data["average_score"]

        # -------------------------------------------------
        # Đóng kết nối
        # -------------------------------------------------

        cursor.close()
        conn.close()

        # -------------------------------------------------
        # Trả kết quả
        # -------------------------------------------------

        return {
            "status": "ok",
            "data": {
                "overview": {
                    "total_students": total_students,
                    "total_teachers": total_teachers,
                    "total_vehicles": total_vehicles,
                    "total_lessons": total_lessons,
                    "total_hours": float(total_hours),
                    "total_tuition": float(total_tuition),
                    "total_paid": float(total_paid),
                    "total_remaining": float(total_remaining)
                },

                "evaluations": {
                    "total_evaluations": total_evaluations,
                    "average_score": round(float(average_score), 2)
                },

                "students_by_teacher": students_by_teacher
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# AI ĐÁNH GIÁ HỌC VIÊN
# =========================================================

@app.post("/evaluations/{evaluation_id}/ai")
def ai_evaluate_student(evaluation_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT
                e.id,
                e.student_id,
                e.vehicle_control,
                e.braking,
                e.lane_change,
                e.observation,
                e.parking,
                e.traffic_rules,
                e.score,
                e.comment,
                s.full_name AS student_name,
                s.license_class
            FROM evaluations e
            JOIN students s
                ON s.id = e.student_id
            WHERE e.id = %s
            """,
            (evaluation_id,)
        )

        evaluation = cursor.fetchone()

        if not evaluation:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đánh giá"
            )

        prompt = f"""
Bạn là AI chuyên đánh giá học viên học lái xe.

Hãy phân tích kết quả học tập của học viên và đưa ra nhận xét
ngắn gọn, dễ hiểu, mang tính xây dựng.

Thông tin học viên:
- Họ tên: {evaluation['student_name']}
- Hạng bằng: {evaluation['license_class']}

Kết quả:
- Điều khiển xe: {evaluation['vehicle_control']}
- Phanh: {evaluation['braking']}
- Chuyển làn: {evaluation['lane_change']}
- Quan sát: {evaluation['observation']}
- Ghép xe: {evaluation['parking']}
- Luật giao thông: {evaluation['traffic_rules']}
- Điểm tổng: {evaluation['score']}

Nhận xét giáo viên:
{evaluation['comment']}

Hãy trả lời bằng tiếng Việt và gồm:
1. Đánh giá tổng quan
2. Điểm mạnh
3. Điểm cần cải thiện
4. Đề xuất luyện tập

Không cần giải thích về AI.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        ai_comment = response.text

        cursor.execute(
            """
            UPDATE evaluations
            SET ai_comment = %s
            WHERE id = %s
            RETURNING
                id,
                student_id,
                score,
                comment,
                ai_comment
            """,
            (ai_comment, evaluation_id)
        )

        updated = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "AI đánh giá học viên thành công",
            "data": updated
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

class AIChatRequest(BaseModel):
    question: str
    student_id: Optional[int] = None


@app.post("/ai/chat")
def ai_chat(request: AIChatRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        student_info = None
        student_summary = None
        evaluations = []

        # =====================================================
        # 1. LẤY THÔNG TIN HỌC VIÊN
        # =====================================================

        if request.student_id:
            cursor.execute(
                """
                SELECT
                    s.id,
                    s.student_code,
                    s.full_name,
                    s.phone,
                    s.license_class,
                    s.tuition_fee,
                    s.status,
                    t.full_name AS teacher_name
                FROM students s
                LEFT JOIN teachers t
                    ON t.id = s.teacher_id
                WHERE s.id = %s
                """,
                (request.student_id,)
            )

            student_info = cursor.fetchone()

            if not student_info:
                cursor.close()
                conn.close()

                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy học viên"
                )

            # =================================================
            # 2. LẤY TỔNG HỢP HỌC VIÊN
            # =================================================

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_lessons,
                    COALESCE(SUM(duration), 0) AS total_hours
                FROM lessons
                WHERE student_id = %s
                """,
                (request.student_id,)
            )

            lessons = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_evaluations,
                    ROUND(AVG(score), 2) AS average_score,
                    ROUND(AVG(vehicle_control), 2) AS vehicle_control,
                    ROUND(AVG(braking), 2) AS braking,
                    ROUND(AVG(lane_change), 2) AS lane_change,
                    ROUND(AVG(observation), 2) AS observation,
                    ROUND(AVG(parking), 2) AS parking,
                    ROUND(AVG(traffic_rules), 2) AS traffic_rules
                FROM evaluations
                WHERE student_id = %s
                """,
                (request.student_id,)
            )

            evaluation_summary = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(amount), 0) AS paid
                FROM payments
                WHERE student_id = %s
                """,
                (request.student_id,)
            )

            payment = cursor.fetchone()

            total_tuition = float(student_info["tuition_fee"] or 0)
            paid = float(payment["paid"] or 0)
            remaining = total_tuition - paid

            student_summary = {
                "total_lessons": lessons["total_lessons"],
                "total_hours": float(lessons["total_hours"] or 0),
                "total_evaluations": evaluation_summary["total_evaluations"],
                "average_score": float(
                    evaluation_summary["average_score"] or 0
                ),
                "skills": {
                    "vehicle_control": float(
                        evaluation_summary["vehicle_control"] or 0
                    ),
                    "braking": float(
                        evaluation_summary["braking"] or 0
                    ),
                    "lane_change": float(
                        evaluation_summary["lane_change"] or 0
                    ),
                    "observation": float(
                        evaluation_summary["observation"] or 0
                    ),
                    "parking": float(
                        evaluation_summary["parking"] or 0
                    ),
                    "traffic_rules": float(
                        evaluation_summary["traffic_rules"] or 0
                    )
                },
                "tuition": {
                    "total": total_tuition,
                    "paid": paid,
                    "remaining": remaining
                }
            }

            # =================================================
            # 3. LẤY LỊCH SỬ ĐÁNH GIÁ
            # =================================================

            cursor.execute(
                """
                SELECT
                    e.score,
                    e.vehicle_control,
                    e.braking,
                    e.lane_change,
                    e.observation,
                    e.parking,
                    e.traffic_rules,
                    e.comment,
                    e.ai_comment,
                    l.lesson_date,
                    l.lesson_type
                FROM evaluations e
                JOIN lessons l
                    ON l.id = e.lesson_id
                WHERE e.student_id = %s
                ORDER BY l.lesson_date DESC
                LIMIT 20
                """,
                (request.student_id,)
            )

            evaluations = cursor.fetchall()

        # =====================================================
        # 4. TẠO PROMPT CHO AI
        # =====================================================

        prompt = f"""
Bạn là AI trợ lý của trung tâm đào tạo lái xe
"AI Driving Center Pro".

Hãy trả lời câu hỏi của giáo viên bằng tiếng Việt,
ngắn gọn, rõ ràng, thực tế và dựa trên dữ liệu thật
của hệ thống.

CÂU HỎI CỦA GIÁO VIÊN:
{request.question}
"""

        if student_info:
            prompt += f"""

====================================================
THÔNG TIN HỌC VIÊN
====================================================

- Mã học viên: {student_info['student_code']}
- Họ tên: {student_info['full_name']}
- Số điện thoại: {student_info['phone']}
- Hạng bằng: {student_info['license_class']}
- Giáo viên: {student_info['teacher_name']}
- Học phí: {student_info['tuition_fee']}
- Trạng thái: {student_info['status']}

====================================================
TỔNG HỢP QUÁ TRÌNH HỌC
====================================================

- Tổng số buổi học: {student_summary['total_lessons']}
- Tổng số giờ học: {student_summary['total_hours']}
- Số lần đánh giá: {student_summary['total_evaluations']}
- Điểm trung bình: {student_summary['average_score']}

====================================================
ĐIỂM TRUNG BÌNH THEO KỸ NĂNG
====================================================

- Điều khiển xe: {student_summary['skills']['vehicle_control']}
- Phanh: {student_summary['skills']['braking']}
- Chuyển làn: {student_summary['skills']['lane_change']}
- Quan sát: {student_summary['skills']['observation']}
- Ghép xe: {student_summary['skills']['parking']}
- Luật giao thông: {student_summary['skills']['traffic_rules']}

====================================================
HỌC PHÍ
====================================================

- Tổng học phí: {student_summary['tuition']['total']}
- Đã đóng: {student_summary['tuition']['paid']}
- Còn lại: {student_summary['tuition']['remaining']}

====================================================
LỊCH SỬ ĐÁNH GIÁ
====================================================

{evaluations}

====================================================
YÊU CẦU PHÂN TÍCH
====================================================

Nếu giáo viên hỏi về học lực hoặc khả năng thi:

1. Xác định kỹ năng mạnh.
2. Xác định kỹ năng yếu nhất.
3. So sánh các kỹ năng dựa trên điểm số thực tế.
4. Đề xuất nội dung cần luyện thêm.
5. Nếu được hỏi cần bao nhiêu buổi, hãy đưa ra
   số buổi luyện tập ƯỚC TÍNH dựa trên mức độ yếu.

Khi đưa ra số buổi luyện tập, phải nói rõ đó là
ước tính của AI, không phải kết luận chính thức.

Không tự bịa ra dữ liệu không có trong hệ thống.
Không tự tạo thêm điểm số.
"""

        else:
            prompt += """

Hiện tại giáo viên chưa chọn học viên cụ thể.

Hãy trả lời câu hỏi dựa trên kiến thức đào tạo lái xe
chung và không tự tạo dữ liệu học viên.

Nếu câu hỏi cần dữ liệu của một học viên cụ thể,
hãy nói rằng giáo viên cần chọn học viên trước.
"""

        # =====================================================
        # 5. GỌI GEMINI
        # =====================================================

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        answer = response.text

        # =====================================================
        # 6. LƯU LỊCH SỬ HỘI THOẠI
        # =====================================================

        cursor.execute(
            """
            INSERT INTO ai_conversations
            (
                student_id,
                question,
                answer
            )
            VALUES (%s, %s, %s)
            RETURNING id, student_id, question, answer, created_at
            """,
            (
                request.student_id,
                request.question,
                answer
            )
        )

        conversation = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "AI trả lời thành công",
            "data": {
                "answer": answer,
                "conversation": conversation
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/ai/conversations/{student_id}")
def get_ai_conversations(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT id, student_code, full_name
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                question,
                answer,
                created_at
            FROM ai_conversations
            WHERE student_id = %s
            ORDER BY created_at DESC
            """,
            (student_id,)
        )

        conversations = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Lấy lịch sử AI thành công",
            "data": {
                "student": student,
                "total": len(conversations),
                "conversations": conversations
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/students/{student_id}/summary")
def get_student_summary(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # ==========================================
        # 1. THÔNG TIN HỌC VIÊN + GIÁO VIÊN
        # ==========================================

        cursor.execute(
            """
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.phone,
                s.date_of_birth,
                s.address,
                s.license_class,
                s.enrollment_date,
                s.tuition_fee,
                s.status,
                t.id AS teacher_id,
                t.teacher_code,
                t.full_name AS teacher_name,
                t.phone AS teacher_phone
            FROM students s
            LEFT JOIN teachers t
                ON t.id = s.teacher_id
            WHERE s.id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # ==========================================
        # 2. TỔNG SỐ BUỔI HỌC + SỐ GIỜ
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_lessons,
                COALESCE(SUM(duration), 0) AS total_hours
            FROM lessons
            WHERE student_id = %s
            """,
            (student_id,)
        )

        lessons = cursor.fetchone()

        # ==========================================
        # 3. ĐÁNH GIÁ + ĐIỂM TRUNG BÌNH
        # ==========================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_evaluations,
                ROUND(AVG(score), 2) AS average_score,

                ROUND(AVG(vehicle_control), 2)
                    AS vehicle_control,

                ROUND(AVG(braking), 2)
                    AS braking,

                ROUND(AVG(lane_change), 2)
                    AS lane_change,

                ROUND(AVG(observation), 2)
                    AS observation,

                ROUND(AVG(parking), 2)
                    AS parking,

                ROUND(AVG(traffic_rules), 2)
                    AS traffic_rules

            FROM evaluations
            WHERE student_id = %s
            """,
            (student_id,)
        )

        evaluations = cursor.fetchone()

        # ==========================================
        # 4. TỔNG TIỀN ĐÃ ĐÓNG
        # ==========================================

        cursor.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS paid
            FROM payments
            WHERE student_id = %s
            """,
            (student_id,)
        )

        payment = cursor.fetchone()

        # ==========================================
        # 5. TÍNH TIỀN CÒN LẠI
        # ==========================================

        total_tuition = float(student["tuition_fee"] or 0)
        paid = float(payment["paid"] or 0)
        remaining = total_tuition - paid

        # ==========================================
        # 6. ĐÓNG KẾT NỐI
        # ==========================================

        cursor.close()
        conn.close()

        # ==========================================
        # 7. TRẢ KẾT QUẢ
        # ==========================================

        return {
            "status": "ok",
            "message": "Lấy tổng hợp học viên thành công",
            "data": {
                "student": {
                    "id": student["id"],
                    "student_code": student["student_code"],
                    "full_name": student["full_name"],
                    "phone": student["phone"],
                    "date_of_birth": student["date_of_birth"],
                    "address": student["address"],
                    "license_class": student["license_class"],
                    "enrollment_date": student["enrollment_date"],
                    "status": student["status"]
                },

                "teacher": {
                    "id": student["teacher_id"],
                    "teacher_code": student["teacher_code"],
                    "full_name": student["teacher_name"],
                    "phone": student["teacher_phone"]
                },

                "lessons": {
                    "total_lessons": lessons["total_lessons"],
                    "total_hours": float(lessons["total_hours"] or 0)
                },

                "evaluations": {
                    "total_evaluations": evaluations["total_evaluations"],
                    "average_score": float(
                        evaluations["average_score"] or 0
                    ),
                    "skills": {
                        "vehicle_control": float(
                            evaluations["vehicle_control"] or 0
                        ),
                        "braking": float(
                            evaluations["braking"] or 0
                        ),
                        "lane_change": float(
                            evaluations["lane_change"] or 0
                        ),
                        "observation": float(
                            evaluations["observation"] or 0
                        ),
                        "parking": float(
                            evaluations["parking"] or 0
                        ),
                        "traffic_rules": float(
                            evaluations["traffic_rules"] or 0
                        )
                    }
                },

                "tuition": {
                    "total": total_tuition,
                    "paid": paid,
                    "remaining": remaining
                }
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# AI TRAINING PLAN
# =========================================================

@app.post("/students/{student_id}/training-plan")
def create_training_plan(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # =====================================================
        # 1. LẤY THÔNG TIN HỌC VIÊN
        # =====================================================

        cursor.execute(
            """
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.license_class,
                s.status,
                t.full_name AS teacher_name
            FROM students s
            LEFT JOIN teachers t
                ON t.id = s.teacher_id
            WHERE s.id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # =====================================================
        # 2. LẤY TỔNG QUAN QUÁ TRÌNH HỌC
        # =====================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_lessons,
                COALESCE(SUM(duration), 0) AS total_hours
            FROM lessons
            WHERE student_id = %s
            """,
            (student_id,)
        )

        lessons = cursor.fetchone()

        # =====================================================
        # 3. LẤY ĐIỂM TRUNG BÌNH CÁC KỸ NĂNG
        # =====================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_evaluations,
                ROUND(AVG(score), 2) AS average_score,
                ROUND(AVG(vehicle_control), 2) AS vehicle_control,
                ROUND(AVG(braking), 2) AS braking,
                ROUND(AVG(lane_change), 2) AS lane_change,
                ROUND(AVG(observation), 2) AS observation,
                ROUND(AVG(parking), 2) AS parking,
                ROUND(AVG(traffic_rules), 2) AS traffic_rules
            FROM evaluations
            WHERE student_id = %s
            """,
            (student_id,)
        )

        evaluation_summary = cursor.fetchone()

        # =====================================================
        # 4. LẤY LỊCH SỬ ĐÁNH GIÁ
        # =====================================================

        cursor.execute(
            """
            SELECT
                e.score,
                e.vehicle_control,
                e.braking,
                e.lane_change,
                e.observation,
                e.parking,
                e.traffic_rules,
                e.comment,
                e.ai_comment,
                l.lesson_date,
                l.lesson_type
            FROM evaluations e
            JOIN lessons l
                ON l.id = e.lesson_id
            WHERE e.student_id = %s
            ORDER BY l.lesson_date DESC
            LIMIT 20
            """,
            (student_id,)
        )

        evaluations = cursor.fetchall()

        # =====================================================
        # 5. TẠO PROMPT CHO GEMINI
        # =====================================================

        prompt = f"""
Bạn là chuyên gia lập kế hoạch đào tạo lái xe
cho trung tâm "AI Driving Center Pro".

Hãy lập kế hoạch luyện thi thực tế cho học viên
dựa HOÀN TOÀN trên dữ liệu được cung cấp.

THÔNG TIN HỌC VIÊN
------------------
Mã học viên: {student['student_code']}
Họ tên: {student['full_name']}
Hạng bằng: {student['license_class']}
Giáo viên: {student['teacher_name']}
Trạng thái: {student['status']}

QUÁ TRÌNH HỌC
-------------
Tổng số buổi: {lessons['total_lessons']}
Tổng số giờ: {float(lessons['total_hours'] or 0)}
Số lần đánh giá: {evaluation_summary['total_evaluations']}
Điểm trung bình: {float(evaluation_summary['average_score'] or 0)}

ĐIỂM KỸ NĂNG
------------
Điều khiển xe: {float(evaluation_summary['vehicle_control'] or 0)}
Phanh: {float(evaluation_summary['braking'] or 0)}
Chuyển làn: {float(evaluation_summary['lane_change'] or 0)}
Quan sát: {float(evaluation_summary['observation'] or 0)}
Ghép xe: {float(evaluation_summary['parking'] or 0)}
Luật giao thông: {float(evaluation_summary['traffic_rules'] or 0)}

LỊCH SỬ ĐÁNH GIÁ
----------------
{evaluations}

YÊU CẦU

Hãy lập kế hoạch luyện thi cho học viên.

Cần trả lời bằng tiếng Việt và gồm:

1. Đánh giá hiện tại
2. Kỹ năng mạnh
3. Kỹ năng yếu
4. Nội dung cần tập trung luyện
5. Kế hoạch từng buổi luyện
6. Số buổi luyện đề xuất
7. Mục tiêu sau khi luyện
8. Đánh giá mức độ sẵn sàng thi

Quy tắc:

- Ưu tiên các kỹ năng có điểm thấp.
- Không tự bịa dữ liệu.
- Số buổi chỉ là ƯỚC TÍNH của AI.
- Không khẳng định chắc chắn học viên sẽ đậu hoặc rớt.
- Nếu dữ liệu chưa đủ để đánh giá, phải nói rõ.
- Kế hoạch phải thực tế và dễ áp dụng cho giáo viên.
"""

        # =====================================================
        # 6. GỌI GEMINI
        # =====================================================

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        training_plan = response.text

        cursor.close()
        conn.close()

        # =====================================================
        # 7. TRẢ KẾT QUẢ
        # =====================================================

        return {
            "status": "ok",
            "message": "AI lập kế hoạch luyện thi thành công",
            "data": {
                "student": {
                    "id": student["id"],
                    "student_code": student["student_code"],
                    "full_name": student["full_name"],
                    "license_class": student["license_class"],
                    "teacher_name": student["teacher_name"]
                },
                "summary": {
                    "total_lessons": lessons["total_lessons"],
                    "total_hours": float(lessons["total_hours"] or 0),
                    "total_evaluations": evaluation_summary["total_evaluations"],
                    "average_score": float(
                        evaluation_summary["average_score"] or 0
                    )
                },
                "training_plan": training_plan
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# PAYMENT API
# =========================================================

class PaymentCreate(BaseModel):
    student_id: int
    amount: float
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    note: Optional[str] = None


@app.post("/payments")
def create_payment(payment: PaymentCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # =====================================================
        # 1. KIỂM TRA HỌC VIÊN
        # =====================================================

        cursor.execute(
            """
            SELECT
                id,
                student_code,
                full_name,
                tuition_fee
            FROM students
            WHERE id = %s
            """,
            (payment.student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # =====================================================
        # 2. KIỂM TRA SỐ TIỀN
        # =====================================================

        if payment.amount <= 0:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Số tiền thanh toán phải lớn hơn 0"
            )

        # =====================================================
        # 3. TÍNH SỐ TIỀN ĐÃ ĐÓNG
        # =====================================================

        cursor.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS paid
            FROM payments
            WHERE student_id = %s
            """,
            (payment.student_id,)
        )

        payment_summary = cursor.fetchone()

        paid_before = float(payment_summary["paid"] or 0)
        tuition_fee = float(student["tuition_fee"] or 0)

        # =====================================================
        # 4. KIỂM TRA KHÔNG CHO ĐÓNG VƯỢT HỌC PHÍ
        # =====================================================

        if paid_before + payment.amount > tuition_fee:
            remaining = tuition_fee - paid_before

            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Số tiền đóng vượt quá học phí. "
                    f"Học phí còn lại: {remaining:,.0f} VNĐ"
                )
            )

        # =====================================================
        # 5. THÊM KHOẢN THANH TOÁN
        # =====================================================

        cursor.execute(
            """
            INSERT INTO payments
            (
                student_id,
                amount,
                payment_date,
                payment_method,
                note
            )
            VALUES
            (
                %s,
                %s,
                COALESCE(%s, CURRENT_DATE),
                %s,
                %s
            )
            RETURNING
                id,
                student_id,
                amount,
                payment_date,
                payment_method,
                note,
                created_at
            """,
            (
                payment.student_id,
                payment.amount,
                payment.payment_date,
                payment.payment_method,
                payment.note
            )
        )

        new_payment = cursor.fetchone()

        # =====================================================
        # 6. TÍNH LẠI TỔNG THANH TOÁN
        # =====================================================

        paid_after = paid_before + payment.amount
        remaining_after = tuition_fee - paid_after

        conn.commit()

        cursor.close()
        conn.close()

        # =====================================================
        # 7. TRẢ KẾT QUẢ
        # =====================================================

        return {
            "status": "ok",
            "message": "Ghi nhận thanh toán thành công",
            "data": {
                "payment": new_payment,
                "student": {
                    "id": student["id"],
                    "student_code": student["student_code"],
                    "full_name": student["full_name"]
                },
                "tuition": {
                    "total": tuition_fee,
                    "paid_before": paid_before,
                    "paid_after": paid_after,
                    "remaining": remaining_after
                }
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# PAYMENT API - GET ALL PAYMENTS
# =========================================================

@app.get("/payments")
def get_payments():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT
                p.id,
                p.student_id,
                s.student_code,
                s.full_name,
                p.amount,
                p.payment_date,
                p.payment_method,
                p.note,
                p.created_at
            FROM payments p
            JOIN students s
                ON p.student_id = s.id
            ORDER BY
                p.payment_date DESC,
                p.id DESC
            """
        )

        payments = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Lấy danh sách thanh toán thành công",
            "total": len(payments),
            "data": payments
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# PAYMENT API - DELETE PAYMENT
# =========================================================

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Kiểm tra giao dịch
        cursor.execute(
            """
            SELECT
                p.id,
                p.student_id,
                p.amount,
                p.payment_date,
                p.payment_method,
                p.note,
                s.student_code,
                s.full_name
            FROM payments p
            JOIN students s
                ON p.student_id = s.id
            WHERE p.id = %s
            """,
            (payment_id,)
        )

        payment = cursor.fetchone()

        if not payment:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giao dịch thanh toán"
            )

        # Xóa giao dịch
        cursor.execute(
            """
            DELETE FROM payments
            WHERE id = %s
            """,
            (payment_id,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Xóa giao dịch thanh toán thành công",
            "data": payment
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# PAYMENT API - GET PAYMENTS BY STUDENT
# =========================================================

@app.get("/students/{student_id}/payments")
def get_student_payments(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # -------------------------------------------------
        # 1. Lấy thông tin học viên
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                student_code,
                full_name,
                tuition_fee
            FROM students
            WHERE id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # -------------------------------------------------
        # 2. Lấy lịch sử thanh toán
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                student_id,
                amount,
                payment_date,
                payment_method,
                note,
                created_at
            FROM payments
            WHERE student_id = %s
            ORDER BY
                payment_date ASC,
                id ASC
            """,
            (student_id,)
        )

        payments = cursor.fetchall()

        # -------------------------------------------------
        # 3. Tính tổng đã đóng
        # -------------------------------------------------
        total_paid = sum(
            float(payment["amount"] or 0)
            for payment in payments
        )

        tuition_fee = float(student["tuition_fee"] or 0)

        remaining = tuition_fee - total_paid

        # Không cho số dư âm
        if remaining < 0:
            remaining = 0

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Lấy lịch sử thanh toán của học viên thành công",
            "data": {
                "student": {
                    "id": student["id"],
                    "student_code": student["student_code"],
                    "full_name": student["full_name"]
                },
                "tuition": {
                    "total": tuition_fee,
                    "paid": total_paid,
                    "remaining": remaining
                },
                "payments": payments
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# PAYMENT API - UPDATE PAYMENT
# =========================================================

class PaymentUpdate(BaseModel):
    amount: float
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    note: Optional[str] = None


@app.put("/payments/{payment_id}")
def update_payment(payment_id: int, payment: PaymentUpdate):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # -------------------------------------------------
        # 1. Kiểm tra giao dịch cần sửa
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                p.id,
                p.student_id,
                p.amount,
                p.payment_date,
                p.payment_method,
                p.note,
                s.student_code,
                s.full_name,
                s.tuition_fee
            FROM payments p
            JOIN students s
                ON p.student_id = s.id
            WHERE p.id = %s
            """,
            (payment_id,)
        )

        old_payment = cursor.fetchone()

        if not old_payment:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy giao dịch thanh toán"
            )

        # -------------------------------------------------
        # 2. Kiểm tra số tiền mới
        # -------------------------------------------------
        if payment.amount <= 0:
            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Số tiền thanh toán phải lớn hơn 0"
            )

        tuition_fee = float(old_payment["tuition_fee"] or 0)
        old_amount = float(old_payment["amount"] or 0)
        new_amount = float(payment.amount)

        # -------------------------------------------------
        # 3. Tính tổng đã đóng trước khi sửa
        #    Không tính giao dịch hiện tại
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS paid_other
            FROM payments
            WHERE student_id = %s
              AND id <> %s
            """,
            (
                old_payment["student_id"],
                payment_id
            )
        )

        result = cursor.fetchone()

        paid_other = float(result["paid_other"] or 0)

        # Tổng sau khi sửa
        paid_after = paid_other + new_amount

        # -------------------------------------------------
        # 4. Không cho vượt học phí
        # -------------------------------------------------
        if paid_after > tuition_fee:
            remaining = tuition_fee - paid_other

            cursor.close()
            conn.close()

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Số tiền sửa vượt quá học phí. "
                    f"Số tiền tối đa có thể nhập: "
                    f"{remaining:,.0f} VNĐ"
                )
            )

        # -------------------------------------------------
        # 5. Cập nhật giao dịch
        # -------------------------------------------------
        cursor.execute(
            """
            UPDATE payments
            SET
                amount = %s,
                payment_date = COALESCE(%s, payment_date),
                payment_method = %s,
                note = %s
            WHERE id = %s
            RETURNING
                id,
                student_id,
                amount,
                payment_date,
                payment_method,
                note,
                created_at
            """,
            (
                new_amount,
                payment.payment_date,
                payment.payment_method,
                payment.note,
                payment_id
            )
        )

        updated_payment = cursor.fetchone()

        # -------------------------------------------------
        # 6. Tính số dư mới
        # -------------------------------------------------
        remaining_after = tuition_fee - paid_after

        if remaining_after < 0:
            remaining_after = 0

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Cập nhật thanh toán thành công",
            "data": {
                "payment": updated_payment,
                "student": {
                    "id": old_payment["student_id"],
                    "student_code": old_payment["student_code"],
                    "full_name": old_payment["full_name"]
                },
                "tuition": {
                    "total": tuition_fee,
                    "paid_before": paid_other + old_amount,
                    "paid_after": paid_after,
                    "remaining": remaining_after
                }
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# DASHBOARD - FINANCE
# =========================================================

@app.get("/dashboard/finance")
def get_finance_dashboard():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # -------------------------------------------------
        # 1. Tổng học phí của tất cả học viên
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(tuition_fee), 0) AS total_tuition,
                COUNT(*) AS total_students
            FROM students
            """
        )

        tuition_summary = cursor.fetchone()

        total_tuition = float(
            tuition_summary["total_tuition"] or 0
        )

        total_students = int(
            tuition_summary["total_students"] or 0
        )

        # -------------------------------------------------
        # 2. Tổng tiền đã thu
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_paid
            FROM payments
            """
        )

        payment_summary = cursor.fetchone()

        total_paid = float(
            payment_summary["total_paid"] or 0
        )

        # -------------------------------------------------
        # 3. Tổng tiền còn phải thu
        # -------------------------------------------------
        total_remaining = total_tuition - total_paid

        if total_remaining < 0:
            total_remaining = 0

        # -------------------------------------------------
        # 4. Tỷ lệ đã thu
        # -------------------------------------------------
        if total_tuition > 0:
            collection_rate = round(
                (total_paid / total_tuition) * 100,
                2
            )
        else:
            collection_rate = 0

        # -------------------------------------------------
        # 5. Thống kê công nợ từng học viên
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.tuition_fee,
                COALESCE(SUM(p.amount), 0) AS paid
            FROM students s
            LEFT JOIN payments p
                ON p.student_id = s.id
            GROUP BY
                s.id,
                s.student_code,
                s.full_name,
                s.tuition_fee
            ORDER BY
                s.id
            """
        )

        student_rows = cursor.fetchall()

        students_debt = []
        fully_paid_students = 0
        debt_students = 0

        for row in student_rows:

            tuition = float(
                row["tuition_fee"] or 0
            )

            paid = float(
                row["paid"] or 0
            )

            remaining = tuition - paid

            if remaining < 0:
                remaining = 0

            if remaining == 0:
                fully_paid_students += 1
            else:
                debt_students += 1

            students_debt.append(
                {
                    "id": row["id"],
                    "student_code": row["student_code"],
                    "full_name": row["full_name"],
                    "tuition_fee": tuition,
                    "paid": paid,
                    "remaining": remaining
                }
            )

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "message": "Lấy Dashboard tài chính thành công",
            "data": {
                "overview": {
                    "total_students": total_students,
                    "total_tuition": total_tuition,
                    "total_paid": total_paid,
                    "total_remaining": total_remaining,
                    "collection_rate": collection_rate,
                    "fully_paid_students": fully_paid_students,
                    "debt_students": debt_students
                },
                "students_debt": students_debt
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# STUDENT FULL PROFILE
# =========================================================

@app.get("/students/{student_id}/full-profile")
def get_student_full_profile(student_id: int):

    conn = get_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # =====================================================
        # 1. THÔNG TIN HỌC VIÊN
        # =====================================================

        cur.execute("""
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.phone,
                s.date_of_birth,
                s.address,
                s.license_class,
                s.enrollment_date,
                s.tuition_fee,
                s.status,
                s.teacher_id
            FROM students s
            WHERE s.id = %s
        """, (student_id,))

        student = cur.fetchone()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy học viên"
            )

        # =====================================================
        # 2. GIÁO VIÊN
        # =====================================================

        teacher = None

        if student["teacher_id"]:

            cur.execute("""
                SELECT
                    id,
                    teacher_code,
                    full_name,
                    phone,
                    license_number,
                    status
                FROM teachers
                WHERE id = %s
            """, (student["teacher_id"],))

            teacher = cur.fetchone()

        # =====================================================
        # 3. THỐNG KÊ BUỔI HỌC
        # =====================================================

        cur.execute("""
            SELECT
                COUNT(*) AS total_lessons,
                COALESCE(SUM(duration), 0) AS total_hours
            FROM lessons
            WHERE student_id = %s
        """, (student_id,))

        lesson_summary = cur.fetchone()

        # =====================================================
        # 4. LỊCH SỬ BUỔI HỌC
        # =====================================================

        cur.execute("""
            SELECT
                l.id,
                l.lesson_date,
                l.start_time,
                l.end_time,
                l.duration,
                l.lesson_type,
                l.content,
                l.notes,

                t.id AS teacher_id,
                t.teacher_code,
                t.full_name AS teacher_name,

                v.id AS vehicle_id,
                v.plate_number,
                v.brand,
                v.model

            FROM lessons l

            LEFT JOIN teachers t
                ON l.teacher_id = t.id

            LEFT JOIN vehicles v
                ON l.vehicle_id = v.id

            WHERE l.student_id = %s

            ORDER BY
                l.lesson_date DESC,
                l.id DESC
        """, (student_id,))

        lessons = cur.fetchall()

        # =====================================================
        # 5. THỐNG KÊ ĐÁNH GIÁ
        # =====================================================

        cur.execute("""
            SELECT
                COUNT(*) AS total_evaluations,
                ROUND(AVG(score)::numeric, 2) AS average_score,

                ROUND(AVG(vehicle_control)::numeric, 2)
                    AS vehicle_control,

                ROUND(AVG(braking)::numeric, 2)
                    AS braking,

                ROUND(AVG(lane_change)::numeric, 2)
                    AS lane_change,

                ROUND(AVG(observation)::numeric, 2)
                    AS observation,

                ROUND(AVG(parking)::numeric, 2)
                    AS parking,

                ROUND(AVG(traffic_rules)::numeric, 2)
                    AS traffic_rules

            FROM evaluations
            WHERE student_id = %s
        """, (student_id,))

        evaluation_summary = cur.fetchone()

        # =====================================================
        # 6. LỊCH SỬ ĐÁNH GIÁ
        # =====================================================

        cur.execute("""
            SELECT
                e.id,
                e.lesson_id,
                e.vehicle_control,
                e.braking,
                e.lane_change,
                e.observation,
                e.parking,
                e.traffic_rules,
                e.score,
                e.comment,
                e.ai_comment,
                e.created_at
            FROM evaluations e
            WHERE e.student_id = %s
            ORDER BY e.id DESC
        """, (student_id,))

        evaluations = cur.fetchall()

        # =====================================================
        # 7. TỔNG HỌC PHÍ
        # =====================================================

        cur.execute("""
            SELECT
                COALESCE(SUM(amount), 0) AS paid
            FROM payments
            WHERE student_id = %s
        """, (student_id,))

        payment_summary = cur.fetchone()

        total_tuition = float(student["tuition_fee"] or 0)
        total_paid = float(payment_summary["paid"] or 0)
        total_remaining = total_tuition - total_paid

        # Không cho số dư âm
        if total_remaining < 0:
            total_remaining = 0

        # =====================================================
        # 8. LỊCH SỬ THANH TOÁN
        # =====================================================

        cur.execute("""
            SELECT
                id,
                amount,
                payment_date,
                payment_method,
                note,
                created_at
            FROM payments
            WHERE student_id = %s
            ORDER BY payment_date DESC, id DESC
        """, (student_id,))

        payments = cur.fetchall()

        # =====================================================
        # 9. CHUYỂN DỮ LIỆU DATETIME / DATE / DECIMAL
        # =====================================================

        def serialize_rows(rows):

            result = []

            for row in rows:

                item = dict(row)

                for key, value in item.items():

                    if hasattr(value, "isoformat"):
                        item[key] = value.isoformat()

                    elif hasattr(value, "as_tuple"):
                        item[key] = float(value)

                result.append(item)

            return result

        # =====================================================
        # 10. RESPONSE
        # =====================================================

        return {
            "status": "ok",
            "message": "Lấy Full Profile học viên thành công",

            "data": {

                # -------------------------------------------------
                # THÔNG TIN HỌC VIÊN
                # -------------------------------------------------

                "student": {
                    "id": student["id"],
                    "student_code": student["student_code"],
                    "full_name": student["full_name"],
                    "phone": student["phone"],
                    "date_of_birth": (
                        student["date_of_birth"].isoformat()
                        if student["date_of_birth"]
                        else None
                    ),
                    "address": student["address"],
                    "license_class": student["license_class"],
                    "enrollment_date": (
                        student["enrollment_date"].isoformat()
                        if student["enrollment_date"]
                        else None
                    ),
                    "tuition_fee": total_tuition,
                    "status": student["status"]
                },

                # -------------------------------------------------
                # GIÁO VIÊN
                # -------------------------------------------------

                "teacher": dict(teacher) if teacher else None,

                # -------------------------------------------------
                # HỌC TẬP
                # -------------------------------------------------

                "learning": {
                    "total_lessons": int(
                        lesson_summary["total_lessons"] or 0
                    ),
                    "total_hours": float(
                        lesson_summary["total_hours"] or 0
                    )
                },

                # -------------------------------------------------
                # ĐÁNH GIÁ
                # -------------------------------------------------

                "evaluations": {
                    "total_evaluations": int(
                        evaluation_summary["total_evaluations"] or 0
                    ),
                    "average_score": (
                        float(evaluation_summary["average_score"])
                        if evaluation_summary["average_score"] is not None
                        else None
                    ),

                    "skills": {
                        "vehicle_control": (
                            float(evaluation_summary["vehicle_control"])
                            if evaluation_summary["vehicle_control"] is not None
                            else None
                        ),
                        "braking": (
                            float(evaluation_summary["braking"])
                            if evaluation_summary["braking"] is not None
                            else None
                        ),
                        "lane_change": (
                            float(evaluation_summary["lane_change"])
                            if evaluation_summary["lane_change"] is not None
                            else None
                        ),
                        "observation": (
                            float(evaluation_summary["observation"])
                            if evaluation_summary["observation"] is not None
                            else None
                        ),
                        "parking": (
                            float(evaluation_summary["parking"])
                            if evaluation_summary["parking"] is not None
                            else None
                        ),
                        "traffic_rules": (
                            float(evaluation_summary["traffic_rules"])
                            if evaluation_summary["traffic_rules"] is not None
                            else None
                        )
                    }
                },

                # -------------------------------------------------
                # LỊCH SỬ HỌC
                # -------------------------------------------------

                "lesson_history": serialize_rows(lessons),

                # -------------------------------------------------
                # LỊCH SỬ ĐÁNH GIÁ
                # -------------------------------------------------

                "evaluation_history": serialize_rows(evaluations),

                # -------------------------------------------------
                # HỌC PHÍ
                # -------------------------------------------------

                "tuition": {
                    "total": total_tuition,
                    "paid": total_paid,
                    "remaining": total_remaining
                },

                # -------------------------------------------------
                # LỊCH SỬ THANH TOÁN
                # -------------------------------------------------

                "payment_history": serialize_rows(payments)
            }
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy Full Profile học viên: {str(e)}"
        )

    finally:

        conn.close()

# =========================================================
# STUDENT MANAGEMENT - ADVANCED LIST
# =========================================================

@app.get("/students/management")
def get_students_management(
    keyword: Optional[str] = None,
    teacher_id: Optional[int] = None,
    license_class: Optional[str] = None,
    status: Optional[str] = None,
    debt_only: bool = False,
    min_score: Optional[float] = None
):
    conn = get_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # =====================================================
        # 1. DANH SÁCH HỌC VIÊN
        # =====================================================

        sql = """
            SELECT
                s.id,
                s.student_code,
                s.full_name,
                s.phone,
                s.date_of_birth,
                s.address,
                s.license_class,
                s.enrollment_date,
                s.tuition_fee,
                s.status,

                t.id AS teacher_id,
                t.teacher_code,
                t.full_name AS teacher_name

            FROM students s

            LEFT JOIN teachers t
                ON s.teacher_id = t.id

            WHERE 1 = 1
        """

        params = []

        # =====================================================
        # 2. TÌM KIẾM
        # =====================================================

        if keyword:
            sql += """
                AND (
                    s.student_code ILIKE %s
                    OR s.full_name ILIKE %s
                    OR s.phone ILIKE %s
                )
            """

            keyword_value = f"%{keyword}%"

            params.extend([
                keyword_value,
                keyword_value,
                keyword_value
            ])

        # =====================================================
        # 3. LỌC GIÁO VIÊN
        # =====================================================

        if teacher_id is not None:

            sql += """
                AND s.teacher_id = %s
            """

            params.append(teacher_id)

        # =====================================================
        # 4. LỌC HẠNG BẰNG
        # =====================================================

        if license_class:

            sql += """
                AND s.license_class = %s
            """

            params.append(license_class)

        # =====================================================
        # 5. LỌC TRẠNG THÁI
        # =====================================================

        if status:

            sql += """
                AND s.status = %s
            """

            params.append(status)

        # =====================================================
        # 6. SẮP XẾP
        # =====================================================

        sql += """
            ORDER BY s.id ASC
        """

        cur.execute(sql, params)

        students = cur.fetchall()

        result = []

        # =====================================================
        # 7. TÍNH THỐNG KÊ CHO TỪNG HỌC VIÊN
        # =====================================================

        for student in students:

            student_id = student["id"]

            # -------------------------------------------------
            # SỐ BUỔI + TỔNG GIỜ
            # -------------------------------------------------

            cur.execute("""
                SELECT
                    COUNT(*) AS total_lessons,
                    COALESCE(SUM(duration), 0) AS total_hours
                FROM lessons
                WHERE student_id = %s
            """, (student_id,))

            lesson = cur.fetchone()

            total_lessons = int(
                lesson["total_lessons"] or 0
            )

            total_hours = float(
                lesson["total_hours"] or 0
            )

            # -------------------------------------------------
            # ĐIỂM TRUNG BÌNH
            # -------------------------------------------------

            cur.execute("""
                SELECT
                    COUNT(*) AS total_evaluations,
                    AVG(score) AS average_score
                FROM evaluations
                WHERE student_id = %s
            """, (student_id,))

            evaluation = cur.fetchone()

            total_evaluations = int(
                evaluation["total_evaluations"] or 0
            )

            average_score = (
                round(float(evaluation["average_score"]), 2)
                if evaluation["average_score"] is not None
                else None
            )

            # -------------------------------------------------
            # HỌC PHÍ
            # -------------------------------------------------

            tuition_fee = float(
                student["tuition_fee"] or 0
            )

            cur.execute("""
                SELECT
                    COALESCE(SUM(amount), 0) AS paid
                FROM payments
                WHERE student_id = %s
            """, (student_id,))

            payment = cur.fetchone()

            paid = float(
                payment["paid"] or 0
            )

            remaining = tuition_fee - paid

            if remaining < 0:
                remaining = 0

            # -------------------------------------------------
            # TỶ LỆ ĐÃ ĐÓNG
            # -------------------------------------------------

            if tuition_fee > 0:

                collection_rate = round(
                    (paid / tuition_fee) * 100,
                    2
                )

                if collection_rate > 100:
                    collection_rate = 100

            else:

                collection_rate = 0

            # -------------------------------------------------
            # LỌC NỢ
            # -------------------------------------------------

            if debt_only and remaining <= 0:
                continue

            # -------------------------------------------------
            # LỌC ĐIỂM
            # -------------------------------------------------

            if (
                min_score is not None
                and (
                    average_score is None
                    or average_score < min_score
                )
            ):
                continue

            # -------------------------------------------------
            # ĐƯA VÀO RESULT
            # -------------------------------------------------

            result.append({
                "id": student["id"],
                "student_code": student["student_code"],
                "full_name": student["full_name"],
                "phone": student["phone"],
                "date_of_birth": (
                    student["date_of_birth"].isoformat()
                    if student["date_of_birth"]
                    else None
                ),
                "address": student["address"],
                "license_class": student["license_class"],
                "enrollment_date": (
                    student["enrollment_date"].isoformat()
                    if student["enrollment_date"]
                    else None
                ),
                "status": student["status"],

                "teacher": {
                    "id": student["teacher_id"],
                    "teacher_code": student["teacher_code"],
                    "full_name": student["teacher_name"]
                } if student["teacher_id"] else None,

                "learning": {
                    "total_lessons": total_lessons,
                    "total_hours": total_hours
                },

                "evaluation": {
                    "total_evaluations": total_evaluations,
                    "average_score": average_score
                },

                "tuition": {
                    "total": tuition_fee,
                    "paid": paid,
                    "remaining": remaining,
                    "collection_rate": collection_rate
                }
            })

        # =====================================================
        # 8. RESPONSE
        # =====================================================

        return {
            "status": "ok",
            "message": "Lấy danh sách Student Management thành công",
            "count": len(result),
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi Student Management: {str(e)}"
        )

    finally:

        conn.close()