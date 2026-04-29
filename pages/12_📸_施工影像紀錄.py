import streamlit as st
import os
from utils import init_sidebar

st.set_page_config(layout="wide")
curr_proj = init_sidebar()
img_dir = f"projects/{curr_proj}/photos"

if not os.path.exists(img_dir):
    os.makedirs(img_dir)

st.title("📸 施工影像紀錄")

# --- 上傳功能 ---
uploaded_file = st.file_uploader("上傳工地現場照片", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    with open(os.path.join(img_dir, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"已儲存：{uploaded_file.name}")

# --- 展示相簿 ---
st.divider()
files = os.listdir(img_dir)
if files:
    cols = st.columns(3)
    for idx, f_name in enumerate(files):
        with cols[idx % 3]:
            st.image(os.path.join(img_dir, f_name), caption=f_name, use_container_width=True)
else:
    st.info("目前尚無施工照片，請由上方上傳。")