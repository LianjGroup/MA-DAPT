from io import BytesIO
import win32clipboard
from PIL import Image

def send_to_clipboard(name):
    image = Image.open(name)
    output = BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

name = ("Saved\Graph_1.png")

send_to_clipboard(name)