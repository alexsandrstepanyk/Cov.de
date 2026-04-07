#!/usr/bin/env python3
"""
Export Main Laws for Ukrainians
Експорт тільки ОСНОВНИХ законів для українців (SGB_2, BGB, і т.д.)
"""

import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('main_laws_export')

OUTPUT_DIR = Path('obsidian_ukraine_laws')
LAWS_DIR = Path('data/german_laws_complete')

# Основні закони для українців
MAIN_LAWS = {
    'SGB_2': 'Соціальний кодекс II (Jobcenter) - допомога по безробіттю',
    'SGB_3': 'Соціальний кодекс III (Агентство з праці) - працевлаштування',
    'SGB_5': 'Соціальний кодекс V (Здоров\'я) - медична страховка',
    'SGB_8': 'Соціальний кодекс VIII (Діти та молодь) - Kindergeld',
    'SGB_12': 'Соціальний кодекс XII - соціальна допомога',
    'BGB': 'Цивільний кодекс - оренда, договори, права',
    'AO': 'Податковий кодекс',
    'ZPO': 'Цивільний процесуальний кодекс - суди',
    'GG': 'Основний закон (Конституція)',
    'AUFENTH': 'Закон про перебування (AufenthG) - візи, посвідки',
}

def find_law_file(law_name: str) -> Path:
    """Знайти файл закону."""
    # Шукаємо в різних варіантах
    variants = [
        LAWS_DIR / law_name[0].lower() / law_name.lower() / 'index.md',
        LAWS_DIR / law_name[0].lower() / f'{law_name.lower()}_2024' / 'index.md',
    ]
    
    for variant in variants:
        if variant.exists():
            return variant
    
    # Шукаємо рекурсивно
    for file_path in LAWS_DIR.rglob('*.md'):
        if file_path.name.lower() == 'index.md':
            dir_name = file_path.parent.name.lower()
            if law_name.lower() in dir_name or dir_name in law_name.lower():
                return file_path
    
    return None

def extract_paragraphs(file_path: Path) -> dict:
    """Витягнути параграфи з текстом."""
    if not file_path or not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    paragraphs = {}
    
    # Патерн для ### § X ...
    pattern = r'^###\s*§\s*(\d+[a-z]?)\s*(.*?)\n(.*?)(?=^###\s*§|\Z)'
    
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    
    for para_num, title, text in matches:
        para_name = f'§ {para_num}'
        full_text = f"{title}\n{text}".strip()
        full_text = re.sub(r'\n\s*\n', '\n', full_text)
        
        if full_text and len(full_text) > 20 and para_name not in paragraphs:
            paragraphs[para_name] = full_text
    
    return paragraphs

def create_file(law_name: str, ua_desc: str, paragraphs: dict) -> str:
    """Створити файл з текстом."""
    content = []
    
    content.append('---')
    content.append(f'title: "{law_name}"')
    content.append(f'ua_name: "{ua_desc}"')
    content.append(f'paragraphs_count: {len(paragraphs)}')
    content.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    content.append(f'tags: #німецьке_право #закони #{law_name.lower()}')
    content.append('---')
    content.append('')
    content.append(f'# {law_name}')
    content.append('')
    content.append(f'**{ua_desc}**')
    content.append('')
    content.append('---')
    content.append('')
    
    if paragraphs:
        sorted_paras = sorted(paragraphs.keys(), 
                             key=lambda x: int(re.search(r'§\s*(\d+)', x).group(1) or 0))
        
        for para in sorted_paras:
            text = paragraphs[para]
            content.append(f'## {para}')
            content.append('')
            content.append(text)
            content.append('')
    
    content.append('---')
    content.append('')
    content.append(f'*Експортовано: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    
    return '\n'.join(content)

def main():
    logger.info("="*70)
    logger.info("  🇺🇦 ЕКСПОРТ ОСНОВНИХ ЗАКОНІВ ДЛЯ УКРАЇНЦІВ")
    logger.info("="*70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for law_name, ua_desc in MAIN_LAWS.items():
        logger.info(f"\n📖 {law_name} - {ua_desc}")
        
        file_path = find_law_file(law_name)
        
        if not file_path:
            logger.warning(f"   ❌ Файл не знайдено")
            continue
        
        logger.info(f"   Файл: {file_path}")
        
        paragraphs = extract_paragraphs(file_path)
        logger.info(f"   Параграфів: {len(paragraphs)}")
        
        if not paragraphs:
            logger.warning(f"   ❌ Параграфи не знайдено")
            continue
        
        # Створюємо файл
        content = create_file(law_name, ua_desc, paragraphs)
        
        filename = f"{law_name}.md"
        with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"   ✅ Експортовано")
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    
    exported = len(list(OUTPUT_DIR.glob('*.md')))
    logger.info(f"   Експортовано законів: {exported}")
    logger.info(f"   Директорія: {OUTPUT_DIR.absolute()}")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ГОТОВО!")
    logger.info("="*70)
    logger.info(f"\n📁 Відкрийте {OUTPUT_DIR}/ в Obsidian")
    logger.info("")

if __name__ == '__main__':
    main()
