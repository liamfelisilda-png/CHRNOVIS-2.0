import cv2
import face_recognition
import pickle
import numpy as np
import sys
import os
import time

sys.path.append(os.path.dirname(__file__))
from db import init_db, get_all_students, log_attendance

def load_known_faces():
    students = get_all_students()
    known_encodings = []
    known_ids = []
    known_names = {}

    for student_id, full_name, encoding_bytes in students:
        encoding = pickle.loads(encoding_bytes)
        known_encodings.append(encoding)
        known_ids.append(student_id)
        known_names[student_id] = full_name

    return known_encodings, known_ids, known_names

def run_scanner():
    init_db()
    known_encodings, known_ids, known_names = load_known_faces()

    if not known_encodings:
        print("No students enrolled yet. Run enroll.py first.")
        return

    cam = cv2.VideoCapture(0)
    print("Scanning for faces. Press ESC to quit.")

    last_seen = {}  # avoid spamming logs for the same face every frame
    cooldown_seconds = 10

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name_display = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                student_id = known_ids[match_index]
                name_display = known_names[student_id]

                now = time.time()
                if student_id not in last_seen or (now - last_seen[student_id]) > cooldown_seconds:
                    status, logged_time = log_attendance(student_id)
                    last_seen[student_id] = now
                    if status == "time_in":
                        print(f"[TIME IN] {name_display} at {logged_time}")
                    elif status == "time_out":
                        print(f"[TIME OUT] {name_display} at {logged_time}")

            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name_display, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Attendance Scanner - Press ESC to quit", frame)
        if cv2.waitKey(1) % 256 == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_scanner()
