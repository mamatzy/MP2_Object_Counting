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

def maskingMaskingGaje(image, h_val, s_val, v_val):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Menentukan range 
    lower_moon = np.array([h_val, 50, 50])
    upper_moon = np.array([130, s_val, v_val])

    mask = cv.inRange(hsv, lower_moon, upper_moon)

    return mask


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


def gabungBoundingBox(mask, minLebar, minPanjang):

    boundingBoxes = []

    boundingBoxes = findContoul(mask, minLebar, minPanjang)

    merged = []
    used = set()
    
    for i, (x1, y1, w1, h1) in enumerate(boundingBoxes):
        if i in used:
            continue
        
        group = [i]
        for j in range(i + 1, len(boundingBoxes)):
            if j in used:
                continue
            
            x2, y2, w2, h2 = boundingBoxes[j]
            
            xOverlap = not (x1 + w1 < x2 or x2 + w2 < x1)
            yOverlap = not (y1 + h1 < y2 or y2 + h2 < y1)
            
            if xOverlap and yOverlap:
                group.append(j)

        # Gabungkan bounding box dalam grup
        if group:
            x_min = min(boundingBoxes[k][0] for k in group)
            y_min = min(boundingBoxes[k][1] for k in group)
            x_max = max(boundingBoxes[k][0] + boundingBoxes[k][2] for k in group)
            y_max = max(boundingBoxes[k][1] + boundingBoxes[k][3] for k in group)
            
            merged.append((x_min, y_min, x_max - x_min, y_max - y_min))
            used.update(group)
    
    return merged

def gambarHasil(image, boundingBoxes):
    result = image.copy()
    
    for i, (x, y, w, h) in enumerate(boundingBoxes, 1):
        cv.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return result

def main(display_width, display_height, h_val, s_val, v_val, minLebar, minPanjang):

    while True:
        frame = cv.imread("parking_ori.jpg")

        mask = maskingMaskingGaje(frame, h_val, s_val, v_val)

        boundingBoxes = gabungBoundingBox(mask, minLebar, minPanjang)

        result = gambarHasil(frame, boundingBoxes)

        # tampilan nilai hsv
        status = f"H:{h_val} S:{s_val} V:{v_val}"
        cv.putText(frame, status, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        show_frame = cv.resize(frame, (display_width, display_height))
        show_result = cv.resize(result, (display_width, display_height))
        show_mask = cv.resize(mask, (display_width, display_height))

        cv.imshow('Original & Status', show_frame)
        cv.imshow('Result', show_result)
        cv.imshow('Mask (Hitam Putih)', show_mask)

        cv.imwrite("counting_mask.png", mask)
        cv.imwrite("counting_result.png", result)

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
    main(display_width, display_height, h_val, s_val, v_val, minLebar, minPanjang)
# mask hitam = 107, 255, 255
# mask merah = 10, 255, 255