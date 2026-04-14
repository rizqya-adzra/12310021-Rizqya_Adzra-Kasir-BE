from rest_framework.response import Response
from rest_framework import status

from rest_framework.response import Response
from rest_framework import status
def response_success(message, data=None, status_code=status.HTTP_200_OK, current_page=None, total_pages=None, total_count=None):
    if total_count is not None:
        count = total_count
    else:
        count = 0
        if data is not None:
            if isinstance(data, (list, tuple)):
                count = len(data)
            elif hasattr(data, 'count'):
                try:
                    count = data.count() 
                except TypeError:
                    count = len(data)
            elif isinstance(data, dict) and not data:
                count = 0
            else:
                count = 1 if data else 0

    response_body = {
        "success": True,
        "status_code": status_code,
        "message": message,
        "count": count, 
        "data": data
    }

    if current_page is not None:
        response_body["current_page"] = current_page
    if total_pages is not None:
        response_body["total_pages"] = total_pages

    return Response(response_body, status=status_code)


def response_error(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    formatted_errors = None
    
    if errors:
        formatted_errors = {}
        if isinstance(errors, dict):
            for key, val in errors.items():
                formatted_errors[key] = val[0] if isinstance(val, list) else str(val)
                if key == 'non_field_errors':
                    formatted_errors['detail'] = formatted_errors.pop('non_field_errors')
        else:
            formatted_errors = {"detail": str(errors)}

    return Response({
        "success": False,
        "status_code": status_code,
        "message": message,
        "errors": formatted_errors
    }, status=status_code)