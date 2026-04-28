import { MachineStatus } from '@/types/recycling';
import { 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  Cog, 
  ArrowDownUp, 
  CircleDot,
  AlertTriangle,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Play } from "lucide-react";
import { Power } from "lucide-react";

interface StatusIndicatorProps {
  status: MachineStatus;
  className?: string;
}

const statusConfig: Record<MachineStatus, {
  label: string;
  icon: React.ElementType;
  colorClass: string;
  bgClass: string;
  glowClass: string;
}> = {
  idle: {
    label: 'PRÊT',
    icon:  CheckCircle2 ,
    colorClass: 'text-primary',
    bgClass: 'bg-primary/20',
    glowClass: 'shadow-[0_0_30px_hsl(142_70%_45%/0.3)]',
  },
  detecting: {
    label: 'DÉTECTION...',
    icon: Loader2,
    colorClass: 'text-info',
    bgClass: 'bg-info/20',
    glowClass: 'shadow-[0_0_30px_hsl(199_89%_48%/0.3)]',
  },
  valid: {
    label: 'BOUTEILLE VALIDÉE',
    icon: CheckCircle2,
    colorClass: 'text-success',
    bgClass: 'bg-success/20',
    glowClass: 'shadow-[0_0_30px_hsl(142_70%_45%/0.4)]',
  },
  invalid: {
    label: 'BOUTEILLE REJETÉE',
    icon: XCircle,
    colorClass: 'text-destructive',
    bgClass: 'bg-destructive/20',
    glowClass: 'shadow-[0_0_30px_hsl(0_72%_51%/0.3)]',
  },
  crushing: {
    label: 'BROYAGE EN COURS',
    icon: Cog,
    colorClass: 'text-warning',
    bgClass: 'bg-warning/20',
    glowClass: 'shadow-[0_0_30px_hsl(38_92%_50%/0.3)]',
  },
  // sorting: { // Tri state removed from UI
  //   label: 'TRI EN COURS',
  //   icon: ArrowDownUp,
  //   colorClass: 'text-info',
  //   bgClass: 'bg-info/20',
  //   glowClass: 'shadow-[0_0_30px_hsl(199_89%_48%/0.3)]',
  // },
  complete: {
    label: 'TERMINÉ',
    icon: Sparkles,
    colorClass: 'text-success',
    bgClass: 'bg-success/20',
    glowClass: 'shadow-[0_0_30px_hsl(142_70%_45%/0.4)]',
  },
  error: {
    label: 'ERREUR',
    icon: AlertTriangle,
    colorClass: 'text-destructive',
    bgClass: 'bg-destructive/20',
    glowClass: 'shadow-[0_0_30px_hsl(0_72%_51%/0.4)]',
  },
  sorting: {
    label: '',
    icon: 'symbol',
    colorClass: '',
    bgClass: '',
    glowClass: ''
  }
};

export const StatusIndicator = ({ status, className }: StatusIndicatorProps) => {
  const config = statusConfig[status];
  const Icon = config.icon;
  const isAnimated = ['detecting', 'crushing'].includes(status);

  return (
    <div
      className={cn(
        'glass-panel p-6 flex items-center gap-6 transition-all duration-500 justify-center',
        config.glowClass,
        className
      )}
    >
      <div className={cn(
        'w-20 h-20 rounded-2xl flex items-center justify-center',
        config.bgClass
      )}>
        <Icon
          className={cn(
            'w-10 h-10',
            config.colorClass,
            isAnimated && status === 'crushing' && 'animate-spin',
            isAnimated && status !== 'crushing' && 'animate-spin-slow'
          )}
        />
      </div>
      <div>
        <p className="text-muted-foreground text-base font-display font-bold uppercase tracking-wider mb-1">
          Statut de la machine
        </p>
        <h2 className={cn(
          'font-display text-2xl font-bold tracking-wide',
          config.colorClass
        )}>
          {config.label}
        </h2>
      </div>
    </div>
  );
};
