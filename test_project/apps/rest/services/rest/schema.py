from pydantic import BaseModel


class UserSchema(BaseModel):
    """Schema for DummyJSON User API."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str


class UsersListResponseSchema(BaseModel):
    """Response schema for /users endpoint."""
    users: list[UserSchema]
    total: int
    skip: int
    limit: int
