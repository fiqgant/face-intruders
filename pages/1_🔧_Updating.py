import streamlit as st 
import cv2
import yaml 
import pickle 
from utils import submitNew, get_info_from_id, deleteOne
import numpy as np

st.set_page_config(layout="wide")
st.title("Sistem Pengenalan Wajah")
st.write("Aplikasi ini digunakan untuk menambahkan wajah baru ke dataset")

menu = ["Menambah", "Menghapus", "Menyesuaikan"]
choice = st.sidebar.selectbox("Opsi", menu)
if choice == "Menambah":
    name = st.text_input("Nama", placeholder='Masukkan nama')
    id = st.text_input("ID", placeholder='Masukkan ID')
    upload = st.radio("Unggah gambar atau gunakan kamera", ("Unggah", "Kamera"))
    if upload == "Unggah":
        uploaded_image = st.file_uploader("Unggah", type=['jpg', 'png', 'jpeg'])
        if uploaded_image is not None:
            st.image(uploaded_image)
            submit_btn = st.button("Kirim", key="submit_btn")
            if submit_btn:
                if name == "" or id == "":
                    st.error("Silakan masukkan nama dan ID")
                else:
                    ret = submitNew(name, id, uploaded_image)
                    if ret == 1: 
                        st.success("Wajah Ditambahkan")
                    elif ret == 0: 
                        st.error("ID Wajah sudah ada")
                    elif ret == -1: 
                        st.error("Tidak ada wajah di gambar")
    elif upload == "Kamera":
        img_file_buffer = st.camera_input("Ambil gambar")
        submit_btn = st.button("Kirim", key="submit_btn")
        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            if submit_btn: 
                if name == "" or id == "":
                    st.error("Silakan masukkan nama dan ID")
                else:
                    ret = submitNew(name, id, cv2_img)
                    if ret == 1: 
                        st.success("Wajah Ditambahkan")
                    elif ret == 0: 
                        st.error("ID Wajah sudah ada")
                    elif ret == -1: 
                        st.error("Tidak ada wajah di gambar")
elif choice == "Menghapus":
    def del_btn_callback(id):
        deleteOne(id)
        st.success("Wajah dihapus")
        
    id = st.text_input("ID", placeholder='Masukkan ID')
    submit_btn = st.button("Kirim", key="submit_btn")
    if submit_btn:
        name, image, _ = get_info_from_id(id)
        if name == None and image == None:
            st.error("ID Wajah tidak ada")
        else:
            st.success(f"Nama Wajah dengan ID {id} adalah: {name}")
            st.warning("Periksa gambar di bawah untuk memastikan Anda menghapus Wajah yang benar")
            st.image(image)
            del_btn = st.button("Hapus", key="del_btn", on_click=del_btn_callback, args=(id,)) 
        
elif choice == "Menyesuaikan":
    def form_callback(old_name, old_id, old_image, old_idx):
        new_name = st.session_state['new_name']
        new_id = st.session_state['new_id']
        new_image = st.session_state['new_image']
        
        name = old_name
        id = old_id
        image = old_image
        
        if new_image is not None:
            image = cv2.imdecode(np.frombuffer(new_image.read(), np.uint8), cv2.IMREAD_COLOR)
            
        if new_name != old_name:
            name = new_name
            
        if new_id != old_id:
            id = new_id
        
        ret = submitNew(name, id, image, old_idx=old_idx)
        if ret == 1: 
            st.success("Wajah Ditambahkan")
        elif ret == 0: 
            st.error("ID Wajah sudah ada")
        elif ret == -1: 
            st.error("Tidak ada wajah di gambar")
    id = st.text_input("ID", placeholder='Masukkan ID')
    submit_btn = st.button("Kirim", key="submit_btn")
    if submit_btn:
        old_name, old_image, old_idx = get_info_from_id(id)
        if old_name == None and old_image == None:
            st.error("ID Wajah tidak ada")
        else:
            with st.form(key='my_form'):
                st.title("Menyesuaikan informasi Wajah")
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Nama", key='new_name', value=old_name, placeholder='Masukkan nama baru')
                new_id  = col1.text_input("ID", key='new_id', value=id, placeholder='Masukkan ID baru')
                new_image = col1.file_uploader("Unggah gambar baru", key='new_image', type=['jpg', 'png', 'jpeg'])
                col2.image(old_image, caption='Gambar saat ini', width=400)
                st.form_submit_button(label='Kirim', on_click=form_callback, args=(old_name, id, old_image, old_idx))
