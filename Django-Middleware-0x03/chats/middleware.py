from datetime import time, datetime
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.http import JsonResponse
from django.http import HttpResponseForbidden



class RequestLoggingMiddleware:

    
    """
    Middleware to log each users request to a file includes timestamp, user and request
    """
    def __init__(self, get_response):
        """
        Constructor that runs once when Django starts get_response: the next middleware in the chain
        """
        
        self.get_response = get_response
        print("RequestLoggingMiddleware initialized") #debug info
        
        def __call__(self, request):
            """
            this method is called for every request 
            request: the HTTP request object
            """
            current_time = time.now()
        
        #Get user information - check of user is authenticated
        
            if request.user.is_authenticated:
                user = request.user.username
            else:
                user = "Anonymous"
                
            # Get the requesr path
            path = request.path
            
            #format the log message as specified
            log_message = f"{current_time} - User:{user} - Path: {path}\n"
            
            #Write to the log file
            
            try:
                #'a' mode appends to file, creates it if doesnt exist
                
                with open('request.log', 'a') as log_file:
                    log_file.write(log_message)
            except Exception as e:
                print(f"Error writing to log file: {e}")
                
            response = self.get_response(request)
            
            return response
class RestictAccessByTimeMiddleware:
    """
    Middleware to restrict chat access between 9 pm and 6 am 
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        #Get current time
        from datetime import datetime
        current_time = datetime.now().time()
        
        #Define restricted hours (9am to 6am)
        start_restriction = time(21,0)
        end_restriction = time(6,0)
        
        is_restricted_time = (
            current_time >= start_restriction or
            current_time <= end_restriction
        )
        
        #Check if the request is for chat-related pathhs
        
        is_chat_path = any([
            '/chat/' in request.path,
            '/messages/' in request.path,
            request.path == '/chat',
            request.path =='/messages'
        ])
        
        if is_restricted_time and is_chat_path:
            #Allow admin users to bypass restriction
            
            if not (request.user.is_authenticated and request.user.is_staff):
                return HttpResponseForbidden(
                    
                    "chat access is restricted between 9pm and 6am"
                    "Please try again during allowed hours"
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
        self.rate_limit = 5
        self.time_window = 60
        
    def __call__ (self, request):
         if request.method == 'POST' and any(path in request.path for path in ['/chat/', '/messages/']):
             
             ip = self.get_client_ip(request)
             cache_key = f"rate_limit_{ip}"
             
             current_data = cache.gett(cache_key, {'count': 0, 'first_request': None})
             
             
             if current_data['first_request'] is None:
                 #First request from this IP
                 
                 current_data = {
                     'count': 1,
                     'first_request': datetime.now()
                 }
             else: 
                
                from datetime import timedelta
                time_diff =(datetime.now() - current_data['first_request']).total_seconds()
                
                if time_diff < self.time_window:
                    
                    current_data['count'] += 1
                else:
                    
                    current_data = {
                        'count': 1,
                        'first_request': datetime.now()
                    }
            
             if current_data['count']> self.rate_limit:
                 return JsonResponse ({
                     'error': f'Rate limit exceed.Maximum {self.rate_limit} messages per minute'
                     
                 }, status=429)
                 
             cache.set(cache_key, current_data, self.time_window)
             
             response = self.get_response(request)
             return response
         def get_client_ip (self, request):
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
    Middleware to check roles for specific actions
    
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        self.protected_paths = {
            '/admin/': ['admin'],
            '/moderator/': ['admin', 'moderator'],
            '/api/delete-message/':['admin', 'moderator'],
            '/api/ban-user/': ['admin'],
        }
    def __call__(self, request):
        
        for path, required_roles in self.protected_paths.items():
            if request.path.startswith(path):
                if not request.user.is_authenticated:
                    return HttpResponseForbidden("Authentication required.")
                
                if not self.user_has_required_role(request.user, required_roles):
                    return HttpResponseForbidden(
                        "You dont have permission to access this resource"
                    )
                break
    def user_has_required_role(self, user, required_roles):
        """
        check if user has any of the required roles
        """
        user_roles = []
        
        #Determine users's roles
        if user.is_superuser or user.is_staff:
            user_roles.append('admin')
            
            #Check for moderatoe role(you might need to customize this)
            #Thid assumes you have a user profile with role field
            
        if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
            user_roles.append(user.profiles.role)
            
        return any(role in user_roles for role in required_roles)
    
                