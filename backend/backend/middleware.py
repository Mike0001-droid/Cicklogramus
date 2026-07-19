class CorsPreflightMiddleware:
    """
    Middleware для кэширования CORS preflight запросов.
    Добавляет правильные заголовки для кэширования OPTIONS запросов.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Добавляем заголовки для кэширования preflight запросов
        if request.method == 'OPTIONS':
            response['Access-Control-Max-Age'] = '3600'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = ', '.join([
                'accept',
                'accept-encoding',
                'authorization',
                'content-type',
                'dnt',
                'origin',
                'user-agent',
                'x-csrftoken',
                'x-requested-with',
            ])

        return response
