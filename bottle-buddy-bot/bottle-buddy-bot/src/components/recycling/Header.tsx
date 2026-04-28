import { Recycle, HelpCircle, Info, MoreVertical, Settings } from 'lucide-react';
import * as React from 'react';
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

interface HeaderProps {
  className?: string;
}

export const Header = ({ className }: HeaderProps) => {
  const currentTime = new Date().toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <header className={cn(
      'flex items-center justify-between px-4 py-2 border-b border-border/50',
      className
    )}>
      <div className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
          <Recycle className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="font-display text-lg font-bold tracking-wider text-foreground">
            RECY-BOT
          </h1>
          <p className="text-[10px] text-muted-foreground">
            Robot de Recyclage Intelligent
          </p>
        </div>
      </div>

      <div className="flex items-center gap-6 text-muted-foreground">
        <Dialog>
          <DialogTrigger asChild>
            <span className="text-foreground font-bold text-lg cursor-pointer hover:underline transition font-display">
             Info
            </span>
          </DialogTrigger>

          {/* ✅ Partie DialogContent améliorée */}
          <DialogContent className="max-w-md rounded-xl shadow-lg border border-border/30 p-6 bg-background/95 backdrop-blur-sm">
            <DialogHeader className="border-b border-border/50 pb-2">
              <DialogTitle className="text-lg font-bold text-foreground">
                 Informations
              </DialogTitle>
            </DialogHeader>

            
            <div className="space-y-3 mt-4">
              <div className="p-3 border border-border/50 rounded-lg bg-muted/5">
                <h4 className="font-semibold mb-1 text-green-600">Info projet</h4>
                <p><span className="font-medium">Nom :</span> RecyBot</p>
                <p><span className="font-medium">Objectif :</span> recyclage des bouteilles PET</p>
                <p className="font-medium mt-2">Fonctionnement :</p>
                <ul className="list-disc list-inside text-sm ml-2">
                  <li>Détection IA (PET, vide, sans bouchon)</li>
                  <li>Broyage automatique</li>
                  <li>Stockage intelligent</li>
                </ul>
              </div>

              <div className="p-3 border border-border/50 rounded-lg bg-muted/5">
                <h4 className="font-semibold mb-1 text-green-600">Équipe</h4>
                <p>Étudiants EMINES – UM6P</p>
              </div>

              <div className="p-3 border border-border/50 rounded-lg bg-muted/5">
                <h4 className="font-semibold mb-1 text-green-600">Version</h4>
                <p>v1.0</p>
              </div>

              <div className="p-3 border border-border/50 rounded-lg bg-muted/5">
                <h4 className="font-semibold mb-1 text-green-600">Contact</h4>
                <p><span className="font-medium">Responsable technique :</span></p>
                <p>📞 +212 6 XX XX XX XX</p>
                <p>📧 <a href="mailto:support.machine@um6p.ma" className="text-primary underline">support.machine@um6p.ma</a></p>
              </div>
            </div>
          </DialogContent>
          {/* ✅ Fin DialogContent améliorée */}

        </Dialog>
      </div>
    </header>
  );
};
