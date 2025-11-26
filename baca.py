import streamlit as st
from PIL import Image
import io

# ================= LOGIKA INTI STEGANOGRAFI (Sama dengan sebelumnya) =================

def gen_data(data):
    """Mengubah data string menjadi format biner 8-bit."""
    new_data = []
    for i in data:
        new_data.append(format(ord(i), '08b'))
    return new_data

def mod_pix(pix, data):
    """Generator untuk memodifikasi piksel berdasarkan data biner."""
    datalist = gen_data(data)
    len_data = len(datalist)
    img_data = iter(pix)

    for i in range(len_data):
        pixels = [value for value in next(img_data)[:3] +
                            next(img_data)[:3] +
                            next(img_data)[:3]]

        for j in range(0, 8):
            if (datalist[i][j] == '0') and (pixels[j] % 2 != 0):
                pixels[j] -= 1
            elif (datalist[i][j] == '1') and (pixels[j] % 2 == 0):
                if pixels[j] != 0: pixels[j] -= 1
                else: pixels[j] += 1
        
        if (i == len_data - 1):
            if (pixels[-1] % 2 == 0):
                if pixels[-1] != 0: pixels[-1] -= 1
                else: pixels[-1] += 1
        else:
            if (pixels[-1] % 2 != 0):
                pixels[-1] -= 1

        pixels = tuple(pixels)
        yield pixels[0:3]
        yield pixels[3:6]
        yield pixels[6:9]

def encode_enc(new_img, data):
    """Menulis data ke dalam piksel gambar."""
    w = new_img.size[0]
    (x, y) = (0, 0)
    for pixel in mod_pix(new_img.getdata(), data):
        new_img.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0; y += 1
        else:
            x += 1

def extract_data(pix):
    """Membaca data dari piksel gambar."""
    img_data = iter(pix)
    binary_str = ""
    while True:
        try:
            pixels = [value for value in next(img_data)[:3] +
                                next(img_data)[:3] +
                                next(img_data)[:3]]
        except StopIteration:
            break

        binstr = ''
        for i in pixels[:8]:
            if i % 2 == 0: binstr += '0'
            else: binstr += '1'
        
        binary_str += binstr
        if pixels[-1] % 2 != 0:
            return binary_str
    return binary_str

def decode_img(img):
    """Menerjemahkan biner menjadi teks."""
    img = img.convert('RGB')
    binary_data = extract_data(img.getdata())
    decoded_text = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8: break
        try:
            decoded_text += chr(int(byte, 2))
        except ValueError:
            break
    return decoded_text

# ================= ANTARMUKA STREAMLIT =================

st.set_page_config(page_title="SteganoWeb", layout="centered")

st.title("🕵️‍♂️ Steganografi Gambar (LSB)")
st.write("Sembunyikan pesan rahasia di dalam gambar tanpa mengubah tampilannya.")

# Membuat Tab untuk memisahkan fitur Encode dan Decode
tab1, tab2 = st.tabs(["🔒 Sembunyikan Pesan (Encode)", "🔓 Baca Pesan (Decode)"])

# --- TAB 1: ENCODE ---
with tab1:
    st.header("Sembunyikan Pesan")
    
    # Upload Gambar
    uploaded_file = st.file_uploader("Upload Gambar (PNG/JPG)", type=["png", "jpg", "jpeg"], key="upload_enc")
    
    # Input Text
    text_input = st.text_area("Masukkan Pesan Rahasia:", height=100)
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Gambar Asli", use_column_width=True)
        
        if st.button("Proses & Sembunyikan Pesan"):
            if len(text_input) == 0:
                st.warning("Mohon isi pesan rahasia terlebih dahulu.")
            else:
                try:
                    # Proses Copy dan Encode
                    new_img = image.copy()
                    encode_enc(new_img, text_input)
                    
                    st.success("Berhasil! Pesan telah disisipkan.")
                    
                    # Konversi gambar hasil ke Bytes agar bisa didownload
                    buf = io.BytesIO()
                    new_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    # Tombol Download
                    st.download_button(
                        label="⬇️ Unduh Gambar Hasil (PNG)",
                        data=byte_im,
                        file_name="stegano_secret.png",
                        mime="image/png"
                    )
                    st.info("Pastikan simpan dalam format PNG agar pesan tidak rusak.")
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- TAB 2: DECODE ---
with tab2:
    st.header("Baca Pesan Tersembunyi")
    
    decode_file = st.file_uploader("Upload Gambar Berisi Pesan (PNG)", type=["png"], key="upload_dec")
    
    if decode_file is not None:
        dec_image = Image.open(decode_file)
        st.image(dec_image, caption="Gambar yang Diupload", width=300)
        
        if st.button("🔍 Baca Pesan"):
            try:
                result = decode_img(dec_image)
                if result and result.isprintable():
                    st.success("Pesan Ditemukan:")
                    st.code(result)
                else:
                    st.error("Tidak ditemukan pesan rahasia yang valid pada gambar ini.")
            except Exception as e:
                st.error(f"Gagal membaca gambar: {e}")

# Footer
st.markdown("---")
st.caption("Dibuat dengan Python & Streamlit | Metode: Least Significant Bit (LSB)")