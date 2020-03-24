from django.conf import settings
from django.db.models.signals import post_save
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S', 'Mens Shirt'),
    ('WA', 'Women Dress'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
    ('E', 'Electronics'),
    ('C', 'Computing devices'),
    ('N', 'Network devices'),
    ('F', 'Furniture'),
    ('FB', 'Food and Beverages'),
    ('U', 'Utensils'),
    ('P', 'Phones'),
    ('SH', 'Shoes'),
    ('BB', 'Baby Care'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

ADDRESS_CHOICES = (
    ('S', 'Shipping'),
    ('B', 'Billing'),
)


# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
#     on_click_purchasing = models.BooleanField(default=False)

#     def __str__(self):
#         return self.user.username


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(
        blank=True, null=True, max_digits=5, decimal_places=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField(max_length=1000, null=True, blank=True)
    additional_info = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'pk': self.pk
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={'pk': self.pk})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={'pk': self.pk})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        else:
            return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, null=True, blank=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apparment_address = models.CharField(max_length=100, null=True)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=50)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES
                                    )
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    email = models.EmailField()
    reason = models.TextField()
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk}"


# def userprofile_reciever(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)


# post_save.connect(userprofile_reciever, sender=settings.AUTH_USER_MODEL)
