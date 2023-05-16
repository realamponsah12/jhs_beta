from ast import Return
from calendar import week
import datetime
from dis import Instruction
from email import message
import json
import re
from django.http import HttpResponse,HttpResponseRedirect
from urllib import request
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render
from kodua import models as md
from django.urls import reverse
from rest_framework import status 
from rest_framework.decorators import api_view


def add_class(request):
    forms = ['Form 1A', 'Form 1B', 'Form 1C', 'Form 2A','Form 2B', 'Form 2C', 'Form 3A', 'Form 3B', 'Form 3C']
    department = md.Departments.objects.filter(is_general=False)
    dep1 = md.Classes.objects.filter(department = department[0])
    return render(request, 'admin_template/add_class.html', {'departments':department, 'classes':dep1, 'forms':forms})

def add_general_department(request):
    if request.method != "POST":
        return HttpResponse("Unauthorized Access")
    data = request.POST
    dep = md.Departments.objects.filter(department_name=data['department'])
    if dep:
        messages.error(request, f"{data['department']} department already exists")
        return HttpResponseRedirect("add_department")
    dep = md.Departments.objects.create(department_name=data['department'], is_general=True)
    dep.save()
    messages.success(request, f"General Department {data['department']} Successfully added")
    return HttpResponseRedirect("add_department")

def check_class_exist(request):
    import re
    dep = [x for x in md.Departments.objects.all() if x.is_general ]
    print(dep)
    if request.method == 'POST':
        clas = request.POST.get('clas')
        prfct = request.POST.get('prefect')
        data = request.POST.get('data')
        c_p = md.CustomUser.objects.filter(username=prfct)
        clas_in = md.Classes.objects.filter(class_name = clas)
        clas_form = clas[-2:]
        if data[-1] != clas[-2]:
            return HttpResponse('error2')
        if clas_in:
            return HttpResponse('error')
        elif c_p:
            return HttpResponse('error1')
        prefect = md.CustomUser.objects.create_user(username=prfct, password=prfct, user_type=3)
        prefect.save()
        departmnt = request.POST.get('data')
        department = md.Departments.objects.get(department_name = departmnt)
        form = request.POST.get('form')
        cls = md.Classes()
        cls.class_name = clas 
        cls.class_form = int(clas_form[0])
        cls.form_data = clas_form[-1]
        cls.prefect = prefect
        cls.save()
        print('trying to add department')
        for depart in dep:
            print("in the for loop", depart)
            cls.department.add(depart)
            cls.save()
        cls.department.add(department)
        cls.save()
        messages.success(request, f'{clas} Successfully added to Classes')
        return HttpResponse('good')


def admin_home(request):
  
    # student_count1=Students.objects.all().count()
    try:
        cur_term = md.TermData.objects.filter(is_current = True)[0]
    except:
        return HttpResponse("Contact Admin with code (E0332x3) No Academic calender found")
    staff_count=md.Staffs.objects.all().count()
    class_count=md.Classes.objects.all().count()
    dept_count = md.Departments.objects.all().count
    present = md.Section.objects.filter(year=cur_term.year.year, term=cur_term.term,was_present=True).count() 
    total =md.Section.objects.filter(year=cur_term.year.year, term=cur_term.term).count()
    try:present = round((present / total) * 100, 2)
    except:present=0
    absent = round(100 - present,2)
    prct = f'{present} %'
    dept_class_name = []
    departmnt_name  = []
    dept_attendance_stat = []

    for dp in md.Departments.objects.filter(is_general=False):
        print(dp)
        departmnt_name.append(dp.department_name)
        dept_class_name.append(dp.classes_set.all().count())
        cs = dp.classes_set.all()
        sec = 0
        pres = 0
        
        for c in cs:
            pres += c.section_set.filter(year=cur_term.year.year, term=cur_term.term,was_present=True).count()
            sec+= c.section_set.filter(year=cur_term.year.year, term=cur_term.term).count()
           
        try: rd = round((pres/sec)*100,2)
        except: rd=0
        dept_attendance_stat.append(rd)
    ##print(dept_attendance_stat)
    t = md.Section.objects.all()
    total_dept_count =[]
    m = 1
    for t in range(1,4):
        clas = md.Classes.objects.filter(class_form=t).count()
        
        total_dept_count.append(clas)
        m+=1
        if m > 3:
            m=1
    #print(total_dept_count)  
    f2_present_list, f2_total_list, f2_course_list = [], [], []
    f3_present_list, f3_total_list, f3_course_list = [], [], []
    for cls in range(2,4):
          cs = md.Classes.objects.filter(class_form=cls)
          for clas in cs:
            if cls == 2:
                f2_total_list.append(clas.section_set.filter(year=cur_term.year.year, term=cur_term.term).count())
                f2_course_list.append(clas.class_name)
                f2_present_list.append(clas.section_set.filter(year=cur_term.year.year, term=cur_term.term,was_present=True).count())
            else:
                f3_total_list.append(clas.section_set.filter(year=cur_term.year.year, term=cur_term.term).count())
                f3_course_list.append(clas.class_name)
                f3_present_list.append(clas.section_set.filter(year=cur_term.year.year, term=cur_term.term,was_present=True).count())
 
    print(f2_course_list,f2_total_list,f2_present_list)
    print(f3_course_list, f3_total_list, f3_present_list)
    cal = md.TermData.objects.filter(is_current =True)[0]
    staff_section_data = []
    cur_week = md.Section.objects.filter(week=cur_term.week)
    ls_week = md.Section.objects.filter(week= cur_term.week - 1)
    for foo in md.Staffs.objects.all():
        prs_cw = cur_week.filter(instructor = foo, was_present=True).count()
        p_tal = cur_week.filter(instructor = foo).count()
        ls_wk = ls_week.filter(instructor = foo, was_present=True).count()
        l_tal = ls_week.filter(instructor = foo).count()
        staff_section_data.append([foo,ls_wk, l_tal, prs_cw, p_tal])
    return render(request,"admin_template/admin_home.html",{
        "weekly_section_data":staff_section_data,
        "atnd_present":present, "atnd_absent":absent,
     "terms":[(1,'1st Term'), (2, '2nd Term'), (3,'3rd Term')],"class_count":class_count,"staff_count":staff_count,
     "attendance_rate":prct,"department_count":dept_count,"department_list":departmnt_name,"department_class":dept_class_name,
     "departmental_attendance":dept_attendance_stat,"student_count_list_in_subject":[12, 14, 12],
     "subject_list":["social","RME","Science"],
     "student_name_list":['Andy', 'Derrick'],"attendance_present_list_student":[ 4, 5, 1],
     "attendance_absent_list_student":[4, 3, 2], "calender":cal,"form_2_classes":f2_course_list,
     "form_2_presents":f2_present_list,"form_2_total":f2_total_list,"form_3_classes":f3_course_list,
     "form_3_presents":f3_present_list,"form_3_total":f3_total_list,
     })

def view_staff(request):
    staff = md.Staffs.objects.all()
    return render(request, 'admin_template/view_staff.html', {"staffs":staff})

@api_view(['POST',])
def update_week(request):
    data = request.POST
    username = data['username']
    password = data['password']
    if username == "TK_infirmary" and password ==  "TK_150":
        cur_term = md.TermData.objects.filter(is_current = True)[0]
        cur_term.week += 1
        cur_term.save()
    
    return HttpResponse("okay")


def view_staff_record(request, staff_id):
    cur_term = md.TermData.objects.filter(is_current = True)[0]
    term = int(cur_term.term)
  
    st = md.Staffs.objects.get(id=staff_id)
    staff_sections = md.Section.objects.filter(instructor=st)
    staff_sec_wek = md.Section.objects.filter(instructor = st, week=1)
    cur_year_section = staff_sections.filter(year=cur_term.year.year).count()
    terms = []
    for i in range(int(cur_term.term)):
        pres = staff_sections.filter(year=cur_term.year.year, term=i+1, was_present=True).count()
        absents =  staff_sections.filter(year=cur_term.year.year, was_present=False, term=i+1).count()
        total  =  staff_sections.filter(year=cur_term.year.year, term=i+1).count()
        try:
            perct = round((pres / total)*100, 2)
        except:
            perct = 0
        terms.append([
            total,
            pres,
            absents,
            perct,
            ])
    #print(term  
    if cur_year_section:
        pass 
    else:
        cur_year_section = 1
    last_year_section_total = staff_sections.filter(year=cur_term.year.year-1).count()
    if last_year_section_total:
        pass 
    else:
        last_year_section_total = 1
    last_year_present = staff_sections.filter(year=cur_term.year.year-1, was_present = True).count()
    last_year_absent = last_year_section_total - last_year_present
    last_year_data = [last_year_absent, last_year_present,last_year_section_total ]  
    # last_year_present_perct = round((last_year_present / last_year_section_total * 100), 2)
    cur_year_present = staff_sections.filter(year= cur_term.year.year, was_present=True).count()
    cur_year_absent = staff_sections.filter(year= cur_term.year.year, was_present=False).count()
    # cur_year_present_perct =  round((cur_year_present / staff_sections.filter(year= cur_term.year.year).count() * 100), 2)
    cur_year_data = [cur_year_section, cur_year_present, cur_year_absent, round((cur_year_present / cur_year_section)*100, 2), st]
    # cur_staff_section = staff_sections.filter(year = cur_term.year.year, term=cur_term.term.term)
    m,t,w,th,f = [],[],[],[],[]
    for x in['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        if x == 'monday':
            m.append(staff_sec_wek.filter(year = cur_term.year.year, term=cur_term.term, day=x))
        elif x == 'tuesday':
            t.append(staff_sec_wek.filter(year = cur_term.year.year, term=cur_term.term, day=x))
        elif x == 'wednesday':
            w.append(staff_sec_wek.filter(year = cur_term.year.year, term=cur_term.term, day=x))
        elif x == 'thursday':
            th.append(staff_sec_wek.filter(year = cur_term.year.year, term=cur_term.term, day=x))
        else:
            f.append(staff_sec_wek.filter(year = cur_term.year.year, term=cur_term.term, day=x))
    return render(request, 'admin_template/view_staff_timetable.html', {'monday':m, 'tuesday':t,'wednesday':w,'thursday':th, 'friday':f, 'last_year':last_year_data, 'terms':terms})
def update_calender(request):
    if request.method == 'POST':
        cal = md.TermData.objects.all()
        for t in cal:
            t.is_current = False
            t.save()
        data = request.POST
        ##print(data)
        n_cal = md.TermData.objects.get_or_create(year =datetime.date(int(data.get('content')), 10,5))
        if not n_cal[1]:
            if n_cal[0].num_weeks >  int(data.get('week')):
                week_change = n_cal[0].num_weeks - int(data.get('week'))
                for d in range(week_change):
                    ns = md.Section.objects.filter(week=n_cal[0].num_weeks-d)
                    ns.delete()
            else:
                week_change = int(data.get('week')) - n_cal[0].num_weeks 
                for d in range(1,week_change + 1):
                    ns = md.Section.objects.filter(week=1)
                    for foo in ns:
                        foo.pk = None
                        foo.week = n_cal[0].week + d
                        foo.save()
                   
                
        ##print(n_cal)
        # n_cal.year = datetime.date(int(data.get('content')), 10,5)
        n_cal[0].term = data.get('term')
        n_cal[0].num_weeks = int(data.get('week'))
        n_cal[0].is_current = True
        n_cal[0].save()
        return HttpResponse('all good')
    else:
        return HttpResponse('not authorized')

def view_class(request):
    clas = md.Classes.objects.all()
    dep_lst = []
    for c in clas:
        nc = c.department.filter(is_general=False)
        print(nc)
    
        dep_lst.append([c,nc[0]])
    return render(request, 'admin_template/view_class.html', {'classes':dep_lst})

def add_staff(request):
    # ##print(request.POST)
    department = md.Departments.objects.all()
    return render(request, "admin_template/add_staff.html",{"departments":department})

def add_department(request):
    return render(request, "admin_template/add_department.html")
    
def add_staff_save(request):
    if request.method != 'POST':
        return HttpResponse('Unauthorized access')
    data = request.POST
    print(data)
    forms = [int(x[-1]) for x in data if x[:-1]=='form' and data[x] == 'true']
    cls = [ md.Classes.objects.filter(class_form=x) for x in forms if   md.Classes.objects.filter(class_form=x)]
    print("trynna filter user")
    user = md.CustomUser.objects.filter(username=data['staff_id'])
    print(user)
    if user:
        print("user exists")
        messages.error(request, f"Staff with ID {data['staff_id']} already exist")
        return HttpResponse("Err")
    print("user filtered")
    user = md.CustomUser.objects.create_user(username = data['staff_id'],password= data['staff_id'], first_name=data['first_name'], last_name=data['last_name'], user_type=2)
    user.save()
    st = md.Staffs.objects.get(admin=user)
    print("we are here5")
    dep = md.Departments.objects.get(department_name=data['department'])
    st.department=dep
    st.save()
    for foo in cls:
        print(foo, 'foo')
        st.classes.add(*foo)
        st.save()
    ##print(data)
    messages.success(request, f"Staff with ID { data['staff_id'] } successfully added")
    return HttpResponse("done")
    

def add_department_save(request):
    if request.method != 'POST':
        return HttpResponse("Unauthorized access")
    data = request.POST
    ##print(data)
    dep = md.Departments.objects.filter(department_name=data['department'])
    if dep:
        messages.error(request, f"{data['department']}  already Exists! ")
        return HttpResponseRedirect("add_department")

    dp = md.Departments.objects.create(department_name=data['department'])
    dp.save()
    messages.success(request, "Department Successfully added")
    return HttpResponseRedirect("add_department")

def view_department(request):
    dep = md.Departments.objects.all().order_by("-created_at")
    return render(request, 'admin_template/manage_department.html',{"departments":dep})


def add_course(request):
    department = md.Departments.objects.all()
    return render(request, 'admin_template/add_course.html', {"departments":department})

def add_course_save(request):
    if request.method != 'POST':
        return HttpResponse("Unauthorized Access")
    data = request.POST
    department = md.Departments.objects.get(id=int(data['department']))
    courses = data['courses'].split(",")
    for course in courses:
        course = course.strip()
        department.course_set.get_or_create(course_name=course.upper())

    messages.success(request, "courses added")
    return HttpResponseRedirect("add_course")

def admin_profile(request):
    admin = request.user
    return render(request, "admin_template/admin_profile.html", {"user":admin})

def admin_profile_save(request):
    if request.method != 'POST':
        return HttpResponse("Unauthorized Access")
    data = request.POST
    password=data["password"]
    try:
        customuser=md.CustomUser.objects.get(pk=request.user.id)
        if password!=None and password!="":
            customuser.set_password(password)
                # if password!=None and password!="":
                #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
    except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
    return HttpResponseRedirect(reverse("admin_profile"))

def reset_password(request):
    return render(request, "admin_template/reset_password.html")

def reset_password_save(request):
    data = request.POST
    username = data['username']
    password = data['password']
    try:
        customuser = md.CustomUser.objects.get(username=username)
        if password!=None and password!="":
            customuser.set_password(password) 
                # if password!=None and password!="":
                #     customuser.set_password(password)
            customuser.save()
    except:  
        messages.error(request, "An error occured,Check The ID and try again")
        return HttpResponseRedirect(reverse("reset_pass"))
   
    messages.success(request, "User Password Successfully updated")
    return HttpResponseRedirect(reverse("reset_pass"))
# def view_departmentid(request, department_id):
#     department = md.Departments.objects.get(id=department_id)
#     clas = department.classes_set.all()
#     return render()

def remove_staff(request):
    return render(request, "admin_template/remove_staff.html")

def remove_staff_save(request):
    if request.method != 'POST':
        return HttpResponse("Unauthorized Access")
    data = request.POST
    cus_user = md.CustomUser.objects.filter(username=data['username'])
    if cus_user:
        usobj = cus_user[0]
        usobj.delete()
        messages.success(request, f"Successfully Delete {data['username']}")
        return HttpResponseRedirect(reverse("remove_staff"))
    messages.error(request, f"Error!staff: {data['username' ]} does not exist")
    return HttpResponseRedirect(reverse("remove_staff"))

def get_issues(request):
    op_tickets = md.IssueTracker.objects.filter(is_resolved=False)
    cl_tickets = md.IssueTracker.objects.filter(is_resolved=True)
    return render(request, "admin_template/issue_tracker.html", {"opened": op_tickets, "closed":cl_tickets})

def view_ticket(request, ticket_id):
    data = request.GET
    ticket = md.IssueTracker.objects.get(id=ticket_id)
    
    return render(request, "admin_template/display_ticket.html", {"content":ticket.content, "tkid": ticket_id})

def resolve(request):
    data = request.POST
    ticket = md.IssueTracker.objects.get(id=data['tkid'])
    ticket.is_resolved = True
    ticket.save()
    messages.success(request, "Ticket has been resolved")
    return HttpResponseRedirect("get_issues")