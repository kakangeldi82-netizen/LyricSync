🎤 LyricSync
LyricSync, bilgisayarında tamamen lokal (çevrimdışı) çalışan, Spotify ve YouTube Music tarzında kelime kelime (word-by-word) akan bir karaoke ve şarkı sözü uygulamasıdır.

Tek yapman gereken bir müzik dosyası yüklemek ve şarkının düz metin (zaman damgasız) sözlerini yapıştırmak. Gerisini arkaplanda yapay zeka sizin için halleder!

💡 Çalışma Mantığı (Nasıl Çalışır?)
LyricSync, zaman damgası olmayan standart şarkı sözlerini müzikle milisaniyelik hassasiyetle hizalamak için 4 adımlı akıllı bir sistem kullanır:

Yapay Zeka ile Ses Dinleme (Transkripsiyon):
Arka planda çalışan faster-whisper yapay zeka modeli şarkıyı dinler ve duyduğu kelimeleri tahmini zaman damgalarıyla (hangi saniyede söylendiği bilgisiyle) çıkarır.

Akıllı Metin Eşleştirme:
Müzikteki arkavokal, enstrüman veya telaffuz farklılıkları nedeniyle yapay zeka bazı kelimeleri yanlış duyabilir. LyricSync, yapay zekanın duyduğu metin ile senin girdiğin gerçek sözleri sırasıyla karşılaştırır. Zamanlamaları alır ve senin %100 doğru metnine aktarır.

Pürüzsüz Zaman Tamamlama (İnterpolasyon):
Arada duyulamayan veya eşleşmeyen kelimeler varsa, sistem bunları yok saymaz. İki bilinen zaman damgası arasında matematiksel olarak orantılı dağıtarak akışı bozmaz.

Hızlı Önbellek (Cache) Sistemi:
Analiz bittiğinde sonuçlar ~/.lyricsync_cache/ klasörüne küçük bir JSON dosyası olarak kaydedilir. Aynı şarkıyı tekrar açtığında saniyeler süren analiz beklenmez, şarkı anında hazır olur.

🛠️ Kurulum ve Hazırlık
Projeyi bilgisayarında çalıştırmak için aşağıdaki adımları sırasıyla uygulayabilirsin.

1. Ön Gereksinim: FFmpeg Kurulumu
faster-whisper ses dosyalarını işleyebilmek için sisteminde FFmpeg aracının kurulu olmasına ihtiyaç duyar.

Windows: Komut satırına (CMD veya PowerShell) winget install ffmpeg yazarak kurabilirsin.

macOS: Terminale brew install ffmpeg yazarak kurabilirsin.

Linux (Ubuntu/Debian): Terminale sudo apt install ffmpeg yazarak kurabilirsin.

2. Projeyi Bilgisayara İndirme
Projeyi bilgisayarına iki farklı yöntemle indirebilirsin:

Yöntem A: Git Kullanarak (Önerilen)
Terminal veya Komut İstemi'ni açıp şu komutu çalıştırın:

Bash
git clone https://github.com/kullaniciadi/lyricsync.git
cd lyricsync
Yöntem B: ZIP Olarak İndirme
GitHub sayfasındaki yeşil Code butonuna tıkla ve Download ZIP seçeneğini seç.

İnen ZIP dosyasını bilgisayarında bir klasöre çıkar.

Terminal / Komut İstemi'ni açıp bu klasörün içine gir:

Bash
cd klasorun/yolu/lyricsync
3. Python Ortamını Kurma ve Çalıştırma
Projeyi çalıştırmadan önce bağımlılıkların sistemindeki diğer projelerle karışmaması için sanal bir ortam (venv) oluşturman önerilir:

Bash
# 1. Sanal ortamı oluşturun
python -m venv venv

# 2. Sanal ortamı aktif edin
# Windows için:
venv\Scripts\activate
# macOS / Linux için:
source venv/bin/activate

# 3. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
Arayüz Uyarısı: İlk çalıştırmada yapay zeka modeli (small modeli, yaklaşık ~500 MB) otomatik olarak indirilir. Bu işlem internet hızına bağlı olarak ilk seferde biraz zaman alabilir. Sonraki çalıştırmalarda internet bağlantısı gerekmez.

🚀 Kullanım Adımları
Terminalde python main.py komutuyla uygulamayı başlat.

🎵 Şarkı Aç: Desteklenen formatlardan biriyle (.mp3, .wav, .m4a, .flac, .ogg) şarkını seç.

📝 Sözleri Gir: Şarkının sözlerini zaman damgası olmadan, doğrudan satır satır yapıştır.

✨ Hizala: "Hizala" butonuna bas. İşlem bilgisayarının gücüne ve şarkı süresine bağlı olarak 10-60 saniye sürebilir.

▶️ Oynat: Şarkı çalmaya başladığında sözler kelime kelime parlayarak (highlight) akar ve aktif satır ekranın ortasında odak kalır.

⚙️ İpuçları ve Özelleştirme
Hız ve Doğruluk Dengesi:

core/aligner.py dosyasındaki model_size ayarını daha hızlı işlem için "tiny" veya "base", daha yüksek doğruluk için "medium" veya "large-v3" yapabilirsin. (Ekran kartın destekliyorsa device="cuda" parametresiyle analizi saniyelere düşürebilirsin).

Tema ve Renkler:

ui/karaoke_view.py içerisindeki renk kodlarını (ACTIVE_COLOR, SUNG_COLOR, DIM_COLOR) değiştirerek kendi görsel temanı oluşturabilirsin.

Önbelleği Temizleme:

Bir şarkının sözlerini değiştirmek veya yeniden hizalamak istersen, ~/.lyricsync_cache/ klasöründeki ilgili .json dosyasını silip uygulamada tekrar "Hizala" butonuna basman yeterlidir.

📂 Proje Yapısı
Plaintext
lyricsync/
├── main.py             # Uygulamanın giriş noktası
├── core/
│   ├── lyrics_model.py # Kelime, satır ve şarkı veri yapıları
│   ├── aligner.py      # Yapay zeka + metin eşleştirme motoru
│   ├── align_worker.py # Hizalama işlemini arka planda takılmadan çalıştıran izlek
│   └── cache.py        # Hizalanmış verileri bilgisayara kaydetme/yükleme
└── ui/
    ├── main_window.py  # Ana pencere ve bileşen yönetimi
    ├── karaoke_view.py # Kelime kelime renklendirme ve kaydırma ekranı
    ├── controls.py     # Oynat, duraklat, ses ve zaman çubuğu
    ├── lyrics_dialog.py# Düz metin söz giriş penceresi
    ├── flow_layout.py  # Kelimeleri ekrana esnek dizen layout
    └── styles.py       # Koyu ve cam efektli (glassmorphism) arayüz stilleri