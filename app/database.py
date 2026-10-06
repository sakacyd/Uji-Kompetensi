"""Package app.database: Penanganan akses basis data relasional SQLite.

Memenuhi persyaratan:
- Penyimpanan persisten (membaca dan menyimpan data di media penyimpan)
- Akses basis data relasional (DDL & DML SQL)
- Penggunaan array / list data
- Penanganan transaksi dan integritas relasional
"""
import sqlite3
import os
from typing import List, Optional, Tuple


class DatabaseManager:
    """Mengelola koneksi basis data SQLite dan operasi CRUD."""

    def __init__(self, db_path: str = "store.db") -> None:
        """Inisialisasi manajer database dengan path file database."""
        self.db_path = db_path
        self._shared_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Membuka dan mengembalikan koneksi SQLite."""
        if self._shared_conn is not None:
            return self._shared_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        """Inisialisasi skema tabel jika belum tersedia (DDL)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    discount_pct REAL DEFAULT 0.0,
                    cost_price REAL DEFAULT 0.0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    product_code TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (product_code) REFERENCES products(code)
                )
            """)
            conn.commit()

    def save_product(
        self,
        code: str,
        name: str,
        price: float,
        stock: int,
        discount_pct: float = 0.0,
        cost_price: float = 0.0
    ) -> None:
        """Menyimpan atau memperbarui data produk (INSERT / UPDATE)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (code, name, price, stock, discount_pct, cost_price)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name = excluded.name,
                    price = excluded.price,
                    stock = excluded.stock,
                    discount_pct = excluded.discount_pct,
                    cost_price = excluded.cost_price
            """, (code, name, price, stock, discount_pct, cost_price))
            conn.commit()

    def get_all_products(self) -> List[Tuple]:
        """Membaca seluruh data produk dari tabel (Array list of tuples)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT code, name, price, stock, discount_pct, cost_price "
                "FROM products ORDER BY code ASC"
            )
            # Mengembalikan array / list data
            return cursor.fetchall()

    def get_product_by_code(self, code: str) -> Optional[Tuple]:
        """Mencari spesifik produk berdasarkan kode."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT code, name, price, stock, discount_pct, cost_price "
                "FROM products WHERE code = ?",
                (code.upper(),)
            )
            return cursor.fetchone()

    def record_sale(self, code: str, quantity: int, total_price: float) -> bool:
        """Mencatat transaksi penjualan dan mengurangi stok barang."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM products WHERE code = ?", (code.upper(),))
            row = cursor.fetchone()
            if not row or row[0] < quantity:
                return False

            new_stock = row[0] - quantity
            cursor.execute(
                "UPDATE products SET stock = ? WHERE code = ?",
                (new_stock, code.upper())
            )
            cursor.execute("""
                INSERT INTO transactions (product_code, quantity, total_price)
                VALUES (?, ?, ?)
            """, (code.upper(), quantity, total_price))
            conn.commit()
            return True

    def delete_product(self, code: str) -> bool:
        """Menghapus produk dari basis data (DELETE)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE code = ?", (code.upper(),))
            conn.commit()
            return cursor.rowcount > 0
