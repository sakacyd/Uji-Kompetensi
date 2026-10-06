"""Pengujian Unit Program (Unit Testing).

Memenuhi kriteria kompetensi: Melaksanakan Pengujian Unit Program (FR-MUK.04 Poin h).
Menggunakan modul bawaan unittest untuk menguji seluruh logika inti aplikasi.
"""
import unittest
from app.models import Product, DiscountedProduct
from app.database import DatabaseManager


class TestProductOOP(unittest.TestCase):
    """Pengujian komponen Pemrograman Berorientasi Objek (OOP)."""

    def setUp(self):
        """Mempersiapkan objek uji sebelum setiap pengujian dijalankan."""
        self.item = Product("B01", "Buku Gambar", 10000.0, 20, 7000.0)
        self.disc_item = DiscountedProduct("B02", "Buku Tulis", 10000.0, 15, 20.0, 6000.0)

    def test_encapsulation_and_properties(self):
        """Menguji getter dan setter properties serta validasi batas nilai."""
        self.assertEqual(self.item.stock, 20)
        self.item.stock = 25
        self.assertEqual(self.item.stock, 25)

        # Validasi: stok tidak boleh negatif
        with self.assertRaises(ValueError):
            self.item.stock = -5

    def test_private_attribute_access(self):
        """Menguji akses atribut privat via property cost_price."""
        self.assertEqual(self.item.cost_price, 7000.0)

    def test_polymorphism_calculate_total(self):
        """Menguji kalkulasi total harga biasa vs diskon (Polymorphism)."""
        # Produk reguler: 10.000 * 2 = 20.000
        self.assertEqual(self.item.calculate_total(2), 20000.0)

        # Produk diskon 20%: (10.000 * 2) - 20% = 16.000
        self.assertEqual(self.disc_item.calculate_total(2), 16000.0)

    def test_method_overloading_restock(self):
        """Menguji method restock dengan variasi argumen (Overloading)."""
        self.item.restock(5)
        self.assertEqual(self.item.stock, 25)

        self.item.restock(10, note="Pengiriman supplier batch 2")
        self.assertEqual(self.item.stock, 35)

        with self.assertRaises(ValueError):
            self.item.restock(0)


class TestDatabaseManager(unittest.TestCase):
    """Pengujian komponen Akses Basis Data (Database Access)."""

    def setUp(self):
        """Menggunakan database SQLite in-memory (:memory:) untuk isolasi pengujian."""
        self.db = DatabaseManager(db_path=":memory:")

    def test_save_and_retrieve_product(self):
        """Menguji penyimpanan dan pembacaan produk."""
        self.db.save_product("T01", "Tas Sekolah", 150000.0, 10, 0.0, 100000.0)
        product = self.db.get_product_by_code("T01")
        self.assertIsNotNone(product)
        self.assertEqual(product[1], "Tas Sekolah")
        self.assertEqual(product[2], 150000.0)
        self.assertEqual(product[3], 10)

    def test_record_sale_reduces_stock(self):
        """Menguji transaksi penjualan dan pengurangan stok di database."""
        self.db.save_product("T02", "Tempat Pensil", 20000.0, 10, 0.0, 12000.0)
        success = self.db.record_sale("T02", 3, 60000.0)
        self.assertTrue(success)

        # Cek sisa stok
        product = self.db.get_product_by_code("T02")
        self.assertEqual(product[3], 7)

    def test_record_sale_insufficient_stock(self):
        """Menguji transaksi ditolak ketika stok tidak mencukupi."""
        self.db.save_product("T03", "Penghapus", 3000.0, 2, 0.0, 1500.0)
        success = self.db.record_sale("T03", 5, 15000.0)
        self.assertFalse(success)

        # Stok harus tetap 2
        product = self.db.get_product_by_code("T03")
        self.assertEqual(product[3], 2)

    def test_delete_product(self):
        """Menguji penghapusan produk dari database."""
        self.db.save_product("T04", "Spidol", 9000.0, 5, 0.0, 6000.0)
        deleted = self.db.delete_product("T04")
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_product_by_code("T04"))


if __name__ == "__main__":
    unittest.main()
