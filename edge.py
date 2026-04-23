import cv2 
import numpy as np

display_width = 1000
display_height = 480


lower = 100

upper = 200
 
img = cv2.imread("parking_ori.jpg")

while(1):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    edge = cv2.Canny(gray, lower, upper)
    
    canny_edges = cv2.resize(edge, (display_width, display_height))

    cv2.imshow('Edge Detected Image', canny_edges)


    # control canny
    key = cv2.waitKey(1) & 0xFF

    if key == ord('z'):
        break

    elif key == ord('q'): lower = min(255, lower + 1)
    elif key == ord('a'): lower = max(0, lower - 1)
    
    # Kontrol SATURATION (0-255)
    elif key == ord('w'): upper = min(255, upper + 5)
    elif key == ord('s'): upper = max(0, upper - 5)

    print (f"Lower: {lower}, Upper: {upper}")
 
cv2.destroyAllWindows()

## lower 72 upper 130