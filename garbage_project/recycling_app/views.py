from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RecyclingCompanyForm


def recycling_company_signup(request):
    if request.method == 'POST':
        form = RecyclingCompanyForm(request.POST)
        if form.is_valid():
            recycling_company = form.save(commit=False)
            recycling_company.save()
            recycling_company.recycler_location.set(form.cleaned_data['recycler_location'])
            form.save_m2m()

            login(request, recycling_company.user) 
            return redirect('recyclingcompany_dashboard')

    else:
        form = RecyclingCompanyForm()

    return render(request, 'recyclingcompany_signup.html', {'form': form})
