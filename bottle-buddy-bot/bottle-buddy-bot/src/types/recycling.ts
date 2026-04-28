export type MachineStatus = 
  | 'idle'           // En attente d'une bouteille
  | 'detecting'      // Détection en cours
  | 'valid'          // Bouteille validée
  | 'invalid'        // Bouteille rejetée (bouchon présent)
  | 'crushing'       // Broyage en cours
  | 'sorting'        // Tri en cours
  | 'complete'       // Cycle terminé
  | 'error';         // Erreur

export type RejectionReason = 'cap_present' | 'filled' | 'no_bottle' | 'not_pet' | 'damaged' | 'unknown';

export type PETType = 'transparent' | 'colored';

export interface StorageLevel {
  type: PETType;
  label: string;
  currentLevel: number;
  maxLevel: number;
}

export interface RecyclingStats {
  totalBottles: number;
  todayBottles: number;
  totalWeight: number;
  co2Saved: number;
  transparentCount: number;
  coloredCount: number;
}

export interface BottleInfo {
  petType: PETType;
  weight: number;
  isValid: boolean;
  hasCap: boolean;
  isFilled: boolean;
  rejectionReason?: RejectionReason;
}
