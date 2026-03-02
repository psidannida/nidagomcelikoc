import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_v21.json"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"ogrenciler": {}}
    return {"ogrenciler": {}}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- 2. EKSİKSİZ MÜFREDAT LİSTESİ ---
m_yks = {
    "TYT Matematik": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "…
[01:38, 03.03.2026] Nida (NURTANIŞ) GÖMCELİ: import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_final_v28.json"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"ogrenciler": {}}
    return {"ogrenciler": {}}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- 2. MÜFREDAT LİSTESİ ---
m_yks = {
    "TYT Matematik": ["Temel Kavramlar", "Sayılar", "Problemler", "Fonksiyonlar", "Olasılık"],
    "TYT Türkçe": ["Paragraf", "Dil Bilgisi", "Yazım-Noktalama"],
    "TYT Felsefe": ["Bilgi Felsefesi", "Varlık Felsefesi", "Ahlak Felsefesi", "Siyaset Felsefesi"],
    "TYT Sosyal": ["Tarih", "Coğrafya", "Din Kültürü"],
    "AYT Matematik": ["Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "AYT Fen": ["Fizik", "Kimya", "Biyoloji"],
    "AYT Edebiyat": ["Şiir Bilgisi", "Edebi Sanatlar", "Dönemler"]
}

m_lgs = {
    "LGS Matematik": ["Çarpanlar", "Üslü", "Kareköklü", "Denklemler", "Üçgenler"],
    "LGS Fen": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler"],
    "LGS Türkçe": ["Fiilimsiler", "Anlam", "Ögeler", "Çatı"],
    "LGS Sosyal/Din/İng": ["İnkılap Tarihi", "Din Kültürü", "İngilizce"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Eğitim Koçu Nida GÖMCELİ", layout="wide")
st.markdown("<style>.stApp { background-color: #05070a; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Eğitim Koçu Nida GÖMCELİ")
    u = st.text_input("Ad Soyad")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Gir"):
        if u == "admin" and p == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif u in st.session_state.db["ogrenciler"] and st.session_state.db["ogrenciler"][u].get("sifre") == p:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u})
            st.rerun()
        else: st.error("Giriş Başarısız!")
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Rapor & WhatsApp", "Grafiksel Analiz"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci"):
                ad = st.text_input("Öğrenci Ad Soyad")
                g = st.selectbox("Sınav", ["LGS", "YKS"])
                t = st.text_input("Veli Telefon (905...)")
                h = st.number_input("Haftalık Soru Hedefi", 100)
                if st.button("Kaydet"):
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "sinav": g, "hedef": h, "tel": t, "sifre": "1234"}
                    veri_kaydet(st.session_state.db); st.success("Eklendi!")

        elif menu == "Rapor & WhatsApp":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db["ogrenciler"].keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            bugun_df = df[df["Tarih"] == bugun] if not df.empty else pd.DataFrame()
            
            # Veri Toplama
            g_toplam = bugun_df["Toplam"].sum() if not bugun_df.empty else 0
            video_sayisi = len(bugun_df[bugun_df["Tür"] == "Video İzleme"])
            ozel_ders_saati = bugun_df[bugun_df["Tür"] == "Özel Ders"]["Toplam"].sum()
            
            ders_detay = ""
            if not bugun_df.empty:
                ozet = bugun_df.groupby("Ders")["Toplam"].sum()
                for d, s in ozet.items():
                    if s > 0: ders_detay += f"\n- {d}: {s} Soru"

            st.write(f"### {sec} - Günlük Rapor")
            st.write(f"Soru: {g_toplam} | Video: {video_sayisi} | Özel Ders: {ozel_ders_saati} Saat")
            
            # Zengin WhatsApp Mesajı
            msg = f"Sayın Velimiz, {sec} bugünkü çalışmasını tamamladı:\n"
            msg += f"✅ Çözülen Soru: {g_toplam}\n"
            msg += f"📺 İzlenen Video: {video_sayisi}\n"
            msg += f"👨‍🏫 Özel Ders: {ozel_ders_saati} Saat\n"
            msg += f"\n📊 Ders Detayları:{ders_detay}\n"
            msg += f"\nEğitim Koçu Nida GÖMCELİ"
            
            url = f"https://wa.me/{o.get('tel','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" style="background-color:#25D366; color:white; padding:12px; text-decoration:none; border-radius:5px; font-weight:bold;">📱 Veliye WhatsApp Raporu Gönder</a>', unsafe_allow_html=True)
            st.table(bugun_df)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = m_lgs if o["sinav"] == "LGS" else m_yks
        st.title(f"Hoş Geldin, {u}")
        
        tab1, tab2 = st.tabs(["📝 Çalışma Girişi", "📊 Gelişim Grafiklerim"])
        with tab1:
            tur = st.selectbox("Ne Çalıştın?", ["Soru Çözümü", "Video İzleme", "Konu Tekrarı", "Özel Ders"])
            ders = st.selectbox("Ders", list(m.keys()))
            konu = st.selectbox("Konu", m[ders])
            
            if tur == "Soru Çözümü":
                d = st.number_input("Doğru", 0); y = st.number_input("Yanlış", 0)
                if st.button("Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Tür": tur, "Toplam": d+y, "Detay": f"{d}D {y}Y"})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")
            elif tur == "Özel Ders":
                saat = st.number_input("Kaç Saat Sürdü?", 1.0)
                if st.button("Özel Dersi Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Tür": tur, "Toplam": saat, "Detay": f"{saat} Saat Ders"})
                    veri_kaydet(st.session_state.db); st.success("Özel ders işlendi!")
            else:
                if st.button("Çalışmayı Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Tür": tur, "Toplam": 0, "Detay": tur})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tab2:
            df = pd.DataFrame(o["soru"])
            if not df.empty:
                fig = px.pie(df, values='Toplam', names='Ders', title="Ders Dağılımın")

                st.plotly_chart(fig
