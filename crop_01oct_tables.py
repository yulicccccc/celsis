import cv2

for p in range(1, 9):
    im = cv2.imread(rf"C:\Users\qchen\temp_celsis_01oct26\page_{p:02d}.png")
    h, w, _ = im.shape
    # Crop the table from 18% to 60%
    crop = im[int(h * 0.18):int(h * 0.60), int(w * 0.04):int(w * 0.96)]
    cv2.imwrite(f"crop_01oct_p{p:02d}.png", crop)

print("Saved crop_01oct_p01.png to p08.png")
