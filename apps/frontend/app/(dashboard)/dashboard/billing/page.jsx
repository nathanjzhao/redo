'use client';
import { Heading } from '@/components/ui/heading';
import { Separator } from '@/components/ui/separator';
import BreadCrumb from '@/components/breadcrumb';
import PaymentButtonToForm from '@/components/forms/payment-button-to-form';
import {Elements} from '@stripe/react-stripe-js';
import {loadStripe} from '@stripe/stripe-js';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';

// Make sure to call `loadStripe` outside of a component’s render to avoid
// recreating the `Stripe` object on every render.
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY);

const breadcrumbItems = [{ title: 'Billing', link: '/dashboard/billing' }];

export default function page() {
  const { data: session } = useSession();

  const options = {
    // passing the client secret obtained from the server
    clientSecret: process.env.STRIPE_CLIENT_SECRET,
  };


  const [paymentMethods, setPaymentMethods] = useState([]);

  useEffect(() => {
    // Fetch the payment methods when the component mounts
    const fetchPaymentMethods = async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/stripe/get-payment-methods`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`
        },
        body: JSON.stringify({
          nodeId: session.nodeId
        }),
      });


      if (response.ok) {
        const data = await response.json();
        setPaymentMethods(data.payment_methods);
      } else {
        console.log('Failed to fetch payment methods');
      }
    };

    fetchPaymentMethods();
  }, []);

  return (
    <>
      <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
        <BreadCrumb items={breadcrumbItems} />
          <div className="flex items-start justify-between">
            <Heading
              title={`Billing`}
              description="Manage users (Client side table functionalities.)"
            />
            <Elements stripe={stripePromise} options={options}>
              <PaymentButtonToForm />
            </Elements>
          </div>
          <Separator />
      </div>
    </>
  );
}