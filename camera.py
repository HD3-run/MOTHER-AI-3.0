# vision/camera.py

import cv2

def capture_image():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[Camera] Failed to open webcam.")
        return None

    print("[Camera] Press 'Space' to capture or 'Esc' to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("MOTHER - Camera View", frame)

        key = cv2.waitKey(1)
        if key % 256 == 27:
            # ESC pressed
            print("[Camera] Cancelled.")
            break
        elif key % 256 == 32:
            # Space pressed
            filename = "data/mother_snapshot.jpg"
            cv2.imwrite(filename, frame)
            print(f"[Camera] Image saved to {filename}")
            cap.release()
            cv2.destroyAllWindows()
            return filename

    cap.release()
    cv2.destroyAllWindows()
    return None
