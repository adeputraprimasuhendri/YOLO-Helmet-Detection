import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np
import time

# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="YOLO Webcam Detection",
    layout="wide"
)

st.title("📷 YOLO Real-time Helmet Detection")
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

# Detection mode selector
detection_mode = st.sidebar.radio(
    "Detection Mode",
    options=["📷 Webcam", "🖼️ Image Upload"],
    index=0
)

conf_threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.1,
    max_value=1.0,
    value=0.4,
    step=0.05
)

# Initialize variables
uploaded_file = None
camera_index = 0
start_camera = False
stop_camera = False

# Webcam settings
if detection_mode == "📷 Webcam":
    camera_index = st.sidebar.selectbox(
        "Camera Device",
        options=[0, 1, 2],
        index=0
    )

    start_camera = st.sidebar.button("▶ Start Camera")
    stop_camera = st.sidebar.button("⏹ Stop Camera")
else:
    # Image upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False
    )

# ===============================
# Session State
# ===============================
if "run" not in st.session_state:
    st.session_state.run = False

if detection_mode == "📷 Webcam":
    if start_camera:
        st.session_state.run = True

    if stop_camera:
        st.session_state.run = False
else:
    st.session_state.run = False

# ===============================
# Camera Display
# ===============================
# Create column layout for 50% width
col1, col2 = st.columns([1, 1])

with col1:
    FRAME_WINDOW = st.empty()
    status_text = st.empty()
    fps_text = st.empty()
    safety_status_text = st.empty()

# ===============================
# Image Upload Mode
# ===============================
if detection_mode == "🖼️ Image Upload":
    if uploaded_file is not None:
        # Read uploaded image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # YOLO inference
        results = model(image, conf=conf_threshold, verbose=False)

        # Draw bounding boxes
        annotated_image = results[0].plot()

        # Check for helmet detection
        detections = results[0].boxes
        helmet_detected = False
        no_helmet_detected = False
        person_detected = False
        no_person_detected = False

        if len(detections) > 0:
            class_id_arr = []
            for box in detections:
                class_id = int(box.cls[0])
                class_id_arr.append(class_id)
                print(f"ID={class_id}")
            has_person = 9 in class_id_arr
            has_helmet = 2 in class_id_arr

            person_detected = has_person
            helmet_detected = has_helmet

            print(f"{helmet_detected} = {no_helmet_detected}")

        # Convert BGR → RGB
        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        # Display image
        FRAME_WINDOW.image(annotated_image, use_container_width=True)

        # Display safety status
        if person_detected and helmet_detected:
            safety_status_text.success("✅ **AMAN: K3 Terpenuhi**")
        elif person_detected and not helmet_detected:
            safety_status_text.error(
                "🚨 **PELANGGARAN: APD TIDAK LENGKAP.** Terdeteksi Pekerja Tanpa Helm."
            )
        elif not person_detected and helmet_detected:
            safety_status_text.error("📌 Helm terdeteksi tanpa pekerja")
        else:
            safety_status_text.info("📌 Tidak terdeteksi pekerja dan juga helm")
        status_text.success("✅ Image processed successfully")
    else:
        status_text.info("📌 Upload an image to begin detection")

# ===============================
# Camera Loop
# ===============================
elif st.session_state.run:
    cap = cv2.VideoCapture(camera_index)

    # Reduce resolution for higher FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        st.error("❌ Cannot access camera")
        st.session_state.run = False

    prev_time = 0

    while st.session_state.run:
        ret, frame = cap.read()
        if not ret:
            status_text.error("❌ Failed to read frame")
            break

        # YOLO inference
        results = model(frame, conf=conf_threshold, verbose=False)

        # Draw bounding boxes
        annotated_frame = results[0].plot()

        # Check for helmet detection
        detections = results[0].boxes
        helmet_detected = False
        no_helmet_detected = False
        person_detected = False
        no_person_detected = False

        if len(detections) > 0:
            class_id_arr = []
            for box in detections:
                class_id = int(box.cls[0])
                class_id_arr.append(class_id)
                print(f"ID={class_id}")
            has_person = 9 in class_id_arr
            has_helmet = 2 in class_id_arr

            person_detected = has_person
            helmet_detected = has_helmet

            print(f"{helmet_detected} = {no_helmet_detected}")

        # Display safety status
        if person_detected and helmet_detected:
            safety_status_text.success("✅ **AMAN: K3 Terpenuhi**")
        elif person_detected and not helmet_detected:
            safety_status_text.error(
                "🚨 **PELANGGARAN: APD TIDAK LENGKAP.** Terdeteksi Pekerja Tanpa Helm."
            )
        elif not person_detected and helmet_detected:
            safety_status_text.error("📌 Helm terdeteksi tanpa pekerja")
        else:
            safety_status_text.info("📌 Tidak terdeteksi pekerja dan juga helm")

        # Convert BGR → RGB
        annotated_frame = cv2.cvtColor(
            annotated_frame, cv2.COLOR_BGR2RGB
        )

        # Show results
        FRAME_WINDOW.image(
            annotated_frame,
            use_container_width=True
        )
        status_text.success("🟢 Camera Running")
    if cap:
        cap.release()
        status_text.warning("🟡 Camera Stopped")

else:
    status_text.info("📌 Click **Start Camera** to begin")

# ===============================
# Footer
# ===============================
st.markdown("---")
st.caption("Pascasarjana - Universitas Pamulang")
