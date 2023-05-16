from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename=view_func.__module__
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "kodua.hodviews":
                    pass
                elif modulename == "kodua.views" or modulename == "django.views.static":
                    pass
                
                elif modulename == "django.contrib.auth.views" or modulename =="django.contrib.admin.sites":
                    pass
                else:
                    return HttpResponseRedirect("admin_home")
            elif user.user_type == "2":
                if modulename == "kodua.views":
                    pass
                elif modulename == "django.views.static"  :
                    pass
                else:
                    return HttpResponseRedirect(reverse("staff_home"))
            else:
                return HttpResponseRedirect(reverse("show_login"))
        else:
            if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views" or modulename =="django.contrib.admin.sites" or request.path == reverse("update_week"):
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))