from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse 
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import DetailView

from .forms import CustomerCreationForm, CustomerEditForm, GarbageCollectorCreationForm, MyCompanyEditForm
from accounts.models import CustomUser


# Create your views here.

def sign_up(request):
   form = GarbageCollectorCreationForm()
   page = "sign_up"

   if request.method == 'POST':
      form = GarbageCollectorCreationForm(request.POST)

      if form.is_valid():
         my_user = form.save(commit=False)
         my_user.is_active = True
         my_user.save()
         form.save_m2m()

         my_user = CustomUser.active_objects.get(email=request.POST.get("email"))
         login(request, my_user)
         return HttpResponseRedirect(reverse("garbage:home_page"))
      messages.error(request, 'An error occurred during details entry, please check ')

   context = {
      "form": form,
      "page": page
   }

   return render(request, "accounts/signin_signup.html", context)

def user_sign_in(request):
   email = request.POST.get("email")
   password = request.POST.get("password")
   page = "sign_in"

   if request.method == "POST":
      try:
         user = CustomUser.active_objects.get(email=email)

      except:
         messages.error(request, "Email does not exist, you should sign up or try checking your e-mail")
         return render(request, "accounts/signin_signup.html", {"page": page})

      user = authenticate(email=email, password=password)

      if user is not None:
         login(request, user)

         return HttpResponseRedirect(reverse("garbage:home_page"))
      messages.error(request, "Invalid login details")
      return render(request, "accounts/signin_signup.html", {"page": page})
   
   elif request.method == "GET":
      return render(request, "accounts/signin_signup.html", {"page": page})
   

def user_sign_out(request):
   logout(request)
   # user_id = request.user.id
   return HttpResponseRedirect(reverse("garbage:home_page"))
# , kwargs={'pk': user_id}

@login_required(login_url="accounts:sign_in")
def user_update_details(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   user = CustomUser.active_objects.get(id=pk)
   form = MyCompanyEditForm(instance=user)
   page = "user_update_details"

   if request.method == "POST":
      form = MyCompanyEditForm(request.POST, request.FILES, instance=user)

      if form.is_valid():
         form.save()

         messages.success(request, "Profile updated Successfully !")
         return HttpResponseRedirect(reverse('garbage:home', args=[user.id]))

      else:
         # print(form.errors)
         messages.error(request, 'Invalid detail entered')
         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

   elif request.method == "GET":
      context = {
         "form": form,
         "page": page,
      }
      return render(request, "accounts/profile_forms.html", context)


@login_required(login_url="accounts:sign_in")
def change_password(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   form = PasswordChangeForm(request.user)
   page = "change_password"

   if request.method == "POST":
      form = PasswordChangeForm(request.user, request.POST)

      if form.is_valid():
         user = form.save()
         update_session_auth_hash(request, user)
         messages.success(request, "Password Changed Successfully")
         return HttpResponseRedirect(reverse("garbage:home_page", args=[pk]))
      else:
         messages.error(request, "please correct the error below")

   context = {"form": form,
            "page": page,
            }
   return render(request, "accounts/profile_forms.html", context)


def recover_password(request):
   if request.method == "POST":
      try:
         email = request.POST.get("email")
         user = CustomUser.active_objects.get(email=email)
         uid = urlsafe_base64_encode(force_bytes(user.id))
         token = default_token_generator.make_token(user)
         current_site = get_current_site(request)

         email_body = {
               'token': token,
               "subject": "Recover Password",
               'message': f"Hi, {user.username} , kindly reset your password by clicking "
                        f"the following link . http://{current_site}/account/reset_password/password-token/{uid}/{token} "
                        f"to change your password",
               "recepient": email,
         }
         # that send email func
         send_mail(
               email_body["subject"],
               email_body["message"],
               settings.EMAIL_HOST_USER,
               [email]

         )
         print(email_body["message"])
         messages.success(request, "A password reset mail has been sent to your mail")
         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
      except CustomUser.DoesNotExist or Exception as e:
         print(e)
         messages.error(request, "User does not exist")
         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

   context = {
      'page': "recover_password",
   }
   return render(request, "accounts/signin_signup.html", context)

def reset_password(request, uid, token):
   if request.method == "POST":
      try:
         id_decode = urlsafe_base64_decode(uid)
         user = CustomUser.active_objects.get(id=id_decode)

         if default_token_generator.check_token(user, token):
               password = request.POST.get("password1")
               confirm_password = request.POST.get("password1")

               if password == confirm_password:
                  user.set_password(password)
                  user.save()
                  messages.success(request, "password Recovered successfully")
                  return HttpResponseRedirect(reverse("garbage:home_page"))
               messages.error(request, "incorrect passwords")
               return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

         else:
               messages.error(request, "Invalid Token")
               return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
      except:
         messages.error(request, "Invalid link")
         return HttpResponseRedirect("accounts:sign_in")

   context = {
      'page': "reset_password",
      "uid": urlsafe_base64_decode(uid),
      "token": CustomUser.active_objects.get(id=urlsafe_base64_decode(uid)),

   }
   return render(request, "accounts/signin_signup.html", context)


# customer's sign_up sign_in and profile_update
def customer_sign_up(request):
   form = CustomerCreationForm()
   page = "customer_sign_up"

   if request.method == 'POST':
      form = CustomerCreationForm(request.POST)

      if form.is_valid():
         my_user = form.save(commit=False)
         my_user.is_active = True
         my_user.save()

         my_user = CustomUser.active_objects.get(email=request.POST.get("email"))
         login(request, my_user)
         return HttpResponseRedirect(reverse("garbage:home_page"))
      messages.error(request, 'An error occurred during details entry, please check ')

   context = {
      "form": form,
      "page": page
   }

   return render(request, "accounts/customer_signin_signup.html", context)

def customer_sign_in(request):
   email = request.POST.get("email")
   password = request.POST.get("password")
   page = "customer_sign_in"

   if request.method == "POST":
      try:
         user = CustomUser.active_objects.get(email=email)

      except:
         messages.error(request, "Email does not exist, you should sign up or try checking your e-mail")
         return render(request, "accounts/customer_signin_signup.html", {"page": page})

      user = authenticate(email=email, password=password)

      if user is not None:
         login(request, user)

         return HttpResponseRedirect(reverse("garbage:home_page"))
      messages.error(request, "Invalid login details")
      return render(request, "accounts/customer_signin_signup.html", {"page": page})
   
   elif request.method == "GET":
      return render(request, "accounts/customer_signin_signup.html", {"page": page})


@login_required(login_url="accounts:sign_in")
def customer_update_details(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   user = CustomUser.active_objects.get(id=pk)
   form = CustomerEditForm(instance=user)
   # page = "user_update_details"

   if request.method == "POST":
      form = CustomerEditForm(request.POST, request.FILES, instance=user)

      if form.is_valid():
         form.save()

         messages.success(request, "Profile updated Successfully !")
         return HttpResponseRedirect(reverse('garbage:home', args=[user.id]))

      else:
         # print(form.errors)
         messages.error(request, 'Invalid detail entered')
         return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

   elif request.method == "GET":
      context = {
         "form": form,
         # "page": page,
      }
      return render(request, "accounts/customer_profile_forms.html", context)
