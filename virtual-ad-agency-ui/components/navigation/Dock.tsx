'use client';

import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Home, Briefcase, FolderOpen, Settings } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useRef } from 'react';
import { cn } from '@/lib/utils';

interface DockItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
}

const DOCK_ITEMS: DockItem[] = [
  { id: 'projects', label: 'Projects', icon: Home, href: '/projects' },
  { id: 'workspace', label: 'Workspace', icon: Briefcase, href: '/workspace' },
  { id: 'assets', label: 'Assets', icon: FolderOpen, href: '/assets' },
  { id: 'settings', label: 'Settings', icon: Settings, href: '/settings' },
];

interface DockIconProps {
  item: DockItem;
  mouseX: any;
  isActive: boolean;
}

function DockIcon({ item, mouseX, isActive }: DockIconProps) {
  const ref = useRef<HTMLDivElement>(null);

  const distance = useTransform(mouseX, (val: number) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 };
    return val - bounds.x - bounds.width / 2;
  });

  const widthSync = useTransform(distance, [-150, 0, 150], [48, 80, 48]);
  const width = useSpring(widthSync, { mass: 0.1, stiffness: 150, damping: 12 });

  const Icon = item.icon;

  return (
    <motion.div
      ref={ref}
      style={{ width }}
      className="relative"
    >
      <Link
        href={item.href}
        className={cn(
          'flex aspect-square w-full items-center justify-center rounded-xl',
          'transition-colors relative group',
          isActive
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        )}
        aria-label={item.label}
        aria-current={isActive ? 'page' : undefined}
      >
        <Icon className="h-6 w-6" />
        
        {/* Tooltip */}
        <div
          className={cn(
            'absolute -top-10 left-1/2 -translate-x-1/2',
            'px-3 py-1.5 rounded-lg',
            'bg-gray-900 text-white text-sm font-medium',
            'opacity-0 group-hover:opacity-100',
            'transition-opacity pointer-events-none',
            'whitespace-nowrap'
          )}
        >
          {item.label}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-gray-900" />
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export function Dock() {
  const mouseX = useMotionValue(Infinity);
  const pathname = usePathname();

  return (
    <motion.div
      onMouseMove={(e) => mouseX.set(e.pageX)}
      onMouseLeave={() => mouseX.set(Infinity)}
      className={cn(
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-50',
        'flex items-end gap-4 px-4 py-3',
        'bg-white/80 backdrop-blur-md',
        'border border-gray-200 rounded-2xl shadow-lg'
      )}
    >
      {DOCK_ITEMS.map((item) => (
        <DockIcon
          key={item.id}
          item={item}
          mouseX={mouseX}
          isActive={pathname?.startsWith(item.href) ?? false}
        />
      ))}
    </motion.div>
  );
}
