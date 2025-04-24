from django.urls import path
from .views import home, portfolio_summary_page
from .apis import portfolio_summary
urlpatterns = [
    path('', home, name='home'),
    path('api/portfolio-summary/', portfolio_summary, name='portfolio-summary'),
    path('portfolio-summary/', portfolio_summary_page, name='portfolio-summary-page'),
]