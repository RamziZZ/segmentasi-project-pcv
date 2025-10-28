from src.background_remover import SmartBackgroundRemover

if __name__ == "__main__":
    input_path = "data/input/sehat_20.png"
    output_path_white = "data/output/sehat_20.png"
    # output_path_transparent = "data/output/hasil_transparan.png"

    remover = SmartBackgroundRemover()

    # === Hasil background putih ===
    remover.remove_background(input_path, output_path_white, white_bg=True)

    # === Hasil background transparan (opsional) ===
    # remover.remove_background(input_path, output_path_transparent, white_bg=False)
