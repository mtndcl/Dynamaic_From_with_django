from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, UpdatePasswordForm, ProjectForm
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from .models import Project, ProjectUser, Rolls, Field
from django.contrib.auth.decorators import login_required

from datetime import date

from django.db import DEFAULT_DB_ALIAS, connections


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from django.template import Context, Template

def welcome_page(request):
    return render(request, 'FocusApp/welcome.html')


def login_page(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            selected_user = User.objects.get(email=email)
            user = authenticate(request, username=selected_user.username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    all_user = User.objects.all()
                    data = {
                        "all_user": all_user
                    }
                    page='0'
                    return HttpResponseRedirect(reverse('adminuser-page',kwargs={'page':page}))
                else:
                    page='0'
                    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))
            else:

                if not selected_user.is_active:

                    messages.warning(request, 'This user not active yet')
                else:
                    messages.warning(request, 'wrong password')
                return HttpResponseRedirect(reverse('login-page'))
        except User.DoesNotExist:
            messages.warning(request, 'Dont have a such email address')
            return HttpResponseRedirect(reverse('login-page'))

    else:
        return render(request, 'FocusApp/login.html')



def backward_page(request,page):
    

    page=int(page)-1
    if page<0:
        page=0
        
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))


def forwardpage_page(request,page):
    page=int(page)+1
    projects_users = ProjectUser.objects.filter(user_id=request.user.id)
    if page>= len(projects_users)/9:
        page=int(len(projects_users)/9)
    
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))
@login_required
def profile_page(request,page=0):
    instance = request.user

    
    
    projects_users = ProjectUser.objects.filter(user_id=instance.id)
    myprojects = []
    for i in range(len(projects_users)):
        myprojects.append(Project.objects.get(id=projects_users[i].project_id))
        # print("----------here----------> : ",projects_users)
    start=int(page)*9
    finish=start+9
    if len(myprojects)<finish:
        finish=len(myprojects)

    myprojects=myprojects[start:finish]
    return render(request, 'FocusApp/profile.html', {'myprojects': myprojects,'page':page})


def forgotpassword_page(request):
    email = request.POST.get('email')

    if request.method == 'POST':

        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            message = render_to_string('FocusApp/password_reset_mail.html', {
                'user': user, 'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })

            mail_subject = 'Reset your password.'

            mail = EmailMessage(mail_subject, message, to=[user.email])
            mail.send()
            directive = 'Please check your email'
            return render(request, 'FocusApp/thank.html', {"directive": directive})
        except User.DoesNotExist:
            messages.warning(request, 'Dont have a such email address')

    return render(request, 'FocusApp/forgotpassword.html')


def clickonresetpasswordlink(request, uidb64, ):
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)

    if request.method == 'POST':

        user = User.objects.get(pk=uid)
        form = UpdatePasswordForm(request.POST, instance=user)

        if form.is_valid():

            print("form is valid")
            form.save()
            return HttpResponseRedirect(reverse('login-page'))
        else:
            print("------------------invalid")
            return render(request, 'FocusApp/new_password.html', {'form': form})
    else:
        if user is not None and account_activation_token.check_token(user, token):
            form = UpdatePasswordForm(instance=user)
            return render(request, 'FocusApp/new_password.html', {'form': form})
        else:
            return HttpResponse('Activation link is invalid!')


@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('login-page'))


@login_required
def isactive_page(request, slug,page):
    selected_user = User.objects.get(username=slug)

    selected_user.is_active = not selected_user.is_active

    selected_user.save()

    if selected_user.is_active:
        mail_message = "Your account is activated by admin you can log in now good luck"
        send_mail('Account Confirmation by FOCUS',
                  mail_message,
                  'design.project.focus@gmail.com',
                  [selected_user.email],
                  fail_silently=False)
    else:
        mail_message = "Your account is Denied by admin pls contact with us"
        send_mail('Account DENIED by FOCUS',
                  mail_message,
                  'design.project.focus@gmail.com',
                  [selected_user.email],
                  fail_silently=False)
    all_user = User.objects.all()

    data = {
        "all_user": all_user
    }
    return HttpResponseRedirect(reverse('adminuser-page',kwargs={'page':page}))

def forwardadminuserpage_page(request,page):
    
    page=int(page)
    
    all_user = User.objects.all()
    if page<(len(all_user)/5-1):
        page=int(page)+1

    return HttpResponseRedirect(reverse(adminuser_page,kwargs={'page':page}))

def backwarddadminpage_page(request,page):

    page=int(page)-1
    if  page<0:
        page=page+1

    return HttpResponseRedirect(reverse(adminuser_page,kwargs={'page':page}))
@login_required
def adminuser_page(request,page):
    all_user = User.objects.all()


    start=int(page)*5
    finish=start+5
    if finish>=len(all_user):
        finish=len(all_user)

    all_user=all_user[start:finish]

    data = {
        "all_user": all_user,
        "page":page

    }





    return render(request, 'FocusApp/adminuser.html', data)

"""

def backward_page(request,page):
    

    page=int(page)-1
    if page<0:
        page=0
        
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))


def forwardpage_page(request,page):
    page=int(page)+1
    projects_users = ProjectUser.objects.filter(user_id=request.user.id)
    if page>= len(projects_users)/9:
        page=int(len(projects_users)/9)
    
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))
"""
def forwardproject_page(request,page):


    page=int(page)+1
    all_project = Project.objects.all()
    if page>= len(all_project)/9:
        page=int(len(all_project)/9)
    return HttpResponseRedirect(reverse('adminproject-page',kwargs={'page':page}))
def backwardproject_page(request,page):

    page=int(page)-1
    if page<0:
        page=0
    return HttpResponseRedirect(reverse('adminproject-page',kwargs={'page':page}))

@login_required
def adminproject_page(request,page):
    all_project = Project.objects.all()

    data = {
        "all_project": all_project,
        "page": page

    }

    return render(request, 'FocusApp/adminproject.html', data)
@login_required
def deleteuser_page(request, slug):
    selected_user = User.objects.get(username=slug)
    selected_user.delete()

    all_user = User.objects.all()

    data = {
        "all_user": all_user
    }

    return render(request, 'FocusApp/adminuser.html', data)


def send_message(request, user, profile):
    try:
        mail_message = 'This user wants to create an account... \nFull Name : ' + user.first_name + '\nE-mail : ' \
                       + user.email + '\nPhone Number : ' + profile.phone_number + '\nOrganization : ' + profile.organization

        current_site = get_current_site(request)
        message = render_to_string('FocusApp/acc_active_email.html', {
            'user': user, 'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })

        mail_subject = 'Confirm your account.'

        mail = EmailMessage(mail_subject, message, to=[user.email])
        mail.send()
        return True

    except:
        return False


def register_page(request):
    print('register page work here ---------------------------------')

    if request.method == 'POST':
        u_form = RegisterForm(request.POST)
        p_form = ProfileForm(request.POST)
        print('postttttttttttt ---------------------------------')

        if u_form.is_valid() and p_form.is_valid():

            print('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv page work here ---------------------------------')
            user = u_form.save(commit=False)
            profile = p_form.save(commit=False)
            if send_message(request, user, profile):
                user = u_form.save()
                profile.user = user
                profile.save()
                directive = ' Thank you for registering. Please check your mailbox.'
                return HttpResponseRedirect(reverse('thank-page', kwargs={'directive': directive}))
            else:
                messages.warning(request, 'Check your internet connection')

    else:
        print('----------------------------->>>>>>>>>>>>Fill the form')
        u_form = RegisterForm()
        p_form = ProfileForm()
    return render(request, 'FocusApp/register.html', {'u_form': u_form, 'p_form': p_form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print(user.username)
        print(user.profile.is_confirm)
        user.profile.is_confirm = True
        user.profile.save()
        print(user.profile.is_confirm)

        user.save()
        mail_message = 'Please click on the link below to email activation.'
        email = 'design.project.focus+userconfirmation@gmail.com'
        send_mail('Account Approval Required',
                  mail_message,
                  'design.project.focus@gmail.com',
                  [email],
                  fail_silently=False)

        directive = 'Your Account Confirmed'
        return render(request, 'FocusApp/thank.html', {'directive': directive})
    else:
        return HttpResponseRedirect(reverse('error-page'))


def thank_page(request, directive):
    return render(request, 'FocusApp/thank.html', {'directive': directive})


def error_page(request):
    return render(request, 'FocusApp/Error.html')

def create_table_as(project_id, queryset, using=DEFAULT_DB_ALIAS):

    
    compiler = queryset.query.get_compiler(using=using)
    sql, params = compiler.as_sql()
    connection = connections[DEFAULT_DB_ALIAS]


    project=Project.objects.get(id=project_id)
    table_name=project.table_name

    rear="(   \"id\" INTEGER PRIMARY KEY AUTOINCREMENT ,   \"author_id\"  VARCHAR(20)  , \"published_date\"   VARCHAR(100) , "

    fields=Field.objects.filter(project_id=project_id)

    mid=""
    for i in range(len(fields)):
        
        mid+='\"' +fields[i].fieldname+'\"'

        if fields[i].fieldtype=='Text':
            mid+=' VARCHAR(20) '
        if fields[i].fieldtype=='Image':
            mid+=' BLOB  '
        elif fields[i].fieldtype=='Integer':
            mid+=' INT '
        elif fields[i].fieldtype=='Double':
            mid+=' INT '

        
        mid+=' DEFAULT \"'+fields[i].fielddefaultvalue +'\"'
        
        if fields[i].fieldmondatory!=None:
            mid+=' NOT NULL '
        
       
        if i+1!=len(fields):
            mid+=' ,'
        
        


    front=" );"
    sql=rear+mid+front

    xx=open('sql.txt','w',encoding='utf-8')
    xx.write(sql)
    xx.close()
    print(sql)

    if  project.have_table==True:
        with connection.cursor() as cursor:
            drop = "DROP TABLE "+table_name
            cursor.execute(drop)
    project.have_table=True
    project.save()

    sql = "CREATE TABLE " + connection.ops.quote_name(table_name)  + sql
   

    with connection.cursor() as cursor:
        cursor.execute(sql, params)


@login_required
def createdatabase_page(request,project_id):
    
    proje=Project.objects.get(id=project_id)
    try:
        create_table_as(project_id,Rolls.objects.values_list('id', 'projectuser'),)

    except:
        proje.delete()
    projects_users = ProjectUser.objects.filter(user_id=request.user.id)
    
    page=str(int(len(projects_users)/9))
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))


@login_required
def addprojectinfo_page(request,project_id):


    proje=Project.objects.get(id=project_id)
    if request.method == 'POST':
        
        title= request.POST.get('title')
        abstract= request.POST.get('abstract')
        
        error=False
       
        if  len(abstract)<4:
            error=True
            messages.warning(request, 'abstract must be longer then 4 characters !!')
        if len(title)<4:

            error=True
            messages.warning(request, 'title must be longer then 4 characters')

        if  error==False :
            
            proje.title= title
            proje.abstract= abstract
            proje.table_name=proje.title[:5]+str(proje.id)
            proje.save()

 

    datas = Field.objects.filter(project_id=project_id)

    return render(request, 'FocusApp/createproject.html', {'datas': datas,'project_id':project_id ,'proje':proje})
def isINt(s):
    if s=='':
        return True
    try: 
        int(s)
        return True
    except ValueError:
        return False
def isDouble(s):

    if s=='':
        return True
        
    try:
        float(s)
        return True
    except ValueError:
        return False
def isDate(s):
    if s=='':
        return True
    try:
        datetime.strptime(s, '%m/%d/%y')
        return True
    except ValueError:
        return False
@login_required
def addfield_page(request,project_id):


    proje=Project.objects.get(id=project_id)
    if request.method == 'POST':
        
      
        fieldname = request.POST.get('fieldname')
        fieldtype = request.POST.get('fieldtype')
        fielddefaultvalue = request.POST.get('fielddefaultvalue')
        fieldmondatory = request.POST.get('fieldmondatory')
        
        
        error=False
        if  'Integer'==fieldtype :

            if isINt(fielddefaultvalue)==False:
                error=True
                messages.warning(request, '{} is not a Integer'.format(fielddefaultvalue))

        elif 'Double'==fieldtype :
            if isDouble(fielddefaultvalue)==False:
                error=True
                messages.warning(request, '{} is not a Double'.format(fielddefaultvalue))
        elif 'Date'==fieldtype :
            if isDate(fielddefaultvalue)==False:
                error=True
                messages.warning(request, 'Date format is MM/DD/YY')
        if fieldname=='':
            error=True
            messages.warning(request, 'Fieldname can not be empty')

        if 0!=Field.objects.filter(project_id=project_id, fieldname=fieldname).count():
            error=True
            messages.warning(request, 'This fieldname exist right now try new fieldname')


        if  error==False :
            
            result=False
            if 'checked'==fieldmondatory:
                result=True

            if 'Checkbox'==fieldtype :
                fielddefaultvalue='True'
                result=False
            fi = Field.objects.create(project_id=project_id, fieldname=fieldname, fieldtype=fieldtype,
                                      fielddefaultvalue=fielddefaultvalue, fieldmondatory=result)
            fi.save()

    datas = Field.objects.filter(project_id=project_id)

    return render(request, 'FocusApp/create_form.html', {'datas': datas,'project_id':project_id ,'proje':proje})

@login_required
def deletefield_page(request,project_id,field_id):


    da=Field.objects.get(project_id=project_id,id=field_id)
    da.delete()
    return HttpResponseRedirect(reverse('addfield-page', kwargs={'project_id': project_id}))
@login_required
def updatefield_page(request,project_id,field_id):


    field=Field.objects.get(project_id=project_id,id=field_id)

    
    if request.method == 'POST':
        
      
        fieldname = request.POST.get('fieldname')
        fieldtype = request.POST.get('fieldtype')
        fielddefaultvalue = request.POST.get('fielddefaultvalue')
        fieldmondatory = request.POST.get('fieldmondatory')
        result=False
        if fieldmondatory=='on':
            result=True
            
        print("cccccccc: ",fieldmondatory)
        error=False
   
        
        if fieldname=='':
            error=True
            messages.warning(request, 'Fieldname can not be empty')

        if 0!=Field.objects.filter(project_id=project_id, fieldname=fieldname).count():
            if field.fieldname!=fieldname:
                error=True
                messages.warning(request, 'This fieldname exist right now try new fieldname')

        if error==False:
            
            if fieldtype=='Checkbox':
                fielddefaultvalue='True'
                result=False
            field.fieldname = fieldname
            field.fieldtype = fieldtype
            field.fielddefaultvalue = fielddefaultvalue
            field.fieldmondatory = result
            field.save()
            messages.warning(request, '{}  is updated '.format(field.fieldname))

    return HttpResponseRedirect(reverse('addfield-page', kwargs={'project_id': project_id}))

@login_required
def createproject_page(request,title,abstract):
   

    return render(request, 'FocusApp/createproject.html',{'title':title,'abstract':abstract})


@login_required
def saveproject_page(request):



    project_id=0
    instance = request.user
    title=''
    abstract=''
    if request.method== 'POST':
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')

        error=False
        if len(title)<3:
            error=True
            messages.warning(request, 'Title must be at least 3  characters')
        elif len(abstract)<3:
            error=True
            messages.warning(request, 'Abstract must be at least 3  characters')
        
        if error==False:
            proje = Project.objects.create(title=title, abstract=abstract, owner=request.user,have_data=False,table_name='None',have_table=False)
            aa=title.replace(' ','')

            

            proje.table_name=aa+str(proje.id)
           

            proje.save()
            print("table is:",proje.table_name)

            roll = Rolls(roll=Rolls.OWNER)
            roll.save()
            project_user = ProjectUser.objects.create(project=proje, user=instance, roll=roll,is_accepted=True)
            project_user.save()
            project_id = proje.id

            managers=User.objects.filter(is_superuser=True , is_active=True)
            for user in managers:
                roll = Rolls(roll=Rolls.ADMIN)
                roll.save()
                project_user = ProjectUser.objects.create(project=proje, user=user, roll=roll,is_accepted=True)
                project_user.save()



            tab='projecttab'
          
            return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id, 'tab': tab}))

    
    if len(title) < 1 :
        
        title=" "
    if len(abstract)< 1 :

        abstract=" "


    return HttpResponseRedirect(reverse('createproject-page', kwargs={'title': title, 'abstract': abstract}))

@login_required
def project_page(request, slug,tab):
    project = Project.objects.get(id=slug)

    project_user = ProjectUser.objects.filter(project_id=project.id)
    current_user = request.user
    current_roll_id=ProjectUser.objects.get(user_id=current_user.id,project_id=project.id).roll_id
    current_roll=Rolls.objects.get(id=current_roll_id)
    members_is_accepted = []
    members_is_not_accepted = []
    rolls_is_accepted = []
    rolls_is_not_accepted = []
    for i in range(len(project_user)):

        if project_user[i].is_accepted is True:
            members_is_accepted.append(User.objects.get(id=project_user[i].user_id))
            rolls_is_accepted.append(Rolls.objects.get(id=project_user[i].roll_id))
        else :
            members_is_not_accepted.append(User.objects.get(id=project_user[i].user_id))
            rolls_is_not_accepted.append(Rolls.objects.get(id=project_user[i].roll_id))
    all_user = User.objects.all()
    unmembers = set(all_user) - set(members_is_not_accepted)-set(members_is_accepted)
    mylist_accepted = zip(members_is_accepted, rolls_is_accepted)
    mylist_not_accepted = zip(members_is_not_accepted, rolls_is_not_accepted)
    owner = User.objects.get(id=project.owner_id)

    
    tabledata=[]

    if project.have_table==True:
        connection = connections[DEFAULT_DB_ALIAS]
        with connection.cursor() as cursor:
           
            sqlite_select_query = 'SELECT * from  ' + project.table_name
            cursor.execute(sqlite_select_query)
            tabledata = cursor.fetchall()

    fields=Field.objects.filter(project_id=project.id)
    records=[]

    for data  in tabledata:

        dic={}
        dic['id']=data[0]
        dic['author_id']=data[1]
        dic['published_date']=data[2]
        for i in  range(len(fields)):
            dic[fields[i].fieldname]=data[3+i]
        records.append(dic)
    

    template='FocusApp/'
    if tab=='projecttab':
        template+='projecttab.html'
    elif tab=='datatab':
        template+='datatab.html'
    elif tab=='messagetab':
        template+='messagetab.html'
    elif tab=='membertab':
        template+='membertab.html'

    authors=[]
    for data in tabledata:
       
        for i in  range(len(data)):
            if i==1:
               
                authors.append(User.objects.get(id=data[i]))
   
    mytable = zip(records, authors)
    return render(request, template, {'project': project, 'mylist_accepted': mylist_accepted, 'mylist_not_accepted': mylist_not_accepted,'unmembers': unmembers,
                                                    'current_roll':current_roll, 'current_user': current_user, 'owner': owner, 'mytable':mytable,'fields':fields})


def addtoproject_page(request, project_id, user_id):

    selected_roll = request.GET.get('roll')
    roll = Rolls(roll=Rolls.MEMBER)
    if selected_roll == "Member":
        roll = Rolls(roll=Rolls.MEMBER)

    elif selected_roll == "Manager":
        roll = Rolls(roll=Rolls.MANAGER)
    roll.save()
    project_user = ProjectUser.objects.create(project_id=project_id, user_id=user_id, roll_id=roll.id, is_accepted=False)
    project_user.save()
    adding_user = User.objects.get(id=user_id)
    
    send_message_invite(request,adding_user,project_id,project_user.id)
    tab = 'membertab'
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id, 'tab': tab}))


def removefromproject_page(request, project_id, user_id):
    project_user = ProjectUser.objects.get(project_id=project_id, user_id=user_id)
    project_user.delete()
    tab='membertab'
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id,'tab':tab}))


def SendNotifications_page(request, project_id, owner_id):
    tab='messagetab'
    current_user = request.user
    if request.method == 'POST':
        message = request.POST.get('message')
        checked = request.POST.get('checked')
        owner = User.objects.get(id=owner_id)
        if checked is None:

            if current_user.id != owner.id:
                send_mail('Topic',
                          message,
                          current_user.email,
                          [owner.email],
                          fail_silently=False)

        else:
            project = Project.objects.get(id=project_id)

            project_user = ProjectUser.objects.filter(project_id=project.id)
            members = []

            for i in range(len(project_user)):
                member = User.objects.get(id=project_user[i].user_id)

                send_mail('Topic',
                          message,
                          current_user.email,
                          [member.email],
                          fail_silently=False)
            if current_user.id != owner.id:
                send_mail('Topic',
                          message,
                          current_user.email,
                          [owner.email],
                          fail_silently=False)
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id,'tab':tab}))


def viewform_page(request, project_id):
    fields = Field.objects.filter(project_id=project_id)

    project=Project.objects.get(id=project_id)
    table=project.table_name
    return render(request, 'FocusApp/viewform.html', {'fields': fields,'project_id':project_id})

def  savetoform_page(request,project_id):
    
    
    project=Project.objects.get(id=project_id)
    if project.have_data==False:
        project.have_data=True
        project.save()

    table=project.table_name
    connection = connections[DEFAULT_DB_ALIAS]
  
    fields=Field.objects.filter(project_id=project_id)
    error=False
    with connection.cursor() as cursor:

        table_field=""
        
        table_field+="INSERT INTO " +table +" VALUES ( %s , %s , %s , "
       
        values=[None]
        values.append(str(request.user.id))
        values.append(str(date.today()))
        val=''
        for i in range(len(fields)):
            table_field+=' %s '
            

            if fields[i].fieldtype=='Checkbox':
                val=request.POST.get(fields[i].fieldname)
                if val!='True':
                    val='False'
            else:
                val=request.POST.get(fields[i].fieldname)
            val=val.strip()

            if fields[i].fieldmondatory==True and val=='':
                error=True
                messages.warning(request, 'Must Fill all mondatory place')

            print("-------- :",)
           

           
           
            values.append(val)
            if i+1!=len(fields):
                table_field+=', '
               
            else:
                table_field+=' ) '
        if error==True:
             return HttpResponseRedirect(reverse('viewform-page', kwargs={'project_id': project_id}))
        else:
            cursor.execute(table_field,tuple(values))
       
        tab="datatab"
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id,'tab':tab}))


def deleteproject_page(request,project_id):
    
    proje=Project.objects.get(id=project_id)

    fields=Field.objects.filter(project_id=project_id)
    fields.delete()
    proje.delete()
    page='0'
    return HttpResponseRedirect(reverse('profile-page',kwargs={'page':page}))


def  deleteDataFromTable_page(request,project_id,data_id):
    

    proje=Project.objects.get(id=project_id)

    connection = connections[DEFAULT_DB_ALIAS]
    number=0
    with connection.cursor() as cursor:
       
        sqlite_select_query ='DELETE FROM '+ proje.table_name+' WHERE id= ' +data_id
        cursor.execute(sqlite_select_query)
        
   
        sqlite_select_query = 'SELECT * from  ' + proje.table_name
        cursor.execute(sqlite_select_query)
        number =len(cursor.fetchall())
        if  number==0:
            proje.have_data=False
            proje.save()
    tab='datatab'
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id,'tab':tab}))


def viewupdateDataFromTable_page(request,project_id,data_id):
    

    fields = Field.objects.filter(project_id=project_id)

    project=Project.objects.get(id=project_id)
    table=project.table_name
    connection = connections[DEFAULT_DB_ALIAS]
    with connection.cursor() as cursor:

        sqlite_select_query = 'SELECT * from  ' + project.table_name +' WHERE id = '+ data_id
        cursor.execute(sqlite_select_query)
        tabledata = cursor.fetchone()




    record={}
    record['id']=tabledata[0]
    record['author_id']=tabledata[1]
    record['published_date']=tabledata[2]
    for i in  range(len(fields)):
        record[fields[i].fieldname]=tabledata[3+i]
    
    tabledata=list(tabledata)
    tabledata.pop(0)
    tabledata.pop(0)
    tabledata.pop(0)

    mydata=zip(tabledata,fields)
    return render(request, 'FocusApp/updateTablodata.html', {'mydata': mydata,'project_id':project_id,'data_id':data_id})

def  updateFromTablo_page(request,project_id,data_id):
    


    project=Project.objects.get(id=project_id)
    table=project.table_name
    #>>> cursor.execute('''UPDATE books SET price = ? WHERE id = ?''', (newPrice, book_id))
    fields=Field.objects.filter(project_id=project_id)

    table_field=""
        
    table_field+="UPDATE  " +table +" SET  "

    values=[]
    connection = connections[DEFAULT_DB_ALIAS]
    
    
    for i in range(len(fields)):
        

        table_field+=fields[i].fieldname+" = %s WHERE id = %s "
        
        values.append(request.POST.get(fields[i].fieldname))
        values.append(data_id)
        sql=table_field
      

        with connection.cursor() as cursor:
            cursor.execute(table_field,tuple(values))
        table_field="UPDATE  " +table +" SET  "
        values.clear()

    v1=[]
    v2=[]
    updateauth="UPDATE  " +table +"   SET author_id  = %s WHERE id =  "+data_id
    v1.append(str(request.user.id))
    v2.append(str(date.today()))
    updatedate="UPDATE  " +table +"  SET published_date = %s WHERE id =  "+data_id
    with connection.cursor() as cursor:
            cursor.execute(updateauth,tuple(v1))
            cursor.execute(updatedate,tuple(v2))
    tab='datatab'
    return HttpResponseRedirect(reverse('project-page', kwargs={'slug': project_id,'tab':tab}))


def send_message_invite(request, user,project_id,roll_id):


    print("innn   right ")
    invite_user=request.user
    try:
        project = Project.objects.get(id=project_id)

        current_site = get_current_site(request)

        message = project.owner.first_name+" invite you a project \nProject Title :" +project.abstract +\
                  "\nProject Abstract :" +project.abstract +"\n Please click on the link below to accept invite.\n"+render_to_string('FocusApp/invite_mail_link.html', {
                'user': user, 'domain': current_site.domain,
                'project_id': project_id,
                'roll_id': roll_id,
                'invite_user_id':user.id,
                'token': account_activation_token.make_token(user)
            })
        mail_subject = 'Invitation'

        mail = EmailMessage(mail_subject, message, to=[user.email])
        mail.send()

      
        return True

    except:
        print('false')
        return False

def accept_invite(request, roll_id):

    directive=''
    try:
        aa=ProjectUser.objects.get(id=roll_id)

        aa.is_accepted=True
        aa.save()
        directive = 'Join the project successfully.'
    except:
        directive = 'Invalid link'

    

    return render(request, 'FocusApp/thank.html', {"directive": directive})


def exportdata_page(request,project_id,data_id):
    tabledata=[]
    project=Project.objects.get(id=project_id)
    if project.have_table==True:
        connection = connections[DEFAULT_DB_ALIAS]
        with connection.cursor() as cursor:
           
            sqlite_select_query = 'SELECT * from  ' + project.table_name +' WHERE id = '+ data_id
            cursor.execute(sqlite_select_query)
            tabledata = cursor.fetchone()
        fields = Field.objects.filter(project_id=project_id)
        dic={}
        dic['id']=tabledata[0]


        a=User.objects.get(id=int(tabledata[1]))
        dic['author_name']=a.first_name
        dic['published_date']=tabledata[2]
        for i in  range(len(fields)):
            dic[fields[i].fieldname]=tabledata[3+i]



    return render(request,'FocusApp/exportdata.html',{'dic':dic,'project_id':project_id,'data_id':data_id})
def exportdata(project_id,data_id):
    tabledata=[]
    project=Project.objects.get(id=project_id)
    if project.have_table==True:
        connection = connections[DEFAULT_DB_ALIAS]
        with connection.cursor() as cursor:
           
            sqlite_select_query = 'SELECT * from  ' + project.table_name +' WHERE id = '+ data_id
            cursor.execute(sqlite_select_query)
            tabledata = cursor.fetchone()
        fields = Field.objects.filter(project_id=project_id)
        dic={}
        dic['id']=tabledata[0]


        a=User.objects.get(id=int(tabledata[1]))
        dic['author_name']=a.first_name
        dic['published_date']=tabledata[2]
        for i in  range(len(fields)):
            dic[fields[i].fieldname]=tabledata[3+i]

    t = Template("FocusApp/exportdata.html")
    c = Context({'dic':dic,'project_id':project_id,'data_id':data_id})
    return  t.render(c)


    
def topdf_page(request,project_id,data_id):

    tabledata=[]
    project=Project.objects.get(id=project_id)
    if project.have_table==True:
        connection = connections[DEFAULT_DB_ALIAS]
        with connection.cursor() as cursor:
           
            sqlite_select_query = 'SELECT * from  ' + project.table_name +' WHERE id = '+ data_id
            cursor.execute(sqlite_select_query)
            tabledata = cursor.fetchone()
        fields = Field.objects.filter(project_id=project_id)
        dic={}
        dic['id']=tabledata[0]


        a=User.objects.get(id=int(tabledata[1]))
        dic['author_name']=a.first_name
        dic['published_date']=tabledata[2]
        for i in  range(len(fields)):
            dic[fields[i].fieldname]=tabledata[3+i]

    context_dict={'dic':dic,'project_id':project_id,'data_id':data_id}
    template = get_template("FocusApp/data.html")
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
