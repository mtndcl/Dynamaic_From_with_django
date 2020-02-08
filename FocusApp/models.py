from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	organization = models.TextField(max_length=500, blank=True,null=True)
	phone_number = models.CharField(max_length=30, blank=True,null=True)
	is_confirm = models.BooleanField(blank=False,null=True,default=False)

class Project(models.Model):


	title = models.TextField(max_length=500, blank=True,null=True)
	abstract= models.TextField(max_length=500, blank=True,null=True)
	owner=models.ForeignKey(User,on_delete=models.CASCADE,default=None)
	have_data = models.BooleanField(blank=False,null=False,default=False)
	table_name=models.TextField(max_length=500, blank=True,null=True)
	have_table= models.BooleanField(blank=False,null=False,default=False)


class Rolls(models.Model):

	ADMIN ="ADMIN"
	OWNER = "OWNER"
	MANAGER = "MANAGER"
	MEMBER = "MEMBER"
	rolls_choices=(
		(OWNER,'owner'),
		(MANAGER,'manager'),
		(MEMBER,'member'),
		(ADMIN,'admin'),

		)
	roll = models.CharField(max_length=100,choices=rolls_choices)



class ProjectUser(models.Model):

	project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None)
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	roll = models.ForeignKey(Rolls, on_delete=models.CASCADE, default=None)
	is_accepted = models.BooleanField(blank=False, null=False, default=False)


class Field(models.Model):

	project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None)
	fieldname = models.TextField(max_length=500, blank=True, null=True)
	fieldtype = models.TextField(max_length=500, blank=True, null=True)
	fielddefaultvalue = models.TextField(max_length=500, blank=True, null=True)
	fieldmondatory =models.BooleanField(blank=False, null=False, default=False)


