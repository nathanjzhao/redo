'use client';
import { Button } from '@/components/ui/button';
import { DataTable } from '@/components/ui/data-table';
import { Heading } from '@/components/ui/heading';
import { Separator } from '@/components/ui/separator';
import { User } from '@/constants/data';
import { Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { columns } from './columns';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';

interface ProductsClientProps {
  data: User[];
}

export const ApiKeyClient: React.FC<ProductsClientProps> = ({ data }) => {
  const router = useRouter();
  const { data: session } = useSession();

  const [apiKeys, setApiKeys] = useState([]);

  useEffect(() => {
    const fetchApiKeys = async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/fetch-api-keys`, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.accessToken}`
        }
      });
      const data = await response.json();
      setApiKeys(data.api_keys);
    };

    fetchApiKeys();
  }, []);


  return (
    <>
      <DataTable
        title="API Keys"
        columns={columns}
        data={apiKeys}
      />
    </>
  );
};
