import datetime
from decimal import Clamped
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import re
from kodua.EmailBackEnd import EmailBackEnd
from django.http import HttpResponse, HttpResponseRedirect
from urllib import request
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render
from kodua import models as md
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .forms import IssueTrackerForms

# from geopy.distance import distance

# def in_radius(reqeust):
#     points = [29.234, 15.3821]

#     input_point= (10.12232, 30.3233)

#     if distance(input_point, points).km<1:
#         #print('within radius')
#     else:
#         #print('out of radius')


def get_cordinates(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip =  request.META.get('REMOTE_ADDR')
    return ip
def close_attendance(request):
    data = request.POST
    section = md.Section.objects.get(id=int(data.get('section_id')))
    eda = datetime.datetime.now().strftime("%H:%M:%S")
    cur_time =datetime.datetime.strptime(f"{eda}","%H:%M:%S") 
    cur_time = timedelta(hours=cur_time.hour, minutes=cur_time.minute)
    e_time = timedelta(seconds=int(section.e_time)) 
    e_time_f = e_time + timedelta(minutes=30)
    if  e_time <= cur_time <= e_time_f:
        clas = md.Classes.objects.get(class_name = data['clas'])
        prefect = data['prefect_id']
        if clas.prefect.username == data['prefect_id']:
            section.in_session=False 
            section.was_present = True
            section.save()
            return HttpResponse('true')
        return HttpResponse('false')
    
    
    return HttpResponse("NT")

def log_attendance(request):
    if request.method != 'POST':
        return HttpResponse('not authorized')
    data = request.POST
    #print(data)
    clas = md.Classes.objects.get(class_name=data['clas'])
    section = md.Section.objects.get(id=data['section_id'])
    if clas.prefect.username == data['prefect_id']:
        section.in_session=True 
        section.save()
        return HttpResponse('true')
    return HttpResponse('false')
    #print(data)
    # clas = data['clas']
    # course = data['course']
    # p_id = data['prefect_id'] 
    # #print(data) 



def attend(request):
    section = md.Section.objects.get(id=int(request.POST.get('content')))
    
    return HttpResponse(json.dumps([section.course.course_name,section.clas.class_name, section.id]))


def make_status(t_time,s_time,e_time, obj):
    
    from datetime import timedelta, datetime
    import time
    time_yet = 0
    e_time = timedelta(seconds=int(e_time))
    cur_time = timedelta(hours=t_time.hour, minutes=t_time.minute)
    s_time = timedelta(seconds=int(s_time))
    print(e_time.seconds//3600, s_time.seconds//3600)
    over = False 
    hrs = (e_time - s_time).seconds//3600
    s_day = datetime.strptime(str(s_time), "%H:%M:%S")
    print(e_time.seconds//3600, s_time.seconds//3600)
    ms = datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S")
    # la = datetime.strptime("17:00", "%H:%M")  
    #print(t_time.strftime("%H:%M:%S"), ms.time())
    print(e_time.seconds//3600, s_time.seconds//3600)
    if s_day.time() > ms.time(): 
        time_yet=1
    if hrs > 1:
        en_time = e_time - timedelta(hours=1, minutes=(e_time.seconds%3600)//60)
    else:
        en_time = e_time - timedelta(minutes=30)
    print(e_time.seconds//3600, s_time.seconds//3600)
        # #print(timedelta(minutes=(e_time.seconds%3600)//60), 'getting mins')

    if s_time <= cur_time <= en_time:
        status = 1
    
    else:
        if cur_time >= e_time + timedelta(minutes=8):
            print('session is over now', cur_time, e_time + timedelta(minutes=8))
            over =True
         
        status = 0
    print(e_time.seconds//3600, s_time.seconds//3600)
  
    return [status, s_time,e_time, obj.course.course_name,obj.clas.class_name,obj.id,obj.was_present, obj.in_session, time_yet, over]

def staff_home(request):
    # ip = get_cordinates(request)
    st = md.Staffs.objects.get(admin=request.user)

    cur_term = md.TermData.objects.filter(is_current = True)[0]
    tot_sec = md.Section.objects.filter(year=cur_term.year.year, term=cur_term.term, instructor=st).count()
    lst = [
    md.Section.objects.filter(year=cur_term.year.year, term=cur_term.term, instructor=st, was_present=True).count(),
    tot_sec]
    if tot_sec>=1: nt=0 
    else:nt=1
    expired = []
    in_sess = []
    day = datetime.datetime.now().strftime("%A") 
    tmrw = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%A")
    instructor_section_today = md.Section.objects.filter(year=cur_term.year.year, term=cur_term.term,week=cur_term.week, day=day.lower(), instructor=st)
    instructor_section_tmrw = md.Section.objects.filter(year=cur_term.year.year,week=cur_term.week, term=cur_term.term,day=tmrw.lower(), instructor=st)
    # instructor_section = sect.meetingtime_set.filter(day='monday')
    foo = 1
    eda = datetime.datetime.now().strftime("%H:%M:%S")
  
    cur_time =datetime.datetime.strptime(f"{eda}","%H:%M:%S") 

    for t in instructor_section_today:
        status = make_status(cur_time.time(), t.s_time,t.e_time,t)
       
        if status[0]:
            in_sess.append(status)
        else:
            expired.append(status)
    if cur_term.ended:
        instructor_section_tmrw = []
        in_sess = []
        nt = []
        expired = []
    return render(request, 'student_template/student_home_template.html', {"cur_term":cur_term, "data":lst,'tomorrows':instructor_section_tmrw,"in_session":in_sess,"nt":nt, "expired":expired})

def tickets(request):
    st = md.Staffs.objects.get(admin=request.user)
    tk = md.IssueTracker.objects.filter(user=st)
    return render(request, "student_template/tickets.html", {"tickets":tk})

def issue_tracker(request):
    if request.method != "POST":
        return render(request, 'student_template/issues.html')
    st = md.Staffs.objects.get(admin=request.user)
    data = request.POST
    
    tk = md.IssueTracker()
    tk.user = st 
    tk.title = data['title']
    tk.content = data['sancont']
    tk.save()
    messages.success(request, "Ticket opened Pending Investigation, You can check if issue is resolved here")
    return HttpResponse("done")

def create_timetable(request):
    # cs = request.user
    if request.method != "POST":
        return HttpResponse("Unauthorized Access")
    st = md.Staffs.objects.get(admin=request.user)
    department = md.Departments.objects.get(department_name=st.department.department_name)
    courses = department.course_set.all()
    class_list = st.classes.all()
    print(class_list, 'class list')
    # class_list = ['Form 1A', 'Form 1B', 'Form 1C', 'Form 2A','Form 2B', 'Form 2C', 'Form 3A', 'Form 3B', 'Form 3C']

    return render(request, 'student_template/personalized_timetable.html',{'courses':courses,'classes':class_list})
 
def save_personal_timetable(request):
    days ={}
    identify = 0
    # user = request.user
    user = md.CustomUser.objects.get(username=request.user.username)
    staff = md.Staffs.objects.get(admin=user)
    dep = staff.department
    datas = json.loads(request.POST.get('content'))
    cur_term = md.TermData.objects.filter(is_current=True)[0]
    for z in range(1, cur_term.num_weeks + 1):
        for data in datas:
            identify +=1
            tmp = []
            for dat in datas[data]:
                if len(datas[data][dat])>2:
                    tmp.append(datas[data][dat])
            if identify ==1:
                days['monday'] = tmp
            elif identify ==2:
                days['tuesday'] = tmp
            elif identify ==3:
                days['wednesday'] = tmp
            elif identify ==4:
                days['thursday'] = tmp
            else:
                days['friday'] = tmp
        
        for day in days:
            
            if days[day]:
                for foo in days[day]:
            
                    dy = foo
                    print(foo)
                    pattern = '[0-9]+'
                    tt = foo[-1]
                    reg_time = re.findall(pattern, tt)
                    start_time = datetime.datetime.strptime(f'{reg_time[0]}:{reg_time[1]} {tt[-2:]}', "%I:%M %p")

                    s_time = timedelta(hours=start_time.time().hour, minutes=start_time.time().minute)
                    
                    e_time = s_time + timedelta(hours=int(foo[2]))

                    clas =  md.Classes.objects.get(class_name = foo[1])
                    print(clas.department.get(is_general=False), 'kkkkkkk')
                    course = md.Course.objects.get(course_name=foo[0], department=dep)
                    
                    section = md.Section()
                    section.day = day
                    section.week = z
                    section.s_time =str(s_time.seconds)
                    section.e_time =str(e_time.seconds)
                    section.year = int(md.TermData.objects.filter(is_current=True)[0].year.year)
                    section.term = md.TermData.objects.filter(is_current=True)[0].term
                    # section.meeting_time = meeting_time
                    section.clas = clas
                    section.instructor = md.Staffs.objects.get(admin=user)
                    section.course = course
                    section.save()

        
    return HttpResponse('all good')


def ShowLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        # captcha_token=request.POST.get("g-recaptcha-response")
        # cap_url="https://www.google.com/recaptcha/api/siteverify"
        # cap_secret="6LeWtqUZAAAAANlv3se4uw5WAg-p0X61CJjHPxKT"
        # cap_data={"secret":cap_secret,"response":captcha_token}
        # cap_server_response=requests.post(url=cap_url,data=cap_data)
        # cap_json=json.loads(cap_server_response.text)

        # if cap_json['success']==False:
        #      messages.error(request,"Invalid Captcha Try Again")
        #      return HttpResponseRedirect("/login.php")
        #print(request.POST)
        user=EmailBackEnd.authenticate(request,username=request.POST.get("username"),password=request.POST.get("password"))
        #print(user)
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect('admin_home')
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse('staff_home'))
           
        else:
            # return HttpResponseRedirect(reverse("student_home"))
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect(reverse("show_login"))

def staff_profile(request):
    return render(request, "student_template/staff_profile.html")

def staff_profile_save(request):
    if request.method != 'POST':
        return HttpResponse("Unauthorized Access")
    data = request.POST
    password=data["password"]
    try:
        customuser=md.CustomUser.objects.get(pk=request.user.id)
        customuser.first_name=data['first_name']
        customuser.last_name=data['last_name']
        if password!=None and password!="":
            customuser.set_password(password)
                # if password!=None and password!="":
                #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
    except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
    return HttpResponseRedirect(reverse("staff_profile"))
    
   
 
def logout_user(request):
    logout(request)
    messages.success(request, "Successfully Logged out")
    return HttpResponseRedirect("/")