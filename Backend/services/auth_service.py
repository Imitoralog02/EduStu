from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from utils.security import verify_password, hash_password, create_access_token


def login(db: Session, username: str, password: str) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
        )
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user}


def change_password(db: Session, user: User, mat_khau_cu: str, mat_khau_moi: str) -> None:
    if not verify_password(mat_khau_cu, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")
    if len(mat_khau_moi) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự")
    if mat_khau_cu == mat_khau_moi:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu cũ")
    user.password_hash = hash_password(mat_khau_moi)
    db.commit()
