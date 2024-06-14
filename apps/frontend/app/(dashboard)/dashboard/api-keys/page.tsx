'use client';
import { CalendarDateRangePicker } from '@/components/date-range-picker';
import { Overview } from '@/components/overview';
import { RecentSales } from '@/components/recent-sales';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Heading } from '@/components/ui/heading';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import BreadCrumb from '@/components/breadcrumb';

const breadcrumbItems = [{ title: 'API Keys', link: '/dashboard/api-keys' }];

export default function page() {
  const router = useRouter();
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
              onClick={() => router.push(`/dashboard/user/new`)}
            >
              <Plus className="mr-2 h-4 w-4" /> Add New
            </Button>
          </div>
          <Separator />
      </div>
    </>
  );
}
