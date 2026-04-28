import { RecyclingStats } from '@/types/recycling';
import { cn } from '@/lib/utils';
import { BarChart } from "lucide-react";
import { Recycle, Calendar, Scale, Leaf, Droplets, Palette } from 'lucide-react';

interface StatsPanelProps {
  stats: RecyclingStats;
  className?: string;
}

export const StatsPanel = ({ stats, className }: StatsPanelProps) => {
  const mainStats = [
    {
      label: 'Total Bouteilles',
      value: stats.totalBottles.toLocaleString(),
      icon: Recycle,
      color: 'text-primary',
      bgColor: 'bg-primary/20',
    },
    {
      label: "Aujourd'hui",
      value: stats.todayBottles.toString(),
      icon: Calendar,
      color: 'text-info',
      bgColor: 'bg-info/20',
    },
    {
      label: 'Poids Total',
      value: `${stats.totalWeight.toFixed(2)} kg`,
      icon: Scale,
      color: 'text-warning',
      bgColor: 'bg-warning/20',
    },
    {
      label: 'CO₂ Économisé',
      value: `${stats.co2Saved.toFixed(2)} kg`,
      icon: Leaf,
      color: 'text-success',
      bgColor: 'bg-success/20',
    },
  ];

  return (
    <div className={cn('glass-panel p-6', className)}>
      <h3 className="font-display text-xl font-semibold tracking-wide mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
          <BarChart className="w-5 h-5 text-primary" />
        </div>
        <div>
          <span>Statistiques</span>
          <p className="text-xs text-muted-foreground font-normal">Performances de recyclage</p>
        </div>
      </h3>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        {mainStats.map((item) => (
          <div 
            key={item.label}
            className="bg-secondary/50 rounded-xl p-4 border border-border/50 hover:border-primary/30 transition-colors"
          >
            <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center mb-3', item.bgColor)}>
              <item.icon className={cn('w-5 h-5', item.color)} />
            </div>
            <p className="text-3xl font-display font-bold text-foreground">
              {item.value}
            </p>
            <p className="text-sm text-muted-foreground mt-1 font-medium">
              {item.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
