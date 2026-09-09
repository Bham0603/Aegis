import React from "react";
import { GlassCard } from "@/components/ui/GlassCard";

interface Column<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string;
  loading?: boolean;
}

export function DataTable<T>({ data, columns, keyExtractor, loading }: DataTableProps<T>) {
  if (loading) {
    return (
      <GlassCard className="w-full h-48 flex items-center justify-center">
        <div className="animate-pulse bg-white/10 h-8 w-3/4 rounded"></div>
      </GlassCard>
    );
  }

  if (!data || data.length === 0) {
    return (
      <GlassCard className="w-full">
        <div className="py-12 text-center text-zinc-500">
          No records found.
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard className="w-full overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/10">
          <thead className="bg-white/5">
            <tr>
              {columns.map((col, i) => (
                <th
                  key={i}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 bg-transparent">
            {data.map((item) => (
              <tr key={keyExtractor(item)} className="hover:bg-white/5 transition-colors">
                {columns.map((col, colIndex) => (
                  <td
                    key={colIndex}
                    className="px-6 py-4 whitespace-nowrap text-sm text-zinc-300"
                  >
                    {col.cell ? col.cell(item) : (col.accessorKey ? String(item[col.accessorKey]) : null)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}
