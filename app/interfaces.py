"""Package app.interfaces: Mendefinisikan interface dan kontrak data.

Menerapkan konsep Interface Pemrograman Berorientasi Objek (OOP)
sesuai standar kompetensi LSP.
"""
from abc import ABC, abstractmethod


class IProduct(ABC):
    """Interface untuk entitas produk dalam sistem."""

    @abstractmethod
    def calculate_total(self, quantity: int) -> float:
        """Menghitung total harga berdasarkan kuantitas yang dibeli."""
        pass

    @abstractmethod
    def get_info(self) -> str:
        """Mendapatkan representasi ringkas informasi produk."""
        pass
