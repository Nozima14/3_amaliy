import streamlit as st
import cv2
import face_recognition
import numpy as np
from cryptography.fernet import Fernet

# Shifrlash uchun kalitni yaratish
if 'key' not in st.session_state:
    st.session_state['key'] = Fernet.generate_key()
cipher = Fernet(st.session_state['key'])

# Foydalanuvchining shifrlangan login va paroli
stored_login = "admin"
stored_password = cipher.encrypt("admin123".encode())

# Yuz ma'lumotlarini oldindan tayyorlash (tanilgan foydalanuvchi yuzi)
# Bu qismda yuz tasviri faylidan ma'lumot olinadi
known_face_encodings = []
known_face_names = []

def load_known_faces():
    image_path = "known_user.jpg"  # Oldindan saqlangan foydalanuvchi yuz tasviri
    image = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(face_encoding)
    known_face_names.append("Admin")

load_known_faces()

# Login va parol kiritish
st.title("Tizimga Kirish")
login_input = st.text_input("Loginni kiriting")
password_input = st.text_input("Parolni kiriting", type="password")

# Kamera orqali yuzni aniqlash
st.write("Yuzingizni aniqlash uchun kamerani yoqing:")
run_camera = st.button("Kamerani ishga tushirish")

if run_camera:
    # Kameradan tasvir olish
    camera = cv2.VideoCapture(0)
    stframe = st.empty()
    face_verified = False

    while True:
        ret, frame = camera.read()
        if not ret:
            st.error("Kameradan tasvir olishda xatolik yuz berdi.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_verified = True
                st.success(f"Yuzingiz aniqlandi: {name}")
                break

        stframe.image(frame, channels="BGR")

        if face_verified:
            camera.release()
            cv2.destroyAllWindows()
            break

    if face_verified:
        # Login va parolni tekshirish
        if login_input == stored_login and cipher.decrypt(stored_password).decode() == password_input:
            st.success("Tizimga muvaffaqiyatli kirdingiz!")
            st.write("Endi tizimdan foydalanishingiz mumkin.")
        else:
            st.error("Login yoki parol noto'g'ri.")
    else:
        st.error("Yuz aniqlanmadi. Iltimos, qayta urinib ko'ring.")

# Kamerani yopish
if not run_camera:
    st.write("Kamera tugmasini bosib, yuzingizni tasdiqlang.")


