FROM python:3.11.3-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgcc1 \
    libgl1-mesa-glx \
    libgtk2.0-dev \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install opencv-python-headless first to avoid conflicts
RUN pip install opencv-python-headless
# Install other requirements
RUN pip install -r requirements.txt
# Ensure opencv-python-headless is used (reinstall if needed)
RUN pip uninstall -y opencv-python || true
RUN pip install --force-reinstall --no-cache-dir opencv-python-headless

# copy project
COPY . /usr/src/app/

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]