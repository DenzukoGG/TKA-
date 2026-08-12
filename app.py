"""
=======================================================================
APLIKASI REKOMENDASI MATA PELAJARAN PILIHAN TKA
=======================================================================
Aplikasi ini membantu siswa menentukan 3 Mapel Pilihan TKA terbaik
dari paket kelas yang dipilih, berdasarkan:
    - Nilai Rapor  (bobot 50%)
    - Minat        (bobot 25%)
    - Bakat        (bobot 25%)

CATATAN PENTING UNTUK SISWA:
Semua perhitungan matematika dilakukan di sini (Python), BUKAN di
JavaScript. JavaScript di index.html hanya bertugas menampilkan/
menyembunyikan form, tidak menghitung apa pun.
=======================================================================
"""

from flask import Flask, render_template, request

app = Flask(__name__)


# -----------------------------------------------------------------
# 1. DATA PAKET KELAS
# -----------------------------------------------------------------
# Dictionary ini menyimpan 7 paket kelas beserta 4 mapel pilihan
# masing-masing. Key = kode paket, Value = daftar nama mapel.
# -----------------------------------------------------------------
PAKET_KELAS = {
    "A": ["Fisika", "Kimia", "Matematika Lanjut", "Informatika"],
    "B": ["Fisika", "Kimia", "Biologi", "Bahasa Inggris Lanjut"],
    "C": ["Fisika", "Biologi", "Ekonomi", "Geografi"],
    "D": ["Fisika", "Kimia", "Ekonomi", "Matematika Lanjut"],
    "E": ["Biologi", "Ekonomi", "Sosiologi", "Bahasa Inggris Lanjut"],
    "F": ["Biologi", "Ekonomi", "Geografi", "Sosiologi"],
    "G": ["Ekonomi", "Sosiologi", "Geografi", "Bahasa Inggris Lanjut"],
}

# Bobot penilaian sesuai instruksi soal.
# Angka ini yang menentukan seberapa besar pengaruh tiap komponen
# terhadap Skor Akhir.
BOBOT_RAPOR = 0.50
BOBOT_MINAT = 0.25
BOBOT_BAKAT = 0.25

# Angka pengali untuk mengubah skala slider (1-5) menjadi skala
# nilai (0-100), supaya "adil" dibandingkan dengan Nilai Rapor
# yang sudah dalam skala 0-100.
# Contoh: slider bernilai 4 -> 4 x 20 = 80
PENGALI_SKALA = 20


# -----------------------------------------------------------------
# 2. HALAMAN UTAMA (FORM INPUT)
# -----------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """
    Menampilkan halaman form.
    Kita kirim data PAKET_KELAS ke index.html supaya HTML/JavaScript
    tahu mapel apa saja yang harus ditampilkan untuk tiap paket,
    TANPA harus menulis ulang datanya secara manual di JavaScript.
    """
    return render_template("index.html", paket_kelas=PAKET_KELAS)


# -----------------------------------------------------------------
# 3. HALAMAN HASIL (PROSES PERHITUNGAN)
# -----------------------------------------------------------------
@app.route("/hasil", methods=["POST"])
def hasil():
    """
    Menerima data form (nilai rapor, minat, bakat untuk 4 mapel),
    lalu menghitung Skor Akhir tiap mapel, mengurutkannya, dan
    menampilkan 3 mapel terbaik sebagai rekomendasi TKA.
    """

    # -- Ambil kode paket yang dipilih siswa (misal: "A", "B", dst) --
    kode_paket = request.form.get("paket")

    # Validasi sederhana: kalau kode paket tidak dikenal, tolak.
    if kode_paket not in PAKET_KELAS:
        return "Paket kelas tidak valid. Silakan kembali dan pilih ulang.", 400

    daftar_mapel = PAKET_KELAS[kode_paket]

    # List kosong untuk menampung hasil perhitungan tiap mapel.
    # Nantinya setiap elemen berupa dictionary berisi:
    # nama mapel, skor akhir, dan rincian (breakdown) poinnya.
    hasil_perhitungan = []

    # -----------------------------------------------------------
    # LOOPING SETIAP MAPEL DALAM PAKET UNTUK DIHITUNG SKORNYA
    # -----------------------------------------------------------
    for mapel in daftar_mapel:

        # Ambil nilai mentah dari form berdasarkan nama input.
        # Nama input di HTML dibuat mengikuti pola:
        #   rapor_<NamaMapel>, minat_<NamaMapel>, bakat_<NamaMapel>
        nilai_rapor_mentah = request.form.get(f"rapor_{mapel}")
        minat_slider_mentah = request.form.get(f"minat_{mapel}")
        bakat_slider_mentah = request.form.get(f"bakat_{mapel}")

        # Ubah dari teks (string) menjadi angka (float) agar bisa dihitung.
        nilai_rapor = float(nilai_rapor_mentah)
        minat_slider = float(minat_slider_mentah)   # masih skala 1-5
        bakat_slider = float(bakat_slider_mentah)   # masih skala 1-5

        # ---------------------------------------------------------
        # LANGKAH WAJIB: KONVERSI SKALA SLIDER (1-5) -> (0-100)
        # ---------------------------------------------------------
        # Slider Minat & Bakat masih dalam skala 1-5, sedangkan
        # Nilai Rapor sudah dalam skala 0-100. Agar rumus pembobotan
        # bekerja secara adil dan akurat, slider WAJIB dikalikan 20
        # terlebih dahulu.
        # Contoh: slider = 4  ->  4 * 20 = 80 (skala 0-100)
        minat_konversi = minat_slider * PENGALI_SKALA
        bakat_konversi = bakat_slider * PENGALI_SKALA

        # ---------------------------------------------------------
        # RUMUS SKOR AKHIR (SUDAH DALAM SKALA 0-100 SEMUA)
        # ---------------------------------------------------------
        # Skor Akhir = (Rapor * 0.50) + (Minat * 0.25) + (Bakat * 0.25)
        #
        # Kita hitung tiap komponen poinnya secara terpisah dulu
        # (poin_rapor, poin_minat, poin_bakat) supaya nanti bisa
        # ditampilkan sebagai "breakdown skor" yang transparan
        # kepada siswa.
        poin_rapor = nilai_rapor * BOBOT_RAPOR
        poin_minat = minat_konversi * BOBOT_MINAT
        poin_bakat = bakat_konversi * BOBOT_BAKAT

        skor_akhir = poin_rapor + poin_minat + poin_bakat

        # Simpan seluruh hasil perhitungan mapel ini ke dalam list.
        # round(..., 2) dipakai supaya angka tidak terlalu panjang
        # desimalnya saat ditampilkan (misal 78.333333 -> 78.33).
        hasil_perhitungan.append({
            "nama_mapel": mapel,
            "nilai_rapor": round(nilai_rapor, 2),
            "minat_slider": int(minat_slider),
            "bakat_slider": int(bakat_slider),
            "minat_konversi": round(minat_konversi, 2),
            "bakat_konversi": round(bakat_konversi, 2),
            "poin_rapor": round(poin_rapor, 2),
            "poin_minat": round(poin_minat, 2),
            "poin_bakat": round(poin_bakat, 2),
            "skor_akhir": round(skor_akhir, 2),
        })

    # -----------------------------------------------------------
    # PENGURUTAN MAPEL DARI SKOR TERTINGGI KE TERENDAH
    # -----------------------------------------------------------
    # key=lambda menentukan berdasarkan apa data diurutkan.
    # Kita urutkan berdasarkan 2 kriteria sekaligus:
    #   1. skor_akhir (utama)     -> makin tinggi makin bagus
    #   2. nilai_rapor (tie-breaker) -> jika skor_akhir SAMA PERSIS,
    #      mapel dengan Nilai Rapor lebih tinggi akan diutamakan.
    # reverse=True artinya urutan dari besar ke kecil (descending).
    hasil_perhitungan.sort(
        key=lambda data_mapel: (data_mapel["skor_akhir"], data_mapel["nilai_rapor"]),
        reverse=True
    )

    # -----------------------------------------------------------
    # AMBIL 3 MAPEL TERATAS SEBAGAI REKOMENDASI TKA
    # -----------------------------------------------------------
    # Slicing [:3] artinya "ambil 3 elemen pertama dari list".
    rekomendasi_tka = hasil_perhitungan[:3]

    # Sisanya (mapel ke-4, yang tidak direkomendasikan) tetap kita
    # kirim ke template supaya siswa bisa lihat perbandingannya juga.
    mapel_tidak_terpilih = hasil_perhitungan[3:]

    # Kita tetap merender index.html yang sama (bukan file baru),
    # tetapi kali ini kita sertakan data hasil perhitungan.
    # Di index.html, bagian "Hasil Rekomendasi" hanya akan muncul
    # jika variabel rekomendasi_tka ini terisi (tidak None).
    return render_template(
        "index.html",
        paket_kelas=PAKET_KELAS,
        kode_paket_terpilih=kode_paket,
        rekomendasi_tka=rekomendasi_tka,
        mapel_tidak_terpilih=mapel_tidak_terpilih,
    )


# -----------------------------------------------------------------
# 4. MENJALANKAN APLIKASI
# -----------------------------------------------------------------
if __name__ == "__main__":
    # debug=True membantu saat belajar: server otomatis restart
    # setiap kali kode diubah, dan menampilkan pesan error yang jelas.
    app.run(debug=True)
