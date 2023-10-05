from django.contrib.auth import logout

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user ID is in the session
        user_id = request.session.get('username')

        if not user_id:
            # User ID is not in the session, log out the user
            logout(request)

        response = self.get_response(request)
        return response
