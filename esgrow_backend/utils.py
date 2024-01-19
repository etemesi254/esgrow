from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # # Now add the HTTP status code to the response.
    # if response is not None:
    #     response.data['status'] = response.status_code
    # response.data['errors'] = {exc.get_codes(): [str(exc)]}
    # response.data["status_description"] = exc.get_codes()
    # response.data.pop('detail', None)
    # response.data["data"] = {}
    return response
