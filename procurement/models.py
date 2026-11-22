from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Contractor(models.Model):
    """Контрагенты (поставщики)."""
    class SupplierType(models.TextChoices):
        MANUFACTURER = "manufacturer", "Производитель"
        DISTRIBUTOR = "distributor", "Дистрибьютор"
        DEALER = "dealer", "Дилер"

    name = models.CharField(max_length=255, verbose_name="Наименование")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    supplier_type = models.CharField(
        max_length=20,
        choices=SupplierType.choices,
        default=SupplierType.DEALER,
        verbose_name="Тип поставщика"
    )
    contact_person = models.CharField(max_length=255, blank=True, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"


class PurchaseRequest(models.Model):
    """Заявка на закупку ПКИ/материалов."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SEARCH = "search", "Поиск предложений"
        ANALYSIS = "analysis", "Анализ цен"
        APPROVED = "approved", "Согласована"
        COMPLETED = "completed", "Завершена"

    number = models.CharField(max_length=50, unique=True, verbose_name="Номер заявки")
    title = models.CharField(max_length=255, verbose_name="Наименование ПКИ / материала")
    article = models.CharField(max_length=100, blank=True, verbose_name="Артикул / ГОСТ / ТУ")
    description = models.TextField(blank=True, verbose_name="Технические характеристики")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Количество")
    unit = models.CharField(max_length=20, default="шт.", verbose_name="Ед. измерения")
    required_date = models.DateField(verbose_name="Требуемый срок поставки")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус заявки"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchase_requests",
        verbose_name="Инициатор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заявка на закупку"
        verbose_name_plural = "Заявки на закупку"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка №{self.number} — {self.title}"


class CommercialProposal(models.Model):
    """Коммерческое предложение (КП) от контрагента по заявке."""
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="proposals",
        verbose_name="Заявка на закупку"
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        related_name="proposals",
        verbose_name="Контрагент"
    )
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена за единицу")
    total_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Общая стоимость")
    vat_included = models.BooleanField(default=True, verbose_name="Включая НДС")
    delivery_days = models.PositiveIntegerField(verbose_name="Срок поставки (дней)")
    document = models.FileField(upload_to="proposals/%Y/%m/", blank=True, null=True, verbose_name="Файл КП (PDF/Excel)")
    is_selected = models.BooleanField(default=False, verbose_name="Выбрано победителем")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения КП")

    class Meta:
        verbose_name = "Коммерческое предложение"
        verbose_name_plural = "Коммерческие предложения"
        unique_together = ("purchase_request", "contractor")
        ordering = ["price_per_unit"]

    def __str__(self):
        return f"КП от {self.contractor.name} по заявке №{self.purchase_request.number}"


class PriceAnalysis(models.Model):
    """Анализ по цене товара (конкурентный лист)."""
    purchase_request = models.OneToOneField(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="price_analysis",
        verbose_name="Заявка на закупку"
    )
    selected_proposal = models.ForeignKey(
        CommercialProposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Выбранное КП"
    )
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Минимальная цена")
    avg_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Средняя цена")
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Максимальная цена")
    justification = models.TextField(blank=True, verbose_name="Обоснование выбора")
    analyzed_at = models.DateTimeField(auto_now=True, verbose_name="Дата анализа")

    class Meta:
        verbose_name = "Анализ цены"
        verbose_name_plural = "Анализы цен"

    def __str__(self):
        return f"Анализ цен по заявке №{self.purchase_request.number}"


class BrowserProductSearch(models.Model):
    """Отдельная таблица для результатов поиска товара в браузере."""
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="browser_searches",
        null=True,
        blank=True,
        verbose_name="Связанная заявка"
    )
    query_text = models.CharField(max_length=255, verbose_name="Поисковый запрос")
    found_title = models.CharField(max_length=255, verbose_name="Найденное наименование")
    source_url = models.URLField(max_length=500, verbose_name="Ссылка на страницу товара")
    seller_name = models.CharField(max_length=255, blank=True, verbose_name="Сайт / Продавец")
    found_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Найденная цена")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата поиска")

    class Meta:
        verbose_name = "Поиск товара в браузере"
        verbose_name_plural = "Поиски товаров в браузере"
        ordering = ["-searched_at"]

    def __str__(self):
        return f"{self.query_text} — {self.seller_name or self.source_url}"



