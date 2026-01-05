import cv2  # Görüntü işleme kütüphanesi (Kamera görüntüsünü almak, işlemek ve üzerine çizim yapmak için)
import tkinter as tk  # Grafiksel Kullanıcı Arayüzü (GUI) oluşturma kütüphanesi (Menüler ve butonlar için)
from tkinter import ttk
import os  # İşletim sistemi işlemleri (Dosya yollarını kontrol etmek, resimlerin varlığını sorgulamak için)
import numpy as np  # Sayısal işlem kütüphanesi (Görüntü matrisleri ve piksel hesaplamaları için)
import time  # Zaman işlemleri (Süre tutmak, bekleme yapmak ve fps hesaplamak için)
import random  # Rastgelelik (Konfetilerin, objelerin rastgele konumlarda çıkması için)
import platform  # İşletim sistemi tespiti (Windows veya Mac olduğunu anlamak için)
import threading  # Eş zamanlı işlem (Arayüz donmadan arka planda ses çalabilmek için)
from datetime import datetime  # Raporlama yaparken o anki tarih ve saati almak için
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageTk  # Gelişmiş resim işleme (Türkçe karakter yazdırma, GIF oynatma vb.)
from abc import ABC, abstractmethod  # SOYUTLAMA (Abstraction) yapısı için gerekli modüller

# --- SES KÜTÜPHANELERİ AYARLARI ---
# Kodun hem Windows hem Mac bilgisayarlarda hata vermeden çalışması için platform kontrolü
if platform.system() == "Windows":
    import winsound
    try:
        import pyttsx3  # Metni sese çeviren (Text-to-Speech) kütüphane
    except ImportError:
        pyttsx3 = None
else:
    pyttsx3 = None

# =============================================================================
# 1. TEMEL SOYUT SINIF (ABSTRACT BASE CLASS) - OOP KALITIM YAPISI
# =============================================================================
class GorevAsistaniTemel(ABC):
    """
    BLUAI'nin temel beyin yapısıdır.
    'Soyut Sınıf' olduğu için tek başına çalışmaz, diğer görevler (El Yıkama, Masa Kurma)
    bu sınıftan özellikleri miras alır (Inheritance). Kod tekrarını önler.
    """
    def __init__(self, gorev_adi, yardim_seviyesi):
        # KAPSÜLLEME (Encapsulation): Sınıf içi değişkenler _ ile korunur.
        self._gorev = gorev_adi
        self._seviye = yardim_seviyesi
        self._os_tipi = platform.system()
        
        # Oyun Durum Değişkenleri
        self._current_step = 1       # Hangi adımda olduğumuzu tutar
        self._islem_sayaci = 0       # Adımın tamamlanma yüzdesi (Progress Bar mantığı)
        self._basarili_adimlar = []  # Başarıyla biten adımların listesi
        self._adim_sureleri = {}     # Rapor için her adımın ne kadar sürdüğünü tutar
        self._exited = False         # Çıkış butonuna basılıp basılmadığı
        
        # Zamanlayıcılar ve Sayaçlar
        self._step_start_time = time.time()  # Adımın başladığı an
        self._total_start_time = time.time() # Görevin başladığı an
        self._glow_timer = 0         # İpucu butonunun yanıp sönme efekti için zamanlayıcı
        self._son_ses = 0            # Sesin sürekli tekrar etmesini önleyen kontrol değişkeni
        self._gif_sayac = 0          # Animasyonların hızını ayarlayan sayaç
        self._el_yok_sayaci = 0      # El kamerada görünmediğinde saymaya başlar
        self._el_yok_cerceve_timer = 0
        self._prev_hand_pos = None   # Elin bir önceki konumu (Hız hesaplamak için kullanılır)
        self._zaman_bitti = False
        self._rapor_kaydedildi = False

        # Hata Analizi (Raporlama için)
        self._hata_sayisi_el_yok = 0
        self._hata_sayisi_tek_el = 0

        # Görsel Efekt Değişkenleri
        self.konfeti_listesi = []
        self.asistan_duygu = "idle"  # Asistanın o anki ruh hali (bekliyor, konuşuyor, mutlu)
        self.asistan_mesaj = "Hadi başlayalım!" if self._seviye != "Bagimsiz Seviye" else ""

        # Windows için Ses Motorunu Başlatma
        if self._os_tipi == "Windows" and pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 140) # Konuşma hızı
            except: self.engine = None
        else: self.engine = None

        # Ortak Görsellerin Yüklenmesi (Asistan karakteri, butonlar vb.)
        self.asistan_idle = self._gif_yukle("asistan_idle.gif", asistan_modu=True)
        self.asistan_konus = self._gif_yukle("asistan_konus.gif", asistan_modu=True)
        self.asistan_mutlu = self._gif_yukle("asistan_mutlu.gif", asistan_modu=True)
        self.cikis_btn_img = self._resim_yukle("kırmızı_buton.png")
        self.yildiz_img = self._resim_yukle("yildiz.png")
        
        # Yazı Tiplerini (Font) Ayarla
        self._font_ayarla()

        # --- YAPAY ZEKA MODELİ: MEDIAPIPE ---
        # Google'ın geliştirdiği MediaPipe kütüphanesi ile el iskeletini tespit ediyoruz.
        import mediapipe.python.solutions.hands as mp_hands
        import mediapipe.python.solutions.drawing_utils as mp_draw
        self.mp_hands = mp_hands
        self.mp_draw = mp_draw
        self.yesil_stil = self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
        self.baglanti_stili = self.mp_draw.DrawingSpec(color=(0, 200, 0), thickness=2)
        # El tespiti için model parametreleri (Güven aralığı 0.5, Maksimum 2 el)
        self.detector = self.mp_hands.Hands(min_detection_confidence=0.5, max_num_hands=2)
        self.cap = cv2.VideoCapture(0) # Bilgisayar kamerasını başlatır
        
        # Video Yardımı Değişkenleri
        self.video_cap = None
        self.video_yuklendi = False

        # Alt sınıflarda doldurulacak boş listeler (Placeholder)
        self.piktogram_dosyalari = []
        self.mesajlar = []
        self.video_yolu = ""
        self.gorev_suresi = 0
        self.gorev_materyalleri = {}
        self.piktogramlar = []

    # --- SOYUT METODLAR (POLYMORPHISM - ÇOK BİÇİMLİLİK) ---
    # Bu metodların içi boştur. Alt sınıflar (El Yıkama / Masa Kurma) 
    # bu metodları kendine göre yeniden yazmak (Override) ZORUNDADIR.
    @abstractmethod
    def _goreve_ozel_yuklemeler(self):
        """Her görevin kendine özel resimlerini ve değişkenlerini yüklediği yer."""
        pass

    @abstractmethod
    def _ozel_cizim_yap(self, img, landmarks):
        """Göreve özel arka plan veya efekt çizimlerinin (sabun köpüğü, masa örtüsü) yapıldığı yer."""
        pass

    @abstractmethod
    def _adim_mantigini_islet(self, landmarks):
        """El hareketlerinin doğru olup olmadığının kontrol edildiği mantık merkezi."""
        pass

    @abstractmethod
    def _hedef_konumlari_al(self):
        """O anki adımda hedefin (sabun, tabak vb.) nerede olması gerektiğini belirtir."""
        pass

    # --- YARDIMCI METODLAR (HELPER METHODS) ---
    def _font_ayarla(self):
        """Yazı tiplerini yükler, dosya bulunamazsa varsayılanı kullanır."""
        try:
            self.font = ImageFont.truetype("arial.ttf", 28)
            self.buyuk_font = ImageFont.truetype("arial.ttf", 45)
            self.tebrik_font = ImageFont.truetype("arial.ttf", 100)
            self.buton_font = ImageFont.truetype("arial.ttf", 35)
            self.balon_font = ImageFont.truetype("arial.ttf", 26)
        except:
            self.font = self.buyuk_font = self.tebrik_font = self.buton_font = self.balon_font = ImageFont.load_default()

    def _resim_yukle(self, dosya_yolu, arka_plani_temizle=True):
        """PNG resimleri yükler ve beyaz arka planları şeffaf hale getirir."""
        if not os.path.exists(dosya_yolu): return None
        try:
            img_pil = Image.open(dosya_yolu).convert("RGBA")
            data = np.array(img_pil) 
            if arka_plani_temizle:
                rgb = data[:, :, :3]
                white_mask = np.all(rgb > 150, axis=-1) # Beyaz pikselleri bul
                data[white_mask, 3] = 0 # Alpha kanalını 0 yap (Görünmez kıl)
            return cv2.cvtColor(data, cv2.COLOR_RGBA2BGRA)
        except: return None

    def _gif_yukle(self, dosya_yolu, asistan_modu=False):
        """GIF dosyalarını kare kare parçalayıp oynatılmaya hazır hale getirir."""
        if not os.path.exists(dosya_yolu): return None
        try:
            img_obj = Image.open(dosya_yolu); kareler = []
            for kare in ImageSequence.Iterator(img_obj):
                kare_rgba = kare.convert("RGBA"); data = np.array(kare_rgba)
                if asistan_modu: # Asistanın arka planını temizle
                    rgb = data[:, :, :3]; white_mask = np.all(rgb > 230, axis=-1); data[white_mask, 3] = 0 
                kareler.append(cv2.cvtColor(data, cv2.COLOR_RGBA2BGRA))
            return kareler
        except: return None

    def _imge_ekle_seffaf(self, img, imge_bgra, x, y, boyut, opacity=1.0):
        """
        Gelişmiş Görüntü İşleme:
        Bir resmi (imge_bgra) başka bir resmin (img) üzerine 
        şeffaflık kanallarını (Alpha Channel) koruyarak yapıştırır.
        """
        if imge_bgra is None: return img
        try:
            imge_res = cv2.resize(imge_bgra, (boyut, boyut))
            h_res, w_res, _ = imge_res.shape; h_img, w_img, _ = img.shape
            x, y = int(x), int(y)
            # Resmin ekran dışına taşmasını engelleme kontrolleri
            if x + w_res > w_img: w_res = w_img - x
            if y + h_res > h_img: h_res = h_img - y
            if h_res <= 0 or w_res <= 0: return img
            roi = img[y:y+h_res, x:x+w_res]
            # Piksel Karıştırma (Alpha Blending)
            alpha = (imge_res[:h_res, :w_res, 3] / 255.0) * opacity
            alpha_inv = 1.0 - alpha
            for c in range(0, 3): roi[:, :, c] = (alpha * imge_res[:h_res, :w_res, c] + alpha_inv * roi[:, :, c])
            img[y:y+h_res, x:x+w_res] = roi
        except: pass
        return img

    def _yazi_yaz(self, img, metin, x, y, font_tipi="normal", renk=(255, 255, 255)):
        """OpenCV'nin desteklemediği Türkçe karakterleri PIL kütüphanesi ile yazar."""
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        if font_tipi == "tebrik": f, sw = self.tebrik_font, 8
        elif font_tipi == "buyuk": f, sw = self.buyuk_font, 4
        elif font_tipi == "buton": f, sw = self.buton_font, 3
        elif font_tipi == "balon": f, sw = self.balon_font, 0
        else: f, sw = self.font, 3
        draw.text((int(x), int(y)), metin, font=f, fill=renk, stroke_width=sw, stroke_fill=(0, 0, 0) if sw > 0 else None)
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    def _seslendir(self, metin):
        """Metni sese çevirir (Thread kullanarak ana döngüyü dondurmaz)."""
        def calistir():
            if self._os_tipi == "Darwin": os.system(f"say '{metin}' &")
            elif self._os_tipi == "Windows" and self.engine:
                try: self.engine.say(metin); self.engine.runAndWait()
                except: pass
        threading.Thread(target=calistir, daemon=True).start()

    def _ping_cal(self):
        """Başarılı işlem sesi çalar."""
        def cal():
            if self._os_tipi == "Darwin": os.system("afplay /System/Library/Sounds/Glass.aiff &")
            elif self._os_tipi == "Windows": winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        threading.Thread(target=cal, daemon=True).start()

    def _gri_yap(self, img_bgra):
        """Resmi siyah-beyaza çevirir (Tamamlanmamış adımları göstermek için)."""
        if img_bgra is None: return None
        b, g, r, a = cv2.split(img_bgra)
        gray = cv2.cvtColor(cv2.merge([b, g, r]), cv2.COLOR_BGR2GRAY)
        return cv2.merge([gray, gray, gray, a])

    def _adimi_bitir(self, basarili=False):
        """Adım tamamlandığında verileri kaydeder ve sonraki adıma geçirir."""
        sure = round(time.time() - self._step_start_time, 2)
        durum = "Basarili" if basarili else "Süre Bitti"
        self._adim_sureleri[self._current_step] = {"sure": sure, "durum": durum}
        
        if basarili:
            self._basarili_adimlar.append(self._current_step)
            self._ping_cal()
            if self._seviye != "Bagimsiz Seviye": 
                self.asistan_duygu, self.asistan_mesaj = "mutlu", random.choice(["Aferin!", "Harika!", "Süpersin!"])
        else:
            if self._seviye != "Bagimsiz Seviye": 
                self.asistan_duygu, self.asistan_mesaj = "idle", "Süre bitti."
        
        self._islem_sayaci = 0
        self._current_step += 1
        self._step_start_time = time.time()
        self._el_yok_sayaci = 0
        self._prev_hand_pos = None

    def _rapor_kaydet(self):
        """Performans verilerini metin dosyasına kaydeder (Öğretmen analizi için)."""
        if self._rapor_kaydedildi: return
        self._rapor_kaydedildi = True
        tarih, toplam_sure = datetime.now().strftime("%d-%m-%Y %H:%M"), round(time.time() - self._total_start_time, 2)
        basari_orani = round((len(self._basarili_adimlar) / 6) * 100, 1)
        with open("performans_raporu.txt", "a") as f:
            f.write(f"\n{'='*40}\nTarih: {tarih}\nGörev: {self._gorev} | Seviye: {self._seviye}\nToplam Süre: {toplam_sure}s | Başarı: %{basari_orani}\nHatalar -> El Yok: {self._hata_sayisi_el_yok}, Tek El: {self._hata_sayisi_tek_el}\nAdım Detayları:\n")
            for adim, veri in self._adim_sureleri.items(): f.write(f"  Adım {adim}: {veri['sure']}s ({veri['durum']})\n")
            f.write(f"{'='*40}\n")

    def _takip_seridi_ciz(self, img):
        """Ekranın üstündeki adım piktogramlarını (görsel yönergeleri) çizer."""
        size, gap = 65, 15
        total_w = (size + gap) * 6 - gap
        start_x = (self.w - total_w) // 2
        y_pos = 10
        for i, p_img in enumerate(self.piktogramlar):
            if p_img is None: continue
            x, step_num = start_x + i * (size + gap), i + 1
            if step_num == self._current_step:
                cv2.rectangle(img, (x-5, y_pos-5), (x+size+5, y_pos+size+5), (0, 255, 255), -1)
                display_img = p_img
            else: display_img = self._gri_yap(p_img)
            img = self._imge_ekle_seffaf(img, display_img, x, y_pos, size, opacity=1.0 if step_num <= self._current_step else 0.4)
        return img
    
    def _yildiz_paneli_ciz(self, img):
        """Kazanılan yıldızları sağ üst köşeye çizer (Oyunlaştırma)."""
        px = self.w - 580 
        for i in range(6):
            x_pos = px + (i * 70)
            if (i + 1) in self._basarili_adimlar:
                if self.yildiz_img is not None: img = self._imge_ekle_seffaf(img, self.yildiz_img, x_pos, 15, 55)
                else: cv2.circle(img, (x_pos + 27, 42), 22, (0, 255, 0), -1)
            else: cv2.circle(img, (x_pos + 27, 42), 20, (180, 180, 180), -1)
        return img
    
    def _asistan_ciz(self, img):
        """Asistan karakterini ve konuşma balonunu ekrana yerleştirir."""
        if self._seviye == "Bagimsiz Seviye": return img
        ax, ay, a_boy = self.w - 350, self.h - 400, 340 
        fr = self.asistan_mutlu if self.asistan_duygu == "mutlu" else (self.asistan_konus if self.asistan_duygu == "konusuyor" else self.asistan_idle)
        if time.time() < self._el_yok_cerceve_timer:
            if self._gif_sayac % 10 < 5: 
                cv2.rectangle(img, (ax - 20, ay - 20), (ax + a_boy + 20, ay + a_boy + 20), (0, 0, 255), 10)
        if fr: img = self._imge_ekle_seffaf(img, fr[self._gif_sayac % len(fr)], ax, ay, a_boy)
        if self.asistan_mesaj:
            bw, bh = 300, 105; bx, by = ax - bw - 20, ay + 40; r = 25 
            border_renk = (0, 255, 255) if time.time() < self._glow_timer else (0, 0, 0)
            cv2.rectangle(img, (bx+r, by), (bx+bw-r, by+bh), (255, 255, 255), -1)
            cv2.rectangle(img, (bx, by+r), (bx+bw, by+bh-r), (255, 255, 255), -1)
            for cp in [(bx+r, by+r), (bx+bw-r, by+r), (bx+r, by+bh-r), (bx+bw-r, by+bh-r)]: cv2.circle(img, cp, r, (255, 255, 255), -1)
            cv2.line(img, (bx+r, by), (bx+bw-r, by), border_renk, 4); cv2.line(img, (bx+r, by+bh), (bx+bw-r, by+bh), border_renk, 4)
            cv2.line(img, (bx, by+r), (bx, by+bh-r), border_renk, 4); cv2.line(img, (bx+bw, by+r), (bx+bw, by+bh-r), border_renk, 4)
            img = self._yazi_yaz(img, self.asistan_mesaj, bx + 25, by + 35, font_tipi="balon", renk=(0, 0, 0))
        return img

    def _video_yardimi_ciz(self, img):
        """Sol altta model olma videosunu oynatır (Video Yardımı seviyesi için)."""
        if self._seviye != "Video Yardimi" or self._current_step > 6:
            if self.video_cap: self.video_cap.release(); self.video_cap = None
            return img
        if not self.video_yuklendi and os.path.exists(self.video_yolu):
            self.video_cap = cv2.VideoCapture(self.video_yolu); self.video_yuklendi = True
        if self.video_cap and self.video_cap.isOpened():
            for _ in range(2): self.video_cap.grab()
            ret, frame = self.video_cap.read()
            if not ret: self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ret, frame = self.video_cap.read()
            if ret:
                vw, vh = 320, 180 
                v_frame = cv2.resize(frame, (vw, vh))
                y_pos, x_pos = self.h - vh - 25, 25
                cv2.rectangle(img, (x_pos-5, y_pos-5), (x_pos+vw+5, y_pos+vh+5), (255, 255, 255), -1)
                img[y_pos:y_pos+vh, x_pos:x_pos+vw] = v_frame
                img = self._yazi_yaz(img, "ÖRNEK UYGULAMA", x_pos, y_pos - 40, renk=(0, 255, 255))
        return img

    def _fare_tiklama(self, event, x, y, flags, param):
        """Mouse tıklamalarını algılar (Çıkış butonu)."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if 20 < x < 120 and 15 < y < 115: self._exited = True
            if self._current_step == 7:
                btx, bty = self.w // 2 - 200, self.h // 2 + 80
                if btx < x < btx + 400 and bty < y < bty + 100: self._exited = True

    # --- ANA DÖNGÜ (MAIN LOOP) ---
    def baslat(self):
        """BLUAI uygulamasını başlatan ana fonksiyon."""
        self._goreve_ozel_yuklemeler() # Polimorfizm: Seçilen göreve göre materyalleri yükle
        self.piktogramlar = [self._resim_yukle(d) for d in self.piktogram_dosyalari]
        
        # Pencere Başlığını Güncelledik: BLUAI
        win_name = "BLUAI - Akilli Egitim Ekrani"
        cv2.namedWindow(win_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(win_name, self._fare_tiklama)
        
        self._step_start_time = time.time()
        self._total_start_time = time.time()

        while self.cap.isOpened() and not self._exited:
            success, img = self.cap.read()
            if not success: break
            img = cv2.flip(img, 1); self.h, self.w, _ = img.shape
            results = self.detector.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            landmarks = results.multi_hand_landmarks
            
            self._gif_sayac += 1
            
            # Üst Bant ve Paneller
            cv2.rectangle(img, (0, 0), (self.w, 85), (240, 240, 240), cv2.FILLED)
            img = self._yildiz_paneli_ciz(img)
            img = self._takip_seridi_ciz(img)

            # --- DÜZELTME: MASA/ARKAPLAN ÇİZİMİ ---
            # Masanın, süre yazısının arkasında kalmaması için önce masayı çiziyoruz.
            img = self._ozel_cizim_yap(img, landmarks)

            if self._current_step < 7:
                # Sesli Yönerge Kontrolü
                if self._current_step != self._son_ses:
                    msg = self.mesajlar[self._current_step-1]
                    if self._seviye != "Bagimsiz Seviye":
                        if self._seviye in ["Ses Yardimi", "Video Yardimi"]: self._seslendir(msg); self._glow_timer = time.time() + 2.0
                        self.asistan_duygu, self.asistan_mesaj = "konusuyor", msg
                    self._son_ses = self._current_step

                # Süre Kontrolü ve Ekrana Yazdırma
                # Süre yazısı artık masanın ÜZERİNE (önüne) yazılıyor.
                kalan_sure = self.gorev_suresi - (time.time() - self._total_start_time)
                if kalan_sure <= 0: self._zaman_bitti = True; self._current_step = 7
                else: 
                    img = self._yazi_yaz(img, f"Süre: {int(kalan_sure)}s", self.w-220, self.h-80, renk=(255,255,255))
                
                # El Yok Kontrolü
                num_hands = len(landmarks) if landmarks else 0
                if num_hands == 0:
                    self._el_yok_sayaci += 1
                    if self._el_yok_sayaci == 30: self._hata_sayisi_el_yok += 1; self._el_yok_cerceve_timer = time.time() + 2.0
                    if self._el_yok_sayaci > 29 and self._seviye != "Bagimsiz Seviye": self.asistan_mesaj = "Elini göremiyorum!"
                else:
                    self._el_yok_sayaci = 0
            
            # Hedef ve Metin Bilgileri
            gx, gy, g_boy, yonerge = self._hedef_konumlari_al()
            
            # Ortak El İskeleti Çizimi (MediaPipe)
            if landmarks and self._current_step < 7:
                for hand_lms in landmarks: self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS, self.yesil_stil, self.baglanti_stili)
                
                # --- POLYMORPHISM: GÖREV MANTIĞI ---
                # Seçilen göreve göre (El yıkama kuralları vs.) mantık işlenir.
                self._adim_mantigini_islet(landmarks)

            # --- GÖREV MATERYALLERİNİN VE YARDIMCILARIN ÇİZİMİ ---
            if self._current_step < 7:
                img = self._video_yardimi_ciz(img)
                
                # İlerleme Yüzdesi
                if self._islem_sayaci > 0:
                    if hasattr(self, 'obj_x') and self.obj_x is not None: prog_x, prog_y = self.obj_x, self.obj_y
                    else: prog_x, prog_y = gx, gy
                    img = self._yazi_yaz(img, f"%{int(self._islem_sayaci)}", prog_x, prog_y + g_boy + 10)
                    if self._islem_sayaci >= 100: self._adimi_bitir(basarili=True)
                
                # Materyali (Sabun, Tabak vs.) Çiz
                materyal = self.gorev_materyalleri.get(self._current_step)
                if hasattr(self, 'obj_x') and self.obj_x is not None: mx, my = self.obj_x, self.obj_y
                else: mx, my = gx, gy

                if materyal is not None:
                    if isinstance(materyal, list): img = self._imge_ekle_seffaf(img, materyal[self._gif_sayac % len(materyal)], mx, my, g_boy)
                    else: img = self._imge_ekle_seffaf(img, materyal, mx, my, g_boy)
                
                img = self._yazi_yaz(img, yonerge, 100, 20, font_tipi="buyuk")

            # --- BİTİŞ EKRANI (ADIM 7) ---
            if self._current_step == 7:
                self._rapor_kaydet()
                basari_durumu = (not self._zaman_bitti) and (len(self._basarili_adimlar) >= 5)
                if basari_durumu:
                    self.asistan_duygu, self.asistan_mesaj = "mutlu", "Harika iş çıkardın!"
                    if not self.konfeti_listesi:
                        for _ in range(150): self.konfeti_listesi.append({'x': random.randint(0, self.w), 'y': random.randint(self.h//2, self.h), 'vx': random.randint(-20, 20), 'vy': random.randint(-30, -10), 'renk': (random.randint(0,255), random.randint(0,255), random.randint(0,255)), 'boyut': random.randint(8, 15), 'gravity': 1.2})
                    for p in self.konfeti_listesi:
                        p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] += p['gravity']
                        if 0 <= p['x'] <= self.w and p['y'] <= self.h: cv2.circle(img, (int(p['x']), int(p['y'])), p['boyut']//2, p['renk'], -1)
                    img = self._yazi_yaz(img, "TEBRİKLER!", self.w//2-300, self.h//2-150, font_tipi="tebrik")
                else:
                    self.asistan_duygu, self.asistan_mesaj = "idle", "Süre doldu..." if self._zaman_bitti else "Tekrar deneyelim!"
                    img = self._yazi_yaz(img, "SÜRE BİTTİ..." if self._zaman_bitti else "OLMADI...", self.w//2-200, self.h//2-150, font_tipi="tebrik", renk=(0,0,255))
                
                cv2.rectangle(img, (self.w//2-200, self.h//2+80), (self.w//2+200, self.h//2+180), (0, 150, 0), -1)
                img = self._yazi_yaz(img, "ANA MENÜYE DÖN", self.w//2-150, self.h//2+110, font_tipi="buton")

            if self.cikis_btn_img is not None:
                img = self._imge_ekle_seffaf(img, self.cikis_btn_img, 20, 15, 80)

            img = self._asistan_ciz(img)
            cv2.imshow(win_name, img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        if self.video_cap: self.video_cap.release()
        self._rapor_kaydet(); self.cap.release(); cv2.destroyAllWindows()


# =============================================================================
# 2. SOMUT SINIF (CONCRETE CLASS) - EL YIKAMA GÖREVİ
# =============================================================================
class ElYikamaAsistani(GorevAsistaniTemel):
    """
    BLUAI'nin El Yıkama modülüdür.
    'GorevAsistaniTemel' sınıfından miras alır ve el yıkama kurallarını uygular.
    """
    def _goreve_ozel_yuklemeler(self):
        self.piktogram_dosyalari = ["p_sabun.png", "p_musluk_ac.png", "p_el_ovustur.png", "p_el_yikama.png", "p_musluk_kapat.png", "p_havlu.png"]
        self.mesajlar = ["Sabunu al.", "Musluğu aç.", "Ellerini ovuştur (İki El).", "Şimdi yıka (İki El).", "Musluğu kapat.", "Ellerini kurula (İki El).", "Bitti!"]
        self.video_yolu = "el_yikama_tam.mp4"
        self.gorev_suresi = 120 
        
        self.microbe_opacity = 1.0
        self.foam_particles = []
        self.mikrop_img = self._resim_yukle("mikrop.png")
        self.kopuk_img = self._resim_yukle("kopuk.png")
        
        self.gorev_materyalleri = {
            1: self._gif_yukle("sabun.gif"), 
            2: self._gif_yukle("musluk.gif"), 
            3: self._gif_yukle("ovustur.gif"), 
            4: self._gif_yukle("ovustur.gif"), 
            5: self._gif_yukle("musluk.gif"), 
            6: self._resim_yukle("kurulama.png") 
        }

    def _hedef_konumlari_al(self):
        gx, gy, g_boy, yonerge = 0, 0, 250, ""
        if self._current_step == 1: gx, gy, yonerge = 100, 150, "1. ADIM: SABUNU AL"
        elif self._current_step == 2: gx, gy, yonerge = self.w-400, 150, "2. ADIM: MUSLUĞU AÇ"
        elif self._current_step == 3: gx, gy, yonerge = self.w//2-125, self.h//2-125, "3. ADIM: ELLERİNİ OVUŞTUR (İki El)"
        elif self._current_step == 4: gx, gy, yonerge = self.w//2-125, self.h//2-125, "4. ADIM: ELLERİNİ YIKA (İki El)"
        elif self._current_step == 5: gx, gy, yonerge = self.w-400, 150, "5. ADIM: MUSLUĞU KAPAT"
        elif self._current_step == 6: gx, gy, yonerge = self.w//2-125, self.h//2-125, "6. ADIM: ELLERİNİ KURULA (İki El)"
        return gx, gy, g_boy, yonerge

    def _ozel_cizim_yap(self, img, landmarks):
        if self._current_step > 4: self.microbe_opacity = 0.0
        
        if self.microbe_opacity > 0 and landmarks:
            for handLms in landmarks:
                for pt in [4, 8, 12, 16, 20, 0, 9]:
                    cx, cy = int(handLms.landmark[pt].x * self.w), int(handLms.landmark[pt].y * self.h)
                    img = self._imge_ekle_seffaf(img, self.mikrop_img, cx-25, cy-25, 50, opacity=self.microbe_opacity)
        
        if self._current_step == 3 and landmarks:
            for handLms in landmarks:
                if self._gif_sayac % 2 == 0:
                    self.foam_particles.append({'x': int(handLms.landmark[9].x * self.w) + random.randint(-40, 40), 'y': int(handLms.landmark[9].y * self.h) + random.randint(-40, 40), 'vx': random.uniform(-2, 2), 'vy': random.uniform(-3, -1), 's': random.randint(20, 50), 'life': 1.0})
        
        for f in self.foam_particles[:]:
            current_opacity = f['life']
            if self._current_step == 4: current_opacity = min(f['life'], self.microbe_opacity)
            img = self._imge_ekle_seffaf(img, self.kopuk_img, int(f['x']), int(f['y']), f['s'], opacity=current_opacity)
            f['x'] += f['vx']; f['y'] += f['vy']; f['life'] -= 0.02 if self._current_step == 4 else 0.005
            if f['life'] <= 0 or current_opacity <= 0: self.foam_particles.remove(f)
        return img

    def _adim_mantigini_islet(self, landmarks):
        gx, gy, g_boy, _ = self._hedef_konumlari_al()
        l = landmarks[0]
        cx, cy = int(l.landmark[8].x * self.w), int(l.landmark[8].y * self.h)
        num_hands = len(landmarks)
        
        hand_speed = 0
        if self._prev_hand_pos: hand_speed = np.sqrt((cx/self.w - self._prev_hand_pos[0])**2 + (cy/self.h - self._prev_hand_pos[1])**2)
        self._prev_hand_pos = (cx/self.w, cy/self.h)

        if self._current_step == 1 and gx < cx < gx+g_boy and gy < cy < gy+g_boy: self._adimi_bitir(basarili=True)
        elif self._current_step in [2, 5] and gx < cx < gx+g_boy and gy < cy < gy+g_boy: self._islem_sayaci += 1.5
        elif self._current_step == 3:
            if num_hands == 2 and hand_speed > 0.01: self._islem_sayaci += 1.2
            elif num_hands == 1: self.asistan_mesaj = "İki elini kullan!"
        elif self._current_step == 4:
            if num_hands == 2: self._islem_sayaci += 1.0; self.microbe_opacity = max(0, self.microbe_opacity - 0.01)
            elif num_hands == 1: self.asistan_mesaj = "İki elini kullan!"
        elif self._current_step == 6:
            if num_hands == 2 and hand_speed > 0.01: self._islem_sayaci += 1.0
            elif num_hands == 1: self.asistan_mesaj = "İki elini kullan!"

# =============================================================================
# 3. SOMUT SINIF (CONCRETE CLASS) - MASA KURMA GÖREVİ
# =============================================================================
class MasaKurmaAsistani(GorevAsistaniTemel):
    """
    BLUAI'nin Masa Kurma modülüdür.
    'GorevAsistaniTemel' sınıfından miras alır ve 'Sürükle-Bırak' algoritmasını uygular.
    """
    def _goreve_ozel_yuklemeler(self):
        self.piktogram_dosyalari = ["tabak.png", "catal.png", "bicak.png", "kasik.png", "bardak.png", "pecete.png"]
        self.mesajlar = ["Tabağı merkeze koy.", "Çatalı sola koy.", "Bıçağı sağa koy.", "Kaşığı yanına ekle.", "Bardağı sağ üste koy.", "Peçeteyi yerleştir.", "Masa Hazır!"]
        self.video_yolu = "masa_kurma_tam.mp4"
        self.gorev_suresi = 180 
        
        self.masa_img = self._resim_yukle("masa.png", arka_plani_temizle=False)
        self.obj_x = None
        self.obj_y = None
        
        self.gorev_materyalleri = {
            1: self._resim_yukle("p_tabak.png"),
            2: self._resim_yukle("p_catal.png"),
            3: self._resim_yukle("p_bicak.png"),
            4: self._resim_yukle("p_kasik.png"),
            5: self._resim_yukle("p_bardak.png"),
            6: self._resim_yukle("p_pecete.png")
        }

    def _hedef_konumlari_al(self):
        gx, gy, g_boy, yonerge = 0, 0, 250, ""
        masa_ustu_y = self.h - 280; center_x = self.w // 2
        if self._current_step == 1: gx, gy, yonerge = center_x - 100, masa_ustu_y, "1. ADIM: TABAĞI YERLEŞTİR"
        elif self._current_step == 2: gx, gy, yonerge = center_x - 300, masa_ustu_y, "2. ADIM: ÇATALI SOLA KOY"
        elif self._current_step == 3: gx, gy, yonerge = center_x + 150, masa_ustu_y, "3. ADIM: BIÇAĞI SAĞA KOY"
        elif self._current_step == 4: gx, gy, yonerge = center_x + 300, masa_ustu_y, "4. ADIM: KAŞIĞI EKLE"
        elif self._current_step == 5: gx, gy, yonerge = center_x + 200, masa_ustu_y - 120, "5. ADIM: BARDAĞI KOY"
        elif self._current_step == 6: gx, gy, yonerge = center_x - 450, masa_ustu_y, "6. ADIM: PEÇETEYİ KOY"
        return gx, gy, g_boy, yonerge

    def _ozel_cizim_yap(self, img, landmarks):
        # Masa Çizimi (Sürenin arkasında kalmaması için önce çizilir)
        if self.masa_img is not None:
            masa_h = 300; masa_w = self.w
            masa_resized = cv2.resize(self.masa_img, (masa_w, masa_h)); y_offset = self.h - masa_h
            alpha_s = masa_resized[:, :, 3] / 255.0; alpha_l = 1.0 - alpha_s
            for c in range(0, 3): img[y_offset:self.h, 0:self.w, c] = (alpha_s * masa_resized[:, :, c] + alpha_l * img[y_offset:self.h, 0:self.w, c])
        
        # Hedef Kutusu Çizimi (Yanıp sönme efektiyle)
        gx, gy, g_boy, _ = self._hedef_konumlari_al()
        box_color = (0, 255, 255) if (self._gif_sayac // 10) % 2 == 0 else (200, 200, 200)
        thickness = 5 if (self._gif_sayac // 10) % 2 == 0 else 2
        cv2.rectangle(img, (gx, gy), (gx + g_boy, gy + g_boy), box_color, thickness)
        
        return img

    def _adim_mantigini_islet(self, landmarks):
        gx, gy, g_boy, _ = self._hedef_konumlari_al()
        l = landmarks[0]
        cx, cy = int(l.landmark[8].x * self.w), int(l.landmark[8].y * self.h)
        
        if self.obj_x is None: self.obj_x = random.randint(100, self.w - 350); self.obj_y = random.randint(150, self.h - 350)
        
        # Tutma Mantığı
        if self.obj_x < cx < self.obj_x + g_boy and self.obj_y < cy < self.obj_y + g_boy: 
            self.obj_x = cx - g_boy // 2; self.obj_y = cy - g_boy // 2
        
        # Bırakma ve Hedef Kontrolü
        if gx < self.obj_x + g_boy // 2 < gx + g_boy and gy < self.obj_y + g_boy // 2 < gy + g_boy: 
            self._islem_sayaci += 2.0 
        
        if self._islem_sayaci >= 100: self.obj_x = None; self.obj_y = None


# =============================================================================
# 4. ARAYÜZ SINIFI (GUI) - ANA MENÜ
# =============================================================================
class UygulamaArayuzu:
    """
    BLUAI'nin giriş kapısı. Menüleri, butonları ve görev seçimlerini yönetir.
    Fabrika Tasarım Deseni (Factory Pattern) benzeri bir yapıyla ilgili görevi başlatır.
    """
    def __init__(self, root):
        self.root = root; 
        self.root.title("BLUAI - Akıllı Eğitim Asistanı") # Başlığı Güncelledik
        self.root.attributes("-fullscreen", True)
        self.canvas = tk.Canvas(root, highlightthickness=0); self.canvas.pack(fill="both", expand=True)
        self.renkler = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#F3D1F4"]
        self.arka_plan_rengi = random.choice(self.renkler)
        self.canvas.configure(bg=self.arka_plan_rengi)
        
        self.img_cache = {}
        self.load_images()
        self.menu_olustur()
    
    def buton_sesi(self):
        ses_yolu = "tik_sesi.wav"
        if not os.path.exists(ses_yolu): return 
        def cal():
            if platform.system() == "Windows":
                winsound.PlaySound(ses_yolu, winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif platform.system() == "Darwin":
                os.system(f"afplay '{ses_yolu}' &")
        threading.Thread(target=cal, daemon=True).start()

    def seffaf_yap(self, dosya, boyut):
        if not os.path.exists(dosya): return None
        img = Image.open(dosya).convert("RGBA")
        data = np.array(img)
        r, g, b, a = data.T
        white_areas = (r > 200) & (g > 200) & (b > 200)
        data[..., 3][white_areas.T] = 0
        return ImageTk.PhotoImage(Image.fromarray(data).resize(boyut, Image.Resampling.LANCZOS))

    def resim_birlestir(self, bg_path, icon_path, size):
        if not os.path.exists(bg_path): return None
        try:
            bg_img = Image.open(bg_path).convert("RGBA")
            bg_img = bg_img.resize(size, Image.Resampling.LANCZOS)
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path).convert("RGBA")
                icon_data = np.array(icon_img)
                rgb = icon_data[:, :, :3]
                white_mask = np.all(rgb > 200, axis=-1)
                icon_data[white_mask, 3] = 0
                icon_img = Image.fromarray(icon_data)
                icon_h = int(size[1] * 0.6)
                aspect = icon_img.width / icon_img.height
                icon_w = int(icon_h * aspect)
                icon_img = icon_img.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
                x = (size[0] - icon_w) // 2
                y = (size[1] - icon_h) // 2
                bg_img.paste(icon_img, (x, y), icon_img)
            return ImageTk.PhotoImage(bg_img)
        except: return None

    def load_images(self):
        self.img_cache["el_yikama_btn"] = self.resim_birlestir("mavi_buton.png", "ana_menu_el_yikama.png", (280, 140))
        self.img_cache["masa_kurma_btn"] = self.resim_birlestir("mavi_buton.png", "ana_menu_masa_kurma.png", (280, 140))
        self.img_cache["video_btn"] = self.resim_birlestir("yesil_buton.png", "ipucu_video.png", (180, 90))
        self.img_cache["ses_btn"] = self.resim_birlestir("yesil_buton.png", "ipucu_ses.png", (180, 90))
        self.img_cache["bagimsiz_btn"] = self.resim_birlestir("yesil_buton.png", "ipucu_bagimsiz.png", (180, 90))
        self.img_cache["cikis_btn"] = self.seffaf_yap("kırmızı_buton.png", (100, 100))

    def menu_olustur(self):
        self.canvas.delete("all")
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        center_x = sw // 2
        center_y = sh // 2

        self.main_frame = tk.Frame(self.canvas, bg="white", padx=40, pady=40, highlightthickness=5, highlightbackground="#5DADE2")
        tk.Label(self.main_frame, text="BLUAI - GÖREV SEÇ", font=("Arial", 40, "bold"), bg="white", fg="#2E4053").pack(pady=20)

        btn_frame = tk.Frame(self.main_frame, bg="white")
        btn_frame.pack()

        btn_el = tk.Button(btn_frame, image=self.img_cache["el_yikama_btn"], text="",
                           command=lambda: [self.buton_sesi(), self.secim_penceresi_ac("El Yikama")],
                           font=("Arial", 16, "bold"), compound="center",
                           bg="white", borderwidth=0, activebackground="white", highlightthickness=0, bd=0, relief="flat")
        btn_el.pack(side="left", padx=20)

        btn_masa = tk.Button(btn_frame, image=self.img_cache["masa_kurma_btn"], text="",
                             command=lambda: [self.buton_sesi(), self.secim_penceresi_ac("Masa Kurma")],
                             font=("Arial", 16, "bold"), compound="center",
                             bg="white", borderwidth=0, activebackground="white", highlightthickness=0, bd=0, relief="flat")
        btn_masa.pack(side="left", padx=20)

        self.canvas.create_window(center_x, center_y - 50, window=self.main_frame)
        
        btn_exit_id = self.canvas.create_image(center_x, center_y + 220, image=self.img_cache["cikis_btn"])
        
        def on_exit_click(event):
            self.buton_sesi()
            self.root.destroy()
            
        self.canvas.tag_bind(btn_exit_id, "<Button-1>", on_exit_click)
        self.canvas.tag_bind(btn_exit_id, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(btn_exit_id, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def secim_penceresi_ac(self, gorev_adi):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True) 
        p_width, p_height = 650, 350
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        popup.geometry(f"{p_width}x{p_height}+{screen_w//2 - p_width//2}+{screen_h//2 - p_height//2}")
        popup.configure(bg="white", highlightthickness=4, highlightbackground="#58D68D")
        popup.grab_set()

        tk.Label(popup, text=f"{gorev_adi.upper()}\nYardım Seviyesi Seç", font=("Arial", 18, "bold"), bg="white", fg="#1D8348").pack(pady=15)
        
        btn_p_frame = tk.Frame(popup, bg="white")
        btn_p_frame.pack(pady=5)

        levels = [("Video Yardimi", "video_btn"), ("Ses Yardimi", "ses_btn"), ("Bagimsiz Seviye", "bagimsiz_btn")]

        for level_key, img_key in levels:
            btn = tk.Button(btn_p_frame, image=self.img_cache[img_key], text="",
                            command=lambda l=level_key: [self.buton_sesi(), self.asistani_ac(gorev_adi, l, popup)],
                            font=("Arial", 11, "bold"), compound="center",
                            bg="white", activebackground="white", borderwidth=0, highlightthickness=0, relief="flat", bd=0)
            btn.pack(side="left", padx=8)

        tk.Button(popup, text="VAZGEÇ", command=lambda: [self.buton_sesi(), popup.destroy()], 
                  font=("Arial", 10, "bold"), fg="red", bg="white", borderwidth=0).pack(pady=15)

    def asistani_ac(self, gorev, seviye, popup_window):
        popup_window.destroy()
        self.root.withdraw()
        
        if gorev == "El Yikama":
            uygulama = ElYikamaAsistani(gorev, seviye)
        else:
            uygulama = MasaKurmaAsistani(gorev, seviye)
            
        uygulama.baslat()
        
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)

if __name__ == "__main__":
    root = tk.Tk(); app = UygulamaArayuzu(root); root.bind("<Escape>", lambda e: root.destroy()); root.mainloop()