// ...existing code...
import { Header } from '@/components/recycling/Header';
import { StatusIndicator } from '@/components/recycling/StatusIndicator';
import { BottleAnimation } from '@/components/recycling/BottleAnimation';
import { StorageLevels } from '@/components/recycling/StorageLevels';
import { StatsPanel } from '@/components/recycling/StatsPanel';
import { ActionButton } from '@/components/recycling/ActionButton';
import { ProcessingOverlay } from '@/components/recycling/ProcessingOverlay';
import { useRecyclingMachine } from '@/hooks/useRecyclingMachine';
import { Play, Check, X, Loader2, Circle, HelpCircle, Video, Hourglass, Clock, RefreshCw } from 'lucide-react';
import * as React from 'react';
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Workflow } from "lucide-react";
import { BadgeCheck } from "lucide-react";



// ValidationItem component (déplacé en haut pour éviter l'erreur JSX/TSX)
function ValidationItem({ label, valid, invalid, loading }: { label: string; valid?: boolean; invalid?: boolean; loading?: boolean }) {
  return (
    <li className="flex items-center justify-between gap-4">
      <span className="text-foreground text-base font-medium">{label}</span>
      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full border border-border bg-background">
        {loading ? (
          <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
        ) : valid ? (
          <Check className="w-5 h-5 text-success" />
        ) : invalid ? (
          <X className="w-5 h-5 text-destructive" />
        ) : (
          <span className="w-3 h-3 rounded-full bg-muted-foreground/20 block" />
        )}
      </span>
    </li>
  );
}

const Index = () => {
    // État pour ouvrir/fermer la vidéo explicative
    const [openVideo, setOpenVideo] = React.useState(false);
  const { status, storageLevels, stats, currentBottle, broyageDuration, broyageFinished, broyageElapsedMs, insertBottle } = useRecyclingMachine();
  const navigate = useNavigate();

  // Nouvel état local pour gérer l'insertion du bouchon
  const [capInserted, setCapInserted] = React.useState(false);
  const [bottleInserted, setBottleInserted] = React.useState(false);
  const isProcessing = !['idle', 'error'].includes(status);
  // Vérifie si le stockage est plein
  const isStorageFull = storageLevels.some(level => level.currentLevel >= level.maxLevel);

  // Simule l'insertion du bouchon
  const handleInsertCap = () => {
    setCapInserted(true);
    setBottleInserted(false);
  };

  // Simule l'insertion de la bouteille (seulement si le bouchon a été inséré)
  const handleInsertBottle = () => {
    setBottleInserted(true);
    window.setTimeout(() => {
      insertBottle();
    }, 4000);
  };

  // Pour réinitialiser le processus (optionnel)
  const handleReset = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      <main className="flex-1 p-1 grid grid-cols-12 gap-1 max-w-full mx-auto w-full items-stretch min-h-[300px] md:min-h-[500px] lg:min-h-[700px]" style={{ minHeight: 'calc(100vh - 60px)' }}>
        {/* Left Column - Controls */}
        <div className="col-span-12 md:col-span-4 flex flex-col h-full min-w-0">
          <div className="flex flex-col h-full min-w-0">
            <div className="flex flex-col gap-1 mt-1 flex-1">
              <ActionButton
                label="Démarrer"
                icon={Play}
                onClick={handleInsertBottle}
                variant={bottleInserted || isStorageFull ? "secondary" : "primary"}
                disabled={bottleInserted || isStorageFull}
              />
              <ActionButton
                label="Aide vidéo"
                icon={Video}
                onClick={() => setOpenVideo(true)}
                variant="secondary"
                className="mt-2"
              />
              <ActionButton
                label="Rafraîchir"
                icon={RefreshCw}
                onClick={() => window.location.reload()}
                variant="secondary"
                className="mt-2"
              />
              {isStorageFull && (
                <div className="text-destructive text-xs mt-1 text-center font-semibold">Stockage plein : impossible d'insérer une nouvelle bouteille</div>
              )}
              {/* Optionnel : bouton de réinitialisation */}
              <button
                className="mt-2 text-xs text-muted-foreground underline hover:text-primary"
                onClick={handleReset}
                type="button"
                disabled={!capInserted && !bottleInserted}
              >
                Réinitialiser le processus
              </button>
              {/* Dialog vidéo explicative */}
              <Dialog open={openVideo} onOpenChange={setOpenVideo}>
                <DialogContent className="max-w-xl">
                  <DialogHeader>
                    <DialogTitle>Vidéo : Comment utiliser la machine</DialogTitle>
                    <DialogDescription>Regardez cette vidéo pour comprendre les étapes d'utilisation.</DialogDescription>
                  </DialogHeader>
                  <div className="w-full aspect-video rounded-lg overflow-hidden bg-black flex items-center justify-center">
                    {/* Remplacez src par le lien réel de la vidéo */}
                    <video controls className="w-full h-full">
                      <source src="/assets/demo-etapes.mp4" type="video/mp4" />
                      Votre navigateur ne supporte pas la lecture vidéo.
                    </video>
                  </div>
                </DialogContent>
              </Dialog>
              {/* Validation Panel classique avec trois validations */}
              <div className="bg-card rounded-xl p-2 shadow mt-1">
                <h3 className="flex items-center gap-3 font-display text-lg font-semibold tracking-wide mb-3 text-foreground">
                  <span className="flex items-center justify-center w-10 h-10 rounded-md bg-primary/20">
                    <BadgeCheck className="w-6 h-6 text-primary" />
                  </span>
                    VALIDATION
                </h3>
                <ul className="space-y-2">
                  <ValidationItem
                    label="Plastique PET"
                    valid={!!currentBottle && currentBottle.rejectionReason !== 'not_pet' && currentBottle.rejectionReason !== 'no_bottle' && status !== 'detecting'}
                    invalid={currentBottle?.rejectionReason === 'not_pet'}
                    loading={status === 'detecting'}
                  />
                  <ValidationItem
                    label="Bouteille vide"
                    valid={!!currentBottle && !currentBottle.isFilled && status !== 'detecting' && currentBottle.rejectionReason !== 'no_bottle'}
                    invalid={!!currentBottle && !!currentBottle.isFilled && status !== 'detecting' && currentBottle.rejectionReason !== 'no_bottle'}
                    loading={status === 'detecting'}
                  />
                  <ValidationItem
                    label="Sans bouchon"
                    valid={!!currentBottle && !currentBottle.hasCap && status !== 'detecting' && currentBottle.rejectionReason !== 'no_bottle'}
                    invalid={!!currentBottle && !!currentBottle.hasCap && status !== 'detecting' && currentBottle.rejectionReason !== 'no_bottle'}
                    loading={status === 'detecting'}
                  />
                </ul>
                {/* Broyage en cours : hourglass animé + timer */}
                {status === 'valid' && !broyageFinished && (
                  <div className="mt-3 flex flex-col items-center gap-2">
                    <style>{`
                      @keyframes hgflip {
                        0%, 49.9% { transform: rotate(0deg); }
                        50%, 100% { transform: rotate(180deg); }
                      }
                      .anim-hgflip { animation: hgflip 1.5s steps(1) infinite; }
                    `}</style>
                    <Hourglass className="w-8 h-8 text-primary anim-hgflip" />
                    <span className="text-sm font-semibold text-primary animate-pulse">Broyage en cours...</span>
                    <span className="text-2xl font-mono font-bold text-primary">{(broyageElapsedMs / 1000).toFixed(1)} s</span>
                  </div>
                )}
                {/* Broyage terminé : notification stylee + durée + bouton OK */}
                {broyageFinished && (
                  <div className="mt-3 flex flex-col items-center gap-3 bg-success/10 border border-success/40 rounded-2xl p-4 shadow-lg">
                    <div className="flex items-center justify-center w-14 h-14 rounded-full bg-success/20 border-2 border-success/50">
                      <Check className="w-8 h-8 text-success" />
                    </div>
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-success text-base font-bold">Broyage terminé !</span>
                      <span className="text-success/80 text-sm font-medium text-center">Bouteille validée, merci pour votre geste !</span>
                      <span className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                        <Clock className="w-4 h-4" />
                        Durée de broyage :
                        <span className="font-bold text-foreground text-base ml-1">
                          {broyageDuration != null ? (broyageDuration / 1000).toFixed(1) + ' s' : '--'}
                        </span>
                      </span>
                    </div>
                    <button
                      onClick={() => window.location.reload()}
                      className="mt-1 px-8 py-2.5 rounded-xl bg-success text-white text-base font-bold shadow-md hover:bg-success/80 active:scale-95 transition-all"
                      type="button"
                    >
                      OK
                    </button>
                  </div>
                )}
                {status === 'invalid' && currentBottle?.rejectionReason !== 'no_bottle' && (
                  <div className="mt-3 flex flex-col items-center gap-3 bg-destructive/10 border border-destructive/40 rounded-2xl p-4 shadow-lg">
                    <div className="flex items-center justify-center w-14 h-14 rounded-full bg-destructive/20 border-2 border-destructive/50">
                      <X className="w-8 h-8 text-destructive" />
                    </div>
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-destructive text-base font-bold">Bouteille refusée !</span>
                      <span className="text-destructive/80 text-sm font-medium text-center">
                        {(() => {
                          const cap = currentBottle?.hasCap;
                          const filled = currentBottle?.isFilled;
                          if (cap && filled)
                            return "Bouteille remplie et bouchon présent. Veuillez vider la bouteille et retirer le bouchon.";
                          if (cap)
                            return "Bouchon détecté. Veuillez retirer le bouchon avant insertion.";
                          if (filled)
                            return "Bouteille remplie. Veuillez la vider avant insertion.";
                          if (currentBottle?.rejectionReason === 'not_pet')
                            return "Plastique non PET. Seules les bouteilles PET sont acceptées.";
                          if (currentBottle?.rejectionReason === 'no_bottle' || currentBottle == null)
                            return "Aucune bouteille détectée. Veuillez insérer une bouteille.";
                          return "Bouteille non conforme. Veuillez réessayer.";
                        })()}
                      </span>
                    </div>
                    <button
                      onClick={() => window.location.reload()}
                      className="mt-1 px-8 py-2.5 rounded-xl bg-destructive text-white text-base font-bold shadow-md hover:bg-destructive/80 active:scale-95 transition-all"
                      type="button"
                    >
                      OK
                    </button>
                  </div>
                )}
              </div>
              {/* Section Étapes d'utilisation améliorée */}
              <div className="bg-card rounded-2xl p-3 shadow-lg mt-1 border border-border min-h-[250px] flex-1">
                <div className="flex items-center gap-4 mb-3">
                  <span className="flex items-center justify-center w-12 h-12 rounded-xl bg-success/10">
                    <Workflow className="w-7 h-7 text-success" />
                  </span>
                  <div>
                    <h3 className="font-display text-lg font-bold tracking-wide text-foreground drop-shadow-sm">
                      ÉTAPES D'UTILISATION
                    </h3>
                  
                  </div>
                </div>
                <ol className="flex flex-col gap-2 mt-3">
                  {/* Étape 1 */}
                  <li className="flex items-center gap-3">
                    <span className="w-9 h-9 flex items-center justify-center rounded-full bg-success text-white font-display font-bold text-lg shadow border-2border-success">1</span>
                    <div className="flex flex-col">
                      <span className="font-semibold text-base text-foreground">Retirer le bouchon de la bouteille</span>
                     
                    </div>
                  </li>
                  {/* Étape 2 */}
                  <li className="flex items-center gap-3">
                    <span className="w-9 h-9 flex items-center justify-center rounded-full bg-success text-white font-display font-bold text-lg shadow border-2 border-success">2</span>
                    <div className="flex flex-col">
                      <span className="font-semibold text-base text-foreground">Mettre le bouchon dans l'ouverture dédiée</span>
                     
                    </div>
                  </li>
                  {/* Étape 3 */}
                  <li className="flex items-center gap-3">
                    <span className="w-9 h-9 flex items-center justify-center rounded-full bg-success text-white font-display font-bold text-lg shadow border-2 border-success">3</span>
                    <div className="flex flex-col">
                      <span className="font-semibold text-base text-foreground">Insérer la bouteille dans l'ouverture principale</span>
                      
                    </div>
                  </li>
                  {/* Étape 4 */}
                  <li className="flex items-center gap-3">
                    <span className="w-9 h-9 flex items-center justify-center rounded-full bg-success text-white font-display font-bold text-lg shadow border-2 border-success">4</span>
                    <div className="flex flex-col">
                      <span className="font-semibold text-base text-foreground">Attendre la validation de la bouteille</span>
                      
                    </div>
                  </li>
                </ol>
              </div>
            </div>
          </div>
          {/* Validation Panel supprimé ici (déplacé plus haut) */}
        </div>

        {/* Center Column - Status + Bottle Animation dans un même bloc, toute la hauteur */}
        <div className="col-span-12 md:col-span-4 flex flex-col items-center h-full min-w-0">
          <div className="w-full h-full bg-card rounded-xl shadow flex flex-col items-center justify-start p-2 flex-1 min-w-0">
            {/* Statut de la machine supprimé (au-dessus de l'animation) */}
            <div className="w-full flex-1 flex items-center justify-center">
              <BottleAnimation status={status} currentBottle={currentBottle} className="w-full" broyageActive={status === 'valid' && !broyageFinished} />
            </div>
          </div>
        </div>

        {/* Right Column - Stats */}
        <div className="col-span-12 md:col-span-4 flex flex-col h-full min-w-0">
          <div className="flex flex-col h-full flex-1 gap-2 min-w-0">
            <StatsPanel stats={stats} className="flex-1" />
            <StorageLevels levels={storageLevels} className="flex-1" />
          </div>
        </div>
      </main>

      {/* Message broyage en cours en bas au centre */}
      {status === 'crushing' && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white shadow-lg animate-pulse">
          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
          <span className="font-display font-semibold text-base">Broyage en cours...</span>
        </div>
      )}
      {status === 'invalid' && currentBottle?.rejectionReason !== 'no_bottle' && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive text-white shadow-lg">
          <X className="w-5 h-5 mr-2" />
          <span className="font-display font-semibold text-base">La bouteille n'est pas valide</span>
        </div>
      )}
    </div>
  );
};

export default Index;
