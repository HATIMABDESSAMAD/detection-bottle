import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface ActionButtonProps {
  label: string;
  icon: LucideIcon;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  className?: string;
}

export const ActionButton = ({
  label,
  icon: Icon,
  onClick,
  variant = 'primary',
  disabled = false,
  className,
}: ActionButtonProps) => {
  const variantClasses = {
    primary: 'bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_20px_hsl(142_70%_45%/0.3)] hover:shadow-[0_0_30px_hsl(142_70%_45%/0.5)]',
    secondary: 'bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border',
    danger: 'bg-destructive hover:bg-destructive/90 text-destructive-foreground shadow-[0_0_20px_hsl(0_72%_51%/0.3)]',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-center justify-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
        variantClasses[variant],
        className
      )}
    >
      <Icon className="w-6 h-6" />
      {label}
    </button>
  );
};
