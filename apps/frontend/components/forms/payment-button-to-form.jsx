/**
 * v0 by Vercel.
 * @see https://v0.dev/t/xIQkjLY3hvQ
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import {CardElement, useStripe, useElements} from '@stripe/react-stripe-js';
import { useSession } from 'next-auth/react';

const options = {
  style: {
    base: {
      color: '#aab7c4',
      fontFamily: 'Arial, sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  }
}

export default function PaymentButtonToForm() {
  const { data: session, status } = useSession();
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!stripe || !elements) {
      return;
    }

    const cardElement = elements.getElement(CardElement);

    const {error, paymentMethod} = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
    });

    
    console.log('paymentMethod', paymentMethod.id)
    if (error) {
      console.log('[error]', error);
    } else {
      // Send the paymentMethod.id to your server
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/stripe/attach-payment-method`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`
        },
        body: JSON.stringify({
          paymentMethodId: paymentMethod.id,
        }),
      });

      if (response.ok) {
        console.log('Payment method attached to customer');
      } else {
        console.log('Failed to attach payment method');
      }
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Add Payment Method</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Payment Method</DialogTitle>
          <DialogDescription>Enter your payment details to complete the transaction.</DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <form onSubmit={handleSubmit}>
            {stripe && elements ? (
              <CardElement options={options} />
            ) : (
              <div>Loading...</div>
            )}
          </form>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleSubmit}>Complete Payment</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}