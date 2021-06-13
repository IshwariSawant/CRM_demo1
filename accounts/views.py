from django.core.files.base import ContentFile
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect
from django.forms import formsets, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import OrderForm,CreateUserForm
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

#-------------------(DETAIL/LIST VIEWS) -------------------#

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('login')
			

		context = {'form':form}
		return render(request, 'accounts/register.html', context)
		
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('dashboard')
			else:
				messages.info(request, 'Username OR password is incorrect')
				
		context = {}
		return render(request, 'accounts/login.html', context)

@login_required(login_url='login')
def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def dashboard(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = Order.objects.all().count()
	delivered = Order.objects.filter(status='Delivered').count()
	pending = Order.objects.filter(status='Pending').count()



	context = {'customers':customers, 'orders':orders ,
	'total_customers':total_customers,'total_orders':total_orders, 
	'delivered':delivered, 'pending':pending}
	return render(request, 'accounts/dashBoard.html',context)

@login_required(login_url='login')
def products(request):
	products = Product.objects.all()
	context = {'products':products}
	return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
def customer(request,pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.all()
	total_orders = orders.count()
	
	myFilter = OrderFilter(request.GET , queryset=orders)
	order = myFilter.qs

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders ,'myFilter':myFilter}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
def createOrder(request,pk):
	OrderFormSet = inlineformset_factory(Customer,Order, fields=('products','status'),extra=8)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST,instance=customer)
		if formsets.is_valid():
			formsets.save()
			return redirect('/')

	context = {'formset':formset }
	return render(request, 'accounts/order_form.html' , context)


@login_required(login_url='login')
def updateOrder(request,pk):

	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST , instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')


	context = {'form':form}	
	return render(request, 'accounts/order_form.html' , context)

@login_required(login_url='login')
def deleteOrder(request,pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')

	context = {'item':order}
	return render(request, 'accounts/delete.html', context )