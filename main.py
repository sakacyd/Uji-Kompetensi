"""Program Utama: Sistem Kasir & Inventaris (SmartPOS Lite).

Titik masuk (entry point) eksekusi program untuk Uji Kompetensi Keahlian Programmer.
"""
import sys
import logging
from app.database import DatabaseManager
from app.ui import run_cli_app

# Konfigurasi Logging untuk kebutuhan Debugging & Audit sistem
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MainApplication")


def seed_sample_data(db: DatabaseManager) -> None:
    """Prosedur pengisian data awal otomatis jika database masih kosong."""
    existing = db.get_all_products()
    if not existing:
        logger.info("Mengisi data awal produk...")
        # Array data sampel produk
        sample_items = [
            ("P01", "Buku Tulis Sinar Dunia 38L", 5000.0, 50, 0.0, 3500.0),
            ("P02", "Pulpen Gel Pilot G2 0.5", 15000.0, 30, 10.0, 11000.0), # Diskon 10%
            ("P03", "Kertas HVS A4 70gr Rim", 55000.0, 15, 5.0, 48000.0),   # Diskon 5%
            ("P04", "Penggaris Besi 30cm", 8000.0, 4, 0.0, 5000.0),          # Stok sedikit (<5)
        ]
        for code, name, price, stock, disc, cost in sample_items:
            db.save_product(code, name, price, stock, disc, cost)
        logger.info("Inisialisasi 4 data produk selesai.")


def main() -> None:
    """Fungsi utama program."""
    logger.info("Aplikasi SmartPOS Lite dimulai.")
    try:
        db = DatabaseManager(db_path="store.db")
        seed_sample_data(db)
        run_cli_app(db)
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    except Exception as exc:
        logger.critical("Fatal error pada aplikasi: %s", exc, exc_info=True)
    finally:
        logger.info("Aplikasi SmartPOS Lite ditutup secara normal.")


if __name__ == "__main__":
    main()
