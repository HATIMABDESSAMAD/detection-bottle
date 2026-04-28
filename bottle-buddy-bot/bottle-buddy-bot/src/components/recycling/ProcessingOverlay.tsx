import { MachineStatus } from '@/types/recycling';
import { cn } from '@/lib/utils';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface ProcessingOverlayProps {
  status: MachineStatus;
  message?: string;
  className?: string;
}

export const ProcessingOverlay = ({ status, message, className }: ProcessingOverlayProps) => {
  const isVisible = ['crushing', 'sorting', 'complete', 'invalid'].includes(status);
  
  if (!isVisible) return null;

  const getIcon = () => {
    switch (status) {
      case 'complete':
        return <CheckCircle2 className="w-24 h-24 text-success animate-scale-in" />;
      case 'invalid':
        return <XCircle className="w-24 h-24 text-destructive animate-scale-in" />;
      default:
        return <Loader2 className="w-24 h-24 text-primary animate-spin" />;
    }
  };

  const getMessage = () => {
    switch (status) {
      case 'crushing':
        return 'Broyage en cours...';
      case 'sorting':
        return 'Tri des matériaux...';
      case 'complete':
        return message || 'Traitement terminé !';
      case 'invalid':
        return message || 'Bouteille non acceptée';
      default:
        return 'Traitement...';
    }
  };

  return (
    <div className={cn(
      'fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-fade-in',
      className
    )}>
      <div className="glass-panel p-12 text-center max-w-md mx-4">
        {getIcon()}
        <p className="mt-6 text-2xl font-display font-semibold text-foreground">
          {getMessage()}
        </p>
        
        {(status === 'crushing' || status === 'sorting') && (
          <div className="mt-6 h-2 bg-secondary rounded-full overflow-hidden">
            <div className="h-full w-1/2 bg-primary rounded-full animate-progress" />
          </div>
        )}
      </div>
    </div>
  );
};
