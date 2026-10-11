import os
import socket

def get_local_ip():
    """Determines the local Wi-Fi / LAN IP address of the Pi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually send data, just identifies routing interface
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '192.168.1.106'
    finally:
        s.close()
    return ip

def generate_qr_code(port=8080, save_path=None):
    """
    Generates an ASCII QR code for terminal display and saves a PNG image.
    Returns the URL string.
    """
    ip = get_local_ip()
    url = f"http://{ip}:{port}"
    
    if save_path is None:
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_code.png")

    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # 1. Print ASCII QR Code to terminal
        print("\n" + "=" * 65)
        print(f"📱 SCAN TO CONNECT PHONE: {url}")
        print("=" * 65)
        qr.print_ascii(invert=True)
        print("=" * 65)

        # 2. Save PNG image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(save_path)
        print(f"Saved high-res QR code image to: {save_path}\n")
    except Exception as e:
        print(f"QR code generation info: URL is {url} ({e})")
        
    return url

if __name__ == "__main__":
    generate_qr_code()
