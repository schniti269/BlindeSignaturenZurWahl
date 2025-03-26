import qrcode
import io
import base64
from PIL import Image


def generate_qr_code(data, box_size=10, border=4):
    """
    Generate a QR code image from the given data and return it as a base64 encoded string.

    Args:
        data (str): The data to encode in the QR code
        box_size (int): The size of each box in the QR code
        border (int): The size of the border around the QR code

    Returns:
        str: Base64 encoded string of the QR code image
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )

        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a BytesIO object
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        buffered.seek(0)

        # Convert to base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return None


# Test the function
if __name__ == "__main__":
    test_data = "http://141.72.12.183:33059/"
    qr_code = generate_qr_code(test_data)
    if qr_code:
        print(f"QR code generated successfully! Length: {len(qr_code)}")
        print(f"First 20 characters: {qr_code[:20]}...")
    else:
        print("Failed to generate QR code")
