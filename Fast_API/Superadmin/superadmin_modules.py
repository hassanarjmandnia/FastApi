from .superadmin_schemas import RoleTableAdd, UserRoleUpdate, UserStatusUpdate
from Fast_API.Database.role_db import RoleDatabaseAction
from Fast_API.Database.user_db import UserDatabaseAction
from fastapi.responses import JSONResponse
from Fast_API.Database.models import Role
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update


class SuperAdminAction:
    def __init__(self, role_database_action, user_database_action):
        self.role_database_action = role_database_action
        self.user_database_action = user_database_action

    def add_role(self, role_name, db_session):
        existing_role = self.role_database_action.get_role_by_name(
            role_name.name, db_session
        )
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role already exists. Please choose a different role name",
            )
        else:
            new_role = Role(**role_name.model_dump())
            new_role = self.role_database_action.add_role(new_role, db_session)
            message = "New Role Add Successfully"
            status_code = 200
            return JSONResponse(content={"message": message}, status_code=status_code)

    def change_role_of_user(self, role_change, db_session):
        user = self.user_database_action.get_user_by_id(role_change.user_id, db_session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this id don't exist!",
            )
        role = self.role_database_action.get_role_by_name(role_change.name, db_session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role with this name don't exist",
            )
        user.role_id = role.id
        self.user_database_action.commit_changes(db_session)
        self.user_database_action.refresh_item(user, db_session)
        return user

    def change_status_of_user(self, status_change, db_session):
        user = self.user_database_action.get_user_by_id(
            status_change.user_id, db_session
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this id don't exist!",
            )
        user.is_active = status_change.new_status
        self.user_database_action.commit_changes(db_session)
        self.user_database_action.refresh_item(user, db_session)
        return user

    def delete_user(self, user_id, db_session):
        user = self.user_database_action.get_user_by_id(user_id, db_session)
        if user:
            self.user_database_action.delete_user(user, db_session)
            message = "User deleted successfully"
            status_code = 200
            return JSONResponse(content={"message": message}, status_code=status_code)

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sorry, the User you're looking for does not exist.",
            )

    def delete_role(self, role_id, db_session):
        role = self.role_database_action.get_role_by_id(role_id, db_session)
        if role:
            if role.name == "user":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="nah, don't even think about it!",
                )
            else:
                default_role = self.role_database_action.get_role_by_name(
                    "user", db_session
                )
                if not default_role:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Role with this name don't exist",
                    )
                self.user_database_action.update_users_role_to_default(
                    db_session, default_role.id, role_id
                )
                self.role_database_action.delete_role(role, db_session)
                message = "Role deleted successfully"
                status_code = 200
                return JSONResponse(
                    content={"message": message}, status_code=status_code
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sorry, the Role you're looking for does not exist.",
            )


class SuperAdminManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.role_database_action = RoleDatabaseAction()
            cls._instance.user_database_action = UserDatabaseAction()
            cls._instance.worker = SuperAdminAction(
                cls._instance.role_database_action, cls._instance.user_database_action
            )
        return cls._instance

    def add_role(self, role_name: RoleTableAdd, db_session: Session):
        return self.worker.add_role(role_name, db_session)

    def change_role_of_user(self, role_change: UserRoleUpdate, db_session: Session):
        return self.worker.change_role_of_user(role_change, db_session)

    def change_status_of_user(
        self, status_change: UserStatusUpdate, db_session: Session
    ):
        return self.worker.change_status_of_user(status_change, db_session)

    def delete_user(self, user_id: int, db_session: Session):
        return self.worker.delete_user(user_id, db_session)

    def delete_role(self, role_id: int, db_session: Session):
        return self.worker.delete_role(role_id, db_session)
