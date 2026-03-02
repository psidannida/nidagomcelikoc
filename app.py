import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_data_v29.json"

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

# --- 3. GİRİŞ & ŞİFRE BELİRLEME ---
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
        np2 = st.text_input("Şifre Tekrar", type="password", key="new_pass_confirm")
        if st.button("Şifremi Kaydet"):
            if nu in st.session_state.db["ogrenciler"]:
                if np == np2 and len(np) >= 4:
                    st.session_state.db["ogrenciler"][nu]["sifre"] = np
                    veri_kaydet(st.session_state.db)
                    st.success("Şifreniz oluşturuldu! Giriş yap sekmesine dönebilirsiniz.")
                else: st.warning("Şifreler eşleşmiyor veya çok kısa!")
            else: st.error("Adınız sistemde bulunamadı. Lütfen Nida Hocanıza danışın.")

else:
    # --- 4. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Rapor & WhatsApp", "Genel Analiz"])
        if st.sidebar.button("Çıkış Yap"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Tanımla"):
                ad = st.text_input("Öğrenci Ad Soyad")
                g = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                t = st.text_input("Veli Tel (Örn: 905xxxxxxxxx)")
                h = st.number_input("Haftalık Soru Hedefi", 100)
                if st.button("Sisteme Ekle"):
                    if ad:
                        st.session_state.db["ogrenciler"][ad] = {"soru": [], "sinav": g, "hedef": h, "tel": t, "sifre": None}
                        veri_kaydet(st.session_state.db)
                        st.success(f"{ad} başarıyla eklendi. Öğrenci artık şifre belirleyebilir.")
        
        elif menu == "Rapor & WhatsApp":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db["ogrenciler"].keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            bugun_df = df[df["Tarih"] == bugun] if not df.empty else pd.DataFrame()
            
            g_toplam = bugun_df["Toplam"].sum() if not bugun_df.empty else 0
            video = len(bugun_df[bugun_df["Tür"] == "Video İzleme"])
            ders_ozeti = ""
            if not bugun_df.empty:
                ozet = bugun_df.groupby("Ders")["Toplam"].sum()
                for d, s in ozet.items():
                    if s > 0: ders_ozeti += f"\n- {d}: {s} Soru"

            msg = f"Sayın Velimiz, {sec} bugünkü çalışmasını tamamladı:\n✅ Toplam Soru: {g_toplam}\n📺 Video: {video}\n{ders_ozeti}\n\nEğitim Koçu Nida GÖMCELİ"
            url = f"https://wa.me/{o.get('tel','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" style="background-color:#25D366; color:white; padding:12px; text-decoration:none; border-radius:5px; font-weight:bold;">📱 Veliye WhatsApp Gönder</a>', unsafe_allow_html=True)
            st.dataframe(bugun_df, use_container_width=True)

    # --- 5. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        st.title(f"Hoş Geldin, {u}")
        tab1, tab2 = st.tabs(["📝 Çalışma Girişi", "📊 Gelişim Grafiğim"])
        
        with tab1:
            tur = st.selectbox("Çalışma Türü", ["Soru Çözümü", "Video İzleme", "Konu Tekrarı", "Özel Ders"])
            ders = st.selectbox("Ders", ["Matematik", "Fen Bilimleri", "Türkçe", "Sosyal Bilgiler", "İngilizce", "Din Kültürü"])
            if tur == "Soru Çözümü":
                d = st.number_input("Doğru", 0); y = st.number_input("Yanlış", 0)
                if st.button("Veriyi Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Tür": tur, "Toplam": d+y, "Detay": f"{d}D {y}Y"})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")
            else:
                top = st.number_input("Kaç Saat/Adet?", 1) if tur == "Özel Ders" else 0
                if st.button("Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Tür": tur, "Toplam": top, "Detay": tur})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tab2:
            df_g = pd.DataFrame(o["soru"])
            if not df_g.empty:
                st.plotly_chart(px.pie(df_g, values='Toplam', names='Ders', title="Ders Dağılımın"))
            else: st.info("Henüz grafik için veri yok.")
