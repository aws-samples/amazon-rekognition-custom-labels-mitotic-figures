import os

import boto3
import io
import streamlit as st
from PIL import Image, ImageDraw

rek_client = boto3.client('rekognition')

# !!!
# Replace the value for your project version ARN.
# !!!
PROJECT_VERSION_ARN = 'arn:aws:rekognition:eu-west-1:038821543405:project/rek-mitotic-figures-workshop/version/1/1661865214266'
# PROJECT_VERSION_ARN = 'arn:aws:rekognition:<AWS_REGION>:<AWS_ACCOUNT_ID>:project/rek-pathology/version/rek-pathology.2021-99-99T11.22.33/1234567890123'


uploaded_file = st.file_uploader('Image file')
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    result = rek_client.detect_custom_labels(
        ProjectVersionArn=PROJECT_VERSION_ARN,
        Image={
            'Bytes': image_bytes
        }
    )
    img = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(img)

    st.write(result['CustomLabels'])
    for custom_label in result['CustomLabels']:
        st.write(f"Label {custom_label['Name']}, confidence {custom_label['Confidence']}")
        geometry = custom_label['Geometry']['BoundingBox']
        w = geometry['Width'] * img.width
        h = geometry['Height'] * img.height
        l = geometry['Left'] * img.width
        t = geometry['Top'] * img.height
        st.write(f"Left, top = ({l}, {t}), width, height = ({w}, {h})")
        draw.rectangle([l, t, l + w, t + h], outline=(0, 0, 255, 255), width=5)

    st_img = st.image(img)

