from django.urls import path,include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django_pdfkit import PDFView

urlpatterns = [
   
    path('',views.welcome_page,name='welcome-page'),
    path('login/',views.login_page,name='login-page'),
    path('register/',views.register_page,name='register-page'),
    path('forgotpassword/',views.forgotpassword_page,name='forgotpassword-page'),
    path('profile/<page>/',views.profile_page,name='profile-page'),
    path('logout/',views.logout_page,name='logout-page'),
    path('logout/',views.logout_page,name='logout-page'),
    path('adminpageusers/<page>/',views.adminuser_page,name='adminuser-page'),
    path('adminpageprojects/<page>/',views.adminproject_page,name='adminproject-page'),
    path(r'Thanks/<directive>',views.thank_page,name='thank-page'),
    path(r'Error/',views.error_page,name='error-page'),
    path(r'CreateProject/<title>/<abstract>/',views.createproject_page,name='createproject-page'),
    path(r'login/block/<slug>/<page>/',views.isactive_page,name='isactive-page'),
    path(r'login/delete/<slug>/',views.deleteuser_page,name='deleteuser-page'),
  	url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
    url(r'^resetpassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.clickonresetpasswordlink, name='clickonresetpasswordlink'),
    path(r'project/<slug>/<tab>/',views.project_page,name='project-page'),
    path(r'Addtoproject/<project_id>/<user_id>/',views.addtoproject_page,name='addtoproject-page'),
    path(r'removefromproject_page/<project_id>/<user_id>/',views.removefromproject_page,name='removefromproject-page'),
    path(r'SendNotifications_page/<project_id>/<owner_id>/',views.SendNotifications_page,name='SendNotifications-page'),
    path(r'viewform/<project_id>/',views.viewform_page,name='viewform-page'),
    path(r'createdatabase/<project_id>/',views.createdatabase_page,name='createdatabase-page'),
    path(r'addfield/<project_id>/',views.addfield_page,name='addfield-page'),
    path(r'savetoform/<project_id>/',views.savetoform_page,name='savetoform-page'),
    path(r'deleteproject/<project_id>/',views.deleteproject_page,name='deleteproject-page'),
    path(r'deleteDataFromTable/<project_id>/<data_id>/',views.deleteDataFromTable_page,name='deleteDataFromTable-page'),
    path(r'viewupdateDataFromTable/<project_id>/<data_id>/',views.viewupdateDataFromTable_page,name='viewupdateDataFromTable-page'),
    path(r'updateFromTablo/<project_id>/<data_id>/',views.updateFromTablo_page,name='updateFromTablo-page'),
    path(r'deletefield/<project_id>/<field_id>/',views.deletefield_page,name='deletefield-page'),
    path(r'updatefield/<project_id>/<field_id>/',views.updatefield_page,name='updatefield-page'),
    path(r'addprojectinfo_page/<project_id>/',views.addprojectinfo_page,name='addprojectinfo-page'),
    path(r'saveproject/',views.saveproject_page,name='saveproject-page'),
    url(r'^accept-invite/(?P<roll_id>[0-9A-Za-z_\-]+)/',views.accept_invite, name='accept-invite'),
    path(r'forwardpage/<page>/',views.forwardpage_page,name='forwardpage-page'),
    path(r'backwardpage/<page>/',views.backward_page,name='backward-page'),
    path(r'exportdata_page/<project_id>/<data_id>/',views.exportdata_page,name='exportdata-page'),
    path(r'forwardadminpage/<page>/',views.forwardadminuserpage_page,name='forwardadminuserpage-page'),
    path(r'backwarddadminpage/<page>/',views.backwarddadminpage_page,name='backwarddadminpage-page'),
    path(r'forwardproject/<page>/',views.forwardproject_page,name='forwardproject-page'),
    path(r'backwardproject/<page>/',views.backwardproject_page,name='backwardproject-page'),
    path(r'topdf/<project_id>/<data_id>/',views.topdf_page,name='topdf-page'),

        


]

urlpatterns +=staticfiles_urlpatterns()
urlpatterns +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)