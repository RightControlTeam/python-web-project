from user_module.user_schemas import UserResponse, UserRequest
from user_module.user import User
from security.password_hashing import hash_password


def user_from_request(request: UserRequest) -> User:
    return User(
        username = request.username,
        password_hash = hash_password(request.password)
    )


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id = user.id,
        username = user.username
    )