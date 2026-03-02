import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px

# --- 1. AYARLAR VE VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_akademi_master_v31.json"
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

# --- 2. MÜFREDAT LİSTELERİ ---
m_lgs = {
    "LGS Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Olasılık", "Cebirsel İfadeler", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik"],
    "LGS Fen": ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri"],
    "LGS Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım-Noktalama"],
    "LGS Sosyal/Din/İng": ["İnkılap Tarihi", "Din Kültürü", "İngilizce"]
}
m_yks = {
    "TYT Matematik": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "Rasyonel Sayılar", "Üslü-Köklü", "Problemler", "Fonksiyonlar", "Geometri"],
    "AYT Matematik": ["Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral", "Analitik Geometri"],
    "TYT Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Dil Bilgisi"],
    "YKS Fen (F-K-B)": ["Fizik", "Kimya", "Biyoloji"],
    "YKS Sosyal/Ed": ["Tarih", "Coğrafya", "Edebiyat", "Felsefe", "Din Kültürü"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Eğitim Koçu Nida GÖMCELİ", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1e2130; color: white; border: 1px solid #4f4f4f; }
    .stButton>button:hover { background-color: #2d3250; border: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GİRİŞ SİSTEMİ ---
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
            else: st.error("Hatalı Giriş!")
            
    with t2:
        nu = st.text_input("Sistemdeki Adınız")
        np = st.text_input("Yeni Şifre Belirle", type="password")
        if st.button("Şifreyi Kaydet"):
            if nu in st.session_state.db["ogrenciler"]:
                st.session_state.db["ogrenciler"][nu]["sifre"] = np
                veri_kaydet(st.session_state.db); st.success("Şifre oluşturuldu!")
            else: st.error("İsim bulunamadı.")

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
            bugun_df = df[df["Tarih"] == bugun] if not df.empty else pd.DataFrame()
            g_toplam = bugun_df["Toplam"].sum() if not bugun_df.empty else 0
            
            st.subheader(f"📊 {sec} Raporu")
            c1, c2 = st.columns(2)
            haftalik = df['Toplam'].sum() if not df.empty else 0
            c1.metric("Bugün", f"{g_toplam} Soru")
            c2.metric("Haftalık Hedef", f"{haftalik} / {o['hedef']}")

            if not df.empty:
                st.plotly_chart(px.line(df, x="Tarih", y="Toplam", title="İlerleme Grafiği", markers=True))
            
            ders_ozet = ""
            if not bugun_df.empty:
                ozet_seri = bugun_df.groupby("Ders")["Toplam"].sum()
                for d_adi, s_sayi in ozet_seri.items():
                    if s_sayi > 0: ders_ozet += f"\n- {d_adi}: {s_sayi} Soru"
            
            msg = f"Sayın Velimiz, {sec} bugün toplam {g_toplam} soru çözmüştür.\n{ders_ozet}\n\nEğitim Koçu Nida GÖMCELİ"
            url = f"https://wa.me/{o.get('tel','')}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px; font-weight:bold; display:block; text-align:center;">📱 VELİYE WHATSAPP GÖNDER</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = m_lgs if o["sinav"] == "LGS" else m_yks
        st.title(f"Hoş Geldin, {u}")
        tab1, tab2, tab3 = st.tabs(["📝 Veri Girişi", "🏆 Deneme Kaydı", "📈 Gelişimim"])
        
        with tab1:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Video İzleme", "Konu Tekrarı", "Özel Ders"])
            ders = st.selectbox("Ders", list(m.keys()))
            konu = st.selectbox("Konu", m[ders])
            if tur == "Soru Çözümü":
                d = st.number_input("Doğru", 0); y = st.number_input("Yanlış", 0)
                if st.button("Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Tür": tur, "Toplam": d+y, "Detay": f"{d}D {y}Y"})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")
            else:
                if st.button("Çalışmayı Kaydet"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Tür": tur, "Toplam": 0, "Detay": tur})
                    veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tab2:
            st.subheader("Deneme Neti")
            yayin = st.text_input("Yayın")
            c1, c2 = st.columns(2)
            if o["sinav"] == "LGS":
                tn = c1.number_input("Türkçe Net", 0.0); mn = c2.number_input("Matematik Net", 0.0)
                puan = 200 + (mn*5) + (tn*4)
            else:
                tyt_n = c1.number_input("TYT Net", 0.0); ayt_n = c2.number_input("AYT Net", 0.0)
                puan = 100 + (tyt_n * 1.5) + (ayt_n * 3)
            if st.button("Denemeyi İşle"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Yayin": yayin, "Puan": round(puan, 2)})
                veri_kaydet(st.session_state.db); st.success(f"Puan: {round(puan,2)}")

        with tab3:
            df_o = pd.DataFrame(o["soru"])
            bugun = datetime.now().strftime("%d/%m")
            bugun_s = df_o[df_o["Tarih"] == bugun]["Toplam"].sum() if not df_o.empty else 0
            st.metric("Bugünkü Sorun", f"{bugun_s}")
            if not df_o.empty:
                st.plotly_chart(px.pie(df_o, values='Toplam', names='Ders', title="Ders Dağılımı"))
            rapor_msg = f"Nida Hocam Merhaba, Ben {u}. Bugün {bugun_s} soru çözdüm. Raporum hazır!"
            hoca_url = f"https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(rapor_msg)}"
            st.markdown(f'<a href="{hoca_url}" target="_blank" style="background-color:#007bff; color:white; padding:15px; text-decoration:none; border-radius:10px; font-weight:bold; display:block; text-align:center;">📤 HOCAMA RAPOR GÖNDER</a>', unsafe_allow_html=True)
