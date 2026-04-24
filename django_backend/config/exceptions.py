from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Exception):
        return Response({
            'status': 'error',
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Business Logic Error',
            'errors': {'detail': str(exc)}
        }, status= status.HTTP_400_BAD_REQUEST)

    if response is not None:
        custom_data = {
            'status': 'error',
            'status_code': response.status_code,
            'message': 'Data validation error' if response.status_code == 400 else 'Server error',
            'errors': response.data
        }
        response.data = custom_data

    return response