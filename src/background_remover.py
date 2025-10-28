# src/background_remover.py
from rembg import remove
from PIL import Image
import io
import os
import concurrent.futures

class SmartBackgroundRemover:
    def __init__(self, max_workers=4):
        """
        max_workers: jumlah thread paralel untuk mempercepat pemrosesan banyak gambar
        """
        self.max_workers = max_workers

    def remove_background(self, input_path, output_path, white_bg=False, transparan_bg=False):
        """Hapus background pada satu gambar."""
        try:
            with open(input_path, "rb") as i:
                input_image = i.read()

            # Gunakan rembg untuk hapus background
            output_image = remove(input_image)

            img = Image.open(io.BytesIO(output_image)).convert("RGBA")

            if white_bg:
                # ganti jadi background putih
                white = Image.new("RGBA", img.size, (255, 255, 255, 255))
                white.paste(img, (0, 0), img)
                white.convert("RGB").save(output_path, optimize=True, quality=95)
            else:
                # simpan transparan (default)
                img.save(output_path, optimize=True)

            print(f"[✅] {os.path.basename(input_path)} selesai → {output_path}")

        except Exception as e:
            print(f"[❌] Gagal memproses {input_path}: {e}")

    def batch_remove(self, input_folder, output_folder, transparan_bg=True, white_bg=False):
        """Proses semua gambar dalam folder secara paralel."""
        os.makedirs(output_folder, exist_ok=True)
        files = [
            f for f in os.listdir(input_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not files:
            print("⚠️ Tidak ada gambar di folder input.")
            return

        print(f"🔄 Memproses {len(files)} gambar secara paralel...\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for filename in files:
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                futures.append(executor.submit(
                    self.remove_background, input_path, output_path,
                    white_bg=white_bg, transparan_bg=transparan_bg
                ))

            # Tunggu semua selesai
            concurrent.futures.wait(futures)

        print("\n🎉 Semua gambar selesai diproses!")
