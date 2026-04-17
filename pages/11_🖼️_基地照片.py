import streamlit as st
import os
from utils import init_sidebar

curr_proj = init_sidebar()
photo_dir = f"projects/{curr_proj}/photos"
if not os.path.exists(photo_dir): os.makedirs(photo_dir)

st.title("🖼️ 基地照片管理")
up = st.file_uploader("上傳照片", accept_multiple_files=True)
if st.button("開始上傳") and up:
    for f in up:
        with open(os.path.join(photo_dir, f.name), "wb") as file: file.write(f.getbuffer())
    st.rerun()

photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
cols = st.columns(3)
for i, p in enumerate(photos):
    with cols[i % 3]:
        st.image(os.path.join(photo_dir, p))
        if st.button(f"🗑️", key=p):
            os.remove(os.path.join(photo_dir, p))
            st.rerun()