from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomerLoginForm
from .models import Customer
import logging

logger = logging.getLogger(__name__)

class CustomerRegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful. Please log in.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors.')
        return super().form_invalid(form)

def user_login(request):
    print("Login view called")  # Debug print
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Debug print
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug print
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            print(f"Attempting to authenticate with phone: {phone_number}")  # Debug print
            
            # Try to authenticate the user
            user = authenticate(request, username=phone_number, password=password)
            print(f"Authentication result: {user}")  # Debug print
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    print(f"User logged in successfully: {user}")  # Debug print
                    messages.success(request, 'Login successful!')
                    try:
                        return redirect(reverse('shop:product_list'))
                    except Exception as e:
                        print(f"Error during redirect: {str(e)}")  # Debug print
                        # Fallback to a direct URL
                        return redirect('/')
                else:
                    print("User account is disabled")  # Debug print
                    messages.error(request, 'Your account is disabled.')
            else:
                print("Authentication failed")  # Debug print
                messages.error(request, 'Invalid phone number or password.')
        else:
            print(f"Form errors: {form.errors}")  # Debug print
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('registration:login')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html', {'user': request.user})
