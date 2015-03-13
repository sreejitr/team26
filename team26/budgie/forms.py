from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from models import * 
from budgie.models import * 
from django.forms import ModelForm
#import settings for constants
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
 
class LoginForm(forms.Form):
	username = forms.EmailField(max_length=64,
    							label="Email",
    							widget=forms.TextInput(attrs={'class' : 'form-control',
    														  'placeholder': 'Email',
    														   'autofocus': 'autofocus'}))
	password = forms.CharField(max_length = 200,
								label = 'Password',
								widget = forms.PasswordInput(attrs={'class' : 'form-control', 
																	'placeholder': 'Password'}))
	def clean(self):
		cleaned_data = super(LoginForm, self).clean()

		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		
		user_login = authenticate(username=username, password=password)

		if user_login is not None and user_login.is_active==False:
			raise forms.ValidationError("User is inactive. Please validate email first")	
		
		if user_login is None:
			raise forms.ValidationError("Invalid username/password")
	
		return cleaned_data

class RegistrationForm(forms.Form):
	username = forms.EmailField(max_length=64,
    							label="Email",
    							widget=forms.TextInput(attrs={'class' : 'form-control',
    														 'autofocus': 'autofocus'}))
	first_name = forms.CharField(max_length=100,
								 label="First Name",
								 widget=forms.TextInput(attrs={'class' : 'form-control'}))
	last_name = forms.CharField(max_length=100,
								label="Last Name",
								widget=forms.TextInput(attrs={'class' : 'form-control'}))
	password1 = forms.CharField(max_length = 200,
								label = 'Password',
								widget = forms.PasswordInput(attrs={'class' : 'form-control'}))
	password2 = forms.CharField(max_length = 200,
								label = 'Confirm Password',
								widget = forms.PasswordInput(attrs={'class' : 'form-control'}))
						
	def clean(self):
		cleaned_data = super(RegistrationForm, self).clean()

		password1 = cleaned_data.get('password1')
		password2 =  cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")
		return cleaned_data

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken")
		return username

class TransactionForm(forms.ModelForm):

	name = forms.CharField(max_length=50,
    							label='Name',
    							widget=forms.TextInput(attrs={'class' : 'form-control',
    														 'autofocus': 'autofocus'}))
	description = forms.CharField(max_length=60,
								 label="Description",
								 widget=forms.TextInput(attrs={'class' : 'form-control'}))

	transaction_type = forms.ChoiceField(required=True,
        										 widget=forms.Select(attrs={'class' : 'form-control'}), 
        										 choices=settings.TYPE_TRANSACTION_CHOICES)

	category = forms.ChoiceField(required=True,
        										 widget=forms.Select(attrs={'class' : 'form-control'}),
        										 choices=settings.CATEGORY_CHOICES)

	amount = forms.DecimalField(max_digits=15,
								decimal_places=2,
    							label="Amount",
    							widget=forms.TextInput(attrs={'class' : 'form-control'}))

	#from_account = forms.ModelChoiceField(queryset=BaseAccount.objects.all(),
	#									  required=False,
	#									  label="From Account:",
    #   								  widget=forms.Select(attrs={'class' : 'form-control'}),)

	#to_account = forms.ModelChoiceField(queryset=BaseAccount.objects.all(), required=False,
	#								label="To Account:",
    #    										 widget=forms.Select(attrs={'class' : 'form-control'}),)
	
	class Meta:
		model = Transaction
		exclude = ('user', 'date', 'account_no', 'frm_acc_end_bal', 'to_acc_end_bal')
		
	def clean(self):
		cleaned_data = super(TransactionForm, self).clean()
		return cleaned_data

class ViewTransactionForm(forms.Form):
	account_type = forms.ChoiceField(required=True,
        							widget=forms.Select(attrs={'class' : 'form-control'}), 
        							choices=settings.VIEW_TRANSACTION_ACCOUNT_CHOICES )
	
	account_numbers = forms.ChoiceField(required=True,
        							widget=forms.Select(attrs={'class' : 'form-control'}), 
        							choices='')

	
	time_options = 	forms.ChoiceField(required=True,
        							widget=forms.Select(attrs={'class' : 'form-control'}), 
        							choices=settings.VIEW_TRANSACTION_TIME_CHOICES)

	def __init__(self, *args, **kwargs):
	    super(ViewTransactionForm, self).__init__(*args, **kwargs)
	    self.fields.keyOrder = [
	    	'account_type',
	        'account_numbers',
	        'time_options',]

	def clean(self):
		cleaned_data = super(ViewTransactionForm, self).clean()
		return cleaned_data
		
class BaseAccountForm(forms.ModelForm):
	account_no = forms.CharField(required=True,
									label="Account Number",
        							widget=forms.TextInput(attrs={'class' : 'form-control',
    														 'autofocus': 'autofocus'}),
        							)

	bank = forms.CharField(max_length=60,
							label="Bank",
							widget=forms.TextInput(attrs={'class' : 'form-control'}))

	account_type = forms.ChoiceField(required=True,
        							widget=forms.Select(attrs={'class' : 'form-control'}), 
        							choices=settings.ACCOUNT_TYPE_CHOICES)

	name = forms.CharField(max_length=50,
    							label='Account Name',
    							widget=forms.TextInput(attrs={'class' : 'form-control'}))

	balance = forms.DecimalField(max_digits=15,
								decimal_places=2,
    							label="Balance",
    							widget=forms.TextInput(attrs={'class' : 'form-control'}))

		
	class Meta:
		model = BaseAccount
		exclude = ('user', 'status')
		
	def clean(self):
		cleaned_data = super(BaseAccountForm, self).clean()
		return cleaned_data


class AssetForm(forms.ModelForm):
	name = forms.CharField(max_length=50,
    							label='Name',
    							widget=forms.TextInput(attrs={'class' : 'form-control',
    								'autofocus': 'autofocus'}))

	asset_type = forms.CharField(max_length=20,
			label='Asset type',
			widget=forms.TextInput(attrs={'class':'form-control'})
		)

	value = forms.DecimalField(max_digits=15,
							decimal_places=2,
    						label="Value of Asset",
    						widget=forms.TextInput(attrs={'class' : 'form-control'}))	

	class Meta:
		model = Asset
		exclude = ('user', 'status')

	def clean(self):
		cleaned_data = super(AssetForm, self).clean()
		return cleaned_data


class LiabilityForm(forms.ModelForm):
	name = forms.CharField(max_length=50,
    						label='Name',
    						widget=forms.TextInput(attrs={'class' : 'form-control',
    							'autofocus': 'autofocus'}))

	liability_type = forms.CharField(max_length=20,
		label='Liability type',
		widget=forms.TextInput(attrs={'class':'form-control'})
		)

	amount = forms.DecimalField(label='Amount', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)

	from_date = forms.DateField(label='From Date',
		#widget = forms.extras.widgets.SelectDateWidget(attrs={'class' : 'form-control'})		
		widget=forms.TextInput(attrs={'class' : 'form-control', 'id':'from_date'})
		)

	to_date = forms.DateField(label='To Date',
		#widget = forms.extras.widgets.SelectDateWidget(attrs={'class' : 'form-control'})
		widget=forms.TextInput(attrs={'class' : 'form-control', 'id':'to_date'})
		)

	class Meta:
		model = Liability
		exclude = ('user', 'status')

	def clean(self):
		cleaned_data = super(LiabilityForm, self).clean()
		return cleaned_data


class BudgetForm(forms.ModelForm):
	housing = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Housing', 
						widget=forms.TextInput(attrs={'class' : 'form-control', 'autofocus': 'autofocus'},)
						)
	transportation = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Transportation', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)

	food = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Food', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)

	education = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Educatiom', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)
	
	health = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Health',
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)
	entertainment = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Entertainment', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)

	other = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Others', 
						widget=forms.TextInput(attrs={'class' : 'form-control'})
						)

	class Meta:
		model = Budget
		exclude = ('name', 'description', 'salary', 'gift', 'user', 'actual_amount_spent', 'year', 'month')

class GoalForm(forms.ModelForm):
	#def __init__(self, *args, **kwargs):
	#	user = kwargs.pop('user', None)

	#	if user:
	#		accounts = BaseAccount.objects.filter(user=user)
	#		choices = []
        
    #    	for i in range(len(accounts)):
    #    		choices.append([i,accounts[i].account_no])

    #		self.fields['account_no'].choices = choices

	name = forms.CharField(max_length=50,
    						label='Name',
    						widget=forms.TextInput(attrs={'class' : 'form-control',
    							'autofocus': 'autofocus'}))

	description = forms.CharField(max_length=60,
    						label='Description',
    						widget=forms.TextInput(attrs={'class' : 'form-control'}))

	expected_amount = forms.DecimalField(max_digits=15,
						decimal_places=2,
						label='Expected Amount', 
						widget=forms.TextInput(attrs={'class' : 'form-control'}))
	

	#account_number = forms.ChoiceField(required=True,
    #    							widget=forms.Select(attrs={'class' : 'form-control'}), 
    #    							choices='')


	date = forms.DateField(label='Achievement Date',
				widget=forms.TextInput(attrs={'class' : 'form-control', 'id':'from_date'}))

	class Meta:
		model = Goal
		exclude = ('user',)

	def clean(self):
		cleaned_data = super(GoalForm, self).clean()
		return cleaned_data
