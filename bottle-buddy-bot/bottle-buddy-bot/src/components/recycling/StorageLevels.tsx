import { StorageLevel } from '@/types/recycling';
import { cn } from '@/lib/utils';
import { Package, Droplets, Palette } from 'lucide-react';

interface StorageLevelsProps {
  levels: StorageLevel[];
  className?: string;
}

export const StorageLevels = ({ levels, className }: StorageLevelsProps) => {
  return (
    <div className={cn('glass-panel p-6', className)}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
          <Package className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-display text-lg font-semibold tracking-wide">
            Stockage PET
          </h3>
          <p className="text-xs text-muted-foreground">Niveaux actuels</p>
        </div>
      </div>
      
      <div className="space-y-5">
        {levels.map((level) => {
          const percentage = (level.currentLevel / level.maxLevel) * 100;
          const isNearFull = percentage >= 80;
          const isFull = percentage >= 95;
          // Supprimer l'icône, garder juste le label
          return (
            <div key={level.type} className="space-y-3">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span className="text-base font-semibold text-foreground">
                    {level.label}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground font-mono">
                    {level.currentLevel}/{level.maxLevel}
                  </span>
                  <span className={cn(
                    'text-base font-mono font-bold px-2 py-1 rounded-md',
                    isFull ? 'bg-destructive/20 text-destructive' : 
                    isNearFull ? 'bg-warning/20 text-warning' : 
                    'bg-primary/20 text-primary'
                  )}>
                    {Math.round(percentage)}%
                  </span>
                </div>
              </div>
              
              <div className="h-4 bg-secondary rounded-full overflow-hidden">
                <div 
                  className={cn(
                    'h-full rounded-full transition-all duration-500 relative',
                    isFull ? 'bg-gradient-to-r from-destructive to-destructive/80' : 
                    isNearFull ? 'bg-gradient-to-r from-warning to-warning/80' : 
                    level.type === 'transparent' 
                      ? 'bg-gradient-to-r from-info to-info/80'
                      : 'bg-gradient-to-r from-warning/70 to-amber-500'
                  )}
                  style={{ width: `${percentage}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
