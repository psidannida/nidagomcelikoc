import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. AYARLAR VE NUMARAN ---
VERI_DOSYASI = "nida_final_v32.json"
HOCA_TEL = "905307368072"

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

# --- 2. KONU LİSTELERİ ---
m_lgs = {
    "LGS Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Olasılık", "Cebirsel", "Denklemler", "Üçgenler"],
    "LGS Fen": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji"],
    "LGS Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Anlam", "Yazım-Noktalama"],
    "LGS Sosyal/Din/İng": ["İnkılap Tarihi", "Din Kültürü", "İngilizce"]
}
m_yks = {
    "TYT Matematik": ["Temel Kavramlar", "Problemler", "Fonksiyonlar", "Geometri"],
    "AYT Matematik": ["Trigonometri", "Logaritma", "Diziler", "Limit-Türev-İntegral"],
    "TYT Türkçe": ["Sözcük-Cümle Anlamı", "Paragraf", "Dil Bilgisi"],
    "YKS Fen/Sosyal": ["Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Edebiyat"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Eğitim Koçu Nida GÖMCELİ", layout="wide")
st.markdown("<style>.stApp { background-color: #05070a; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ VE ŞİFRE ---
if "logged_in" not in st.session_state:
    st.title("🎓 Eğitim Koçu Nida GÖMCELİ")
    t1, t2 = st.tabs(["🔐 Giriş Yap", "🆕 İlk Şifremi Belirle"])
    with t1:
        u = st.text_input("Ad Soyad")
        p = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş"):
            if u == "admin" and p == "nida2024":
                st.session_state.update({"logged_in": True, "role": "admin"})
                st.rerun()
            elif u in st.session_state.db["ogrenciler"] and st.session_state.db["ogrenciler"][u].get("sifre") == p:
                st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u})
                st.rerun()
            else: st.error("Bilgiler Hatalı!")
    with t2:
        nu = st.text_input("Sistemdeki Adınız")
        np = st.text_input("Yeni Şifre", type="password")
        if st.button("Şifremi Kaydet"):
            if nu in st.session_state.db["ogrenciler"]:
                st.session_state.db["ogrenciler"][nu]["sifre"] = np
                veri_kaydet(st.session_state.db); st.success("Şifre Tamam! Giriş yapabilirsin.")

else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Gelişim & WhatsApp"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci"):
                ad = st.text_input("Ad Soyad")
                g = st.selectbox("Sınav", ["LGS", "YKS"])
                t = st.text_input("Veli Tel (905...)")
                h = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": g, "hedef": h, "tel": t, "sifre": None}
                    veri_kaydet(st.session_state.db); st.success("Eklendi!")

        elif menu == "Gelişim & WhatsApp":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db["ogrenciler"].keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            g_toplam = df[df["Tarih"] == bugun]["Toplam"].sum() if not df.empty else 0
            
            st.subheader(f"📊 {sec} Raporu")
            st.metric("Bugün Çözülen", f"{g_toplam} Soru")
            if not df.empty:
                st.plotly_chart(px.line(df, x="Tarih", y="Toplam", title="Soru Çözüm Grafiği"))
            
            msg = f"Sayın Velimiz, {sec} bugün toplam {g_toplam} soru çözmüştür. Eğitim Koçu Nida GÖMCELİ"
            url = f"https://wa.me/{o.get('tel','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE WHATSAPP GÖNDER</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = m_lgs if o.get("sinav") == "LGS" else m_yks
        st.title(f"Hoş Geldin, {u}")
        tab1, tab2, tab3 = st.tabs(["📝 Soru Girişi", "🏆 Deneme Kaydı", "📈 Gelişimim"])
        
        with tab1:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Video İzleme", "Konu Tekrarı"])
            ders = st.selectbox("Ders", list(m.keys()))
            konu = st.selectbox("Konu", m[ders])
            d = st.number_input("Doğru", 0); y = st.number_input("Yanlış", 0)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Toplam": d+y, "Net": d-(y/4 if o.get("sinav")=="YKS" else y/3)})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tab2:
            st.subheader("Deneme Neti Gir")
            yay = st.text_input("Yayın")
            c1, c2 = st.columns(2)
            dn = c1.number_input("Doğru", 0); yn = c2.number_input("Yanlış", 0)
            if st.button("Denemeyi İşle"):
                net = dn - (yn/4 if o.get("sinav")=="YKS" else yn/3)
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Yayin": yay, "Net": net})
                veri_kaydet(st.session_state.db); st.success(f"Netin: {net}")

        with tab3:
            df_o = pd.DataFrame(o["soru"])
            if not df_o.empty:
                st.plotly_chart(px.pie(df_o, values='Toplam', names='Ders', title="Ders Dağılımı"))
            bugun_s = df_o[df_o["Tarih"] == datetime.now().strftime("%d/%m")]["Toplam"].sum() if not df_o.empty else 0
            rapor_msg = f"Nida Hocam Merhaba, Ben {u}. Bugün {bugun_s} soru çözdüm!"
            st.markdown(f'<a href="https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(rapor_msg)}" target="_blank" style="background-color:#007bff; color:white; padding:15px; text-decoration:none; border-radius:10px;">📤 HOCAMA RAPOR GÖNDER</a>', unsafe_allow_html=True)
