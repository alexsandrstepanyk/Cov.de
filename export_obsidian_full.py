#!/usr/bin/env python3
"""
Export Laws to Obsidian (FULL TEXT)
Експорт ПОВНОГО тексту німецьких законів в Obsidian

Бере текст з вихідних файлів german_laws_complete/
"""

import re
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger('obsidian_full_export')

# Конфігурація
OUTPUT_DIR = Path('obsidian_laws_full')
LAWS_DIR = Path('data/german_laws_complete')

# Мапа кодексів
CODES_UA = {
    'BGB': 'Цивільний кодекс Німеччини',
    'SGB_2': 'Соціальний кодекс II (Jobcenter)',
    'SGB_3': 'Соціальний кодекс III (Агентство з праці)',
    'SGB_5': 'Соціальний кодекс V (Здоров\'я)',
    'AO': 'Податковий кодекс',
    'ZPO': 'Цивільний процесуальний кодекс',
    'StGB': 'Кримінальний кодекс',
    'HGB': 'Торговельний кодекс',
}

def extract_law_name(file_path: Path) -> str:
    """Витягнути назву закону з шляху."""
    if file_path.stem.lower() == 'index':
        return file_path.parent.name.upper()
    return file_path.stem.upper()

def parse_law_file(file_path: Path) -> dict:
    """
    Розпарсити файл закону і витягнути всі параграфи з текстом.
    
    Returns:
        dict: {paragraph_name: paragraph_text}
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        paragraphs = {}
        
        # Патерн для пошуку параграфів з текстом
        # Шукаємо: ### § XX або ##### § XX ... текст ...
        pattern = r'#{3,6}\s*§\s*(\d+[a-z]?)\s*\n(.*?)(?=\n\s*#{3,6}\s*§|\Z)'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for para_num, text in matches:
            para_name = f'§ {para_num}'
            # Очищаємо текст
            text = text.strip()
            text = re.sub(r'\n\s*\n', '\n', text)
            
            if text and len(text) > 10:  # Пропускаємо пусті
                paragraphs[para_name] = text
        
        return paragraphs
        
    except Exception as e:
        logger.warning(f"⚠️ Помилка {file_path}: {e}")
        return {}

def create_obsidian_file(law_name: str, paragraphs: dict) -> str:
    """Створити Markdown файл для Obsidian з повним текстом."""
    
    ua_name = CODES_UA.get(law_name, f'Закон: {law_name}')
    
    # Теги
    tags = ['#німецьке_право', '#закони']
    if 'SGB' in law_name:
        tags.append('#соціальне_право')
    if 'BGB' in law_name:
        tags.append('#цивільне_право')
    
    content = []
    
    # Frontmatter
    content.append('---')
    content.append(f'title: "{law_name}"')
    content.append(f'ua_name: "{ua_name}"')
    content.append(f'paragraphs_count: {len(paragraphs)}')
    content.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    content.append(f'tags: {" ".join(tags)}')
    content.append('---')
    content.append('')
    
    # Заголовок
    content.append(f'# {law_name}')
    content.append('')
    content.append(f'**{ua_name}**')
    content.append('')
    content.append('---')
    content.append('')
    
    # Статистика
    content.append('## 📊 Статистика')
    content.append('')
    content.append(f'- **Всього параграфів:** {len(paragraphs)}')
    if paragraphs:
        first = list(paragraphs.keys())[0]
        last = list(paragraphs.keys())[-1]
        content.append(f'- **Перший параграф:** {first}')
        content.append(f'- **Останній параграф:** {last}')
    content.append('')
    content.append('---')
    content.append('')
    
    # Параграфи з текстом
    content.append('## 📑 Текст законів')
    content.append('')
    
    # Сортуємо параграфи
    def sort_key(para):
        match = re.search(r'§\s*(\d+)', para)
        return int(match.group(1)) if match else 0
    
    sorted_paras = sorted(paragraphs.keys(), key=sort_key)
    
    # Групуємо по десятках
    groups = {}
    for para in sorted_paras:
        match = re.search(r'§\s*(\d+)', para)
        if match:
            num = int(match.group(1))
            decade = (num // 10) * 10
            if decade not in groups:
                groups[decade] = []
            groups[decade].append(para)
    
    # Виводимо групи
    for decade in sorted(groups.keys()):
        content.append(f'### Параграфи {decade}-{decade+9}')
        content.append('')
        
        for para in groups[decade]:
            text = paragraphs[para]
            content.append(f'#### {para}')
            content.append('')
            content.append(text)
            content.append('')
    
    # Посилання
    content.append('---')
    content.append('')
    content.append('## 🔗 Посилання')
    content.append('')
    content.append('- [[німецьке_право]]')
    content.append('- [[закони_Німеччини]]')
    if 'SGB' in law_name:
        content.append('- [[соціальне_право]]')
        content.append('- [[Jobcenter]]')
    
    content.append('')
    content.append('---')
    content.append('')
    content.append(f'*Експортовано: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    
    return '\n'.join(content)

def export_full_laws():
    """Експорт повних текстів законів."""
    logger.info("="*70)
    logger.info("  📚 ЕКСПОРТ ПОВНИХ ТЕКСТІВ ЗАКОНІВ")
    logger.info("="*70)
    
    # Знаходимо всі .md файли
    logger.info("\n🔍 Пошук законів...")
    md_files = list(LAWS_DIR.rglob('*.md'))
    md_files = [f for f in md_files if f.name.lower() not in ['readme.md', 'license.md']]
    
    logger.info(f"   Знайдено: {len(md_files):,} файлів")
    
    # Створюємо директорію
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Експортуємо
    logger.info(f"\n📝 Експорт в {OUTPUT_DIR}/...")
    
    exported = 0
    total_paragraphs = 0
    
    for i, file_path in enumerate(md_files):
        try:
            law_name = extract_law_name(file_path)
            
            if len(law_name) < 2:
                continue
            
            # Парсимо файл
            paragraphs = parse_law_file(file_path)
            
            if not paragraphs:
                continue
            
            # Створюємо файл
            content = create_obsidian_file(law_name, paragraphs)
            
            filename = f"{law_name}.md"
            file_path_out = OUTPUT_DIR / filename
            
            with open(file_path_out, 'w', encoding='utf-8') as f:
                f.write(content)
            
            exported += 1
            total_paragraphs += len(paragraphs)
            
            if (i + 1) % 500 == 0:
                logger.info(f"   Експортовано: {i + 1}/{len(md_files)} | Параграфів: {total_paragraphs:,}")
                
        except Exception as e:
            logger.warning(f"⚠️ Помилка {file_path}: {e}")
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    logger.info(f"   Експортовано законів: {exported:,}")
    logger.info(f"   Всього параграфів з текстом: {total_paragraphs:,}")
    logger.info(f"   Директорія: {OUTPUT_DIR.absolute()}")
    
    # Топ 10
    logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ:")
    
    # Рахуємо параграфи по файлах
    law_counts = {}
    for file_path in OUTPUT_DIR.glob('*.md'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            count = content.count('#### §')
            if count > 0:
                law_counts[file_path.stem] = count
    
    sorted_laws = sorted(law_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (law, count) in enumerate(sorted_laws, 1):
        ua_name = CODES_UA.get(law, law)
        logger.info(f"   {i}. {law} ({ua_name}): {count:,} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ЕКСПОРТ ЗАВЕРШЕНО!")
    logger.info("="*70)
    logger.info(f"\n📁 Відкрийте {OUTPUT_DIR}/ в Obsidian")
    logger.info("")

if __name__ == '__main__':
    export_full_laws()
