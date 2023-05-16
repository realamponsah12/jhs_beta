from operator import mod
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime


# Create your models here.


DAYS_OF_WEEK = (
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
)
class CustomUser(AbstractUser):
    user_type_data=((1,"HOD"),(2,"Staff"),(3,"Student"))
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)


class AdminHOD(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()

class Departments(models.Model):
    department_name= models.CharField(max_length=200, null=True, blank=True)
    is_general = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()
   
class Classes(models.Model):
    prefect = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    class_name = models.CharField(max_length=200, null=True, blank=True)
    department = models.ManyToManyField(Departments)
    clas=((1,"Form 1"),(2,"Form 2"),(3,"Form 3"))
    clas_data=(("A","A"),("B","B"),("C","C"))
    class_form = models.CharField(default=1,choices=clas,max_length=10)
    form_data = models.CharField(default=1,choices=clas_data,max_length=10)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    
    objects=models.Manager()

    def __str__(self):
        return f'{self.class_name}'

class Staffs(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address=models.TextField(blank=True, null=True)
    department = models.ForeignKey(Departments, blank=True, null=True, on_delete=models.DO_NOTHING)
    classes = models.ManyToManyField(Classes)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()


class TermData(models.Model):
    form_choice = (
        (1, 'First Term'),
        (2, 'Second Term'),
        (3, 'Third Term')
    )
    year =models.DateField()
    term = models.CharField(default=1,choices=form_choice,max_length=10)
    is_current = models.BooleanField(default=False)
    week = models.IntegerField(default=1)
    num_weeks = models.IntegerField(default=0)
    ended = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)



class Course(models.Model):
    course_name = models.CharField(max_length=40)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True)
    # clas = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    # instructors = models.ForeignKey(Staffs, on_delete=models.CASCADE, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.course_name

class Section(models.Model):
    # section_id = models.CharField(max_length=25, primary_key=True)
    clas = models.ForeignKey(Classes, on_delete=models.CASCADE, blank=True, null=True)
    instructor = models.ForeignKey(Staffs, on_delete=models.CASCADE, blank=True, null=True)
    was_present = models.BooleanField(default=False)
    in_session = models.BooleanField(default=False)
    week = models.IntegerField(default=1)
    year = models.IntegerField(default=0)
    term = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    s_time = models.CharField(max_length=200, null=True, blank=True)
    e_time = models.CharField(max_length=200, null=True, blank=True)
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects=models.Manager()
    

class TotalAtendance(models.Model):
    instructor = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    overall_count = models.IntegerField(default=0)
    current_count = models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    
   
# class SectionAttendance(models.Model):
#     section=models.ForeignKey(Section, on_delete=models.DO_NOTHING)
#     attendance_count = models.IntegerField(default=0)
#     is_present = models.BooleanField(default=False)
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now_add=True)
class IssueTracker(models.Model):
    id=models.AutoField(primary_key=True)
    title = models.CharField(max_length=100,blank=True,null=True)
    # address=models.TextField()
    content = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Staffs, on_delete=models.CASCADE, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    fcm_token=models.TextField(default="")
    objects=models.Manager()
@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
   
    if created:
        if instance.user_type==1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type==2:
            Staffs.objects.create(admin=instance,address="")
        if instance.user_type==3:
            pass
            # Students.objects.create(admin=instance,course_id=PartnerSchools.objects.get(id=1),address="",profile_pic="",gender="")

@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type==1:
        instance.adminhod.save()
    if instance.user_type==2:
        instance.staffs.save()
    if instance.user_type==3:
        pass
        # instance.students.save()