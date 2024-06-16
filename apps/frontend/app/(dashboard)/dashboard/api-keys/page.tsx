'use client';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Heading } from '@/components/ui/heading';
import { Separator } from '@/components/ui/separator';
import BreadCrumb from '@/components/breadcrumb';
import { useSession } from 'next-auth/react';
import ApiKeyForm from '@/components/forms/api-key-form';
import { ApiKeyClient } from '@/components/tables/api-key-tables/client';

const breadcrumbItems = [{ title: 'API Keys', link: '/dashboard/api-keys' }];

export default function page() {
  const router = useRouter();
  const { data: session } = useSession();

  const generateAndCopyApiKey = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/create-api-key`, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.accessToken}`
        }
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
      const apiKey = data.api_key;
      console.log(data)
    
      // Copy the API key to the clipboard
      await navigator.clipboard.writeText(apiKey);
    
      alert('API key has been generated and copied to the clipboard');
    } catch (error) {
      alert('Failed to generate API key');
    }
  };

  return (
    <>
      <div className="flex-1 space-y-4  p-4 pt-6 md:p-8">
        <BreadCrumb items={breadcrumbItems} />
          <div className="flex items-start justify-between">
            <Heading
              title={`API Keys`}
              description="Manage users (Client side table functionalities.)"
            />
            <Button
              className="text-xs md:text-sm"
              onClick={generateAndCopyApiKey}
            >
              <Plus className="mr-2 h-4 w-4" /> Create API Key
            </Button>
          </div>
          <Separator />

          <ApiKeyClient data={[]} />
          {/* <ApiKeyForm /> */}
      </div>
    </>
  );
}
