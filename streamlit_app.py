import streamlit as st
try:
    import cv2
except ImportError as e:
    import streamlit as st
    st.error(
        "❌ OpenCV (cv2) gagal di-load.\n\n"
        "Pastikan `opencv-python-headless` ada di requirements.txt"
    )
    st.stop()

import numpy as np
from ultralytics import YOLO

# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="YOLO Helmet Detection",
    layout="wide"
)

st.title("📷 YOLO Helmet Detection (Cloud Safe)")

# ===============================
# Load YOLO Model (cached)
# ===============================
@st.cache_resource
def load_model():
    return YOLO("models/best.pt")

model = load_model()

# ===============================
# Sidebar Controls
# ===============================
st.sidebar.header("⚙️ Settings")

mode = st.sidebar.radio(
    "Detection Mode",
    ["📷 Camera", "🖼️ Image Upload"]
)

conf_threshold = st.sidebar.slider(
    "Confidence Threshold",
    0.1, 1.0, 0.4, 0.05
)

# ===============================
# Layout
# ===============================
col1, col2 = st.columns([1, 1])

with col1:
    image_box = st.empty()
    status_box = st.empty()
    info_box = st.empty()

# ===============================
# IMAGE UPLOAD MODE
# ===============================
if mode == "🖼️ Image Upload":
    uploaded = st.sidebar.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        file_bytes = np.asarray(
            bytearray(uploaded.read()), dtype=np.uint8
        )
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        results = model(image, conf=conf_threshold, verbose=False)
        annotated = results[0].plot()

        boxes = results[0].boxes
        helmet = False
        no_helmet = False

        for box in boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id].lower()

            if "helmet" in cls_name or "hard hat" in cls_name:
                helmet = True
            elif "person" in cls_name:
                no_helmet = True

        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        image_box.image(annotated, use_container_width=True)

        if no_helmet:
            status_box.error("🚨 **PELANGGARAN: APD TIDAK LENGKAP**")
        elif helmet:
            status_box.success("✅ **AMAN: K3 Terpenuhi**")
        else:
            status_box.info("📌 Tidak ada deteksi")

        info_box.info(f"🔍 Total Detections: {len(boxes)}")
    else:
        status_box.info("📌 Upload image untuk memulai")

# ===============================
# CAMERA MODE (STREAMLIT CLOUD SAFE)
# ===============================
else:
    camera_image = st.camera_input("📷 Ambil Gambar dari Kamera")

    if camera_image:
        file_bytes = np.asarray(
            bytearray(camera_image.read()), dtype=np.uint8
        )
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        results = model(frame, conf=conf_threshold, verbose=False)
        annotated = results[0].plot()

        boxes = results[0].boxes
        helmet = False
        no_helmet = False

        for box in boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id].lower()

            if "helmet" in cls_name or "hard hat" in cls_name:
                helmet = True
            elif "person" in cls_name:
                no_helmet = True

        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        image_box.image(annotated, use_container_width=True)

        if no_helmet:
            status_box.error("🚨 **PELANGGARAN: APD TIDAK LENGKAP**")
        elif helmet:
            status_box.success("✅ **AMAN: K3 Terpenuhi**")
        else:
            status_box.info("📌 Tidak ada deteksi")

        info_box.info(f"🔍 Total Detections: {len(boxes)}")
    else:
        status_box.info("📌 Ambil gambar dari kamera")

# ===============================
# Footer
# ===============================
st.markdown("---")
st.caption("Pascasarjana - Universitas Pamulang")
