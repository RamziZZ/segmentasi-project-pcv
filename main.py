import os
from src.background_remover import SmartBackgroundRemover

if __name__ == "__main__":
    input_folder = "data/input"
    output_folder = "data/output"

    remover = SmartBackgroundRemover()

    # Pastikan folder output ada
    os.makedirs(output_folder, exist_ok=True)

    # Loop semua file di folder input
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            print(f"[🔄] Memproses: {filename} ...")
            remover.remove_background(input_path, output_path, transparan_bg=True)
            print(f"[✅] Selesai → {output_path}")

    print("\n🎉 Semua gambar selesai diproses!")
