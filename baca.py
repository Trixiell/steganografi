import streamlit as st
from PIL import Image

# ================= LOGIKA DECODING (ENGINE) =================
# Logika ini mengekstrak bit LSB dari piksel gambar

def extract_data(pix):
    """Membaca bit LSB dari piksel sampai menemukan stopper bit."""
    img_data = iter(pix)
    binary_str = ""
    
    while True:
        try:
            # Ambil 3 piksel (9 nilai RGB)
            pixels = [value for value in next(img_data)[:3] +
                                next(img_data)[:3] +
                                next(img_data)[:3]]
        except StopIteration:
            break

        # Baca 8 bit data dari 8 nilai pertama
        binstr = ''
        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
        
        binary_str += binstr
        
        # Cek Stopper Bit (nilai ke-9)
        # Ganjil berarti STOP, Genap berarti LANJUT
        if pixels[-1] % 2 != 0:
            return binary_str

    return binary_str

def decode_img(img):
    """Menerjemahkan biner dari gambar menjadi teks."""
    img = img.convert('RGB')
    binary_data = extract_data(img.getdata())
    
    decoded_text = ""
    # Konversi string biner panjang kembali menjadi karakter ASCII
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8: break 
        try:
            decoded_text += chr(int(byte, 2))
        except ValueError:
            break

    return decoded_text

# ================= TAMPILAN (UI) STREAMLIT =================

# Konfigurasi Halaman
st.set_page_config(page_title="Stegano Reader", page_icon="🔓")

# Judul & Header
st.title("🔓 Steganography Reader")
st.markdown("""
Aplikasi ini khusus untuk **membaca pesan rahasia** yang tersembunyi di dalam gambar 
menggunakan metode LSB.
""")

st.divider()

# 1. Upload Gambar
uploaded_file = st.file_uploader("Upload Gambar Steganografi (PNG)", type=["png"])

if uploaded_file is not None:
    try:
        # Tampilkan Gambar yang diupload
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(image, caption="Gambar yang Diupload", use_column_width=True)
            
        with col2:
            st.write("### Hasil Deteksi")
            
            # Tombol Eksekusi
            if st.button("🔍 Buka Pesan Sekarang", type="primary"):
                with st.spinner('Sedang memindai piksel...'):
                    # Proses Decode
                    hidden_message = decode_img(image)
                
                # Menampilkan Hasil
                if hidden_message and hidden_message.isprintable():
                    st.success("Pesan Ditemukan!")
                    st.text_area("Isi Pesan:", value=hidden_message, height=150)
                else:
                    st.warning("⚠️ Tidak ditemukan pesan.")
                    st.caption("Kemungkinan gambar ini tidak mengandung pesan rahasia, atau dibuat dengan algoritma yang berbeda.")
                    
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses gambar: {e}")

else:
    st.info("Silakan upload file .PNG untuk memulai.")

