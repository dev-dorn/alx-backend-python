             
                
from datetime import datetime, time
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache

class RequestLoggingMiddleware:
    """
    Middleware to log each user's requests to a file
    Includes timestamp, user, and request path
    """
    
    def __init__(self, get_response):
        """
        Constructor that runs once when Django starts
        get_response: the next middleware in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for every request
        request: the HTTP request object
        """
        # Get current timestamp
        current_time = datetime.now()
        
        # Get user information - check if user is authenticated
        if request.user.is_authenticated:
            user = request.user.username
        else:
            user = "Anonymous"
        
        # Get the request path
        path = request.path
        
        # Format the log message as specified
        log_message = f"{current_time} - User: {user} - Path: {path}\n"
        
        # Write to the log file
        try:
            # 'a' mode appends to file, creates it if doesn't exist
            with open('requests.log', 'a') as log_file:
                log_file.write(log_message)
        except Exception as e:
            # If file writing fails, print error but don't break the application
            print(f"Error writing to log file: {e}")
        
        # Continue to the next middleware/view
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict chat access between 9 PM and 6 AM
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current time
        current_time = datetime.now().time()
        
        # Define restricted hours (9 PM to 6 AM)
        start_restriction = time(21, 0)  # 9:00 PM
        end_restriction = time(6, 0)     # 6:00 AM
        
        # Check if current time is within restricted hours
        is_restricted_time = (
            current_time >= start_restriction or 
            current_time <= end_restriction
        )
        
        # Check if the request is for chat-related paths
        is_chat_path = any([
            '/chat/' in request.path,
            '/messages/' in request.path,
            request.path == '/chat',
            request.path == '/messages',
        ])
        
        # If it's restricted time and accessing chat, block access
        if is_restricted_time and is_chat_path:
            # Allow admin users to bypass restriction
            if not (request.user.is_authenticated and request.user.is_staff):
                return HttpResponseForbidden(
                    "Chat access is restricted between 9 PM and 6 AM. "
                    "Please try again during allowed hours."
                )
        
        # Continue with normal processing
        response = self.get_response(request)
        return response


class RateLimitMiddleware:
    """
    Middleware to limit chat messages to 5 per minute per IP
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 5  # 5 messages
        self.time_window = 60  # 1 minute in seconds

    def __call__(self, request):
        # Only apply to POST requests (sending messages)
        if request.method == 'POST' and any(path in request.path for path in ['/chat/', '/messages/']):
            # Get client IP address
            ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{ip}"
            
            # Get current count from cache
            current_data = cache.get(cache_key, {'count': 0, 'first_request': None})
            
            if current_data['first_request'] is None:
                # First request from this IP
                current_data = {
                    'count': 1,
                    'first_request': datetime.now()
                }
            else:
                # Check if still within time window
                time_diff = (datetime.now() - current_data['first_request']).total_seconds()
                
                if time_diff < self.time_window:
                    # Within time window, increment count
                    current_data['count'] += 1
                else:
                    # Time window expired, reset
                    current_data = {
                        'count': 1,
                        'first_request': datetime.now()
                    }
            
            # Check if rate limit exceeded
            if current_data['count'] > self.rate_limit:
                return JsonResponse({
                    'error': f'Rate limit exceeded. Maximum {self.rate_limit} messages per minute.'
                }, status=429)
            
            # Update cache
            cache.set(cache_key, current_data, self.time_window)
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        Extract client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware:
    """
    Middleware to check user roles for specific actions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected paths and required roles
        self.protected_paths = {
            '/admin/': ['admin'],
            '/moderator/': ['admin', 'moderator'],
            '/api/delete-message/': ['admin', 'moderator'],
            '/api/ban-user/': ['admin'],
        }

    def __call__(self, request):
        # Check if current path requires special permissions
        for path, required_roles in self.protected_paths.items():
            if request.path.startswith(path):
                if not request.user.is_authenticated:
                    return HttpResponseForbidden("Authentication required.")
                
                # Check if user has required role
                if not self.user_has_required_role(request.user, required_roles):
                    return HttpResponseForbidden(
                        "You don't have permission to access this resource."
                    )
                break  # Found matching path, no need to check others
        
        response = self.get_response(request)
        return response

    def user_has_required_role(self, user, required_roles):
        """
        Check if user has any of the required roles
        """
        user_roles = []
        
        # Determine user's roles
        if user.is_superuser or user.is_staff:
            user_roles.append('admin')
        
        # Check for moderator role (you might need to customize this)
        # This assumes you have a user profile with role field
        if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
            user_roles.append(user.profile.role)
        
        # Check if user has any of the required roles
        return any(role in user_roles for role in required_roles)