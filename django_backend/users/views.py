from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from sqlalchemy.sql.functions import user

from .models import User
from .jwt_utils import generate_token
import logging
from .notifications import send_registration_email, send_security_alert

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register(request):
    """Регистрация нового пользователя"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'}, 
            status=status.HTTP_409_CONFLICT
        )
    
    user = User.objects.create_user(username=username, password=password)
    token = generate_token(user.id)
    
    # Логируем как в старом FastAPI
    logger.info(f"Создан новый пользователь: {user.username}")
    send_registration_email(username)
    
    return Response({
        'access_token': token,
        'token_type': 'Bearer',
        'user_id': user.id,
        'username': user.username,
        'balance': user.balance
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    """Вход пользователя"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = generate_token(user.id)
    
    # Логируем как в старом FastAPI
    logger.info(f"Пользователь {username} вошел в систему")
    send_security_alert(username)
    
    return Response({
        'access_token': token,
        'token_type': 'Bearer',
        'user_id': user.id,
        'username': user.username,
        'balance': user.balance
    })

@api_view(['GET'])
def get_me(request):
    """Получить свой профиль (нужен токен)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'error': 'No token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        user_id = int(payload['sub'])
        user = User.objects.get(id=user_id)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'balance': user.balance
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def update_me(request):
    """Обновить свой профиль"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'error': 'No token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        user_id = int(payload['sub'])
        user = User.objects.get(id=user_id)
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username:
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                return Response({'error': 'Username already exists'}, status=409)
            user.username = username
        if password:
            user.set_password(password)
        
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'balance': user.balance
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
def delete_me(request):
    """Удалить свой профиль"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'error': 'No token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        user_id = int(payload['sub'])
        user = User.objects.get(id=user_id)
        user.delete()
        
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_balance(request):
    amount = request.data.get('amount')
    order_id = request.data.get('order_id')
    user = request.user
    if not amount:
        return Response({'error': 'Amount required'}, status=status.HTTP_400_BAD_REQUEST)
    new_balance = user.balance + amount
    if new_balance < 0:
        return Response({'error': 'Balance cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
    user.balance = new_balance
    user.save()
    return Response({
        'user_id': user.id,
        'balance': user.balance,
        'order_id': order_id
        },
        status=status.HTTP_200_OK
    )


