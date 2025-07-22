import streamlit as st
from PIL import Image
import base64
from io import BytesIO


# Function to encode the message into the image
def encode_message(message, image):
    encoded_image = image.copy()

    # Encoding the message into the image
    encoded_image.putdata(encode_data(image, message))

    # Save the encoded image
    encoded_image_path = "encoded.png"
    encoded_image.save(encoded_image_path)

    st.success("Image encoded successfully.")
    show_encoded_image(encoded_image_path)


# Function to decode the hidden message from the image
def decode_message(image):
    # Decode the hidden message from the image
    decoded_message = decode_data(image)

    st.write("Hidden Message: " + decoded_message)
    show_decoded_image(image)  # Call the function to display the decoded image


# Function to display the decoded image in the UI
def show_decoded_image(decoded_image):
    st.image(decoded_image, caption="Decoded Image", use_column_width=True)


# Function to encode the data (message) into the image
def encode_data(image, data):
    data = data + "$"  # Adding a delimiter to identify the end of the message
    data_bin = ''.join(format(ord(char), '08b') for char in data)

    pixels = list(image.getdata())
    encoded_pixels = []

    index = 0
    for pixel in pixels:
        if index < len(data_bin):
            red_pixel = pixel[0]
            new_pixel = (red_pixel & 254) | int(data_bin[index])
            encoded_pixels.append((new_pixel, pixel[1], pixel[2]))
            index += 1
        else:
            encoded_pixels.append(pixel)

    return encoded_pixels


# Function to decode the data (message) from the image
def decode_data(image):
    pixels = list(image.getdata())

    data_bin = ""
    for pixel in pixels:
        # Extracting the least significant bit of the red channel
        data_bin += bin(pixel[0])[-1]

    data = ""
    for i in range(0, len(data_bin), 8):
        byte = data_bin[i:i + 8]
        data += chr(int(byte, 2))
        if data[-1] == "$":
            break

    return data[:-1]  # Removing the delimiter


# Function to display the encoded image in the UI and add a download button
def show_encoded_image(image_path):
    encoded_image = Image.open(image_path)

    st.image(encoded_image, caption="Encoded Image", use_column_width=True)

    buffered = BytesIO()
    encoded_image.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode()

    href = ('<a href="data:file/png;base64,' + img_str + '" '
            'download="' + image_path + '">Download Encoded Image</a>')

    st.markdown(href, unsafe_allow_html=True)


# Streamlit GUI setup
st.set_page_config(
    page_title="Image Steganography",
    page_icon=":shushing_face:",
    layout="wide"
)

st.markdown("""
    <style>
    .select-container {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 3rem;
        margin-bottom: 3rem;
    }
    .select-box {
        background: #f0f2f6;
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        padding: 3rem 2.5rem;
        text-align: center;
        cursor: pointer;
        transition: box-shadow 0.2s, transform 0.2s;
        width: 300px;
        border: 3px solid #e0e0e0;
    }
    .select-box:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        transform: translateY(-4px) scale(1.03);
        border: 3px solid #4f8cff;
    }
    .select-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .selected {
        border: 3px solid #4f8cff;
        background: #eaf1ff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Hide your secrets!!! 🤫")

if 'mode' not in st.session_state:
    st.session_state['mode'] = None

if st.session_state['mode'] is None:
    st.markdown('<div class="select-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("\U0001F512\nEncode", key="encode_btn", help="Hide a message in an image", use_container_width=True):
            st.session_state['mode'] = 'encode'
    with col2:
        if st.button("\U0001F50E\nDecode", key="decode_btn", help="Reveal a hidden message from an image", use_container_width=True):
            st.session_state['mode'] = 'decode'
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #888; font-size: 1.2rem;'>Select an action to get started</p>", unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align:right; margin-bottom:1rem;'>"
                "<a href='/' style='color:#4f8cff; text-decoration:none; font-weight:bold;'>← Back</a>"
                "</div>", unsafe_allow_html=True)
    if st.session_state['mode'] == 'encode':
        st.header("🔒 Encode a Message into an Image")
        message = st.text_input("Enter Message to Hide", key="encode_message")
        image_file = st.file_uploader("Choose an Image", type=["png", "jpg", "jpeg"], key="encode_image")
        if message and image_file:
            image = Image.open(image_file)
            encode_message(message, image)
    elif st.session_state['mode'] == 'decode':
        st.header("🔍 Decode a Message from an Image")
        decode_image_file = st.file_uploader(
            "Choose an Encoded Image", type=["png", "jpg", "jpeg"], key="decode_image")
        if decode_image_file:
            decode_image = Image.open(decode_image_file)
            decode_message(decode_image)
