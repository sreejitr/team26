from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from forms import * 
from budgie.models import * 
from django import forms 
from datetime import datetime, date, timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from mimetypes import guess_type
from django.http import HttpResponse, Http404
import uuid
from itertools import chain
import operator
import pdb
from django.db.models import Q
from django.contrib import messages

from django.utils import timezone

#For the PDF
#import ho.pisa as pisa
import cStringIO as StringIO
import cgi
from django.template import RequestContext
from io import BytesIO
import sys

#Exception handling
from django.core.exceptions import ObjectDoesNotExist
# Token generator
from django.contrib.auth.tokens import default_token_generator
import json
from django.db.models import Sum
import calendar
from functions import list_of_months_years
import sys

def home(request):
	context = {}
	return render(request, 'budgie/home.html', context)

def about(request):
	context = {}
	return render(request, 'budgie/about.html', context)

def contact(request):
	context = {}
	return render(request, 'budgie/contact.html', context)   

@login_required
def index(request):
	context = {}
	return render(request, 'budgie/index.html', context)

@login_required
def profile(request):
	context = {}

	try:
		assets = Asset.objects.filter(user=request.user)
		liabilities = Liability.objects.filter(user=request.user)
		
	except (Asset.DoesNotExist, Liability.DoesNotExist):	
		pass
	context = {'assets': assets, 'liabilities': liabilities}
	return render(request, 'budgie/profile.html', context)

def user_login(request):
	context = {}

	try:
		if request.method == 'GET':
			context['form'] = LoginForm()
			return render (request, 'budgie/login.html', context)

		form = LoginForm(request.POST) 
		context['form'] = form
		if not form.is_valid(): 
			return render(request, 'budgie/login.html', context)

		user_login = authenticate(username=form.cleaned_data['username'], 
								  password=form.cleaned_data['password'])
		login(request, user_login)
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
	return redirect(reverse('profile'))

@transaction.atomic
def register(request):
	context = {}
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render (request, 'budgie/register.html', context)

	try:
		form = RegistrationForm(request.POST) 
		context['form'] = form
		if not form.is_valid(): 
			return render(request, 'budgie/register.html', context)

		new_user = User.objects.create_user(username=form.cleaned_data['username'],
										password=form.cleaned_data['password1'], 
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
		new_user.save()
		new_user.is_active=False
		new_user.save()

		verification_id = uuid.uuid4().hex
		new_user_profile = UserProfile(user_id=new_user.id, verification_id=verification_id)
		new_user_profile.save()
		
		link = 'http://' + request.get_host() + '/budgie/confirm/' + new_user.username + '/' + verification_id
		html_content='<br> <a href="' + link + '">' + 'Click here to activate account</a>'
		send_confirmation(new_user.username, html_content)
		context['User'] = new_user
		return render(request, 'budgie/check-mail.html', context)
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		messages.add_message(request, message.SUCCESS, "Incorrect Credentials")

def send_confirmation(email, html_content):
    subject, from_email, to = 'Validate your email', 'susanal@andrew.cmu.edu', email
    text_content = 'To validate your account, please click the following link: '
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send() 


@transaction.atomic
def confirm(request, email, verification_id):
	request_user = User.objects.get(username=email)
	context = {}

	try:
		context['User'] = request.user
			
		user_in_sys = User.objects.get(username=email)
		user_id = user_in_sys.id
		if UserProfile.objects.get(user_id=user_id).verification_id == verification_id:
			user_in_sys.is_active=True
			user_in_sys.save()
			return render(request, 'budgie/confirm.html', context)
		else:
			return redirect(reverse('index'))
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		messages.add_message(request, message.SUCCESS, "Invalid token!!!! Possible hack attempt!!")
		return redirect(reverse('index'))


@login_required
@transaction.atomic
def add_transaction(request):
	context = {}
	context['User'] = request.user
	message= ''
	try:
		form = TransactionForm()

		if request.method == 'GET':
			context['form'] = form
			form.fields["from_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="From Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)

			form.fields["to_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="To Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)

			return render(request, 'budgie/add_transaction.html', context)
		now = datetime.now()

		new_transaction = Transaction(user=request.user, date=now)
		form = TransactionForm(request.POST, instance=new_transaction)
		
		if not form.is_valid():
			context['form'] = form
			form.fields["from_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="From Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)

			form.fields["to_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="To Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
			return render(request, 'budgie/add_transaction.html', context)
		
		from_account = form.cleaned_data['from_account']
		to_account = form.cleaned_data['to_account']
		amount = form.cleaned_data['amount']
		transaction_type = form.cleaned_data['transaction_type']

		if (transaction_type == "CR"):
			b = BaseAccount.objects.get(account_no=to_account)
			b.balance += amount
			b.save()
			trans = form.save(commit=False)
			trans.to_acc_end_bal = b.balance
			trans.save()	
		elif (transaction_type == "DR"):
			b = BaseAccount.objects.get(account_no=from_account)
			b.balance = b.balance - amount
			if (int(b.balance) < 0):
				message="Your account does not have enough funds to complete the transaction"
				context['form'] = form
				form.fields["from_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="From Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
				messages.add_message(request, messages.SUCCESS, message)
				return render(request, 'budgie/add_transaction.html', context)
			else:
				b.save()	
				trans = form.save(commit=False)
				trans.frm_acc_end_bal = b.balance
				trans.save()
		else:
			b1 = BaseAccount.objects.get(account_no=from_account)
			b2 = BaseAccount.objects.get(account_no=to_account)
			b1.balance = b1.balance - amount
			if (int(b1.balance) < 0):
				message="Your account does not have enough funds to complete the transaction"
				context['form'] = form
				form.fields["from_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="From Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
				form.fields["to_account"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="To Account:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
				messages.add_message(request, messages.SUCCESS, message)
				return render(request, 'budgie/add_transaction.html', context)
			else:
				b1.save()
				b2.balance = b2.balance + amount
				b2.save()
				trans = form.save(commit=False)
				trans.frm_acc_end_bal = b1.balance
				trans.to_acc_end_bal = b2.balance
				trans.save()
				

		messages.add_message(request, messages.SUCCESS, 'Transaction Added Succesfully.')
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		messages.add_message(request, messages.SUCCESS, 'Oops something went wrong. Try Again!')
	
	#Transactions = Transaction.objects.filter(user=request.user)
	#context['transactions'] = Transactions
	context['form'] = form
	context['balance_message'] = message
	context['trans'] = trans
	context['all_accounts'] = BaseAccount.objects.filter(user=request.user)

	
	#context['form'] = TransactionForm()
	return render(request, 'budgie/view_transaction.html', context)


@login_required
def view_transaction(request):
	context = {}
	context['User'] = request.user
	return render(request, 'budgie/view_transaction.html', context)

#To populate the dropdown list of accounts
def get_accounts(request, account_type):
	context = {}
	
	if account_type == 'All':
		accounts = BaseAccount.objects.filter(user=request.user)
	else:
		accounts = BaseAccount.objects.filter(user=request.user, account_type=account_type)

	context = {'User': request.user, 'accounts': accounts}
	return render(request, 'budgie/accounts.html', context)

def get_transactions(request, account_type, account_number, time_options):
	context = {}

	try:
		if account_type == 'All':
			 transactions = Transaction.objects.filter(user=request.user)
		else: 
			account_no = BaseAccount.objects.get(account_no=account_number).id
			transactions = Transaction.objects.filter(user=request.user).filter(Q(from_account=account_no) | Q(to_account=account_no))

		end_date = datetime.now()
		start_date = end_date - timedelta(days=7)
		month = start_date.month

		if time_options == "Week":
			transactions = transactions.filter(date__range=[start_date, end_date])
		else:
			transactions = transactions.filter(user=request.user, date__month=month)

		context['transactions'] = transactions
		context['User'] = request.user
		return render(request, 'budgie/transactions.html', context, content_type="application/html")
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		return redirect('/budgie/view_transaction')

@login_required
@transaction.atomic
def add_account(request):
	context = {}
	context['User'] = request.user

	try:
		form = BaseAccountForm()

		if request.method == 'GET':
			context['form'] = form
			return render(request, 'budgie/create_account.html', context)
		
		new_account = BaseAccount(user=request.user, status="open")
		form = BaseAccountForm(request.POST, instance=new_account)
		
		if not form.is_valid():
			context = {'form':form}
			return render(request, 'budgie/create_account.html', context)

		initial_amount = float(form.cleaned_data['balance'])
		form.save()


		if(request.POST['account_type'] == "CC"):
			new_type_account = CreditCard(account_no=new_account)
		elif(request.POST['account_type'] == "CHK"):
			new_type_account = Checking(account_no=new_account)
		elif(request.POST['account_type'] == "SAV"):
			new_type_account = Saving(account_no=new_account)

		new_type_account.save()
		
		t = Transaction(user=request.user, name='Initial Deposit', description='Deposit-Account creation', 
					transaction_type='CR', category='DEP', amount=initial_amount, date=datetime.now(),
					to_account=new_account, to_acc_end_bal=initial_amount)
		t.save()
		show_messages(request,'Account Added Succesfully.')
		
		context['form'] = BaseAccountForm()
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		show_messages(request,'Error while creating Account.')
	return redirect('/budgie/view_accounts')

	
@login_required
@transaction.atomic
def edit_account(request, id):

	entry_to_edit = get_object_or_404(BaseAccount, user=request.user, id=id)
	if request.method == 'GET':
		form = BaseAccountForm(instance=entry_to_edit)  # Creates form from the 
		form.fields['account_no'].widget.attrs['readonly'] = True
		form.fields['account_type'].widget.attrs['readonly'] = True
		form.fields['balance'].widget.attrs['readonly'] = True
		context = {'form':form, 'id':id}          # existing entry.
		return render(request, 'budgie/edit_account.html', context, content_type='application/html')

	context ={}
	try:
		if "account_no" in request.POST or "account_type" in request.POST or "balance" in request.POST:
			if entry_to_edit.account_no != request.POST["account_no"] or entry_to_edit.account_type != request.POST["account_type"] or entry_to_edit.balance != float(request.POST["balance"]):
				context['error_message'] = "Permission denied to edit account details! Possible hack into account"
				return render(request, 'budgie/error.html', context)

	    # if method is POST, get form data to update the model
		form = BaseAccountForm(request.POST, instance=entry_to_edit)

		if not form.is_valid():
			context = {'form':form, 'id':id} 
			return render(request, 'budgie/edit_account.html', context, content_type='application/html')

		form.save()
		context['is_edit'] = "true"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['edit_error'] = "error"
	
	context['credit_card_acc'] = BaseAccount.objects.filter(user=request.user, account_type="CC")
	context['checking_accounts'] = BaseAccount.objects.filter(user=request.user, account_type="CHK")
	context['savings_accounts'] = BaseAccount.objects.filter(user=request.user, account_type="SAV")

	return render(request, 'budgie/account_ajax.html', context, content_type="application/html")

@login_required
@transaction.atomic
def create_assets(request):
	context = {}
	context['User'] = request.user

	try:
		form = AssetForm()

		if request.method == 'GET':
			context['form'] = form
			return render(request, 'budgie/create_assets.html', context)
		
		new_asset = Asset(user=request.user, status="activefliab")
		form = AssetForm(request.POST, instance=new_asset)
		
		if not form.is_valid():
			context = {'form':form}
			return render(request, 'budgie/create_assets.html', context)

		form.save()
		show_messages(request,'Asset Created Succesfully.')
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		show_messages(request,'Error while creating Asset.')
	return redirect('/budgie/profile')

@login_required
@transaction.atomic
def edit_assets(request, id):
	
	entry_to_edit = get_object_or_404(Asset, user=request.user, id=id)
	if request.method == 'GET':
		form = AssetForm(instance=entry_to_edit)  # Creates form from the 
		context = {'form':form, 'id':id}          # existing entry.
		return render(request, 'budgie/edit_assets.html', context, content_type='application/html')

	context = {}
	try:
	    # if method is POST, get form data to update the model
		form = AssetForm(request.POST, instance=entry_to_edit)

		if not form.is_valid():
			context = {'form':form, 'id':id} 
			return render(request, 'budgie/edit_assets.html', context, content_type='application/html')

		form.save()
		context['is_edit'] = "true"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['edit_error'] = "error"	
	
	context['assets'] = Asset.objects.filter(user=request.user)
	return render(request, 'budgie/assets_ajax.html', context, content_type='application/html')

@login_required
@transaction.atomic
def delete_assets(request, id):
	context = {}
	try:
		entry_to_delete = Asset.objects.get(user=request.user, id=id)
		if entry_to_delete:
			entry_to_delete.delete()
		else:
			context['error'] = "error"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['error'] = "error"

	context['assets'] = Asset.objects.filter(user=request.user)
	return render(request, 'budgie/assets_ajax.html', context, content_type='application/html')


@login_required
@transaction.atomic
def create_liability(request):
	context = {}
	context['User'] = request.user

	try:
		form = LiabilityForm()

		if request.method == 'GET':
			context['form'] = form
			return render(request, 'budgie/create_liability.html', context)
		
		new_liability = Liability(user=request.user, status="active")
		form = LiabilityForm(request.POST, instance=new_liability)
		

		if not form.is_valid():
			context = {'form':form}
			return render(request, 'budgie/create_liability.html', context)

		form.save()
		show_messages(request,'Liability Added Succesfully.')
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		show_messages(request, "Failed to create liability")
	
	return redirect('/budgie/profile')

@login_required
@transaction.atomic
def edit_liability(request, id):

	entry_to_edit = get_object_or_404(Liability, user=request.user, id=id)
	if request.method == 'GET':
		form = LiabilityForm(instance=entry_to_edit)  # Creates form from the 
		context = {'form':form, 'id':id}          # existing entry.
		return render(request, 'budgie/edit_liability.html', context, content_type='application/html')

	context = {}
	try:
	    # if method is POST, get form data to update the model
		form = LiabilityForm(request.POST, instance=entry_to_edit)

		if not form.is_valid():
			context = {'form':form, 'id':id} 
			return render(request, 'budgie/edit_liability.html', context, content_type='application/html')

		form.save()
		context['is_edit'] = "true"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['edit_error'] = "error"
	
	context['liabilities'] = Liability.objects.filter(user=request.user)
	return render(request, 'budgie/liability_ajax.html', context, content_type='application/html')

@login_required
@transaction.atomic
def delete_liability(request, id):
	context = {}
	try:
		entry_to_delete = Liability.objects.get(user=request.user, id=id)
		entry_to_delete.delete()
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['error'] = "error"

	context['liabilities'] = Liability.objects.filter(user=request.user)
	return render(request, 'budgie/liability_ajax.html', context, content_type='application/html')

@login_required
@transaction.atomic
def create_budget(request):
	context = {}

	if Budget.objects.filter(user=request.user):
		context['error_message'] = "You cannot create another budget plan.  Edit or Delete existing plan"
		return render(request, 'budgie/error.html', context)

	context['User'] = request.user

	try:
		form = BudgetForm()

		if request.method == 'GET':
			context['form'] = form
			return render(request, 'budgie/create_budget.html', context)
		
		new_budget = Budget(user=request.user)
		form = BudgetForm(request.POST, instance=new_budget)
		
		if not form.is_valid():
			context = {'form':form}
			return render(request, 'budgie/create_budget.html', context)

		form.save()
		context['budget'] = Budget.objects.filter(user=request.user)

		show_messages(request,'Budget Plan Created Succesfully.')
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		show_messages(request, "Unable to create budget!")
	return redirect('/budgie/view_budget')

@login_required
@transaction.atomic
def edit_budget(request, id):

	entry_to_edit = get_object_or_404(Budget, user=request.user, id=id)
	if request.method == 'GET':
		form = BudgetForm(instance=entry_to_edit)  # Creates form from the 
		context = {'form':form, 'id':id}          # existing entry.
		return render(request, 'budgie/edit_budget.html', context, content_type='application/html')

	context = {}

	try:
	    # if method is POST, get form data to update the model
		form = BudgetForm(request.POST, instance=entry_to_edit)

		if not form.is_valid():
			context = {'form':form, 'id':id} 
			return render(request, 'budgie/edit_budget.html', context, content_type='application/html')

		form.save()
		context['is_edit'] = "true"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['edit_error'] = "error"
	context['budget'] = Budget.objects.filter(user=request.user)
	return render(request, 'budgie/budget_ajax.html', context, content_type='application/html')


@login_required
@transaction.atomic
def create_goal(request):
	context = {}
	context['User'] = request.user

	try:
		form = GoalForm()

		goals = Goal.objects.filter(user=request.user)
		if request.method == 'GET':

			context['form'] = form

			form.fields["account_no"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="Account Number:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
			return render(request, 'budgie/create_goal.html', context)
		
		new_goal = Goal(user=request.user)
		form = GoalForm(request.POST, instance=new_goal)
		
		if not form.is_valid():
			context = {'form':form}
			form.fields["account_no"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="Account Number:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
			return render(request, 'budgie/create_goal.html', context)

		expected_amount = form.cleaned_data['expected_amount']
		account_no = form.cleaned_data['account_no']
		form_date = form.cleaned_data['date']

		goals = Goal.objects.filter(user=request.user)
		account = BaseAccount.objects.get(account_no=account_no)
		account_balance = account.balance
		expected_balance = 0

		for g in goals:
			if str(g.account_no) == str(account_no):
				expected_balance = expected_balance + g.expected_amount
		expected_balance = expected_balance + expected_amount

		if (expected_balance < account_balance):
			context = {'form':form}
			form.fields["account_no"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="Account Number:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
			show_messages(request,'The goal is already achieved.')
			return render(request, 'budgie/create_goal.html', context)
		elif ( date.today() > form_date):
			context = {'form':form}
			form.fields["account_no"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
											  required=False,
											  label="Account Number:",
	        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
			show_messages(request,'Please choose an appropriate date.')
			return render(request, 'budgie/create_goal.html', context)
		else:
			form.save()
			show_messages(request,'Goal Plan Added Succesfully.')
			
		context['expected_balance'] = expected_balance
		context['account_balance'] = account_balance

		context['goals'] = Goal.objects.filter(user=request.user)
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		show_messages(request, "Unable to create goal!!")
	
	return redirect('/budgie/view_goals')

@login_required
@transaction.atomic
def edit_goal(request, id):

	entry_to_edit = get_object_or_404(Goal, user=request.user, id=id)
	if request.method == 'GET':
		form = GoalForm(instance=entry_to_edit)  # Creates form from the 
		form.fields["account_no"] = forms.ModelChoiceField(queryset=BaseAccount.objects.filter(user=request.user),
										  required=False,
										  label="Account Number:",
        								  widget=forms.Select(attrs={'class' : 'form-control'}),)
		context = {'form':form, 'id':id}          # existing entry.
		return render(request, 'budgie/edit_goal.html', context, content_type='application/html')

	context = {}
	try:
	    # if method is POST, get form data to update the model
		form = GoalForm(request.POST, instance=entry_to_edit)

		if not form.is_valid():
			context = {'form':form, 'id':id} 
			return render(request, 'budgie/edit_goal.html', context, content_type='application/html')

		form.save()
		context['is_edit'] = "true"
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['edit_error'] = "error"

	context = get_all_goals(request)
	return render(request, 'budgie/goals_ajax.html', context, content_type='application/html')


def get_all_goals(request):
	context = {}
	accounts_list = []
	goals_balance = []
	accounts_balance = []
	expirations = []
	today_date = date.today()

	goals = Goal.objects.filter(user=request.user)
	accounts = BaseAccount.objects.filter(user=request.user)

	for g in goals:
		accounts_list.append(g.account_no)
		if (g.date < today_date):
			expired = 'Yes'
		else:
			expired = 'No'
		expirations.append(expired)

	accounts_list = list(set(accounts_list)) #To filter the unique accounts numbers. 
	

	for acct in accounts_list:
		expected_balance = 0
		for g in goals:
			if g.account_no == acct:
				expected_balance = expected_balance + g.expected_amount
		goals_balance.append(expected_balance)

	for acct in accounts_list:
		for a in accounts:
			if str(acct) == str(a.account_no):
				accounts_balance.append(a.balance)

	goals_track = zip(accounts_list, accounts_balance, goals_balance)
	goals_pack = zip(goals, expirations)
	context['goals_track'] = goals_track
	context['user'] = request.user
	context['goals'] = goals
	context['goals_pack'] = goals_pack
 	return context

@login_required
@transaction.atomic
def delete_goal(request, id):
	context = {}
	try:
		entry_to_delete = Goal.objects.get(user=request.user, id=id)
		entry_to_delete.delete()
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['error'] = "error"

	context = get_all_goals(request)
	return render(request, 'budgie/goals_ajax.html', context, content_type='application/html')

@login_required
@transaction.atomic
def view_accounts(request):
	context = {}
	all_accounts = {}
	credit_card_acc = {}
	checking_account = {}
	savings_account = {}

	try:
		all_accounts = BaseAccount.objects.filter(user=request.user, status="open")
		credit_card_acc = CreditCard.objects.filter(account_no=all_accounts)
		checking_accounts = Checking.objects.filter(account_no=all_accounts)
		savings_accounts = Saving.objects.filter(account_no=all_accounts)
		
	except (BaseAccount.DoesNotExist, CreditCard.DoesNotExist, Checking.DoesNotExist, Saving.DoesNotExist):	
		print "Exception caught: %s " % sys.exc_info()[0]
		pass
	context = {'all_accounts': all_accounts, 'credit_card_acc': credit_card_acc, 'checking_accounts': checking_accounts, 
			    'savings_accounts': savings_accounts}
	return render(request, 'budgie/view_accounts.html', context)

@login_required
@transaction.atomic
def view_goals(request):
	context = {}
	context = get_all_goals(request)
	
 	return render(request, 'budgie/view_goals.html', context)

@login_required
@transaction.atomic
def view_budget(request):
	context ={}
	context['budget'] = Budget.objects.filter(user=request.user)
	return render(request, 'budgie/view_budget.html', context)

@login_required
@transaction.atomic
def delete_budget(request, id):
	context = {}
	try:
		entry_to_delete = Budget.objects.get(user=request.user, id=id)
		entry_to_delete.delete()
	except:
		print "Exception caught: %s " % sys.exc_info()[0]
		context['error'] = "error"
	
	context['goals'] = Budget.objects.filter(user=request.user)
	return render(request, 'budgie/budget_ajax.html', context, content_type='application/html')

def show_messages(request,textMessage):
	storage = messages.get_messages(request)
	storage.used = True
	messages.add_message(request, messages.SUCCESS, textMessage)

def generte_pdf(html):
	try:
		result = StringIO.StringIO()	
		pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
		if not pdf.err:
			return HttpResponse(result.getvalue(), content_type='application/pdf')
		return HttpResponse('Error generating PDF: %s' % cgi.escape(html))
	except:
		return HttpResponse('Error generating PDF: %s' % cgi.escape(html))

@login_required
@transaction.atomic
def report_pdf(request):
	context = {}
	today = timezone.now()
	month = today.month
	
	accounts = BaseAccount.objects.filter(user=request.user)
	assets = Asset.objects.filter(user=request.user)
	liabilities = Liability.objects.filter(user=request.user)
	transactions = Transaction.objects.filter(user=request.user, date__month=month)
	
	context['User'] = request.user
	context['accounts'] = accounts
	context['assets'] = assets
	context['liabilities'] = liabilities
	context['transactions'] = transactions
	context['pagesize'] = 'A4'
	context['today'] = today
	
	html = render_to_string('budgie/report.html', context, context_instance=RequestContext(request))
	print html
	return generte_pdf(html)

@login_required
@transaction.atomic
def dashboard(request):
	context = {}
	return render(request, 'budgie/dashboardmain.html', context)

@login_required
@transaction.atomic
def allaccounts(request):
	context = {}
	return render(request, 'budgie/allaccounts.html', context)

@login_required
@transaction.atomic
def get_allaccounts(request):
	months = []
	years = []
	month_year = []
	balances_checking = []
	balances_savings = []
	curr_bal_savings = 0
	curr_bal_checking = 0
	number = 5
	months, years, month_year = list_of_months_years(number)
	
	try:
		accounts = BaseAccount.objects.filter(user=request.user)
		#Checking Accounts
		checking_accounts_all = accounts.filter(account_type="CHK")
		checking_accounts = checking_accounts_all.values_list('id', flat=True)
		query1 = Q(from_account_id__in=checking_accounts) | Q(to_account_id__in=checking_accounts)
		months_bal_checking = Transaction.objects.filter(user=request.user).filter(query1)

		#Savings Accounts
		savings_accounts_all = accounts.filter(account_type="SAV")
		savings_accounts = savings_accounts_all.values_list('id', flat=True)
		query2 = Q(from_account_id__in=savings_accounts) | Q(to_account_id__in=savings_accounts)
		months_bal_savings = Transaction.objects.filter(user=request.user).filter(query2)
		
		for i, month in enumerate(months):
			balance_chk = 0
			balance_sav = 0
			first = date(years[i], months[i], 1)
			prevMonth = first - timedelta(days=1)
			try:
				for id in checking_accounts:
					q = Q(from_account_id=id) | Q(to_account_id=id)
					month_bal_checking = months_bal_checking.filter(date__month=month, date__year=years[i]).filter(q).order_by('-date').first()
					if month_bal_checking == None:
						month_bal_checking = months_bal_checking.exclude(date__gt=prevMonth).filter(q).order_by('-date').first()
						
					if month_bal_checking != None:
						if month_bal_checking.frm_acc_end_bal != None:
							balance_chk = balance_chk + int(month_bal_checking.frm_acc_end_bal)  
						else: 
							balance_chk = balance_chk + int(month_bal_checking.to_acc_end_bal)
							
				for id in savings_accounts:
					q = Q(from_account_id=id) | Q(to_account_id=id)
					month_bal_savings = months_bal_savings.filter(date__month=month, date__year=years[i]).filter(q).order_by('-date').first()
					if month_bal_savings == None:
						month_bal_savings = months_bal_savings.exclude(date__gt=prevMonth).filter(q).order_by('-date').first()

					if month_bal_savings != None:
						if month_bal_savings.frm_acc_end_bal != None:
							balance_sav = balance_sav + int(month_bal_savings.frm_acc_end_bal)  
						else: 
							balance_sav = balance_sav + int(month_bal_savings.to_acc_end_bal)
			except:
				pass
			balances_checking.append(balance_chk)	
			balances_savings.append(balance_sav)
				
	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		if checking_accounts_all:
			for account in checking_accounts_all:
				curr_bal_checking = curr_bal_checking + int(account.balance)

		if savings_accounts_all:
			for account in savings_accounts_all:
				curr_bal_savings = curr_bal_savings + int(account.balance)
		
		data = [[{"type": 'column',"name": 'Checking Accounts',"data": balances_checking},{"type": 'column',"name": 'Savings Accounts',"data": balances_savings},{"type": 'pie',"name": 'Current Balance',"data": [{"name": 'Checking Accounts',"y": curr_bal_checking },{"name": 'Savings Accounts',"y": curr_bal_savings }], "center": [110, 90],"size": 150,"showInLegend": False,"dataLabels": {"enabled": False}}], month_year]
		return HttpResponse(json.dumps(data), content_ype='application/json')
	raise Http404 

@login_required
@transaction.atomic
def checkingaccounts(request):
	context = {}
	return render(request, 'budgie/checkingaccounts.html', context)

@login_required
@transaction.atomic
def get_checking_accounts(request):
	months = []
	years = []
	month_year = []
	series = []
	months, years, month_year = list_of_months_years(5)
	try:
		accounts = BaseAccount.objects.filter(user=request.user)
		#Checking Accounts
		checking_accounts_all = accounts.filter(account_type="CHK")
		checking_accounts = checking_accounts_all.values_list('id', flat=True)
		query1 = Q(from_account_id__in=checking_accounts) | Q(to_account_id__in=checking_accounts)
		months_bal_checking = Transaction.objects.filter(user=request.user).filter(query1)
		if months_bal_checking:
			for id in checking_accounts:
				data = []
				series_point = {}
				q = Q(from_account_id=id) | Q(to_account_id=id)
				for i, month in enumerate(months):
					first = date(years[i], months[i], 1)
					prevMonth = first - timedelta(days=1)
					try:
						month_bal_checking = months_bal_checking.filter(date__month=month, date__year=years[i]).filter(q).order_by('-date').first()
						if month_bal_checking == None:
							month_bal_checking = months_bal_checking.exclude(date__gt=prevMonth).filter(q).order_by('-date').first()
						
						if month_bal_checking:
							if month_bal_checking.frm_acc_end_bal != None:
								data.append(int(month_bal_checking.frm_acc_end_bal))  
							else: 
								data.append(int(month_bal_checking.to_acc_end_bal))
						else:
							data.append(0)
					except:
						pass

				series_point["name"] = "Account No. " + str(accounts.get(id=id).account_no)
				series_point["data"] = data
				series.append(series_point)

	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		data = [series, month_year]
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404

@login_required
@transaction.atomic
def savingsaccounts(request):
	context = {}
	return render(request, 'budgie/savingsaccounts.html', context)

@login_required
@transaction.atomic
def get_savings_accounts(request):
	months = []
	years = []
	month_year = []
	series = []
	months, years, month_year = list_of_months_years(5)
	try:
		accounts = BaseAccount.objects.filter(user=request.user)
		#Savings Accounts
		savings_accounts_all = accounts.filter(account_type="SAV")
		savings_accounts = savings_accounts_all.values_list('id', flat=True)
		query2 = Q(from_account_id__in=savings_accounts) | Q(to_account_id__in=savings_accounts)
		months_bal_savings = Transaction.objects.filter(user=request.user).filter(query2)
		if months_bal_savings:
			for id in savings_accounts:
				data = []
				series_point = {}
				q = Q(from_account_id=id) | Q(to_account_id=id)
				for i, month in enumerate(months):
					first = date(years[i], months[i], 1)
					prevMonth = first - timedelta(days=1)
					try:
						month_bal_savings = months_bal_savings.filter(date__month=month, date__year=years[i]).filter(q).order_by('-date').first()
						if month_bal_savings == None:
							month_bal_savings = months_bal_savings.exclude(date__gt=prevMonth).filter(q).order_by('-date').first()
						
						if month_bal_savings:
							if month_bal_savings.frm_acc_end_bal != None:
								data.append(int(month_bal_savings.frm_acc_end_bal))  
							else: 
								data.append(int(month_bal_savings.to_acc_end_bal))
						else:
							data.append(0)
					except:
						pass

				series_point["name"] = "Account No. " + str(accounts.get(id=id).account_no)
				series_point["data"] = data
				series.append(series_point)

	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		data = [series, month_year]
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404

@login_required
@transaction.atomic
def incvsexp(request):
	context = {}
	return render(request, 'budgie/incvsexp.html', context)

@login_required
@transaction.atomic
def get_incvsexp(request):
	months = []
	years = []
	month_year = []
	income = []
	expense = []
	number = 12
	months, years, month_year = list_of_months_years(12)
	
	try:
		accounts_all = BaseAccount.objects.filter(user=request.user)
		q = Q(account_type="CHK") | Q(account_type="SAV")
		accounts_all = accounts_all.filter(q)
		account_ids = accounts_all.values_list('id', flat=True)
		#Income
		query1 = Q(to_account_id__in=account_ids)
		months_income = Transaction.objects.filter(user=request.user, transaction_type="CR").filter(query1)
		#Expense
		query2 = Q(from_account_id__in=account_ids)
		months_expense = Transaction.objects.filter(user=request.user, transaction_type="DR").filter(query2)
		for i, month in enumerate(months):
			totalincome = 0
			totalexpense = 0
			try:
				if months_income:
					sum_of_income = months_income.filter(date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_income["amount__sum"] != None:
						totalincome = int(sum_of_income["amount__sum"])

				income.append(totalincome)
				
				if months_expense:
					sum_of_expense = months_expense.filter(date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						totalexpense = int(sum_of_expense["amount__sum"])

				expense.append(totalexpense)
			except:
				pass
				
	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		data = [[{"name": 'Income', "data": income}, {"name": 'Expense', "data": expense}], month_year]
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404 

@login_required
@transaction.atomic
def totalincome(request):
	context = {}
	return render(request, 'budgie/totalincome.html', context)

@login_required
@transaction.atomic
def get_totalincome(request):
	months = []
	years = []
	month_year = []
	income_total = 0.0
	income_salary = 0.0
	income_gift = 0.0
	temp = 0.0
	title_text = "Total Income, " + datetime.now().strftime("%Y") + ": "
	#salary = []
	#gift = []	
	data = []
	number = 12
	months, years, month_year = list_of_months_years(12)
	
	try:
		accounts_all = BaseAccount.objects.filter(user=request.user)
		q = Q(account_type="CHK") | Q(account_type="SAV")
		accounts_all = accounts_all.filter(q)
		account_ids = accounts_all.values_list('id', flat=True)
		#Income
		query1 = Q(to_account_id__in=account_ids)
		months_income = Transaction.objects.filter(user=request.user, transaction_type="CR").filter(query1)

		for i, month in enumerate(months):
			sum_of_income = {}
			totalincome_sal = 0
			totalincome_gft = 0
			try:
				if months_income:
					sum_of_income_sal = months_income.filter(category="SAL", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_income_sal["amount__sum"] != None:
						totalincome_sal = float(sum_of_income_sal["amount__sum"])

					sum_of_income_gft = months_income.filter(category="GFT", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_income_gft["amount__sum"] != None:
						totalincome_gft = float(sum_of_income_gft["amount__sum"])

				income_salary +=  totalincome_sal
				income_gift +=  totalincome_gft
			except:
				pass
				
	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		#pdb.set_trace()
		income_total = income_salary + income_gift
		data.append(income_total)
		#temp = (income_salary / income_total) * 100
		temp = 20.0
		#salary.append(temp)
		data.append(income_salary)
		#temp = (income_gift / income_total) * 100
		temp = 80.0
		#gift["y"] = temp 
		data.append(income_gift)
		title_text = title_text + str(income_total) + " USD"
		data.append(title_text)
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404 

@login_required
@transaction.atomic
def totalexpenses(request):
	context = {}
	return render(request, 'budgie/totalexpenses.html', context)

@login_required
@transaction.atomic
def get_totalexpenses(request):
	months = []
	years = []
	month_year = []
	expense_shares = {"HOU": 0.0, "TRA": 0.0, "FOO": 0.0, "EDU": 0.0, "HEA": 0.0, "ENT": 0.0, "UTL": 0.0}
	temp = 0.0
	title_text = "Total Expenses, " + datetime.now().strftime("%Y") + ": "
	#salary = []
	#gift = []	
	data = []
	number = 12
	months, years, month_year = list_of_months_years(12)
	
	try:
		accounts_all = BaseAccount.objects.filter(user=request.user)
		q = Q(account_type="CHK") | Q(account_type="SAV")
		accounts_all = accounts_all.filter(q)
		account_ids = accounts_all.values_list('id', flat=True)
		#Expense
		query1 = Q(from_account_id__in=account_ids)
		months_expense = Transaction.objects.filter(user=request.user, transaction_type="DR").filter(query1)

		for i, month in enumerate(months):
			sum_of_expense = {}
			try:
				if months_expense:
					sum_of_expense = months_expense.filter(category="HOU", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["HOU"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="TRA", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["TRA"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="FOO", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["FOO"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="EDU", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["EDU"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="HEA", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["HEA"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="ENT", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["ENT"] += float(sum_of_expense["amount__sum"])

					sum_of_expense = months_expense.filter(category="UTL", date__month=month, date__year=years[i]).aggregate(Sum('amount'))
					if sum_of_expense["amount__sum"] != None:
						expense_shares["UTL"] += float(sum_of_expense["amount__sum"])
			except:
				pass
				
	except (BaseAccount.DoesNotExist):
		pass
	if request.is_ajax():
		for key, value in expense_shares.items():
			data.append(value)
			
		data.append(title_text)
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404 

@login_required
@transaction.atomic
def budgetplan(request):
	context = {}
	return render(request, 'budgie/budgetplan.html', context)

@login_required
@transaction.atomic
def get_budgetplan(request):
	title_text = "Budget Plan, " + datetime.now().strftime("%m %Y") + " - Total Budget: "	
	data = []
	try:
		budget = Budget.objects.get(user=request.user)
		data.append(round(budget.housing,2))
		data.append(round(budget.transportation,2))
		data.append(round(budget.food,2))
		data.append(round(budget.education,2))
		data.append(round(budget.health,2))
		data.append(round(budget.entertainment,2))
		data.append(round(budget.other,2))
				
	except (Budget.DoesNotExist):
		pass
	if request.is_ajax():
		data.append(title_text)
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404 

@login_required
@transaction.atomic
def budgetvsexpense(request):
	context = {}
	return render(request, 'budgie/budgetvsexpense.html', context)

@login_required
@transaction.atomic
def get_budgetvsexpense(request):
	today = datetime.now()
	income_expense_shares = {"HOU": 0.0, "TRA": 0.0, "FOO": 0.0, "EDU": 0.0, "HEA": 0.0, "ENT": 0.0}
	title_text = "Budget vs Actuals, " + datetime.now().strftime("%m %Y")	
	data = []
	budget_plan = []
	actuals = []
	#pdb.set_trace()
	try:
		#Budget Plan
		budget = Budget.objects.get(user=request.user)
		budget_plan.insert(0, float(budget.housing))
		budget_plan.insert(1, float(budget.transportation))
		budget_plan.insert(2, float(budget.food))
		budget_plan.insert(3, float(budget.education))
		budget_plan.insert(4, float(budget.health))
		budget_plan.insert(5, float(budget.entertainment))
		print budget_plan
		#Actuals
		accounts_all = BaseAccount.objects.filter(user=request.user)
		q = Q(account_type="CHK") | Q(account_type="SAV")
		accounts_all = accounts_all.filter(q)
		account_ids = accounts_all.values_list('id', flat=True)
		#Expense
		query2 = Q(from_account_id__in=account_ids)
		total_expense = Transaction.objects.filter(user=request.user, transaction_type="DR").filter(query2)

		if total_expense:
			try:
				sum_of_expense = total_expense.filter(category="HOU", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["HOU"] += float(sum_of_expense["amount__sum"])

				sum_of_expense = total_expense.filter(category="TRA", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["TRA"] += float(sum_of_expense["amount__sum"])

				sum_of_expense = total_expense.filter(category="FOO", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["FOO"] += float(sum_of_expense["amount__sum"])

				sum_of_expense = total_expense.filter(category="EDU", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["EDU"] += float(sum_of_expense["amount__sum"])

				sum_of_expense = total_expense.filter(category="HEA", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["HEA"] += float(sum_of_expense["amount__sum"])

				sum_of_expense = total_expense.filter(category="ENT", date__month=today.month, date__year=today.year).aggregate(Sum('amount'))
				if sum_of_expense["amount__sum"] != None:
					income_expense_shares["ENT"] += float(sum_of_expense["amount__sum"])

			except:
				pass
				
	except (BaseAccount.DoesNotExist, Budget.DoesNotExist):
		pass
	if request.is_ajax():
		i = 0
		#for key, value in income_expense_shares.items():
		#	actuals.insert(i, value)
		#	i += 1
		#Maintain order of values for displaying the chart
		actuals.insert(0, income_expense_shares["HOU"])
		actuals.insert(1, income_expense_shares["TRA"])
		actuals.insert(2, income_expense_shares["FOO"])
		actuals.insert(3, income_expense_shares["EDU"])
		actuals.insert(4, income_expense_shares["HEA"])
		actuals.insert(5, income_expense_shares["ENT"])

		data.append(budget_plan)
		data.append(actuals)	
		data.append(title_text)
		return HttpResponse(json.dumps(data), content_type='application/json')
	raise Http404
