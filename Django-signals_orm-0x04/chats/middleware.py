import logging
from django.http import HttpResponseForbidden
from datetime import datetime
from time import time

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Set up a logger for requests.log
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("requests.log")
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        # Only allow access between 6PM (18:00) and 9PM (21:00)
        if not (now.hour >= 18 and now.hour < 21):
            return HttpResponseForbidden("Access to chat is only allowed between 6PM and 9PM.")
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_times = {}

    def __call__(self, request):
        # Only apply to POST requests to the message endpoint
        if request.method == "POST" and "/messages" in request.path:
            ip = request.META.get('REMOTE_ADDR')
            now = time()
            window = 60  # 1 minute
            limit = 5    # 5 messages per minute

            # Clean up old entries
            self.ip_message_times.setdefault(ip, [])
            self.ip_message_times[ip] = [t for t in self.ip_message_times[ip] if now - t < window]

            if len(self.ip_message_times[ip]) >= limit:
                return HttpResponseForbidden("Message rate limit exceeded. Try again later.")

            self.ip_message_times[ip].append(now)

        return self.get_response(request)

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce for authenticated users and for chat actions (customize path as needed)
        if request.user.is_authenticated and "/messages" in request.path:
            # Check for 'admin' or 'moderator' role (adjust field as per your User model)
            user_role = getattr(request.user, "role", None)
            if user_role not in ("admin", "moderator"):
                return HttpResponseForbidden("You do not have permission to perform this action.")
        return self.get_response(request)
