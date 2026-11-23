from django.shortcuts import render
from .models import PurchaseRequest, Contractor, CommercialProposal, PriceAnalysis


def index(request):
    """Главная страница (дашборд закупок)."""
    context = {
        'requests_count': PurchaseRequest.objects.count(),
        'contractors_count': Contractor.objects.count(),
        'proposals_count': CommercialProposal.objects.count(),
        'recent_requests': PurchaseRequest.objects.all()[:5],
    }
    return render(request, 'procurement/index.html', context)


def orders_list(request):
    """Раздел «Заказы» (заявки на закупку)."""
    requests = PurchaseRequest.objects.all()
    return render(request, 'procurement/orders.html', {'requests': requests})


def product_search(request):
    """Раздел «Поиск» (поиск товаров в браузере и по базе)."""
    return render(request, 'procurement/search.html')


def price_analysis(request):
    """Раздел «Анализ» (конкурентный лист и анализ цен)."""
    analyses = PriceAnalysis.objects.select_related('purchase_request', 'selected_proposal').all()
    return render(request, 'procurement/analysis.html', {'analyses': analyses})

