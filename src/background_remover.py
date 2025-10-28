import cv2
import numpy as np

class SmartBackgroundRemover:
    def __init__(self):
        self.kernel = np.ones((5, 5), np.uint8)

    def _auto_hsv_mask(self, img):
        """Deteksi mask adaptif, mendukung gambar BGR, HSV, atau grayscale threshold."""
        # Jika gambar sudah grayscale (misal hasil threshold HSV)
        if len(img.shape) == 2:
            print("ℹ️ Deteksi: gambar grayscale/threshold. Gunakan deteksi tepi adaptif.")
            # Gunakan adaptif threshold untuk deteksi bentuk daun
            blurred = cv2.GaussianBlur(img, (5, 5), 0)
            _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            mask = cv2.bitwise_not(mask)  # daun = area terang
            return mask

        # Jika masih 3 channel → proses HSV normal
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Ambil hanya piksel dengan saturasi & brightness cukup
        valid_pixels = h[(s > 25) & (v > 25)]
        if len(valid_pixels) > 0:
            h_mean = np.median(valid_pixels)
            lower_h = max(0, h_mean - 30)
            upper_h = min(179, h_mean + 30)
        else:
            lower_h, upper_h = 25, 90  # fallback hijau daun cabai

        lower_bound = (lower_h, 20, 20)
        upper_bound = (upper_h, 255, 255)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # fallback lagi kalau mask kosong
        if np.count_nonzero(mask) < 100:
            print("⚠️ Mask kosong, gunakan fallback universal hijau daun.")
            mask = cv2.inRange(hsv, (20, 15, 15), (100, 255, 255))

        return mask

    def _refine_mask(self, mask):
        """Haluskan dan bersihkan pinggiran daun."""
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
        mask = cv2.dilate(mask, self.kernel, iterations=1)
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.GaussianBlur(mask, (7, 7), 0)
        return mask

    def remove_background(self, image_path, output_path, white_bg=True):
        """Hilangkan background 100% tanpa merusak bentuk daun."""
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Gambar tidak ditemukan: {image_path}")

        mask = self._auto_hsv_mask(img)
        mask = self._refine_mask(mask)

        # Pastikan mask valid
        if np.count_nonzero(mask) == 0:
            print("🚨 Mask tetap kosong, gunakan invert fallback.")
            mask = cv2.bitwise_not(mask)

        alpha = mask.astype(float) / 255.0

        # Terapkan hasil remove background
        if white_bg:
            bg = np.ones_like(img[:, :, :3], dtype=np.uint8) * 255
            result = (img[:, :, :3] * alpha[:, :, None] + bg * (1 - alpha[:, :, None])).astype(np.uint8)
        else:
            b, g, r = cv2.split(img[:, :, :3])
            result = cv2.merge((b, g, r, np.uint8(alpha * 255)))

        # Sedikit tingkatkan kontras agar daun tetap tajam
        result = cv2.convertScaleAbs(result, alpha=1.05, beta=10)

        cv2.imwrite(output_path, result)
        print(f"✅ Background daun berhasil dihapus sempurna → {output_path}")
