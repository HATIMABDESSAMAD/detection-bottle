import { Header } from '@/components/recycling/Header';
import { ArrowLeft, Volume2, Bell, Moon, Gauge, Info } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useState } from 'react';

const SettingsToggle = ({ 
  enabled, 
  onChange 
}: { 
  enabled: boolean; 
  onChange: (value: boolean) => void;
}) => (
  <button
    onClick={() => onChange(!enabled)}
    className={cn(
      'w-14 h-8 rounded-full transition-all duration-300 relative',
      enabled ? 'bg-primary' : 'bg-secondary'
    )}
  >
    <div className={cn(
      'absolute top-1 w-6 h-6 rounded-full bg-white shadow-md transition-all duration-300',
      enabled ? 'left-7' : 'left-1'
    )} />
  </button>
);

const Settings = () => {
  const [settings, setSettings] = useState({
    sound: true,
    notifications: true,
    darkMode: true,
    highContrast: false,
  });

  const updateSetting = (key: keyof typeof settings) => (value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      
      <main className="flex-1 p-6 max-w-2xl mx-auto w-full">
        <Link 
          to="/" 
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Retour</span>
        </Link>

        <h1 className="font-display text-3xl font-bold mb-8">Paramètres</h1>

        <div className="space-y-6">
          {/* Sound Settings */}
          <div className="glass-panel p-6">
            <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-3">
              <Volume2 className="w-5 h-5 text-primary" />
              Audio
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Sons système</p>
                <p className="text-sm text-muted-foreground">
                  Sons de confirmation et alertes
                </p>
              </div>
              <SettingsToggle 
                enabled={settings.sound} 
                onChange={updateSetting('sound')} 
              />
            </div>
          </div>

          {/* Notification Settings */}
          <div className="glass-panel p-6">
            <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-3">
              <Bell className="w-5 h-5 text-primary" />
              Notifications
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Alertes de stockage</p>
                <p className="text-sm text-muted-foreground">
                  Alerte quand un bac est presque plein
                </p>
              </div>
              <SettingsToggle 
                enabled={settings.notifications} 
                onChange={updateSetting('notifications')} 
              />
            </div>
          </div>

          {/* Display Settings */}
          <div className="glass-panel p-6">
            <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-3">
              <Moon className="w-5 h-5 text-primary" />
              Affichage
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Mode sombre</p>
                  <p className="text-sm text-muted-foreground">
                    Interface sombre pour réduire la fatigue visuelle
                  </p>
                </div>
                <SettingsToggle 
                  enabled={settings.darkMode} 
                  onChange={updateSetting('darkMode')} 
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Contraste élevé</p>
                  <p className="text-sm text-muted-foreground">
                    Améliore la lisibilité
                  </p>
                </div>
                <SettingsToggle 
                  enabled={settings.highContrast} 
                  onChange={updateSetting('highContrast')} 
                />
              </div>
            </div>
          </div>

          {/* Machine Info */}
          <div className="glass-panel p-6">
            <h2 className="font-display text-lg font-semibold mb-4 flex items-center gap-3">
              <Info className="w-5 h-5 text-primary" />
              Information Machine
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Modèle</span>
                <span className="font-mono">ECO-CRUSHER v2.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Numéro de série</span>
                <span className="font-mono">EC-2024-0847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Version logicielle</span>
                <span className="font-mono">1.2.4</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dernière maintenance</span>
                <span className="font-mono">05/01/2025</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;
