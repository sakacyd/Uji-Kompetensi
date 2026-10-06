"""Package app.ui: Antarmuka pengguna terminal modern dengan Rich library.

Memenuhi persyaratan:
- Interface input dan output (tampilan) pengguna
- Struktur kontrol percabangan (if..elif..else)
- Struktur kontrol pengulangan (while, for)
- Prosedur dan fungsi
- Pemanfaatan Array / List
- Pemanfaatan library eksternal (Rich)
"""
import logging
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from app.database import DatabaseManager
from app.models import Product, DiscountedProduct

console = Console()
logger = logging.getLogger("AppUI")


def display_banner() -> None:
    """Prosedur untuk menampilkan banner antarmuka aplikasi."""
    banner_text = (
        "[bold cyan]SISTEM KASIR & INVENTARIS (SMARTPOS LITE)[/bold cyan]\n"
        "[dim]Uji Kompetensi Keahlian Programmer - LSP Informatika[/dim]"
    )
    console.print(Panel(banner_text, expand=False, border_style="cyan"))


def render_product_table(products_data: List[Tuple]) -> None:
    """Prosedur untuk menampilkan array data produk dalam bentuk tabel Rich.

    Mengimplementasikan iterasi struktur pengulangan (for-loop) pada Array.
    """
    table = Table(title="Daftar Stok Produk", border_style="bright_blue", show_lines=True)
    table.add_column("No", justify="center", style="dim", width=4)
    table.add_column("Kode", style="bold yellow")
    table.add_column("Nama Produk", style="white")
    table.add_column("Harga (Rp)", justify="right", style="green")
    table.add_column("Stok", justify="center")
    table.add_column("Tipe / Status", justify="center", style="magenta")

    # Menggunakan pengulangan for untuk menelusuri array/list
    for idx, row in enumerate(products_data, start=1):
        code, name, price, stock, discount, _ = row
        tipe = f"Diskon {discount:.0f}%" if discount > 0 else "Reguler"
        stock_style = "[bold red]" if stock <= 5 else "[green]"
        table.add_row(
            str(idx),
            str(code),
            str(name),
            f"{price:,.0f}",
            f"{stock_style}{stock}[/]",
            tipe
        )

    console.print(table)


def run_cli_app(db: DatabaseManager) -> None:
    """Fungsi utama pengendali alur logika dan menu program."""
    display_banner()

    # Struktur pengulangan utama (while loop)
    while True:
        console.print("\n[bold yellow]=== MENU UTAMA ===[/bold yellow]")
        console.print("1. Lihat Daftar Produk")
        console.print("2. Tambah / Ubah Produk")
        console.print("3. Transaksi Penjualan (Kasir)")
        console.print("4. Hapus Produk")
        console.print("5. Keluar")

        choice = Prompt.ask("Pilih menu", choices=["1", "2", "3", "4", "5"], default="1")

        # Struktur percabangan (if..elif..else)
        if choice == "1":
            # Membaca data array dari database
            items = db.get_all_products()
            if not items:
                console.print("[yellow]Informasi: Belum ada data produk di basis data.[/yellow]")
            else:
                render_product_table(items)

        elif choice == "2":
            try:
                code = input("Kode Produk (misal: P01): ").strip().upper()
                if not code:
                    console.print("[red]Kode produk tidak boleh kosong![/red]")
                    continue

                name = input("Nama Produk: ").strip()
                if not name:
                    console.print("[red]Nama produk tidak boleh kosong![/red]")
                    continue

                price = float(input("Harga Jual (Rp): "))
                stock = int(input("Stok Awal: "))
                disc = float(input("Diskon % (0 jika reguler): ") or 0)
                cost = float(input("Harga Modal (default 0): ") or 0)

                # Menerapkan OOP & Polymorphism saat membuat instansiasi objek
                if disc > 0:
                    item = DiscountedProduct(code, name, price, stock, disc, cost)
                else:
                    item = Product(code, name, price, stock, cost)

                db.save_product(
                    item.code,
                    item.name,
                    item.price,
                    item.stock,
                    getattr(item, "discount_pct", 0.0),
                    item.cost_price
                )
                console.print(f"[bold green]Sukses:[/] {item.get_info()} berhasil disimpan.")
            except ValueError as err:
                logger.error("Terjadi kesalahan input data: %s", err)
                console.print(f"[bold red]Error Input:[/] {err}")

        elif choice == "3":
            code = input("Masukkan Kode Produk yang dibeli: ").strip().upper()
            row = db.get_product_by_code(code)
            if not row:
                console.print(f"[bold red]Produk dengan kode '{code}' tidak ditemukan.[/bold red]")
                continue

            _, name, price, stock, disc, cost = row
            item = DiscountedProduct(code, name, price, stock, disc, cost) if disc > 0 else Product(code, name, price, stock, cost)

            console.print(f"Produk: [bold]{item.name}[/] | Stok: [cyan]{item.stock}[/] | Harga: Rp{item.price:,.0f}")
            try:
                qty = int(input("Jumlah Beli: "))
                if qty <= 0:
                    console.print("[bold red]Jumlah beli harus minimal 1.[/bold red]")
                    continue
                if qty > item.stock:
                    console.print(f"[bold red]Stok tidak cukup! Stok saat ini: {item.stock}[/bold red]")
                    continue

                # Polymorphic calculation (berbeda untuk Product vs DiscountedProduct)
                total = item.calculate_total(qty)
                if db.record_sale(item.code, qty, total):
                    receipt = (
                        f"[bold green]TRANSAKSI BERHASIL[/bold green]\n"
                        f"Kode: {item.code}\n"
                        f"Nama: {item.name}\n"
                        f"Jumlah: {qty} unit\n"
                        f"Total Bayar: [bold yellow]Rp{total:,.0f}[/bold yellow]"
                    )
                    console.print(Panel(receipt, title="Struk Transaksi", border_style="green"))
            except ValueError:
                console.print("[bold red]Input jumlah harus berupa angka bilangan bulat![/bold red]")

        elif choice == "4":
            code = input("Masukkan kode produk yang ingin dihapus: ").strip().upper()
            if db.delete_product(code):
                console.print(f"[bold green]Produk {code} berhasil dihapus dari database.[/bold green]")
            else:
                console.print(f"[bold red]Gagal: Produk {code} tidak ditemukan.[/bold red]")

        elif choice == "5":
            console.print("[bold cyan]Terima kasih telah menggunakan SmartPOS Lite. Sesi berakhir.[/bold cyan]")
            break
