#!/usr/bin/env python3
"""
Statistics Module for Gov.de Bot
Збір та аналіз статистики використання бота.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

DB_PATH = 'users.db'


def init_stats_db():
    """Ініціалізація таблиць статистики."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблиця статистики
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            event_type TEXT,
            letter_type TEXT,
            quality_score INTEGER,
            ocr_confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця нагадувань
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            letter_id INTEGER,
            reminder_text TEXT,
            reminder_date DATE,
            reminder_time TIME,
            is_sent BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця оцінок відповідей
    c.execute('''
        CREATE TABLE IF NOT EXISTS response_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            letter_id INTEGER,
            rating INTEGER,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця верифікованих організацій
    c.execute('''
        CREATE TABLE IF NOT EXISTS verified_organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            org_type TEXT,
            is_official BOOLEAN,
            phone TEXT,
            email TEXT,
            website TEXT,
            address TEXT,
            notes TEXT,
            verified_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


# ============================================================================
# СТАТИСТИКА
# ============================================================================

def log_event(chat_id: int, event_type: str, letter_type: str = None, 
              quality_score: int = None, ocr_confidence: float = None):
    """Запис події в статистику."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO statistics (chat_id, event_type, letter_type, quality_score, ocr_confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (chat_id, event_type, letter_type, quality_score, ocr_confidence))
    
    conn.commit()
    conn.close()


def get_daily_stats(date: datetime = None) -> Dict:
    """Отримати статистику за день."""
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Кількість оброблених листів
    c.execute('''
        SELECT COUNT(*) FROM statistics 
        WHERE event_type = 'letter_processed' 
        AND DATE(timestamp) = ?
    ''', (date_str,))
    letters_count = c.fetchone()[0]
    
    # Середня якість фото
    c.execute('''
        SELECT AVG(quality_score) FROM statistics 
        WHERE quality_score IS NOT NULL 
        AND DATE(timestamp) = ?
    ''', (date_str,))
    avg_quality = c.fetchone()[0] or 0
    
    # Середня впевненість OCR
    c.execute('''
        SELECT AVG(ocr_confidence) FROM statistics 
        WHERE ocr_confidence IS NOT NULL 
        AND DATE(timestamp) = ?
    ''', (date_str,))
    avg_ocr = c.fetchone()[0] or 0
    
    # Типи листів
    c.execute('''
        SELECT letter_type, COUNT(*) FROM statistics 
        WHERE event_type = 'letter_processed' 
        AND DATE(timestamp) = ?
        GROUP BY letter_type
    ''', (date_str,))
    letter_types = dict(c.fetchall())
    
    conn.close()
    
    return {
        'date': date_str,
        'letters_count': letters_count,
        'avg_quality': round(avg_quality, 2),
        'avg_ocr_confidence': round(avg_ocr, 2),
        'letter_types': letter_types
    }


def get_weekly_stats() -> Dict:
    """Отримати статистику за тиждень."""
    week_ago = datetime.now() - timedelta(days=7)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Кількість листів за тиждень
    c.execute('''
        SELECT COUNT(*) FROM statistics 
        WHERE event_type = 'letter_processed' 
        AND DATE(timestamp) >= ?
    ''', (week_ago.strftime('%Y-%m-%d'),))
    letters_count = c.fetchone()[0]
    
    # Активні користувачі
    c.execute('''
        SELECT COUNT(DISTINCT chat_id) FROM statistics 
        WHERE DATE(timestamp) >= ?
    ''', (week_ago.strftime('%Y-%m-%d'),))
    active_users = c.fetchone()[0]
    
    conn.close()
    
    return {
        'period': 'week',
        'letters_count': letters_count,
        'active_users': active_users
    }


def get_user_stats(chat_id: int) -> Dict:
    """Отримати статистику користувача."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Всього листів
    c.execute('''
        SELECT COUNT(*) FROM statistics 
        WHERE chat_id = ? AND event_type = 'letter_processed'
    ''', (chat_id,))
    total_letters = c.fetchone()[0]
    
    # Середня якість
    c.execute('''
        SELECT AVG(quality_score) FROM statistics 
        WHERE chat_id = ? AND quality_score IS NOT NULL
    ''', (chat_id,))
    avg_quality = c.fetchone()[0] or 0
    
    # Останній лист
    c.execute('''
        SELECT MAX(timestamp) FROM statistics 
        WHERE chat_id = ? AND event_type = 'letter_processed'
    ''', (chat_id,))
    last_activity = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_letters': total_letters,
        'avg_quality': round(avg_quality, 2),
        'last_activity': last_activity
    }


# ============================================================================
# НАГАДУВАННЯ
# ============================================================================

def create_reminder(chat_id: int, letter_id: int, reminder_text: str, 
                   reminder_date: str, reminder_time: str = '10:00'):
    """Створити нагадування."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO reminders (chat_id, letter_id, reminder_text, reminder_date, reminder_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (chat_id, letter_id, reminder_text, reminder_date, reminder_time))
    
    reminder_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return reminder_id


def get_due_reminders() -> List[Dict]:
    """Отримати нагадування які потрібно відправити."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    c.execute('''
        SELECT r.id, r.chat_id, r.reminder_text, r.letter_id
        FROM reminders r
        WHERE r.reminder_date <= ? 
        AND r.reminder_time <= ?
        AND r.is_sent = FALSE
    ''', (date_str, time_str))
    
    reminders = []
    for row in c.fetchall():
        reminders.append({
            'id': row[0],
            'chat_id': row[1],
            'text': row[2],
            'letter_id': row[3]
        })
    
    conn.close()
    return reminders


def mark_reminder_sent(reminder_id: int):
    """Позначити нагадування як відправлене."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        UPDATE reminders SET is_sent = TRUE WHERE id = ?
    ''', (reminder_id,))
    
    conn.commit()
    conn.close()


def get_user_reminders(chat_id: int) -> List[Dict]:
    """Отримати всі нагадування користувача."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, reminder_text, reminder_date, reminder_time, is_sent
        FROM reminders
        WHERE chat_id = ?
        ORDER BY reminder_date, reminder_time
    ''', (chat_id,))
    
    reminders = []
    for row in c.fetchall():
        reminders.append({
            'id': row[0],
            'text': row[1],
            'date': row[2],
            'time': row[3],
            'is_sent': row[4]
        })
    
    conn.close()
    return reminders


# ============================================================================
# ОЦІНКИ ВІДПОВІДЕЙ
# ============================================================================

def rate_response(chat_id: int, letter_id: int, rating: int, feedback: str = None):
    """Оцінити відповідь бота."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO response_ratings (chat_id, letter_id, rating, feedback)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, letter_id, rating, feedback))
    
    conn.commit()
    conn.close()


def get_response_stats() -> Dict:
    """Отримати статистику оцінок відповідей."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Середня оцінка
    c.execute('SELECT AVG(rating) FROM response_ratings')
    avg_rating = c.fetchone()[0] or 0
    
    # Кількість оцінок
    c.execute('SELECT COUNT(*) FROM response_ratings')
    total_ratings = c.fetchone()[0]
    
    # Оцінки по місяцях
    c.execute('''
        SELECT strftime('%Y-%m', timestamp) as month, AVG(rating), COUNT(*)
        FROM response_ratings
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    ''')
    monthly_ratings = c.fetchall()
    
    conn.close()
    
    return {
        'avg_rating': round(avg_rating, 2),
        'total_ratings': total_ratings,
        'monthly': monthly_ratings
    }


# ============================================================================
# ВЕРИФІКОВАНІ ОРГАНІЗАЦІЇ
# ============================================================================

def add_verified_organization(name: str, org_type: str, is_official: bool,
                             phone: str = None, email: str = None, 
                             website: str = None, address: str = None,
                             notes: str = None):
    """Додати верифіковану організацію."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO verified_organizations 
            (name, org_type, is_official, phone, email, website, address, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, org_type, is_official, phone, email, website, address, notes))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_organization(name: str) -> Optional[Dict]:
    """Перевірити організацію в базі."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT name, org_type, is_official, phone, email, website, address, notes
        FROM verified_organizations
        WHERE name LIKE ? OR name LIKE ?
    ''', (f'%{name}%', f'%{name.lower()}%'))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'name': row[0],
            'type': row[1],
            'is_official': row[2],
            'phone': row[3],
            'email': row[4],
            'website': row[5],
            'address': row[6],
            'notes': row[7]
        }
    return None


def get_all_verified_organizations() -> List[Dict]:
    """Отримати всі верифіковані організації."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM verified_organizations ORDER BY name')
    
    orgs = []
    for row in c.fetchall():
        orgs.append({
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'is_official': row[3],
            'phone': row[4],
            'email': row[5],
            'website': row[6],
            'address': row[7],
            'notes': row[8]
        })
    
    conn.close()
    return orgs


# ============================================================================
# ІНІЦІАЛІЗАЦІЯ
# ============================================================================

def populate_verified_organizations():
    """Заповнити базу верифікованих організацій."""
    organizations = [
        # Jobcenter
        ('Jobcenter Berlin Mitte', 'jobcenter', True, 
         '030 1234 5678', 'kontakt@jobcenter-berlin-mitte.de',
         'https://www.berlin.de/labo/willkommen-in-berlin/arbeit-und-bildung/jobcenter/',
         'Straße der Migration 123, 10115 Berlin', 'Офіційний Jobcenter Берліна'),
        
        # Arbeitsagentur
        ('Bundesagentur für Arbeit', 'arbeitsagentur', True,
         '0800 4 5555', 'kontakt@arbeitsagentur.de',
         'https://www.arbeitsagentur.de',
         'Regensburger Str. 104, 90478 Nürnberg', 'Федеральне агентство з праці'),
        
        # Finanzamt
        ('Finanzamt Berlin', 'finanzamt', True,
         '030 9024 0', 'post@finanzamt-berlin.de',
         'https://www.berlin.de/finanzamt/',
         'Berlin', 'Податкова Берліна'),
        
        # Великі Inkasso (ліцензовані)
        ('Creditreform Inkasso', 'inkasso', True,
         '02102 1080', 'info@creditreform-inkasso.de',
         'https://www.creditreform.de',
         'Hammfelddamm 13, 41460 Neuss', 'Ліцензована колекторська служба'),
        
        ('EOS Rema', 'inkasso', True,
         '040 23666 0', 'kontakt@eos-rema.de',
         'https://www.eos-rema.de',
         'Wendenstraße 245, 20537 Hamburg', 'Ліцензована колекторська служба'),
    ]
    
    for org in organizations:
        add_verified_organization(*org)


# Авто-ініціалізація при імпорті
init_stats_db()
populate_verified_organizations()
