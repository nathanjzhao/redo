import stripe
from stripe.error import CardError, StripeError

def stripe_charge(amount, payment_details):
    try:
        # Create a PaymentIntent or charge the user's card
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"],
            payment_method_data={
                "card": {
                    "number": payment_details.card_number,
                    "exp_month": payment_details.exp_month,
                    "exp_year": payment_details.exp_year,
                    "cvc": payment_details.cvc,
                },
            },
            confirm=True,
        )
    except (CardError, StripeError) as e:
        raise e