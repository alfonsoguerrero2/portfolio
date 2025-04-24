from django.shortcuts import render
from .models import Portfolio

def home(request):
    portfolios = Portfolio.objects.prefetch_related('holdings__asset')
    return render(request, 'home.html', {'portfolios': portfolios})

def portfolio_summary_page(request):
    return render(request, 'portfolio_summary.html')