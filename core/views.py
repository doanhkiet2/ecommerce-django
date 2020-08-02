from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Address
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
# Create your views here.

import stripe
import random
import string
from core.models import Refund, UserProfile
# stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
stripe.api_key = settings.STRIPE_SECRET_KEY
# stripe.api_key = settings.STRIPE_PUBLIC_KEY
# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
# charge = stripe.Charge.retrieve(
#   "ch_1H0QhL2eZvKYlo2CIL7eWmLJ",
#   api_key="sk_test_4eC39HqLyjWDarjtT1zdp7dc"
# )
# charge.save()


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = 'home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(order)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "you dont have an active order")
            # return redirect("/")
            return redirect(self.request.META.get('HTTP_REFERER'))



class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            print("tessssssssssssssst")
            order = Order.objects.get(user=self.request.user, ordered=False)
            print("tessssssssssssssst", order)
            # number of active order_item
            if not len(order.items.filter(pre_delete=False)):
                raise Exception("number of active order_item = 0 ")
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,

            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True,
            )

            if shipping_address_qs.exists():
                context.update({
                    'default_shipping_address': shipping_address_qs[0]
                })

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True,
            )

            if billing_address_qs.exists():
                context.update({
                    'default_billing_address': billing_address_qs[0]
                })

            return render(self.request, 'checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
            # return redirect("core:home")
            return redirect(self.request.META.get('HTTP_REFERER'))

        except Exception:
            # the page that called the current function.
            messages.warning(self.request, 'You have no active orderitem')
            # return redirect("core:home")
            return redirect(self.request.META.get('HTTP_REFERER'))


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                print(form.cleaned_data)

                # use default shipping
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True,
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "no default shipping address available")
                else:
                    print('user is entering a new shipping address')

                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zipcode = form.cleaned_data.get(
                        'shipping_zipcode')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zipcode]):
                        print("is valid form shipping_address")
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zipcode=shipping_zipcode,
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
                            self.request, "please fill in the required shipping address fields")

                # check same shipping address > use_default_billing
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')

                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                billing_address_qs = Address.objects.filter(
                    user=self.request.user,
                    address_type='B',
                    default=True,
                )

                print(shipping_address)
                if same_billing_address:
                    if not billing_address_qs.exists():
                        billing_address = shipping_address
                        billing_address.pk = None
                        billing_address.address_type = 'B'
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                elif use_default_billing:
                    print("using the default billing address")
                    if billing_address_qs.exists():
                        billing_address = billing_address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "no default billing address available")
                else:
                    print('user is entering a new billing address')

                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zipcode = form.cleaned_data.get('billing_zipcode')

                    if is_valid_form([billing_address1, billing_country, billing_zipcode]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zipcode=billing_zipcode,
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
                            self.request, "please fill in the required billing address fields")

            payment_option = form.cleaned_data.get('payment_option')
            # TODO: add redirect to the selected payment option
            if payment_option == 'S':
                return redirect('core:payment', payment_option='stripe')
            elif payment_option == 'P':
                return redirect('core:payment', payment_option='paypal')
            else:
                messages.info(
                    self.request, "Invalid payment option choice.")
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "you dont have an active order")
            return redirect("/")


class PaymentView(View):
    def get(self, *args, **kwargs):
        print("aaaaaaaaaaaa",self.request.META.get('HTTP_REFERER'))
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # number of active order_item
            if not len(order.items.filter(pre_delete=False)):
                raise Exception("number of active order_item = 0 ")
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
            return redirect(self.request.META.get('HTTP_REFERER'))
            # return redirect("core:home")
        except Exception:
            messages.warning(self.request, 'You have no active orderitem')
            return redirect(self.request.META.get('HTTP_REFERER'))
            # return redirect("core:home")

        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }

            userprofile = self.request.user.userprofile
            if userprofile.one_click_purcharsing:
                # flech the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card',
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "you have not add billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        print("token", token)
        print("request.post", self.request.POST)
        print("request.data", self.request)
        order = Order.objects.get(user=self.request.user, ordered=False)

        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purcharsing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            # https://stripe.com/docs/api/errors/handling
            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "your order was success")
                return redirect("/")

            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.info(self.request, 'Rate limit error')
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.info(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, 'Not authenticated')
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, 'Netword error')
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, 'some thing went wrong. You were not charge. Please try again')
                return redirect("/")

            except Exception as e:
                # Send an email to ourselves
                messages.info(
                    self.request, 'A serrios error occurred. We have been notifed')
                return redirect("/")


# need to know
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order_item in the order
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.pre_delete == True:
                order_item.pre_delete = False
                order_item.quantity = 0
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "this item quantity was update.")
            return redirect('core:order-summary')

        else:
            order.items.add(order_item)
            messages.info(request, "this item  was added to your cart.")
            return redirect('core:order-summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "this item  was added to your cart.")
        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order_item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "this item  was remove to your cart.")
            return redirect('core:product', slug=slug)
        else:
            messages.info(request, "this item  was not in your cart.")
            return redirect('core:product', slug=slug)
    else:
        return redirect('core:product', slug=slug)
        messages.info(request, "you dont have an active order.")


@login_required
def minus_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order_item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            if order_item.pre_delete == True:
                order_item.pre_delete = False
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                print("=0")
                # order.items.remove(order_item)
                # order_item.delete()
                order_item.pre_delete = True
                order_item.save()

            messages.info(request, "this item quantity was update.")
            return redirect('core:order-summary')
        else:
            messages.info(request, "this item  was not in your cart.")
            return redirect('core:order-summary')
    else:
        return redirect('core:order-summary')
        messages.info(request, "you dont have an active order.")


@login_required
def toggle_pre_delete_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order_item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            print(order_item.pre_delete)
            if order_item.pre_delete == True:
                order_item.pre_delete = False
            else:
                print("else")
                order_item.pre_delete = True
            order_item.save()
            return redirect('core:order-summary')

        else:
            messages.info(request, "this item  was not in your cart.")
            return redirect('core:order-summary')
    else:
        return redirect('core:order-summary')
        messages.info(request, "you dont have an active order.")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, 'this coupon does not exist')
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')
                    order = Order.objects.get(
                        user=self.request.user, ordered=False)
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    return redirect("core:checkout")

                except ObjectDoesNotExist:
                    messages.success(self.request, 'successfully add a coupon')
                    return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()
                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, 'your request was receive.')
                return redirect("core:request-refund")
            except ObjectDoesNotExist:
                messages.info(self.request, 'this order ref_code does not exist.')
                return redirect("core:request-refund")
