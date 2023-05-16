from cgitb import reset
from django.urls import path,include
from kodua import views as staff_views
from kodua import hodviews as hod_views
from django.conf.urls.static import static
from TK import settings
from kodua.models import *




urlpatterns = [
    path("", staff_views.ShowLoginPage, name="show_login"),
    path("staff_home",staff_views.staff_home, name='staff_home'),
    path("add_general_department", hod_views.add_general_department, name="add_general_department"),
    path('timetable', staff_views.create_timetable, name='timetable'),
    path('save_personal_timetable', staff_views.save_personal_timetable, name='save_personal_timetable'),
    path('add_class', hod_views.add_class, name='add_class'),
    path('check_class_exist', hod_views.check_class_exist, name='check_class_exist'),
    path('attend', staff_views.attend, name='attend'),
    path('admin_home', hod_views.admin_home, name='admin_home'),
    path('update_calender', hod_views.update_calender, name='update_calender'),
    path("view_staff", hod_views.view_staff, name="view_staff"),
    path("view_staff_record/<str:staff_id>", hod_views.view_staff_record, name="view_staff_record"),
    # path("view_department/<str:department_id>"hod_views.view_departmentid, name="view_departmentid")
    path("view_class", hod_views.view_class,name="view_class"),
    path("log_attendance", staff_views.log_attendance, name="log_attendance"),
    path('close_attendance', staff_views.close_attendance, name="close_attendance"),
    path('add_staff', hod_views.add_staff, name="add_staff"),
    path("add_department", hod_views.add_department, name="add_department"),
    path("add_staff_save", hod_views.add_staff_save, name="add_staff_save"),
    path("add_department_save", hod_views.add_department_save, name="add_department_save"),
    path("view_departments", hod_views.view_department, name="view_department"),
    path("login", staff_views.ShowLoginPage, name="show_login"),
    path("do_login", staff_views.doLogin, name="do_login"),
    path("logout_user", staff_views.logout_user, name="logout_user"),
    path("add_course", hod_views.add_course, name="add_course"),
    path("add_course_save", hod_views.add_course_save, name="add_course_save"),
    path("staff_profile", staff_views.staff_profile, name="staff_profile"),
    path("staff_profile_save", staff_views.staff_profile_save, name="staff_profile_save"),
    path("admin_profile", hod_views.admin_profile, name="admin_profile"),
    path("admin_profile_save", hod_views.admin_profile_save, name="admin_profile_save"),
    path("reset_password", hod_views.reset_password, name="reset_pass"),
    path("reset_password_save", hod_views.reset_password_save, name="reset_pass_save"),
    path("update_week", hod_views.update_week, name="update_week"),
    path("remove_staff", hod_views.remove_staff, name="remove_staff"),
    path("remove_staff_save", hod_views.remove_staff_save, name="remove_staff_save"),
    path("issue_tracker", staff_views.issue_tracker, name="issue_tracker"),
    path("summernote/", include('django_summernote.urls')),
    path("tickets", staff_views.tickets, name="tickets"),
    path("view_ticket/<str:ticket_id>", hod_views.view_ticket, name="view_ticket"),
    path("get_issues", hod_views.get_issues,name="get_issues"),
    path("resolve" ,hod_views.resolve, name="resolve"),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
