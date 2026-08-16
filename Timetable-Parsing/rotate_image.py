import cv2

def rotate_270(img_path, output_path):
    img = cv2.imread(img_path)
    # Rotate 90 degrees counter-clockwise (270 clockwise)
    rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(output_path, rotated)
    print(f"Correctly oriented upright timetable saved to: {output_path}")

if __name__ == "__main__":
    rotate_270("another timetable.jpeg", "another_timetable_upright.jpeg")
