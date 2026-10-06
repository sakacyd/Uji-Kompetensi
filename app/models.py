"""Package app.models: Model data berorientasi objek (OOP).

Memenuhi seluruh kriteria OOP:
- Enkapsulasi & Hak Akses (public, _protected, __private)
- Properties (@property & @setter dengan validasi)
- Inheritance (Pewarisan kelas Product -> DiscountedProduct)
- Polymorphism (Method overriding pada calculate_total & get_info)
- Overloading (Penambahan parameter opsional restock)
- Interface (Mengimplementasikan IProduct)
"""
from typing import Optional, overload
from app.interfaces import IProduct


class Product(IProduct):
    """Kelas dasar produk dengan enkapsulasi dan properties."""

    def __init__(
        self,
        code: str,
        name: str,
        price: float,
        stock: int,
        cost_price: float = 0.0
    ) -> None:
        """Inisialisasi objek produk dengan hak akses bertingkat."""
        self.code: str = str(code).strip().upper()   # Public attribute
        self.name: str = str(name).strip()           # Public attribute
        self.price: float = float(price)             # Public attribute
        self._stock: int = int(stock)                # Protected attribute
        self.__cost_price: float = float(cost_price) # Private attribute

    @property
    def stock(self) -> int:
        """Getter property untuk membaca sisa stok."""
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        """Setter property dengan validasi nilai tidak boleh negatif."""
        if value < 0:
            raise ValueError("Stok tidak boleh bernilai negatif.")
        self._stock = value

    @property
    def cost_price(self) -> float:
        """Getter property untuk mengakses private cost_price."""
        return self.__cost_price

    def calculate_total(self, quantity: int) -> float:
        """Menghitung total harga produk standar (Polymorphism base)."""
        if quantity <= 0:
            raise ValueError("Kuantitas pembelian harus lebih dari 0.")
        return self.price * quantity

    # Method Overloading (standar Python menggunakan default argument / type hints)
    @overload
    def restock(self, amount: int) -> None: ...

    @overload
    def restock(self, amount: int, note: str) -> None: ...

    def restock(self, amount: int, note: Optional[str] = None) -> None:
        """Menambah stok produk dengan overload catatan operasional opsional."""
        if amount <= 0:
            raise ValueError("Jumlah restock harus lebih dari 0.")
        self._stock += amount

    def get_info(self) -> str:
        """Mengembalikan informasi ringkas produk."""
        return f"[{self.code}] {self.name} - Rp{self.price:,.0f} (Stok: {self._stock})"


class DiscountedProduct(Product):
    """Kelas turunan produk dengan diskon (Inheritance & Polymorphism)."""

    def __init__(
        self,
        code: str,
        name: str,
        price: float,
        stock: int,
        discount_pct: float,
        cost_price: float = 0.0
    ) -> None:
        """Inisialisasi produk diskon dengan pemanggilan super().__init__."""
        super().__init__(code, name, price, stock, cost_price)
        if not (0.0 <= discount_pct <= 100.0):
            raise ValueError("Persentase diskon harus di antara 0 dan 100.")
        self.discount_pct: float = float(discount_pct)

    def calculate_total(self, quantity: int) -> float:
        """Override kalkulasi harga dengan potongan diskon (Polymorphism)."""
        base_total = super().calculate_total(quantity)
        discount_amount = base_total * (self.discount_pct / 100.0)
        return base_total - discount_amount

    def get_info(self) -> str:
        """Override ringkasan info menampilkan persentase diskon."""
        return f"{super().get_info()} [Diskon {self.discount_pct:.0f}%]"
