import { useState, useCallback, useRef, useEffect } from 'react';
import { MachineStatus, RecyclingStats, StorageLevel, BottleInfo, PETType, RejectionReason } from '@/types/recycling';

const PET_MAX_CAPACITY = 100;

const initialStorageLevels: StorageLevel[] = [
  { type: 'transparent', label: 'PET Transparent', currentLevel: 0, maxLevel: PET_MAX_CAPACITY },
];

const initialStats: RecyclingStats = {
  totalBottles: 0,
  todayBottles: 0,
  totalWeight: 0,
  co2Saved: 0,
  transparentCount: 0,
  coloredCount: 0,
};

export const useRecyclingMachine = () => {
  const [status, setStatus] = useState<MachineStatus>('idle');
  const [storageLevels, setStorageLevels] = useState<StorageLevel[]>(initialStorageLevels);
  const [stats, setStats] = useState<RecyclingStats>(initialStats);
  const [currentBottle, setCurrentBottle] = useState<BottleInfo | null>(null);
  const [broyageDuration, setBroyageDuration] = useState<number | null>(null);
  const [broyageFinished, setBroyageFinished] = useState(false);
  const [broyageElapsedMs, setBroyageElapsedMs] = useState(0);

  const pollingRef = useRef<number | null>(null);
  const timeoutRef = useRef<number | null>(null);
  const broyageStartRef = useRef<number | null>(null);
  const broyageElapsedIntervalRef = useRef<number | null>(null);
  const broyageFinishedPollingRef = useRef<number | null>(null);

  const fetchCsvStats = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/csv-stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
        setStorageLevels([{ type: 'transparent', label: 'PET Transparent', currentLevel: data.transparentCount ?? 0, maxLevel: PET_MAX_CAPACITY }]);
      }
    } catch (_) { /* silencieux si backend pas dispo */ }
  }, []);

  useEffect(() => {
    fetchCsvStats();
  }, [fetchCsvStats]);

  const stopPolling = () => {
    if (pollingRef.current != null) {
      window.clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    if (timeoutRef.current != null) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const stopBroyageTracking = () => {
    if (broyageElapsedIntervalRef.current != null) {
      window.clearInterval(broyageElapsedIntervalRef.current);
      broyageElapsedIntervalRef.current = null;
    }
    if (broyageFinishedPollingRef.current != null) {
      window.clearInterval(broyageFinishedPollingRef.current);
      broyageFinishedPollingRef.current = null;
    }
  };

  const insertBottle = useCallback(async () => {
    if (status !== 'idle') return;

    stopPolling();
    stopBroyageTracking();
    setCurrentBottle(null);
    setBroyageDuration(null);
    setBroyageFinished(false);
    setBroyageElapsedMs(0);
    setStatus('detecting');

    const startedAt = Date.now();
    const pollIntervalMs = 350;
    const maxWaitMs = 15000;

    const fetchStatus = async () => {
      const response = await fetch('http://localhost:5000/status');
      if (!response.ok) {
        throw new Error(`Backend status error: ${response.status}`);
      }
      return response.json() as Promise<{
        bottleExists: boolean;
        numBottles: number;
        isFilled: boolean;
        hasCap: boolean;
        valid: boolean;
        rejectionReason: RejectionReason | null;
      }>;
    };

    const decide = (s: { bottleExists: boolean; isFilled: boolean; hasCap: boolean; valid: boolean; rejectionReason: RejectionReason | null; }) => {
      if (!s.bottleExists) {
        // Timeout — aucune bouteille détectée
        setCurrentBottle({ petType: 'transparent', weight: 0.03, isValid: false, hasCap: false, isFilled: false, rejectionReason: 'no_bottle' });
        setStatus('invalid');
        return;
      }
      // Bouteille détectée — attendre 2s pour que Python verrouille les labels et écrive dans le CSV
      window.setTimeout(async () => {
        try {
          const response = await fetch('http://localhost:5000/csv-stats');
          if (response.ok) {
            const data = await response.json();
            setStats({ totalBottles: data.totalBottles, todayBottles: data.todayBottles, totalWeight: data.totalWeight, co2Saved: data.co2Saved, transparentCount: data.transparentCount, coloredCount: data.coloredCount });
            setStorageLevels([{ type: 'transparent', label: 'PET Transparent', currentLevel: data.transparentCount ?? 0, maxLevel: PET_MAX_CAPACITY }]);
            const lb = data.lastBottle;
            const bottleInfo: BottleInfo = lb
              ? {
                  petType: 'transparent', weight: 0.03, isValid: lb.valid,
                  hasCap: lb.hasCap, isFilled: lb.isFilled,
                  rejectionReason: lb.valid ? undefined : (lb.hasCap ? 'cap_present' : lb.isFilled ? 'filled' : 'unknown'),
                }
              : {
                  // CSV pas encore écrit — fallback sur les valeurs temps-réel
                  petType: 'transparent', weight: 0.03, isValid: s.valid,
                  hasCap: s.hasCap, isFilled: s.isFilled,
                  rejectionReason: (s.rejectionReason ?? (s.valid ? undefined : 'unknown')) || undefined,
                };
            const isValid = lb ? lb.valid : s.valid;
            setCurrentBottle(bottleInfo);
            if (isValid) {
              broyageStartRef.current = Date.now();
              setBroyageDuration(null);
              setBroyageFinished(false);
              setBroyageElapsedMs(0);
              // Timer visible : incrémente toutes les 100ms
              broyageElapsedIntervalRef.current = window.setInterval(() => {
                setBroyageElapsedMs(prev => prev + 100);
              }, 100);
              // Polling Arduino « Finished » via backend
              broyageFinishedPollingRef.current = window.setInterval(async () => {
                try {
                  const r = await fetch('http://localhost:5000/broyage-finished');
                  if (r.ok) {
                    const d = await r.json();
                    if (d.finished) {
                      stopBroyageTracking();
                      const elapsed = broyageStartRef.current != null
                        ? Math.round(Date.now() - broyageStartRef.current)
                        : null;
                      setBroyageDuration(elapsed);
                      setBroyageFinished(true);
                    }
                  }
                } catch (_) {}
              }, 800);
            }
            setStatus(isValid ? 'valid' : 'invalid');
          }
        } catch (_) { setStatus('error'); }
      }, 2000);
    };

    // Timeout global
    timeoutRef.current = window.setTimeout(() => {
      stopPolling();
      decide({ bottleExists: false, isFilled: false, hasCap: false, valid: false, rejectionReason: 'no_bottle' });
    }, maxWaitMs);

    // Polling
    pollingRef.current = window.setInterval(async () => {
      try {
        const s = await fetchStatus();

        // Attendre qu'une bouteille soit détectée après le clic "Démarrer"
        if (!s.bottleExists) {
          if (Date.now() - startedAt > maxWaitMs) {
            stopPolling();
            decide({ bottleExists: false, isFilled: false, hasCap: false, valid: false, rejectionReason: 'no_bottle' });
          }
          return;
        }

        stopPolling();
        decide(s);
      } catch (e) {
        stopPolling();
        setStatus('error');
        setCurrentBottle(null);
      }
    }, pollIntervalMs);
  }, [status]);

  const resetMachine = useCallback(() => {
    stopPolling();
    setStatus('idle');
    setCurrentBottle(null);
  }, []);

  return {
    status,
    storageLevels,
    stats,
    currentBottle,
    broyageDuration,
    broyageFinished,
    broyageElapsedMs,
    insertBottle,
    resetMachine,
  };
};
