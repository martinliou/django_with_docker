from rest_framework.views import exception_handler

def custom_exception_handler(exc, context = None):
    '''Override JWT default error response'''
    response = exception_handler(exc, context)
    try:
        # ovverride IsAuthenticated permission class exception
        if response and (response.data['detail'].code in \
         ['not_authenticated', 'authentication_failed', 'token_not_valid']):
            response.data['status'] = -2
            response.data['message'] = 'Invalid access token or not authenticated'
            for key in ['detail', 'code', 'messages']:
                if key in response.data:
                    del response.data[key] 
    except Exception as e:
        pass

    return response