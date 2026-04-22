from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.user import LoginRequest, LoginResponse, UserOut, ChangePasswordRequest
import services.auth_service as svc

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = svc.login(db, body.username, body.password)
    return LoginResponse(access_token=result["token"], user=UserOut.model_validate(result["user"]))


@router.put("/password")
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc.change_password(db, current_user, body.mat_khau_cu, body.mat_khau_moi)
    return {"message": "Đổi mật khẩu thành công"}
