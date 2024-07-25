import streamlit as st
import cv2
import face_recognition as frg
import yaml 
from utils import recognize, build_dataset

st.set_page_config(layout="wide")
# Konfigurasi
cfg = yaml.load(open('config.yaml','r'), Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Pengaturan")

# Buat menu bar
menu = ["Gambar", "Kamera"]
choice = st.sidebar.selectbox("Tipe Input", menu)

# Slider untuk menyesuaikan toleransi
TOLERANCE = st.sidebar.slider("Toleransi", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Toleransi adalah ambang batas untuk pengenalan wajah. Semakin rendah toleransi, semakin ketat pengenalan wajah. Semakin tinggi toleransi, semakin longgar pengenalan wajah.")

# Bagian Informasi
st.sidebar.title("Informasi Wajah")
name_container = st.sidebar.empty()
id_container = st.sidebar.empty()
name_container.info('Nama: Tidak Diketahui')
id_container.success('ID: Tidak Diketahui')

if choice == "Gambar":
    st.title("Sistem Pengenalan Wajah")
    st.write(PICTURE_PROMPT)
    uploaded_images = st.file_uploader("Unggah", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if len(uploaded_images) != 0:
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, id = recognize(image, TOLERANCE) 
            name_container.info(f"Nama: {name}")
            id_container.success(f"ID: {id}")
            st.image(image)
    else: 
        st.info("Silakan unggah gambar")
    
elif choice == "Kamera":
    st.title("Sistem Pengenalan Wajah")
    st.write(WEBCAM_PROMPT)
    # Pengaturan Kamera
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set to full HD width
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Set to full HD height
    FRAME_WINDOW = st.image([])

    while True:
        ret, frame = cam.read()
        if not ret:
            st.error("Gagal mengambil frame dari kamera")
            st.info("Silakan matikan aplikasi lain yang menggunakan kamera dan restart aplikasi")
            st.stop()
        image, name, id = recognize(frame, TOLERANCE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        name_container.info(f"Nama: {name}")
        id_container.success(f"ID: {id}")
        FRAME_WINDOW.image(image)

with st.sidebar.form(key='my_form'):
    st.title("Bagian Pengembang")
    submit_button = st.form_submit_button(label='BANGUN ULANG DATASET')
    if submit_button:
        with st.spinner("Membangun ulang dataset..."):
            build_dataset()
        st.success("Dataset telah direset")
