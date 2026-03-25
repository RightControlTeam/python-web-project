from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'status': 'error',
            'status_code': response.status_code,
            'message': 'Data validation error' if response.status_code == 400 else 'Server error',
            'errors': response.data
        }
        response.data = custom_data

    return response