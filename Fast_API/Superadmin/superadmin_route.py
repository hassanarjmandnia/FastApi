from .superadmin_schemas import RoleTableAdd, UserRoleUpdate, UserStatusUpdate
from Fast_API.Database.database import DatabaseManager
from Fast_API.User.user_modules import UserManager
from .superadmin_modules import SuperAdminManager
from Fast_API.Database.models import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


superadmin_router = APIRouter()


@superadmin_router.post("/add_role")
async def add_role(
    role_name: RoleTableAdd,
    superadmin_user: User = Depends(UserManager().authenticate_and_verify_super_admin),
    db_session: Session = Depends(DatabaseManager().get_session),
    super_admin_manager: SuperAdminManager = Depends(SuperAdminManager),
):
    return super_admin_manager.add_role(role_name, db_session)


@superadmin_router.post("/change_role")
async def change_role_of_user(
    role_change: UserRoleUpdate,
    superadmin_user: User = Depends(UserManager().authenticate_and_verify_super_admin),
    db_session: Session = Depends(DatabaseManager().get_session),
    super_admin_manager: SuperAdminManager = Depends(SuperAdminManager),
):
    return super_admin_manager.change_role_of_user(role_change, db_session)


@superadmin_router.post("/change_user_status")
async def change_user_status(
    status_change: UserStatusUpdate,
    superadmin_user: User = Depends(UserManager().authenticate_and_verify_super_admin),
    db_session: Session = Depends(DatabaseManager().get_session),
    super_admin_manager: SuperAdminManager = Depends(SuperAdminManager),
):
    return super_admin_manager.change_status_of_user(status_change, db_session)


@superadmin_router.delete("/delete_user/{user_id}")
async def delete_user(
    user_id: int,
    superadmin_user: User = Depends(UserManager().authenticate_and_verify_super_admin),
    db_session: Session = Depends(DatabaseManager().get_session),
    super_admin_manager: SuperAdminManager = Depends(SuperAdminManager),
):
    return super_admin_manager.delete_user(user_id, db_session)
