class DebugOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(">>> Django sees Origin:", request.headers.get('Origin'))
        print("HOST: ", request.headers.get('Host'))

        return self.get_response(request)