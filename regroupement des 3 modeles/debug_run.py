import traceback
import sys
import faulthandler
faulthandler.enable()

try:
    from unified_bottle_detection import UnifiedBottleDetection
    detector = UnifiedBottleDetection()
    detector.webcam_mode()
except Exception as e:
    print(f"\n{'='*60}")
    print(f"ERREUR CAPTUREE: {type(e).__name__}: {e}")
    print(f"{'='*60}")
    traceback.print_exc()
    print(f"{'='*60}")
    input("Appuyez sur Entree...")
    sys.exit(1)
