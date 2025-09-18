# Streamlit Cloud Deployment Instructions

## 🚀 Deployment Adımları

### 1. Repository Setup
- Bu projeyi GitHub'a push edin
- Streamlit Cloud'da yeni app oluşturun

### 2. Environment Variables
Streamlit Cloud'da aşağıdaki environment variable'ları ekleyin:

```
DATABASE_URL=postgresql://your_postgres_connection_string
OPENING_CASH=0
```

### 3. Database Table Creation
İlk deploy'dan sonra, Streamlit Cloud terminalinde şu komutu çalıştırın:

```bash
python create_tables.py
```

Bu komut:
- ✅ `daily_note` tablosunu oluşturur
- ✅ Tüm tabloları kontrol eder
- ✅ Test verileri ekler

### 4. Verification
Tablolar oluşturulduktan sonra uygulamayı yeniden başlatın ve "Notlar" sayfasını test edin.

## 🔧 Troubleshooting

### "relation daily_note does not exist" Hatası
Bu hatayı alırsanız:

1. Streamlit Cloud terminalinde:
   ```bash
   python create_tables.py
   ```

2. App'i yeniden başlatın

### PostgreSQL Connection Issues
- DATABASE_URL environment variable'ının doğru olduğundan emin olun
- Railway/Supabase/Neon.tech connection string formatını kontrol edin

### Manual SQL (Son Çare)
Eğer script çalışmazsa, PostgreSQL admin panelinde manuel çalıştırın:

```sql
CREATE TABLE IF NOT EXISTS daily_note (
    id SERIAL PRIMARY KEY,
    date_ DATE NOT NULL UNIQUE,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_daily_note_date ON daily_note(date_);
```

## 📁 Dosya Yapısı
```
nehirseramik/
├── app.py              # Ana Streamlit uygulaması
├── create_tables.py    # Tablo oluşturma scripti  
├── requirements.txt    # Python dependencies
└── README.md          # Bu dosya
```

## 🎯 Production Checklist
- [ ] GitHub repository oluşturuldu
- [ ] Streamlit Cloud'da app oluşturuldu
- [ ] DATABASE_URL environment variable eklendi
- [ ] `python create_tables.py` çalıştırıldı
- [ ] App test edildi
- [ ] Notlar sayfası çalışıyor

## 🏺 Nehir Seramik
Ultra-Modern Atölye Yönetim Sistemi