from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('profile', views.profile, name="profile"),
    #authentication
    path('register', views.register, name="register"),
    path('login', views.user_login, name="login"),
    path('logout', views.user_logout, name="logout"),
    path('otp_verification', views.otp_verification, name="otp_verification"),
    #mentor videos 
    path('mentor', views.mentor, name="mentor"),
    path('explorecourses', views.explorecourses, name="explorecourses"),
    path('clanguage', views.clanguage, name="clanguage"),
    path('java', views.java, name="java"),
    path('python', views.python, name="python"),
    #jobs 
    path('jobs', views.jobs, name="jobs"),
    #loans
    path('loans', views.loans, name="loans"),
    #practice
    path('practice', views.practice, name="practice"),
    #material urls
    path('material', views.material, name="material"),
    path('c_material', views.c_material, name="c_material"),
    path('cpp_material', views.cpp_material, name="cpp_material"),
    path('python_material', views.python_material, name="python_material"),
    path('java_material', views.java_material, name="java_material"),
    path('html_material', views.html_material, name="html_material"),
    path('help_desk', views.help_desk, name="help_desk"),
    #progress urls
    path('tests', views.progress, name="progress"),
    # c progress
    path('progress', views.analysis, name="analysis"),
    path('c_progress', views.c_progress, name="c_progress"),
    path('c_basics', views.c_progress, name="c_progress"),
    path('c_printf_scanf', views.c_printf_scanf, name="c_printf_scanf"),
    path('c_variables', views.c_variables, name="c_variables"),
    path('c_datatypes', views.c_datatypes, name="c_datatypes"),
    path('c_typeConversion', views.c_typeConversion, name="typeConversion"),
    path('c_operators', views.c_operators, name="c_operators"),
    path('c_conditional_statements', views.c_conditional_statements, name="c_conditional_statements"),
    path('c_loops', views.c_loops, name="c_loops"),
    path('c_break_continue', views.c_break_continue, name="c_break_continue"),
    path('c_strings', views.c_strings, name="c_strings"),
    path('c_arrays', views.c_arrays, name="c_arrays"),
    path('c_pointers', views.c_pointers, name="c_pointers"),
    path('c_functions', views.c_functions, name="c_functions"),
    path('c_files', views.c_files, name="c_files"),
    path('c_structures', views.c_structures, name="c_structures"),


    path('cpp_progress', views.cpp_progress, name="cpp_progress"),
    path('python_progress', views.python_progress, name="python_progress"),
    path('java_progress', views.java_progress, name="java_progress"),
    path('html_progress', views.html_progress, name="html_progress"),
]