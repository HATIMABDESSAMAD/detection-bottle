const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(cors());
app.use(express.json());

// Chemin du fichier JSON temps-réel généré par unified_bottle_detection.py
// __dirname = .../bottle-buddy-bot/bottle-buddy-bot/backend → remonter 3 niveaux vers regroupement des 3 modeles
const REALTIME_STATUS_PATH = path.resolve(__dirname, '..', '..', '..', 'regroupement des 3 modeles', 'data_logs', 'realtime_status.json');

function parseOuiNon(value) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value === 1;
  if (typeof value !== 'string') return false;
  const v = value.trim().toLowerCase();
  return v === 'oui' || v === 'true' || v === '1';
}

function getRejectionReason({ bottleExists, isFilled, hasCap }) {
  if (!bottleExists) return 'no_bottle';
  if (hasCap) return 'cap_present';
  if (isFilled) return 'filled';
  return null;
}

function toArduinoMessage({ bottleExists, numBottles, isFilled, hasCap }) {
  // Format utilisé par Python: <B,N,F,C> avec F=non_remplie, C=sans_bouchon
  const b = bottleExists ? 1 : 0;
  const n = Number.isFinite(numBottles) ? numBottles : (bottleExists ? 1 : 0);
  const notFilled = isFilled ? 0 : 1;
  const noCap = hasCap ? 0 : 1;
  return {
    bits: { b, n, notFilled, noCap },
    message: `<${b},${n},${notFilled},${noCap}>`,
  };
}

// Simule la détection d'une bouteille
app.post('/detect', (req, res) => {
  // Appel du script Python unifié
  const { imagePath } = req.body;
  const { spawn } = require('child_process');
  // Chemin vers unified_bottle_detection.py
  const pythonScript = '../../regroupement-des-3-modeles/unified_bottle_detection.py';
  // On suppose que unified_bottle_detection.py accepte --api et optionnellement --image <imagePath>
  const args = ['--api'];
  if (imagePath) args.push('--image', imagePath);
  const python = spawn('python', [pythonScript, ...args]);

  let output = '';
  python.stdout.on('data', (data) => {
    output += data.toString();
  });
  python.stderr.on('data', (data) => {
    console.error('Erreur Python:', data.toString());
  });
  python.on('close', (code) => {
    try {
      // On suppose que le script Python retourne un JSON
      const result = JSON.parse(output);
      res.json(result);
    } catch (e) {
      res.status(500).json({ error: 'Erreur de parsing ou exécution Python', details: output });
    }
  });
});

// Statut temps-réel provenant du modèle (le modèle tourne déjà en arrière-plan)
app.get('/status', (req, res) => {
  try {
    if (!fs.existsSync(REALTIME_STATUS_PATH)) {
      return res.status(404).json({
        error: 'realtime_status.json introuvable',
        expectedPath: REALTIME_STATUS_PATH,
      });
    }

    const rawText = fs.readFileSync(REALTIME_STATUS_PATH, 'utf-8');
    const raw = JSON.parse(rawText);

    const bottleExists = parseOuiNon(raw.bouteille_existe);
    const numBottles = Number(raw.nombre_bouteilles ?? (bottleExists ? 1 : 0));
    const isFilled = parseOuiNon(raw.bouteille_remplie);
    const hasCap = parseOuiNon(raw.bouteille_avec_bouchon);

    const valid = bottleExists && !isFilled && !hasCap;
    const rejectionReason = getRejectionReason({ bottleExists, isFilled, hasCap });
    const arduino = toArduinoMessage({ bottleExists, numBottles, isFilled, hasCap });

    res.json({
      timestamp: raw.timestamp ?? null,
      bottleExists,
      numBottles,
      isFilled,
      hasCap,
      valid,
      rejectionReason,
      arduino,
      raw,
    });
  } catch (e) {
    res.status(500).json({ error: 'Erreur lecture/parsing status', details: String(e) });
  }
});

// Simule les statistiques
app.get('/stats', (req, res) => {
  res.json({
    totalBottles: 123,
    todayBottles: 12,
    totalWeight: 45.6,
    co2Saved: 8.9,
    transparentCount: 80,
    coloredCount: 43
  });
});

const CSV_STATS_PATH = 'G:\\Mon Drive\\csv file robotique\\detection_unifie.csv';

// Statistiques calculées depuis le CSV unifié
app.get('/csv-stats', (req, res) => {
  try {
    if (!fs.existsSync(CSV_STATS_PATH)) {
      return res.json({ totalBottles: 0, todayBottles: 0, totalWeight: 0, co2Saved: 0, transparentCount: 0, coloredCount: 0, lastBottle: null });
    }
    const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const lines = fs.readFileSync(CSV_STATS_PATH, 'utf-8').split('\n').filter(l => l.trim());
    const rows = lines.slice(1); // ignorer header
    let totalBottles = 0;
    let todayBottles = 0;
    for (const row of rows) {
      const cols = row.split(',');
      if (cols.length < 5) continue;
      const statut = cols[4].trim();
      if (statut !== 'ACCEPTEE') continue;
      totalBottles++;
      const ts = cols[0].trim(); // "2026-04-26 18:05:23.123"
      if (ts.startsWith(today)) todayBottles++;
    }
    const totalWeight = parseFloat((totalBottles * 0.03).toFixed(2));
    const co2Saved = parseFloat((totalWeight * 2.5).toFixed(2));
    // Dernière bouteille (toutes lignes, pas seulement ACCEPTEE)
    const allValidRows = rows.filter(r => r.split(',').length >= 5);
    const lastRow = allValidRows[allValidRows.length - 1];
    let lastBottle = null;
    if (lastRow) {
      const cols = lastRow.split(',');
      const isFilled = cols[2].trim() === 'REMPLIE';
      const hasCap = cols[3].trim() === 'OUI';
      const valid = cols[4].trim() === 'ACCEPTEE';
      lastBottle = { isFilled, hasCap, valid, timestamp: cols[0].trim() };
    }
    res.json({ totalBottles, todayBottles, totalWeight, co2Saved, transparentCount: totalBottles, coloredCount: 0, lastBottle });
  } catch (e) {
    res.status(500).json({ error: 'Erreur lecture CSV stats', details: String(e) });
  }
});

// Statut du broyage : retourne finished + durationMs depuis le JSON temps-réel
app.get('/broyage-finished', (req, res) => {
  try {
    if (!fs.existsSync(REALTIME_STATUS_PATH)) {
      return res.json({ finished: false, durationMs: null });
    }
    const raw = JSON.parse(fs.readFileSync(REALTIME_STATUS_PATH, 'utf-8'));
    res.json({
      finished: raw.broyage_finished === true,
      durationMs: raw.broyage_duration_ms ?? null,
    });
  } catch (e) {
    res.json({ finished: false, durationMs: null });
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
