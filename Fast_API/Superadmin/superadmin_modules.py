from .superadmin_schemas import RoleTableAdd, UserRoleUpdate
from Fast_API.Database.role_db import RoleDatabaseAction
from Fast_API.Database.user_db import UserDatabaseAction
from fastapi.responses import JSONResponse
from Fast_API.Database.models import Role
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


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
