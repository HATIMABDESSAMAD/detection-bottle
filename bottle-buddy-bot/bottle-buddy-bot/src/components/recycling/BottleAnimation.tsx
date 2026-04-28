import { MachineStatus, BottleInfo, RejectionReason } from '@/types/recycling';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface BottleAnimationProps {
  status: MachineStatus;
  currentBottle: BottleInfo | null;
  className?: string;
  broyageActive?: boolean;
}

const getRejectionMessage = (reason?: RejectionReason): { title: string; subtitle: string } => {
  switch (reason) {
    case 'cap_present':
      return { 
        title: '⚠️ BOUCHON DÉTECTÉ', 
        subtitle: 'Veuillez retirer le bouchon et réessayer' 
      };
    case 'filled':
      return {
        title: '✗ BOUTEILLE REMPLIE',
        subtitle: 'Veuillez vider la bouteille et réessayer'
      };
    case 'no_bottle':
      return {
        title: '✗ AUCUNE BOUTEILLE',
        subtitle: 'Veuillez insérer une bouteille dans l’ouverture'
      };
    case 'not_pet':
      return { 
        title: '✗ MATÉRIAU NON PET', 
        subtitle: 'Seules les bouteilles PET sont acceptées' 
      };
    case 'damaged':
      return { 
        title: '✗ BOUTEILLE ENDOMMAGÉE', 
        subtitle: 'La bouteille ne peut pas être traitée' 
      };
    default:
      return { 
        title: '✗ BOUTEILLE REJETÉE', 
        subtitle: 'Veuillez vérifier la bouteille' 
      };
  }
};

export const BottleAnimation = ({ status, currentBottle, className, broyageActive }: BottleAnimationProps) => {
  const isIdle = status === 'idle';
  const isCrushing = status === 'crushing';
  const isComplete = status === 'complete';
  const isInvalid = status === 'invalid';

  const rejectionInfo = isInvalid && currentBottle 
    ? getRejectionMessage(currentBottle.rejectionReason)
    : null;

  return (
    <div className={cn(
       'p-8 flex flex-col items-center justify-center relative overflow-hidden',
      className
    )}>
      {broyageActive && (
        <style>{`
          @keyframes bottleShake {
            0%, 100% { transform: translate(0,0) rotate(0deg); }
            10%  { transform: translate(-4px,-2px) rotate(-1.5deg); }
            20%  { transform: translate(4px, 2px) rotate(1.5deg); }
            30%  { transform: translate(-5px, 1px) rotate(-1deg); }
            40%  { transform: translate(5px,-1px) rotate(1deg); }
            50%  { transform: translate(-3px, 4px) rotate(-2deg); }
            60%  { transform: translate(3px,-4px) rotate(2deg); }
            70%  { transform: translate(-4px, 2px) rotate(-1deg); }
            80%  { transform: translate(4px,-2px) rotate(1deg); }
            90%  { transform: translate(-2px,-1px) rotate(-0.5deg); }
          }
          @keyframes crackGrow {
            0%   { stroke-dashoffset: 60; opacity: 0; }
            20%  { opacity: 1; }
            100% { stroke-dashoffset: 0; opacity: 1; }
          }
          @keyframes bottleCompress {
            0%,100% { transform: scaleY(1)   scaleX(1); }
            25%     { transform: scaleY(0.96) scaleX(1.03); }
            50%     { transform: scaleY(0.92) scaleX(1.06); }
            75%     { transform: scaleY(0.96) scaleX(1.03); }
          }
          @keyframes fragFly1 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(-38px,-48px) rotate(-130deg);opacity:0;} }
          @keyframes fragFly2 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(42px,-40px) rotate(110deg);opacity:0;} }
          @keyframes fragFly3 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(-30px,50px) rotate(160deg);opacity:0;} }
          @keyframes fragFly4 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(36px,44px) rotate(-90deg);opacity:0;} }
          @keyframes fragFly5 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(2px,-55px) rotate(210deg);opacity:0;} }
          @keyframes fragFly6 { 0%{transform:translate(0,0) rotate(0deg);opacity:1;} 100%{transform:translate(-44px,10px) rotate(-170deg);opacity:0;} }
          .anim-shake   { animation: bottleShake 0.35s ease-in-out infinite; }
          .anim-compress{ animation: bottleCompress 0.7s ease-in-out infinite; }
          .anim-crack   { stroke-dasharray:60; animation: crackGrow 0.8s ease-out forwards; }
          .frag1 { animation: fragFly1 1.1s ease-in infinite; animation-delay:0.0s; }
          .frag2 { animation: fragFly2 1.2s ease-in infinite; animation-delay:0.2s; }
          .frag3 { animation: fragFly3 1.0s ease-in infinite; animation-delay:0.4s; }
          .frag4 { animation: fragFly4 1.3s ease-in infinite; animation-delay:0.15s; }
          .frag5 { animation: fragFly5 0.9s ease-in infinite; animation-delay:0.35s; }
          .frag6 { animation: fragFly6 1.1s ease-in infinite; animation-delay:0.55s; }
        `}</style>
      )}
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className={cn(
          'absolute inset-0 transition-all duration-1000',
          isInvalid && 'bg-gradient-to-b from-destructive/10 to-transparent',
          status === 'valid' && 'bg-gradient-to-b from-success/10 to-transparent',
          isComplete && 'bg-gradient-to-b from-success/15 to-transparent',
          isCrushing && 'bg-gradient-to-b from-warning/10 to-transparent'
        )} />
        
        {/* Floating particles effect */}
        {isComplete && (
          <div className="absolute inset-0">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-success/40 rounded-full animate-float"
                style={{
                  left: `${20 + i * 12}%`,
                  animationDelay: `${i * 0.3}s`,
                  animationDuration: '3s'
                }}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Main bottle visualization */}
      <div className={cn(
        'relative z-10 transition-all duration-500',
        isCrushing && 'animate-crushing',
        broyageActive && 'anim-shake'
      )}>
        <div className="relative">
          {/* Bottle SVG */}
          <svg 
            viewBox="0 0 120 220" 
            className={cn(
              'w-60 h-82 transition-all duration-500',
              isIdle && 'opacity-90',
              status === 'detecting' && 'opacity-70 animate-pulse',
              status === 'valid' && 'opacity-100',
              isInvalid && 'opacity-100',
              isCrushing && 'opacity-90',
              status === 'sorting' && 'opacity-70',
              isComplete && 'opacity-50'
            )}
          >
            {/* Glow effect */}
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <linearGradient id="bottleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" className={cn(
                  isInvalid ? 'stop-color-destructive' : 
                  status === 'valid' || isComplete ? 'stop-color-success' :
                  isCrushing ? 'stop-color-warning' : 'stop-color-primary'
                )} style={{ stopColor: isInvalid ? 'hsl(0 72% 51%)' : status === 'valid' || isComplete ? 'hsl(142 70% 45%)' : isCrushing ? 'hsl(38 92% 50%)' : 'hsl(142 70% 45%)' }} />
                <stop offset="100%" className="stop-color-transparent" style={{ stopColor: 'transparent' }} />
              </linearGradient>
            </defs>
            
            {/* Bottle cap - shown when rejected due to cap */}
            {currentBottle?.hasCap && isInvalid && (
              <g className="animate-pulse">
                <rect 
                  x="42" y="5" width="36" height="22" rx="4" 
                  fill="hsl(0 72% 51%)" 
                  stroke="hsl(0 72% 40%)" 
                  strokeWidth="2"
                />
                <line x1="48" y1="10" x2="48" y2="22" stroke="hsl(0 72% 40%)" strokeWidth="1" />
                <line x1="60" y1="10" x2="60" y2="22" stroke="hsl(0 72% 40%)" strokeWidth="1" />
                <line x1="72" y1="10" x2="72" y2="22" stroke="hsl(0 72% 40%)" strokeWidth="1" />
              </g>
            )}
            
            {/* Bottle neck ring */}
            <ellipse 
              cx="60" cy="28" rx="18" ry="4" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              className={cn(
                isInvalid ? 'text-destructive' : 
                status === 'valid' || isComplete ? 'text-success' :
                isCrushing ? 'text-warning' : 'text-primary'
              )}
            />
            
            {/* Bottle body */}
            <path 
              d="M48 28 L48 45 L35 65 L35 195 Q35 210 60 210 Q85 210 85 195 L85 65 L72 45 L72 28" 
              fill="url(#bottleGradient)"
              fillOpacity="0.3"
              stroke="currentColor"
              strokeWidth="3"
              filter={status !== 'idle' ? 'url(#glow)' : ''}
              className={cn(
                'transition-colors duration-500',
                isInvalid ? 'text-destructive' : 
                status === 'valid' || isComplete ? 'text-success' :
                isCrushing ? 'text-warning' : 
                status === 'sorting' ? 'text-info' : 'text-primary'
              )}
            />
            
            {/* Liquid inside (when valid) */}
            {(status === 'valid' || status === 'detecting') && (
              <path 
                d="M40 80 L40 190 Q40 205 60 205 Q80 205 80 190 L80 80 Z" 
                className={cn(
                  'transition-all duration-500',
                  currentBottle?.petType === 'transparent' 
                    ? 'fill-info/30' 
                    : 'fill-warning/30'
                )}
              />
            )}
            
            {/* Cracks when broyage active */}
            {broyageActive && (
              <>
                {/* Crack 1 — left */}
                <path className="anim-crack" d="M50 75 L44 92 L53 108" fill="none" stroke="hsl(38 92% 50%)" strokeWidth="2" strokeLinecap="round" />
                {/* Crack 2 — right */}
                <path className="anim-crack" d="M70 95 L76 112 L67 128" fill="none" stroke="hsl(38 92% 50%)" strokeWidth="2" strokeLinecap="round" style={{animationDelay:'0.15s'}} />
                {/* Crack 3 — center */}
                <path className="anim-crack" d="M58 135 L52 148 L62 162 L56 175" fill="none" stroke="hsl(38 92% 50%)" strokeWidth="1.5" strokeLinecap="round" style={{animationDelay:'0.3s'}} />
                {/* Crack 4 — upper right */}
                <path className="anim-crack" d="M68 60 L74 72 L66 82" fill="none" stroke="hsl(38 92% 50%)" strokeWidth="1.5" strokeLinecap="round" style={{animationDelay:'0.45s'}} />
                {/* Flying fragments */}
                <polygon className="frag1" points="48,80 54,75 50,88" fill="hsl(38 92% 50%)" opacity="0.9" />
                <polygon className="frag2" points="72,100 78,95 74,108" fill="hsl(38 92% 60%)" opacity="0.9" />
                <polygon className="frag3" points="42,140 48,135 44,150" fill="hsl(38 92% 50%)" opacity="0.9" />
                <polygon className="frag4" points="76,155 82,150 78,163" fill="hsl(38 92% 60%)" opacity="0.9" />
                <polygon className="frag5" points="58,65 64,60 60,74" fill="hsl(38 92% 50%)" opacity="0.9" />
                <polygon className="frag6" points="38,100 44,96 40,110" fill="hsl(38 92% 60%)" opacity="0.9" />
              </>
            )}
          </svg>
          
          {/* Status icon overlay */}
          {/* Pas d'icône pour le statut 'prêt' */}
          {isInvalid && (
            <div className="absolute -top-2 -right-2 w-10 h-10 bg-destructive rounded-full flex items-center justify-center animate-scale-in shadow-lg shadow-destructive/30">
              {currentBottle?.rejectionReason === 'cap_present' ? (
                <AlertTriangle className="w-6 h-6 text-destructive-foreground" />
              ) : (
                <XCircle className="w-6 h-6 text-destructive-foreground" />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Status message */}
      <div className="mt-8 text-center relative z-10">
        {isIdle && (
          <div className="animate-bounce-subtle">
            <p className="text-2xl font-display font-bold text-foreground mb-2">
              Insérez une bouteille
            </p>
            <p className="text-muted-foreground text-sm">
              Bouteilles PET sans bouchon uniquement
            </p>
          </div>
        )}
        
        {status === 'detecting' && (
          <div className="space-y-2">
            <div className="flex items-center justify-center gap-2">
              <div className="w-2 h-2 bg-info rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-info rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-info rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
            </div>
            <p className="text-info text-xl font-semibold">Analyse en cours...</p>
            <p className="text-muted-foreground text-sm">Détection du matériau</p>
          </div>
        )}
        
        {status === 'valid' && currentBottle && (
          <div className="space-y-2">
            <p className="text-success text-xl font-display font-bold">
              ✓ Bouteille PET {currentBottle.petType === 'transparent' ? 'Transparent' : 'Coloré'}
            </p>
            <p className="text-muted-foreground text-sm">Préparation au broyage...</p>
          </div>
        )}
        
        {isInvalid && rejectionInfo && (
          <div className="space-y-3 animate-fade-in">
            <p className="text-destructive text-xl font-display font-bold">
              {rejectionInfo.title}
            </p>
            <p className="text-destructive/80 text-sm max-w-xs mx-auto">
              {rejectionInfo.subtitle}
            </p>
          </div>
        )}
        
        {isCrushing && (
          <div className="space-y-2">
            <p className="text-warning text-xl font-display font-bold">
              Broyage en cours...
            </p>
            <div className="w-48 h-2 bg-secondary rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-warning animate-progress rounded-full" />
            </div>
          </div>
        )}
        
        {/* Tri (sorting) state UI removed as requested */}
        
        {/* Message de fin (Merci/Vous contribuez...) retiré comme demandé */}
      </div>
    </div>
  );
};
