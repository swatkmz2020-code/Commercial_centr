from django.contrib import admin
from .models import (
    Contractor,
    PurchaseRequest,
    CommercialProposal,
    PriceAnalysis,
    BrowserProductSearch,
)


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("name", "inn", "supplier_type", "contact_person", "phone")
    search_fields = ("name", "inn")
    list_filter = ("supplier_type",)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "quantity", "unit", "required_date", "status")
    search_fields = ("number", "title", "article")
    list_filter = ("status",)


@admin.register(CommercialProposal)
class CommercialProposalAdmin(admin.ModelAdmin):
    list_display = ("purchase_request", "contractor", "price_per_unit", "total_price", "delivery_days", "is_selected")
    list_filter = ("is_selected", "vat_included")


@admin.register(PriceAnalysis)
class PriceAnalysisAdmin(admin.ModelAdmin):
    list_display = ("purchase_request", "selected_proposal", "min_price", "avg_price", "max_price", "analyzed_at")


@admin.register(BrowserProductSearch)
class BrowserProductSearchAdmin(admin.ModelAdmin):
    list_display = ("query_text", "found_title", "seller_name", "found_price", "in_stock", "searched_at")
    search_fields = ("query_text", "found_title", "seller_name")

