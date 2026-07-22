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


class DisableCSRFForAPI:
    """
    Middleware для отключения CSRF проверки для API endpoints.
    API использует JWT токены вместо сессий, поэтому CSRF не нужен.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Отключаем CSRF проверку для API endpoints
        if request.path.startswith('/api/'):
            request.csrf_processing_done = True

        return self.get_response(request)
