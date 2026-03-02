import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_data_v30.json"

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

# --- 2. TASARIM ---
st.set_page_config(page_title="Eğitim Koçu Nida GÖMCELİ", layout="wide")
st.markdown("<style>.stApp { background-color: #05070a; color: white; }</style>", unsafe_allow_html=True)

# --- 3. GİRİŞ VE ŞİFRE BELİRLEME ---
if "logged_in" not in st.session_state:
    st.title("🎓 Eğitim Koçu Nida GÖMCELİ")
    tab_giris, tab_sifre = st.tabs(["🔐 Giriş Yap", "🆕 İlk Şifremi Oluştur"])
    
    with tab_giris:
        u = st.text_input("Ad Soyad", key="login_user")
        p = st.text_input("Şifre", type="password", key="login_pass")
        if st.button("Sisteme Giriş"):
            if u == "admin" and p == "nida2024":
                st.session_state.update({"logged_in": True, "role": "admin"})
                st.rerun()
            elif u in st.session_state.db["ogrenciler"] and st.session_state.db["ogrenciler"][u].get("sifre") == p:
                st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u})
                st.rerun()
            else: st.error("Kullanıcı adı veya şifre hatalı!")

    with tab_sifre:
        st.info("Sistemde kayıtlıysanız buradan ilk şifrenizi belirleyebilirsiniz.")
        nu = st.text_input("Sistemdeki Tam Adınız", key="new_user")
        np = st.text_input("Yeni Şifreniz", type="password", key="new_pass")
        if st.button("Şifremi Kaydet"):
            if nu in st.session_state.db["ogrenciler"]:
                st.session_state.db["ogrenciler"][nu]["sifre"] = np
                veri_kaydet(st.session_state.db)
                st.success("Şifreniz oluşturuldu! Giriş yap sekmesine dönebilirsiniz.")
            else: st.error("Adınız sistemde bulunamadı.")

else:
    # --- 4. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Rapor & WhatsApp", "Analiz"])
        if st.sidebar.button("Çıkış Yap"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Tanımla"):
                ad = st.text_input("Öğrenci Ad Soyad")
                t = st.text_input("Veli Telefon (905...)")
                h = st.number_input("Haftalık Soru Hedefi", 100)
                if st.button("Sisteme Ekle"):
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "hedef": h, "tel": t, "sifre": None}
                    veri_kaydet(st.session_state.db); st.success(f"{ad} eklendi.")
        
        elif menu == "Rapor & WhatsApp":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db["ogrenciler"].keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            bugun_df = df[df["Tarih"] == bugun] if not df.empty else pd.DataFrame()
            g_toplam = bugun_df["Toplam"].sum() if not bugun_df.empty else 0
            
            msg = f"Sayın Velimiz, {sec} bugünkü çalışmasında {g_toplam} soruya ulaştı. İyi çalışmalar dileriz."
            url = f"https://wa.me/{o.get('tel','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" style="background-color:#25D366; color:white; padding:10px; text-decoration:none; border-radius:5px;">📱 Veliye Gönder</a>', unsafe_allow_html=True)

    # --- 5. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        st.title(f"Hoş Geldin, {u}")
        tab1, tab2 = st.tabs(["📝 Veri Girişi", "📈 Gelişimim & Rapor Gönder"])
        
        with tab1:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Video İzleme", "Konu Tekrarı", "Özel Ders"])
            ders = st.selectbox("Ders", ["Matematik", "Fen", "Türkçe", "Sosyal", "İngilizce", "Din"])
            if tur == "Soru Çözümü":
                d = st.number_input("Doğru", 0); y = st.number_input("Yanlış", 0)
                if st.button("Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Tür": tur, "Toplam": d+y, "Detay": f"{d}D {y}Y"})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")
            else:
                if st.button("Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Tür": tur, "Toplam": 0, "Detay": tur})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tab2:
            df_g = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            gunluk_toplam = df_g[df_g["Tarih"] == bugun]["Toplam"].sum() if not df_g.empty else 0
            
            st.metric("Bugünkü Toplam Sorun", f"{gunluk_toplam} Soru")
            
            # --- ÖĞRENCİ İÇİN WHATSAPP BUTONU ---
            st.write("### 🚀 Günlük Raporunu Hocana Gönder")
            rapor_mesaji = f"Hocam Merhaba, Ben {u}. Bugün toplam {gunluk_toplam} soru çözdüm. Çalışmamı tamamladım! ✨"
            hoca_tel = "90505XXXXXXX" # BURAYA KENDİ NUMARANI YAZABİLİRSİN HOCAM
            wa_url = f"https://wa.me/{hoca_tel}?text={urllib.parse.quote(rapor_mesaji)}"
            
            st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color:#007bff; color:white; padding:12px; text-decoration:none; border-radius:8px; font-weight:bold;">📤 Hocama Rapor Gönder</a>', unsafe_allow_html=True)
            
            if not df_g.empty:
                st.plotly_chart(px.pie(df_g, values='Toplam', names='Ders', title="Ders Dağılımın"))
