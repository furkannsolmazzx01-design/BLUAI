# 🧩 BLUAI - Otizm Spektrum Bozukluğu Olan Özel Gereksinimli Öğrenciler İçin Yapay Zekâ Destekli Öğrenme Asistanı Oluşturulması - Creating an AI Supported Learning Assistant for Students with Special Needs and Autism Spectrum Disorder

**BLUAI**, Otizm Spektrum Bozukluğu (OSB) tanısı olan çocukların günlük yaşam becerilerini (özbakım ve sorumluluklar) bağımsız olarak kazanmalarını desteklemek amacıyla geliştirilmiş, yapay zeka tabanlı etkileşimli bir eğitim yazılımıdır.

## 🎯 Projenin Amacı
Bu proje, **Otizm Spektrum Bozukluğu tanısı olan özel gereksinimli öğrencilerin** eğitiminde "görsel modelleme", "beceri analizi" ve "anında dönüt" yöntemlerini teknoloji ile birleştirir. Sistem, bilgisayar kamerası aracılığıyla çocuğun fiziksel hareketlerini takip eder, doğru davranışları pekiştirir ve süreci oyunlaştırarak öğrenmeyi kalıcı hale getirir.

* **Hedef Kitle:** Otizm Spektrum Bozukluğu olan çocuklar, özel öğrenme güçlüğü yaşayan bireyler ve özel eğitim öğrencileri.
* **Temel Kazanım:** "El Yıkama" ve "Masa Kurma" gibi temel becerilerin, başkasına ihtiyaç duymadan (bağımsız) yapılabilmesini sağlamak.

## 🚀 Temel Özellikler

* **🖐️ Gerçek Zamanlı El Takibi:** Google MediaPipe teknolojisi ile çocuğun el hareketleri milisaniyelik hızla analiz edilir. Fiziksel temas gerektirmez.
* **🤖 Sesli ve Görsel Asistan:** Her adımda (Örn: "Sabunu al", "Musluğu kapat") sesli yönergeler verilir ve ekranda ilgili piktogramlar (görsel kartlar) gösterilir.
* **⭐ Oyunlaştırma (Gamification):**
    * Başarılı tamamlanan her adımda yıldız kazanma.
    * Görev bitiminde konfeti efektleri ve motivasyon artırıcı sesli tebrikler.
* **📊 Gelişim Raporlama:** Eğitimciler ve ebeveynler için, çocuğun performansını analiz eden otomatik bir `.txt` raporu oluşturulur (Hangi adımda ne kadar süre harcandı, hata sayısı vb.).
* **🎮 Etkileşimli Modüller:**
    * **El Yıkama Modülü:** Sanal mikroplar (eller yıkandıkça kaybolan) ve köpük efektleri ile hijyen eğitimi somutlaştırılır.
    * **Masa Kurma Modülü:** "Sürükle-Bırak" mantığıyla tabağı, çatalı ve bardağı ekrandaki doğru hedef noktalarına yerleştirme becerisi çalışılır.

## 🛠️ Kullanılan Teknolojiler

Bu proje **Python** dili ile geliştirilmiştir.

* **Görüntü İşleme:** OpenCV
* **Yapay Zeka / İskelet Takibi:** MediaPipe
* **Arayüz (GUI):** Tkinter
* **Görüntü Manipülasyonu:** NumPy & Pillow (PIL)

## 💻 Kurulum ve Çalıştırma Rehberi

Projeyi bilgisayarınızda sorunsuz çalıştırmak için **sanal ortam (virtual environment)** kullanılması önerilir. Bu yöntem, bilgisayarınızdaki diğer projelerle çakışma yaşanmasını engeller.

!!! Proje Python 3.11.9 sürümü ile geliştirilmiştir. 

Lütfen işletim sisteminize uygun adımları takip edin:

### 1. Projeyi Bilgisayarınıza İndirin (Klonlayın)
Terminali (veya Komut İstemi'ni) açın ve şu komutları girin:
```bash
git clone [https://github.com/furkannsolmazzx01-design/BLUAI.git](https://github.com/furkannsolmazzx01-design/BLUAI.git)
cd BLUAI


###  Sanal Ortam (Virtual Environment) Oluşturun
** Windows Kullanıcıları İçin: **

python -m venv .venv
.venv\Scripts\activate

** Mac/Linux Kullanıcıları için: **

python3 -m venv .venv
source .venv/bin/activate

!!!NOT: Komutu yazdıktan sonra terminal satırının başında (.venv) ibaresini görmelisiniz. Bu, sanal ortamın aktif olduğunu gösterir.

###  Gerekli Kütüphaneleri Yükleyin
Sanal ortam aktifken, proje için gerekli olan tüm paketleri (OpenCV, MediaPipe vb.) tek komutla yükleyin:

pip install -r requirements.txt

###  Uygulamayı Başlatın
Kurulum tamamlandı! Şimdi asistanı çalıştırabilirsiniz:

python BLUAI.py
```  

### 2. 📝 Kullanım İpuçları
Uygulama açıldığında karşınıza **Görev Seçim Ekranı** gelecektir:

1. **Görev Seçin:** El Yıkama veya Masa Kurma.
2. **Seviye Belirleyin:**
    * **Video Yardımı:** Ekranda model olan bir video oynatılır.
    * **Ses Yardımı:** Sadece sesli ve görsel piktogram desteği verilir.
    * **Bağımsız Seviye:** İpucu en aza indirilir, çocuğun görevleri bağımsız olarak tamamlaması beklenir.
3. **Çıkış:** Uygulamadan çıkmak için görev ekranında bulunan sol üstteki kırmızı butona basıp, ya da görev seçme ekranındaki kırmızı butona basıp uygulamadan çıkış yapabilirsiniz.

---
*Bu proje Ankara Üniversitesi, Eğitim Bilimleri Fakültesi, Bilgisayar ve Öğretim Teknolojileri Eğitimi Bölümü (BÖTE) öğrencisi tarafından geliştirilmiştir.*

## Lisans ve Telif Hakkı 

Bu proje, Ankara Üniversitesi BOZ213 - Nesne Tabanlı Programlama dersi kapsamında geliştirilmiştir. 

Kaynak kodlar yalnızca eğitim ve inceleme amacıyla kullanılabilir. İzinsiz ticari kullanım, kopyalama ve dağıtım yasaktır. 

**© 2026 Furkan Solmaz. Tüm hakları saklıdır.**
