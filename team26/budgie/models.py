from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	verification_id = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.user.username

class BaseAccount(models.Model):
	account_no = models.CharField(max_length=50, blank=False)
	user = models.ForeignKey(User)
	name = models.CharField(max_length=50, blank=False)
	account_type = models.CharField(max_length=20, blank=False)
	bank = models.CharField(max_length=50, blank=False)
	status = models.CharField(max_length=20, blank=False)
	balance = models.DecimalField(max_digits=15, decimal_places=2, blank=False)

	def __unicode__(self):
		return self.account_no

		
class CreditCard(models.Model):
	account_no = models.ForeignKey(BaseAccount)
	due = models.DecimalField(max_digits=15, decimal_places=2, blank=False, default=0)
	payment_due_date = models.DateTimeField(default=datetime.now())
	

class Saving(models.Model):
	account_no = models.ForeignKey(BaseAccount)
	

class Checking(models.Model):
	account_no = models.ForeignKey(BaseAccount)


class Asset(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=50, blank=False)
	asset_type = models.CharField(max_length=20, blank=True)
	value = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
	status = models.CharField(max_length=20, blank=False)

	def __unicode__(self):
		return self.name
	
class Liability(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=50, blank=False)
	liability_type = models.CharField(max_length=20, blank=True, default="Loan")
	amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
	status = models.CharField(max_length=20, blank=False)
	from_date = models.DateField()
	to_date = models.DateField()

	def __unicode__(self):
		return self.name

class Transaction(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=50, blank=False)
	description = models.CharField(max_length=60, blank=True)
	transaction_type = models.CharField(max_length=2, choices=settings.TYPE_TRANSACTION_CHOICES)
	category = models.CharField(max_length=3, choices=settings.CATEGORY_CHOICES)
	amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
	date = models.DateTimeField(auto_now=True, auto_now_add=True)
	from_account = models.ForeignKey(BaseAccount, null=True, blank=True, related_name='from_account')
	frm_acc_end_bal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
	to_account = models.ForeignKey(BaseAccount, null=True, blank=True, related_name='to_account')
	to_acc_end_bal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

	def __unicode__(self):
		return self.name

class Budget(models.Model):
	user = models.OneToOneField(User)
	housing = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	transportation = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	food = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	education = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	health = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	entertainment = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	salary = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	gift = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	other = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	actual_amount_spent = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)
	month = models.CharField(max_length=15, blank=False, choices=settings.MONTH_CHOICES)
	year = models.CharField(max_length=4, blank=False, choices=settings.YEAR_CHOICES)

class Goal(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=50, blank=False)
	description = models.CharField(max_length=60, blank=True)
	expected_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
	account_no = models.ForeignKey(BaseAccount, null=True, blank=True)
	date = models.DateField()

	def __unicode__(self):
		return self.name
