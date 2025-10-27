import os
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from django.db import transaction
from django.core.exceptions import ValidationError

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 

        role_permissions, _ = RolePermissions.objects.get_or_create(role=self)

        if self.name.lower() == "admin":
            for field in RolePermissions._meta.fields:
                if isinstance(field, models.BooleanField):
                    setattr(role_permissions, field.name, True)
        else:
            role_permissions.dashboard_v = True
            role_permissions.accounts_v = True
            role_permissions.customer_v = True
            role_permissions.customer_a = True
            role_permissions.orders_v = True
            role_permissions.orders_a = True

        role_permissions.save()

    def __str__(self):
        return f"{self.name}"


class RolePermissions(models.Model):  
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')

    dashboard_v = models.BooleanField(default=False)

    accounts_v = models.BooleanField(default=False)
    accounts_a = models.BooleanField(default=False)
    accounts_e = models.BooleanField(default=False)
    accounts_d = models.BooleanField(default=False)

    roles_v = models.BooleanField(default=False)
    roles_a = models.BooleanField(default=False)
    roles_e = models.BooleanField(default=False)
    roles_d = models.BooleanField(default=False)
    
    users_v = models.BooleanField(default=False)
    users_a = models.BooleanField(default=False)
    users_e = models.BooleanField(default=False)
    users_d = models.BooleanField(default=False)

    customer_v = models.BooleanField(default=False)
    customer_a = models.BooleanField(default=False)
    customer_e = models.BooleanField(default=False)
    customer_d = models.BooleanField(default=False)

    products_v = models.BooleanField(default=False)
    products_a = models.BooleanField(default=False)
    products_e = models.BooleanField(default=False)
    products_d = models.BooleanField(default=False)

    category_v = models.BooleanField(default=False)
    category_a = models.BooleanField(default=False)
    category_e = models.BooleanField(default=False)
    category_d = models.BooleanField(default=False)

    all_products_v = models.BooleanField(default=False)
    all_products_a = models.BooleanField(default=False)
    all_products_e = models.BooleanField(default=False)
    all_products_d = models.BooleanField(default=False)

    daily_production_v = models.BooleanField(default=False)
    daily_production_a = models.BooleanField(default=False)
    daily_production_e = models.BooleanField(default=False)
    daily_production_d = models.BooleanField(default=False)

    inventory_v = models.BooleanField(default=False)
    inventory_a = models.BooleanField(default=False)
    inventory_e = models.BooleanField(default=False)
    inventory_d = models.BooleanField(default=False)

    orders_v = models.BooleanField(default=False)
    orders_a = models.BooleanField(default=False)
    orders_e = models.BooleanField(default=False)
    orders_d = models.BooleanField(default=False)

    reports_v = models.BooleanField(default=False)
    s_reports_v = models.BooleanField(default=False)
    c_reports_v = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.role.name}"
    

class User(models.Model):
    role = models.ForeignKey(Role,on_delete=models.SET_NULL, null=True, related_name="role")
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255,null=True, blank=True)
    state = models.CharField(max_length=255,null=True, blank=True)
    pincode = models.CharField(max_length=10,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.role}"

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customers')
    customer_name = models.CharField(max_length=255,null=True,blank=True)
    full_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(unique=True, null=True,blank=True)
    phone_number = models.CharField(unique=True, max_length=50, null=True,blank=True)
    shop_type = models.CharField(
        max_length=50,
        choices=[
            ('NMT', 'National Modern Trade'),
            ('MT', 'Modern Trade'),
            ('SMT', 'Semi Modern Trade'),
            ('SPECIAL', 'Speciality Store'),
            ('GT', 'General Trade'),
        ],
        blank=True, null=True
    )
    gst_number = models.CharField(max_length=100,null=True,blank=True)
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    shop_city = models.CharField(max_length=255)
    shop_district = models.CharField(max_length=255)
    shop_pincode = models.CharField(max_length=50)
    shop_state = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=True)
    is_gst_registered = models.BooleanField(default=False, help_text="Is the customer GST registered?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    weekday_footfall = models.PositiveIntegerField(help_text="Average number of visitors during weekdays",null=True,blank=True)
    weekend_footfall = models.PositiveIntegerField(help_text="Average number of visitors during weekends",null=True,blank=True)
    credit_period = models.CharField(max_length=100,help_text="Credit period in No of Days", null=True, blank=True)
    nature_of_business = models.TextField(blank=True, null=True)  
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.shop_name} ({self.full_name})"
    


def shop_image_upload_path(instance, filename):
    return os.path.join(str(instance.customer.id),  filename)

class CustomerShopImage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shop_images')
    image = models.ImageField(upload_to=shop_image_upload_path)
    description = models.CharField(max_length=255, blank=True, null=True)  # optional: e.g., "Front view", etc.

    def __str__(self):
        return f"{self.customer.full_name} ({self.customer.shop_name})"
    
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('COMPONENT', 'Component'),
        ('OLD LAPTOP', 'Old Laptop'),
        ('REFURBISHED', 'Refurbished Laptop'),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='REFURBISHED',
        help_text="Defines whether this is a component, old laptop, or refurbished laptop"
    )

    unit = models.CharField(
        max_length=50,
        choices=[('Pieces', 'Pieces')],
        default='Pieces'
    )
    description = models.TextField(blank=True)
    hsn_code = models.CharField(max_length=20, blank=True, null=True)
    gstpercentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    brand_name = models.CharField(
        max_length=50,
        choices=[
            ('Dell', 'Dell'),
            ('Lenovo', 'Lenovo'),
            ('HP', 'HP'),
            ('Apple', 'Apple'),
            ('Asus', 'Asus'),
            ('Acer', 'Acer'),
            ('Other', 'Other'),
        ],
        blank=True, null=True
    )

    model_name = models.CharField(max_length=100, blank=True, null=True)
    product_picture = models.ImageField(upload_to='product_images/', null=True, blank=True)

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost price or component purchase rate")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Selling price or MRP for refurbished units")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.product_type})"

    

class PurchaseOrder(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="purchase_orders")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    is_received = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"PO-{self.id} ({self.vendor.name})"

class PurchaseItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
class Component(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, default='Pieces')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    

class RefurbishedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="refurbished_batches")
    serial_number = models.CharField(max_length=100, unique=True)
    production_date = models.DateField(default=timezone.now)
    produced_quantity = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product.name} - SN: {self.serial_number}"

class ComponentUsage(models.Model):
    refurbished_product = models.ForeignKey(RefurbishedProduct, on_delete=models.CASCADE, related_name="components_used")
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # Deduct used components from stock
        if self.component.stock_quantity < self.quantity_used:
            raise ValidationError(f"Not enough stock for {self.component.name}")
        self.component.stock_quantity -= self.quantity_used
        self.component.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.component.name} x {self.quantity_used} → {self.refurbished_product.serial_number}"
   

class DailyProduction(models.Model):
    refurbished_product = models.ForeignKey(RefurbishedProduct, on_delete=models.CASCADE, related_name='daily_productions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    refurbished_date = models.DateField(default=timezone.now)
    stock_in = models.PositiveIntegerField(default=0)
    stock_out = models.PositiveIntegerField(default=0)
    current_stock = models.IntegerField(default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    serial_number = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.current_stock = self.stock_in - self.stock_out
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.serial_number or self.refurbished_product.serial_number})"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    opening_stock = models.PositiveIntegerField(default=0)
    stock_in = models.PositiveIntegerField(default=0)
    stock_out = models.PositiveIntegerField(default=0)
    current_stock = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.current_stock}"

    def update_stock(self):
        self.current_stock = self.opening_stock + self.stock_in - self.stock_out
        self.save()


class SalesOrder(models.Model):
    ORDER_TYPE_CHOICES = [
        ('telephone', 'Telephone'),
        ('location', 'Location'),
        ('email', 'Email'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
    order_date = models.DateTimeField(auto_now_add=True)

    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='telephone')

    # 🔹 Frontend terminology fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=50, choices=DELIVERY_STATUS_CHOICES, default='processing')

    def update_payment_status(self):
        self.total_paid = sum(t.amount_paid for t in self.transactions.all())
        self.balance_due = self.grand_total - self.total_paid

        if self.total_paid == 0:
            self.payment_status = 'pending'
        elif self.total_paid < self.grand_total:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'paid'

        self.save(update_fields=['total_paid', 'balance_due', 'payment_status'])

    def __str__(self):
        return f"Order #{self.id} - {self.customer.shop_name}"




class SaleItem(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)





class VoucherNumber(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Payment Voucher"
    prefix = models.CharField(max_length=10)              # e.g., "PAY"
    start_from = models.PositiveIntegerField(default=1)
    current_number = models.PositiveIntegerField(default=0)  # Auto-incremented

    def get_next_voucher(self):
        self.current_number += 1
        self.save(update_fields=['current_number'])
        return f"{self.prefix}{str(self.current_number).zfill(4)}"  # e.g., PAY0001

    def __str__(self):
        return f"{self.name} ({self.prefix})"

class PaymentTransaction(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='transactions')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('upi', 'UPI'),
            ('bank_transfer', 'Bank Transfer'),
            ('cheque', 'Cheque'),
            ('other', 'Other')
        ]
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount_paid}"
    

class Invoice(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            super().save(*args, **kwargs)  # Save first to get ID
            self.invoice_number = f"INV{self.id:03d}-ORD{self.order.id}"
            return super().save(update_fields=['invoice_number'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number}"




class Ledger(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='ledger_entries')
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.customer.full_name} - {self.date.date()}"

    def save(self, *args, **kwargs):
        last_entry = Ledger.objects.filter(customer=self.customer).order_by('-date').first()
        previous_balance = last_entry.balance if last_entry else 0
        self.balance = previous_balance + self.credit - self.debit
        super().save(*args, **kwargs)

from django.db import models
from django.utils import timezone
from datetime import timedelta

class Attendance(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="attendances")
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    working_hours = models.DurationField(null=True, blank=True)  # store time difference

    def save(self, *args, **kwargs):
        # ✅ Auto-calculate working hours if check_out exists
        if self.check_in and self.check_out:
            self.working_hours = self.check_out - self.check_in
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.working_hours or 'Not calculated'})"

from django.db import models
from django.utils import timezone

class GspToken(models.Model):
    access_token = models.TextField()
    token_type = models.CharField(max_length=30, default="Bearer")
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    gspappid = models.CharField(max_length=100)
    gspappsecret = models.CharField(max_length=100)

    class Meta:
        ordering = ["-created_at"]  # always latest first

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at



class SalesmanVisit(models.Model):
    salesman = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)

    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_address = models.CharField(max_length=255, blank=True, null=True)
    
    visit_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.salesman.username} - {self.customer} ({self.check_in_time})"