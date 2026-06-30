import cv2
import face_recognition
import pickle
import sys
import os

sys.path.append(os.path.dirname(__file__))
from db import init_db, add_student

def enroll_student(student_id, full_name):
    init_db()
    cam = cv2.VideoCapture(0)
    print("Press SPACE to capture the photo, or ESC to cancel.")

    encoding = None
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to access camera.")
            break

        cv2.imshow("Enroll - Press SPACE to capture", frame)
        key = cv2.waitKey(1)

        if key % 256 == 27:  # ESC
            print("Cancelled.")
            break
        elif key % 256 == 32:  # SPACE
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if len(face_locations) != 1:
                print("Please make sure exactly ONE face is visible. Try again.")
                continue

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            encoding = face_encodings[0]
            print("Face captured successfully.")
            break

    cam.release()
    cv2.destroyAllWindows()

    if encoding is not None:
        encoding_bytes = pickle.dumps(encoding)
        add_student(student_id, full_name, encoding_bytes)
        print(f"Enrolled: {full_name} ({student_id})")
    else:
        print("No face was enrolled.")

if __name__ == "__main__":
    sid = input("Enter Student ID: ")
    name = input("Enter Full Name: ")
    enroll_student(sid, name)
