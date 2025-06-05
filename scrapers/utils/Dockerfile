# THIS DOCKERFILE IS NOT MEANT FOR SCRIPT CONTANERS
# IT IS USED TO CREATE A BASE IMAGE WITH THE
# NECESSARY SYSTEM PACKAGES FOR UTILS
FROM python:3.13-alpine

# Installing necessary system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-lav \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    lcms2-dev \
    openjpeg-dev \
    freetype-dev \
    libwebp-dev \
    harfbuzz-dev \
    fribidi-dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copying utils to app/utils directory
WORKDIR /app/utils
COPY . /app/utils

# Do nothing since its a base image
CMD ["python"]