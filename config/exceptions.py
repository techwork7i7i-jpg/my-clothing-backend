"""
Centralized API error responses for consistent frontend handling.
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # Wrap DRF errors in a predictable shape
        if isinstance(response.data, dict) and "detail" not in response.data:
            response.data = {
                "success": False,
                "errors": response.data,
            }
        elif isinstance(response.data, dict):
            response.data = {
                "success": False,
                "errors": response.data,
            }
    return response
