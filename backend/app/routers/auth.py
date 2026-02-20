from fastapi import APIRouter, HTTPException, status
from ..database import get_connection
from ..schemas.user import UserCreate, User, Token
from ..utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=User)
def register(user: UserCreate):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT id, email, password_hash, created_at FROM users WHERE email = :email",
                         {"email": user.email})
            existing_user = cursor.fetchone()

            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Create new user
            hashed_password = get_password_hash(user.password)
            cursor.execute("""
                INSERT INTO users (email, password_hash)
                VALUES (:email, :password_hash)
            """, {
                "email": user.email,
                "password_hash": hashed_password
            })

            # Get the inserted user data (Oracle doesn't support RETURNING INTO the same way)
            cursor.execute("""
                SELECT id, email, password_hash, created_at
                FROM users
                WHERE email = :email
                ORDER BY created_at DESC
                FETCH FIRST 1 ROW ONLY
            """, {"email": user.email})

            user_data = cursor.fetchone()
            if not user_data:
                raise HTTPException(status_code=500, detail="Failed to create user")

            conn.commit()

            return User(
                id=user_data[0],
                email=user_data[1],
                created_at=user_data[3]
            )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
def login(user: UserCreate):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash FROM users WHERE email = :email",
                         {"email": user.email})
            db_user = cursor.fetchone()

            if not db_user:
                raise HTTPException(status_code=400, detail="Incorrect email or password")

            if not verify_password(user.password, db_user[2]):
                raise HTTPException(status_code=400, detail="Incorrect email or password")

            access_token = create_access_token(data={"sub": db_user[1]})
            return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")