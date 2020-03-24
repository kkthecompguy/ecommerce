from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund
from .forms import CheckoutForm, CouponForm, RefundForm, RegisterForm
from .filters import ItemFilter

import stripe
import random
import string
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


class RegisterView(View):
    def get(self, *args, **kwargs):
        form = RegisterForm()
        context = {
            'form': form
        }
        return render(self.request, 'core/register.html', context)

    def post(self, *args, **kwargs):
        form = RegisterForm(self.request.POST or None)
        if form.is_valid():
            user = form.save()
            return redirect('account_login')
        else:
            messages.warning(self.request, 'The two passwords did not match')
            return redirect('core:register')


def logout_view(request):
    logout(request)
    return redirect('account_login')


class HomeView(ListView):
    model = Item
    paginate_by = 10
    filter_set = ItemFilter
    template_name = 'core/home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': order}
            return render(self.request, 'core/order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an  active order')
            return redirect('core:index')


def product(request, pk):
    item = Item.objects.get(pk=pk)
    extra_items = Item.objects.all()[3:5]
    context = {
        'item': item,
        'extra_items': extra_items
    }
    return render(request, 'core/product-page.html', context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True,
                'order': order
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, 'core/checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, 'You do not have an active order')
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, 'No default shipping address available')
                        return redirect('core:checkout')
                else:
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apparment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, 'Please fill in the required fields')

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print('Using the default billing address')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, 'No default billing address available')
                        return redirect('core:checkout')
                else:
                    print('User is entering a new billing address')
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apparment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, 'Please fill in the required fields')

                payment_option = form.cleaned_data.get('payment_option')
                # redirect to selected payment method
                if payment_option == 'S':
                    return redirect("core:payment", payment_option="stripe")
                elif payment_option == 'P':
                    return redirect("core:payment", payment_option="paypal")
                else:
                    messages.warning(self.request, 'Invalid Payment Method')
                    return redirect("core:checkout")
            else:
                message.error(self.request, 'Please correct the errors below')
                return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('core:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, 'core/payment.html', context)
        else:
            messages.warning(
                self.request, 'You have not added a billing address')
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')

        amount = int(order.get_total() * 100)
        try:

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )

            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # update all order to True
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            # assign payment to order
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, 'Your purchase was successful!')
            return redirect('core:index')

        except stripe.error.CardError as e:
            body == e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{e.error.message}")
            return redirect('core:index')
        except stripe.error.RateLimitError as e:
            messages.warning(self.request, 'Rate Limit Error')
            return redirect('core:index')
        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, 'InvalidRequest Error')
            return redirect('core:index')
        except stripe.error.AuthenticationError as e:
            messages.warning(self.request, 'Authentication Error')
            return redirect('core:index')
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request, 'Network Error')
            return redirect('core:index')
        except stripe.error.StripeError as e:
            messages.warning(
                self.request, 'Something went wrong. You were not charged. Please try again')
            return redirect('core:index')
        except Exception as e:
            messages.warning(
                self.request, 'A serious error occured. We have been notified')
            return redirect('core:index')


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated.')
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, 'This item was added to your cart.')
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart.')
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        # check if the order item is in the order
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            print(order_item)
            order.items.remove(order_item)
            messages.info(request, 'This item was removed from your cart.')
            return redirect("core:order-summary")
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect("core:product", pk=pk)
    else:
        messages.info(request, 'You do not have an active order')
        return redirect("core:product", pk=pk)


@login_required
def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        # check if the order item is in the order
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, 'This item quantity was updated.')
            return redirect("core:order-summary")
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect("core:product", pk=pk)
    else:
        messages.info(request, 'You do not have an active order')
        return redirect("core:product", pk=pk)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, 'This coupon does not exist')
        return redirect('core:checkout')


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, 'Successfully added coupon')
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(request, 'You do not have an active order')
                return redirect("core:checkout")


class RequestFundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'core/request-refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.email = email
                refund.reason = message
                refund.save()

                messages.info(self.request, 'Your request was recieved.')
                return redirect('core:request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, 'Sorry that order does not exist')
                return redirect('core:request-refund')
