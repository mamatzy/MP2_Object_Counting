import cv2 as cv
import numpy as np

##====== Parameter Awal ======
## display
display_width = 1000
display_height = 800
## warna 
h_val, s_val, v_val = 0, 255, 255
## contour
minPanjang = 141
minLebar = 56
## Morpho
param_kernel = 10
## Logika Merge Bounding Box
batasLebarBesar = 200 #pembeda mobil dengan kaca 
gap_x_max = 290 #maksimal jarak horizontal untuk merge kaca kiri kanan

### mendingan kernel 10 trus yang bounding box kecil gabung aja
### paling bagus counting_result10.png tinggal 
# bounding box yang lebarnya kecil cari yang boundingbox lebarnya kecil
# terus kalau jarak horizontalnya dekat dan posisi y nya gak terlalu jauh, gabung aja bounding box nya

def maskingMaskingGaje(image, h_val, s_val, v_val, param_kernel):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower_moon = np.array([h_val, 50, 50])
    upper_moon = np.array([130, s_val, v_val])
    mask = cv.inRange(hsv, lower_moon, upper_moon)

    #  Morphological Closing 
    kernel = np.ones((param_kernel, param_kernel), np.uint8) 
    mask_closed = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    
    return mask_closed


def findContoul(mask, minLebar, minPanjang):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    contours_demensipas = []
    for i in contours:
        x, y, w, h = cv.boundingRect(i)
        
        dimensi_kecil = min(w, h)
        dimensi_besar = max(w, h)
        
        if dimensi_kecil >= minLebar and dimensi_besar >= minPanjang:
            contours_demensipas.append((x, y, w, h))
            
    return contours_demensipas

def gabungBoundingBox(mask, minLebar, minPanjang, batasLebarBesar, gap_x_max):
    boundingBoxes = findContoul(mask, minLebar, minPanjang)

    merged = []
    used = set()
    
    # Urutkan dari kiri ke kanan (Sumbu X)
    boundingBoxes.sort(key=lambda b: b[0])
    
    for i, (x1, y1, w1, h1) in enumerate(boundingBoxes):
        if i in used:
            continue
        
        group = [i]
        is_besar_1 = w1 >= batasLebarBesar
        
        for j in range(i + 1, len(boundingBoxes)):
            if j in used:
                continue
            
            x2, y2, w2, h2 = boundingBoxes[j]
            is_besar_2 = w2 >= batasLebarBesar
            
            # --- Menghitung Jarak ---
            # Jarak Kanan-Kiri (Sumbu X)
            gap_x = max(0, max(x1, x2) - min(x1 + w1, x2 + w2))
            # Jarak Atas-Bawah (Sumbu Y)
            gap_y = max(0, max(y1, y2) - min(y1 + h1, y2 + h2))
            
            # Menghitung Kesejajaran Vertikal (Untuk cek satu baris parkir)
            center_y1 = y1 + h1 / 2
            center_y2 = y2 + h2 / 2
            vertical_diff = abs(center_y1 - center_y2)
            
            # --- LOGIKA MERGE BARU ---
            
            # Aturan 1: Merge Mutlak (Jarak sangat dekat 0-10 di X dan Y)
            # Kita cek gap_y juga agar tidak merge dengan mobil di baris atas/bawahnya
            merge_mutlak = gap_x <= 20 and gap_y <= 10
            
            # Aturan 2: Merge Bounding Box Kecil (Kaca Kiri & Kanan)
            # - Keduanya harus kecil
            # - Jarak horizontal maksimal 200
            # - Harus dalam satu baris (vertical_diff kecil)
            merge_kecil = (not is_besar_1 and not is_besar_2) and (gap_x <= gap_x_max) and (vertical_diff <= 100)
            
            if merge_mutlak or merge_kecil:
                group.append(j)

        # Proses menggabungkan koordinat grup menjadi satu Bounding Box
        if group:
            x_min = min(boundingBoxes[k][0] for k in group)
            y_min = min(boundingBoxes[k][1] for k in group)
            x_max = max(boundingBoxes[k][0] + boundingBoxes[k][2] for k in group)
            y_max = max(boundingBoxes[k][1] + boundingBoxes[k][3] for k in group)
            
            merged.append((x_min, y_min, x_max - x_min, y_max - y_min))
            used.update(group)
    
    return merged

def gambarHasil(image, boundingBoxes, batasLebarBesar):
    result = image.copy()
    
    for (x, y, w, h) in boundingBoxes:
        # Cek hanya LEBAR (w) setelah proses merge
        if w >= batasLebarBesar:
            warna = (0, 255, 0)      # Hijau 
            ketebalan_font = 2
        else:
            warna = (0, 165, 255)    # Oranye 
            ketebalan_font = 1
        
        cv.rectangle(result, (x, y), (x + w, y + h), warna, 2)
    
    return result

def main(display_width, display_height, h_val, s_val, v_val, minLebar, minPanjang, param_kernel, batasLebarBesar, gap_x_max):

    while True:
        frame = cv.imread("parking_ori.jpg")

        mask = maskingMaskingGaje(frame, h_val, s_val, v_val, param_kernel)

        boundingBoxes = gabungBoundingBox(mask, minLebar, minPanjang, batasLebarBesar, gap_x_max)

        result = gambarHasil(frame, boundingBoxes, batasLebarBesar)

        #  MENAMPILKAN JUMLAH TOTAL MOBIL DI GAMBAR HASIL 
        total_mobil = len(boundingBoxes)
        teks_jumlah = f"Total Mobil: {total_mobil}"
        cv.putText(result, teks_jumlah, (40, 60), cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

        # tampilan nilai hsv
        status = f"H:{h_val} S:{s_val} V:{v_val}"
        cv.putText(frame, status, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        show_frame = cv.resize(frame, (display_width, display_height))
        show_result = cv.resize(result, (display_width, display_height))
        show_mask = cv.resize(mask, (display_width, display_height))

        cv.imshow('Original & Status', show_frame)
        cv.imshow('Result', show_result)
        cv.imshow('Mask (Hitam Putih)', show_mask)

        cv.imwrite(f"counting_mask{param_kernel}_gap{gap_x_max}.png", mask)
        cv.imwrite(f"counting_result{param_kernel}_gap{gap_x_max}.png", result)

        key = cv.waitKey(1) & 0xFF
        
        if key == 27: 
            break
        
        # Kontrol HUE (0-179)
        elif key == ord('q'): h_val = min(179, h_val + 1)
        elif key == ord('a'): h_val = max(0, h_val - 1)
        
        # Kontrol SATURATION (0-255)
        elif key == ord('w'): s_val = min(255, s_val + 5)
        elif key == ord('s'): s_val = max(0, s_val - 5)
        
        # Kontrol VALUE/Brightness (0-255)
        elif key == ord('e'): v_val = min(255, v_val + 5)
        elif key == ord('d'): v_val = max(0, v_val - 5)

    cv.destroyAllWindows()


if __name__ == "__main__":
    main(display_width, display_height, h_val, s_val, v_val, minLebar, minPanjang, param_kernel, batasLebarBesar, gap_x_max)
# mask hitam = 107, 255, 255
# mask merah = 10, 255, 255