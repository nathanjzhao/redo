'use client'
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

// NOT ACTUALLY NEEDED -- handled by provider

export default function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { data: session, status } = useSession();
    const router = useRouter();

    useEffect(() => {
      console.log(status)
      if (status === 'unauthenticated') {
        router.push('/');
      }
    }, [status]);

    if (status === 'loading') {
      return <div>Loading...</div>;
    }

    return <Component {...props} />;
  };
}