#!/usr/bin/env python3
"""
Streamlit Cloud için tablo oluşturma scripti
Bu dosyayı bir kez çalıştırarak daily_note tablosunu manuel oluşturun.
"""

import os
from sqlmodel import SQLModel, create_engine, text, Session
from datetime import date, datetime

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nehir.db")
engine = create_engine(DATABASE_URL, echo=True)

def create_daily_note_table():
    """Manuel olarak daily_note tablosunu oluştur"""
    print("🚀 Daily Note tablosu oluşturuluyor...")
    
    try:
        # PostgreSQL için SQL
        if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
            sql = """
                CREATE TABLE IF NOT EXISTS daily_note (
                    id SERIAL PRIMARY KEY,
                    date_ DATE NOT NULL UNIQUE,
                    note TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                
                -- Index for faster date queries
                CREATE INDEX IF NOT EXISTS idx_daily_note_date ON daily_note(date_);
            """
        else:
            # SQLite için SQL
            sql = """
                CREATE TABLE IF NOT EXISTS daily_note (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_ DATE NOT NULL UNIQUE,
                    note TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Index for faster date queries
                CREATE INDEX IF NOT EXISTS idx_daily_note_date ON daily_note(date_);
            """
        
        with Session(engine) as session:
            # Split SQL commands and execute one by one
            commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip()]
            
            for command in commands:
                print(f"Executing: {command[:50]}...")
                session.exec(text(command))
            
            session.commit()
            print("✅ daily_note tablosu başarıyla oluşturuldu!")
            
            # Test the table
            result = session.exec(text("SELECT COUNT(*) FROM daily_note")).first()
            print(f"📊 Tablo test edildi. Mevcut kayıt sayısı: {result}")
            
            # Insert a test note if table is empty
            if result == 0:
                test_sql = """
                    INSERT INTO daily_note (date_, note, created_at, updated_at) 
                    VALUES (?, ?, ?, ?)
                """
                if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
                    test_sql = """
                        INSERT INTO daily_note (date_, note, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s)
                    """
                
                session.exec(text(test_sql), (
                    date.today(),
                    "🎉 Not sistemi aktif! Bu test notunu silebilirsiniz.",
                    datetime.now(),
                    datetime.now()
                ))
                session.commit()
                print("🎯 Test notu eklendi!")
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return False
    
    return True

def verify_all_tables():
    """Tüm tabloların varlığını kontrol et"""
    print("\n🔍 Tablo kontrolü yapılıyor...")
    
    required_tables = [
        'person', 'course', 'sessionmodel', 'enrollment', 
        'payment', 'expense', 'charge', 'piece', 
        'material', 'stock_movement', 'daily_note'
    ]
    
    try:
        with Session(engine) as session:
            existing_tables = []
            
            for table in required_tables:
                try:
                    # Try to query the table
                    session.exec(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    existing_tables.append(table)
                    print(f"✅ {table}")
                except:
                    print(f"❌ {table} - EKSIK!")
            
            print(f"\n📊 Sonuç: {len(existing_tables)}/{len(required_tables)} tablo mevcut")
            return len(existing_tables) == len(required_tables)
            
    except Exception as e:
        print(f"❌ Tablo kontrolü hatası: {e}")
        return False

if __name__ == "__main__":
    print("🏺 Nehir Seramik - Tablo Oluşturma Scripti")
    print(f"🔗 Database: {DATABASE_URL}")
    print("-" * 50)
    
    # 1. daily_note tablosunu oluştur
    success = create_daily_note_table()
    
    # 2. Tüm tabloları kontrol et
    all_ok = verify_all_tables()
    
    print("-" * 50)
    if success and all_ok:
        print("🎉 TÜM TABLOLAR HAZIR!")
        print("🚀 Artık Streamlit uygulamasını çalıştırabilirsiniz.")
    else:
        print("⚠️  Bazı tablolar eksik olabilir.")
        print("💡 Ana app.py'yi çalıştırarak otomatik oluşturmayı deneyin.")
    
    print("\n📝 Bu scripti Streamlit Cloud'da terminalde çalıştırın:")
    print("   python create_tables.py")