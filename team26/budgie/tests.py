from django.test import TestCase
from django.utils import unittest
from budgie.models import * 
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.test.client import Client
from forms import * 
from django import forms 
from django.contrib.auth.models import User
#fixtures = ['budgie.json']

#Testing URLS
class UrlsTests(unittest.TestCase):
	def test_home(self):
		client = Client()
		response = client.get('/budgie/')
		self.assertEqual(response.status_code, 200)

	def test_profile(self):
		client = Client()
		response = client.get('/budgie/profile')
		self.assertEqual(response.status_code, 302)

	def test_login(self):
		client = Client()
		response = client.get('/budgie/login')
		self.assertEqual(response.status_code, 200)
	
	def test_logout(self):
		client = Client()
		response = client.get('/budgie/logout')
		self.assertEqual(response.status_code, 302)

	def test_register(self):
		client = Client()
		response = client.get('/budgie/login')
		self.assertEqual(response.status_code, 200)

	def test_confirm_email(self):
		client = Client()
		response = client.get('/budgie/confirm/a@a.com/12345678')
		self.assertEqual(response.status_code, 301)

	def test_add_transaction(self):
		client = Client()
		response = client.get('/budgie/add_transaction')
		self.assertEqual(response.status_code, 302)

	def test_view_transactions(self):
		client = Client()
		response = client.get('/budgie/view_transaction')
		self.assertEqual(response.status_code, 302)

	def test_add_account(self):
		client = Client()
		response = client.get('/budgie/add_account')
		self.assertEqual(response.status_code, 302)

	def test_create_assets(self):
		client = Client()
		response = client.get('/budgie/create_assets')
		self.assertEqual(response.status_code, 302)

	def test_view_accounts(self):
		client = Client()
		response = client.get('/budgie/view_accounts')
		self.assertEqual(response.status_code, 302)

	def test_create_liability(self):
		client = Client()
		response = client.get('/budgie/create_liability')
		self.assertEqual(response.status_code, 302)

	def test_create_budget(self):
		client = Client()
		response = client.get('/budgie/create_budget')
		self.assertEqual(response.status_code, 302)
	
	def test_view_budget(self):
		client = Client()
		response = client.get('/budgie/view_budget')
		self.assertEqual(response.status_code, 302)

	def test_create_goal(self):
		client = Client()
		response = client.get('/budgie/create_goal')
		self.assertEqual(response.status_code, 302)

	def test_view_goals(self):
		client = Client()
		response = client.get('/budgie/view_goals')
		self.assertEqual(response.status_code, 302)

	def test_get_accounts(self):
		client = Client()
		response = client.get('/budgie/get_accounts/CHK')
		self.assertEqual(response.status_code, 301)

	def test_about(self):
		client = Client()
		response = client.get('/budgie/about')
		self.assertEqual(response.status_code, 200)

	def test_contact(self):
		client = Client()
		response = client.get('/budgie/contact')
		self.assertEqual(response.status_code, 200)


#Testing models
class ModelsTest(unittest.TestCase):
	def setUp(self):
		self.user1 = User.objects.create_user(username='user1', password='123', first_name='Susana', last_name='Lau')
		self.userprofile1 = UserProfile.objects.create(user=self.user1, verification_id='123')
		self.account = BaseAccount.objects.create(account_no='12345678', user=self.user1, name='MyCC', account_type='CC', 
									  bank='Bank A', balance=9000, status='open')
		self.transaction = Transaction.objects.create(user=self.user1, name="Food", description="Food", transaction_type="DR", 
													category="Food", amount=19.99, from_account=self.account)
		self.goal = Goal.objects.create(user=self.user1, name='Goal1', description='Goal1', expected_amount=90000, 
										account_no=self.account, date='2018-08-12')
		self.asset = Asset.objects.create(user=self.user1, name='House', asset_type='House', value=120000)
		self.liability = Liability.objects.create(user=self.user1, name='Loan', liability_type='Loan', amount=900, 
												from_date='2014-04-04', to_date='2014-05-04')
				
	def test_account(self):
		self.assertTrue(isinstance(self.account, BaseAccount))
		self.assertEqual(self.account.__unicode__(), self.account.account_no)
				
	def test_asset(self):
		self.assertTrue(isinstance(self.asset, Asset))
		self.assertEqual(self.asset.__unicode__(), self.asset.name)

	def test_liability(self):
		self.assertTrue(isinstance(self.liability, Liability))
		self.assertEqual(self.liability.__unicode__(), self.liability.name)

	def test_transaction(self):
		self.assertTrue(isinstance(self.transaction, Transaction))
		self.assertEqual(self.transaction.__unicode__(), self.transaction.name)

	def test_goal(self):
		self.assertTrue(isinstance(self.goal, Goal))
		self.assertEqual(self.goal.__unicode__(), self.goal.name)

	def tearDown(self):
		self.user1.delete()
		self.userprofile1.delete()
		self.account.delete()


#Testing forms
class FormsTests(TestCase):
	#def setUp(self):
	#	self.user1 = User.objects.create_user(username='user1', password='123', first_name='Susana', last_name='Lau')
	#	self.userprofile1 = UserProfile.objects.create(user=self.user1, verification_id='123')
	#	self.account = BaseAccount.objects.create(account_no='12345678', user=self.user1, name='MyCC', account_type='CC', 
	#								  bank='Bank A', balance=9000, status='open')   
	
	def test_valid_register_form(self):
		form = RegistrationForm(data={'username': 'abc@abc.com', 'first_name':'Name', 'last_name':'Last', 'password1':'123', 'password2':'123'})
		self.assertTrue(form.is_valid())


	def test_valid_account_form(self):
		form = BaseAccountForm(data={'account_no': '12345678', 'bank':'PNC', 'account_type':'CC', 'name':'MyAccount', 'balance':9000})
		self.assertTrue(form.is_valid())


	def test_valid_asset_form(self):
		form = AssetForm(data={'name': 'House', 'asset_type':'House', 'value':120000})
		self.assertTrue(form.is_valid())


	def test_valid_liability_form(self):
		form = LiabilityForm(data={'name': 'Loan', 'liability_type':'Loan', 'amount':120, 'from_date': '04/05/2014', 'to_date':'04/06/2014'})
		self.assertTrue(form.is_valid())


	def test_valid_budget_form(self):
		form = BudgetForm(data={'housing': 0 , 'transportation':0, 'food':0, 'health':0, 'education':0, 'entertainment':0, 'other':0})
		self.assertTrue(form.is_valid())

	#def test_valid_transaction_form(self):
	#	form = TransactionForm(data={'name':'Transaction1', 'description':'Transaction1', 'transaction_type':'Expense', 'from_account':str(self.account.account_no), 'category':'Housing', 'amount':90})
	#	self.assertTrue(form.is_valid())

	#def tearDown(self):
	#	self.user1.delete()
	#	self.userprofile1.delete()
	#	self.account.delete()


#class BaseTest(TestCase):
 
 #   def test_some_things(self):
 #       self.assertRedirects(response, expected_url, status_code, target_status_code)
 #       self.assertContains(response, text, count, status_code)
 #       self.assertNotContains(response, text, count, status_code)
 #       self.assertFormError(response, form, field, errors)
 #       self.assertTemplateUsed(response, template_name)
 #       self.assertTemplateNotUsed(response, template_name)
 #       self.assertQuerysetEqual(qs, values)