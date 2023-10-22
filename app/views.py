import base64
import io
import pyotp
import pandas as p
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.staticfiles.finders import find
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from quality_education import settings
from . import models


users = User.objects.all()
c_language = models.c_language.objects.all()

def home(request):
    if request.user.is_authenticated:
        logged_in = 1
    else:
        logged_in = 0
    return render(request, "home.html", {'logged':logged_in})



#authentication
def user_login(request):
    err = {}
    if request.method == "POST":
        uname = request.POST['uname']
        password = request.POST['password']

        user = authenticate(username = uname, password = password )
        if user is not None:
            login(request, user)
            request.session['username'] = uname
            return redirect('home')

        else:
            return redirect('login')
            err['loginerr'] = "invalid credintails!"
    return render(request, "authentication/login.html",err)


def register(request):
    values = {}
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['password']
        email = request.POST['email']
        uname = request.POST['uname']
        if User.objects.filter(email=email).exists():
            #print("email")
            values['emailerr'] = "email already exists."
            values['fname'] = fname
            values['lname'] = lname
            values['email'] = email
            values['uname'] = uname

        elif User.objects.filter(username=uname).exists():
            #print("uname")
            values['fname'] = fname
            values['lname'] = lname
            values['email'] = email
            values['uname'] = uname
            values['exists'] = "UserName already exists."
        else:
            values['email'] = email
            # print("email")
            request.session['fname'] = fname
            request.session['lname'] = lname
            request.session['pass1'] = pass1
            request.session['email'] = email
            request.session['uname'] = uname
            # Generate OTP
            otp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(otp_secret)
            otp = totp.now()
            print(otp)
            subject = 'Welcome to the website'
            message = f'Hello {fname} { lname }!!\n\nplease verify your account\nYour OTP for email verification is: {otp}\n\nThank You!!!'

            # Send OTP via email
            from_email = settings.EMAIL_HOST_USER
            to_list = [email]
            sent = send_mail(subject, message, from_email, to_list, fail_silently=True)
            print(sent)
            request.session['otp'] = otp

            return redirect('otp_verification')
    return render(request, "authentication/register.html", values)


def otp_verification(request):
    values = {}
    fname = request.session.get('fname', '')
    lname = request.session.get('lname', '')
    pass1 = request.session.get('pass1', '')
    email = request.session.get('email', '')
    uname = request.session.get('uname', '')
    otp = request.session.get('otp', '')
    values['email'] = email
    if request.method == 'POST':
        user_otp = request.POST['otp']
        if user_otp == otp:
            userobj = User.objects.create_user(
                username=uname,
                password=pass1,
                email=email,
                first_name=fname,
                last_name=lname
            )
            userobj.save()
            models.c_language.objects.create(
                username = uname
            )
            user = authenticate(username = uname, password = pass1 )
            login(request, user)
            return redirect('home')
        else:
            values['opterr'] = "Invalid OTP"

    return render(request, 'authentication/otp_verification.html', values)


def user_logout(request):
    logout(request)
    return redirect('login')

#practice
@login_required
def practice(request):
    return render(request, 'practice.html')


#courses

@login_required
def mentor(request):
    return render(request, "mentor/index.html")

@login_required
def explorecourses(request):
    return render(request, "mentor/explorecourses.html")

@login_required
def clanguage(request):
    return render(request, "mentor/clanguage.html")
@login_required
def java(request):
    return render(request, "mentor/java.html")
@login_required
def python(request):
    return render(request, "mentor/python.html")
#chatbot
@login_required
def help_desk(request):
    return render(request, "help_desk.html")


#jobs
@login_required
def jobs(request):
    jobs = {}
    if request.method == "POST":
        try:
            data = p.read_excel(find('job_data.xlsx'))
            data = data.drop('Unnamed: 0', axis=1)
            job = request.POST['job']
            jobs["domain"] = job

            def search(query):
                results = data[data['Job Title'].str.contains(query, case=False, na=False)]
                return results

            jobs_list = search(job).sample(n=20)
            jobs_data = jobs_list[['Company Name', 'Job Title', 'Salary', 'Location','Employment Status']].values.tolist()

            jobs['job_data'] = jobs_data
        except:
            jobs['err'] = "No Jobs found...please check your Domain"

    return render(request, "jobs.html", jobs)
#loans
@login_required
def loans(request):
    return render(request, "loans.html")

#tutorial
@login_required
def material(request):
    return render(request, "tutorial/material.html")

@login_required
def c_material(request):
    return render(request, "tutorial/c.html")


@login_required
def cpp_material(request):
    return render(request, "tutorial/cpp.html")


@login_required
def python_material(request):
    return render(request, "tutorial/python.html")


@login_required
def java_material(request):
    return render(request, "tutorial/java.html")


@login_required
def html_material(request):
    return render(request, "tutorial/html.html")

#progress
@login_required
def progress(request):
    uname = request.session.get('username','')
    if uname == '':
        logout(request)
        return redirect('login')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.basics
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(basics=score)
        else:
            models.c_language.objects.create(
                username = uname,
                basics = score
            )
    return render(request, "progress/c/c.html", values)
#c progress
@login_required
def c_progress(request):
    uname = request.session.get('username','')
    if uname == '':
        logout(request)
        return redirect('login')

    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.basics
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(basics=score)
        else:
            models.c_language.objects.create(
                username = uname,
                basics = score
            )
    return render(request, "progress/c/c.html", values)

@login_required
def c_printf_scanf(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.printf_scanf
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','B','B','A','B','C','D']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(printf_scanf=score)

        else:
            models.c_language.objects.create(
                username = uname,
                printf_scanf = score
            )
    print(userans)
    print(score)
    return render(request, "progress/c/c_printf_scanf.html", values)

@login_required
def c_variables(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.variables
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','A','C','C','B','B','B','B','A']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(variables=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                variables = score
            )
    return render(request, "progress/c/c_variables.html", values)

@login_required
def c_datatypes(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.datatypes
    values = {'maxscore':max_score}
    score = 0
    ans = ['D','B','B','C','B','A','C','D','B','A']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(datatypes=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                datatypes = score
            )
    return render(request, "progress/c/c_datatypes.html", values)

@login_required
def c_typeConversion(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.typeConversion
    values = {'maxscore':max_score}
    score = 0
    ans = ['D','B','B','C','B','A','C','D','B','A']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(typeConversion=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                typeConversion = score
            )
    return render(request, "progress/c/c_typeConversion.html", values)

@login_required
def c_operators(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.operators
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','C','D','A','A','C','D','A','A']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(operators=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                operators = score
            )
    return render(request, "progress/c/c_operators.html", values)

@login_required
def c_conditional_statements(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.conditional_statements
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(conditional_statements=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                conditional_statements = score
            )
    return render(request, "progress/c/c_conditional_statements.html", values)

@login_required
def c_loops(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.loops
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(loops=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                loops = score
            )
    return render(request, "progress/c/c_loops.html", values)

@login_required
def c_break_continue(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.break_continue
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(break_continue=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                break_continue = score
            )
    return render(request, "progress/c/c_break_continue.html", values)

@login_required
def c_strings(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.strings
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(strings=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                strings = score
            )
    return render(request, "progress/c/c_strings.html", values)

@login_required
def c_arrays(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.arrays
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(arrays=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                arrays = score
            )
    return render(request, "progress/c/c_arrays.html", values)

@login_required
def c_pointers(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.pointers
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(pointers=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                pointers = score
            )
    return render(request, "progress/c/c_pointers.html", values)

@login_required
def c_functions(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.functions
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(functions=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                functions = score
            )
    return render(request, "progress/c/c_functions.html", values)

@login_required
def c_files(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.files
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(files=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                files = score
            )
    return render(request, "progress/c/c_files.html", values)

@login_required
def c_structures(request):
    uname = request.session.get('username','')
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    max_score = c_language.structures
    values = {'maxscore':max_score}
    score = 0
    ans = ['A','B','D','C','A','A','B','C','D','C']
    userans = []
    if request.method == 'POST':
        for i in range(1, 11):
            try:
                user_answer = request.POST.get(f'q{i}', 0)
                userans.append(user_answer)
            except:
                userans.append(0)
        for i in range(10):
            if userans[i] == ans[i]:
                score += 1
        if models.c_language.objects.filter(username = uname).exists():
            if score > max_score:
                models.c_language.objects.filter(username = uname).update(structures=score)
                max_score = score
        else:
            models.c_language.objects.create(
                username = uname,
                structures = score
            )
    return render(request, "progress/c/c_structures.html", values)


@login_required
def analysis(request):
    uname = request.session.get('username','')
    if uname == '':
        logout(request)
        return redirect('login')
    need_to_learn = []
    try:
        c_language = models.c_language.objects.get(username = uname)
    except:
            models.c_language.objects.create(
                username = uname
            )
            c_language = models.c_language.objects.get(username = uname)
    data = {
        'basics':c_language.basics,
        'printf_scanf':c_language.printf_scanf,
        'variables':c_language.variables,
        'datatypes':c_language.datatypes,
        'typeConversion':c_language.typeConversion,
        'operators':c_language.operators,
        'conditional_statements':c_language.conditional_statements,
        'loops':c_language.loops,
        'break_continue':c_language.break_continue,
        'strings':c_language.strings,
        'arrays':c_language.arrays,
        'pointers':c_language.pointers,
        'functions':c_language.functions,
        'files':c_language.files,
        'structures':c_language.structures
    }
    df = p.DataFrame([data])
    for topic, value in data.items():
        if value < 5:
            need_to_learn.append(topic)
    df = df.transpose()

    plt.figure(figsize=(14, 6))
    for column in df.columns:
        plt.plot(df.index, df[column], marker='o', label=column)

    for column in df.columns:
        for i, value in enumerate(df[column]):
            plt.annotate(f"{value:.2f}", (i, value), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.xlabel('Topics')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    lineplot = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return render(request, "analysis.html" , {'lineplot':lineplot, 'need_to_learn':need_to_learn})




@login_required
def cpp_progress(request):
    return render(request, "progress/cpp.html")

@login_required
def python_progress(request):
    return render(request, "progress/python.html")

@login_required
def java_progress(request):
    return render(request, "progress/java.html")

@login_required
def html_progress(request):
    return render(request, "progress/html.html")

@login_required
def profile(request):
    user_data = {}
    uname = request.session.get('username', '')
    if uname == '':
        logout(request)
        return redirect('login')
    user = User.objects.get(username = uname)
    user_data['user'] = user
    if request.method == "POST":
        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        oldpass = request.POST['oldpass']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if fname.isalnum() and lname.isalnum():
            if len(password)>6 and password.isalnum():
                if password == cpassword :
                    if user.check_password(oldpass):
                        # The old password matches, update user information
                        user.username = uname
                        user.first_name = fname
                        user.last_name = lname

                        # Check if a new password is provided and update it
                        if password:
                            user.set_password(password)
                            # Update the session authentication hash
                            update_session_auth_hash(request, user)

                        user.save()
                        user_data['warning'] = "Updated Successfully"
                    else:
                        user_data['warning'] = "Check your Old Password"
                else:
                    user_data['warning'] = "Password and Confirm Password doesn't match"
            else:
                 user_data['warning'] = "Password must be at least 6 characters long and should contain both alphabets and numbers"
        else:
            user_data['warning'] = "First Name and Last Name must contain only Alphabets"


    # print(user_data['first_name'])
    return render(request, "profile.html", user_data)