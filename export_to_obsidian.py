#!/usr/bin/env python3
"""
Export Laws to Obsidian
Експорт німецьких законів в форматі для Obsidian

Створює Markdown файли з:
- Frontmatter (YAML)
- Тегами
- Посиланнями
- Зручною структурою
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger('obsidian_export')

# Конфігурація
OUTPUT_DIR = Path('obsidian_laws')
INDEX_FILE = Path('data/fast_law_index.json')

# Мапа кодексів з українськими назвами
CODES_UA = {
    'BGB': 'Цивільний кодекс Німеччини',
    'SGB_1': 'Соціальний кодекс I (Загальна частина)',
    'SGB_2': 'Соціальний кодекс II (Jobcenter)',
    'SGB_3': 'Соціальний кодекс III (Агентство з праці)',
    'SGB_4': 'Соціальний кодекс IV',
    'SGB_5': 'Соціальний кодекс V (Здоров\'я)',
    'SGB_6': 'Соціальний кодекс VI (Пенсії)',
    'SGB_7': 'Соціальний кодекс VII (Страхування від нещасних випадків)',
    'SGB_8': 'Соціальний кодекс VIII (Діти та молодь)',
    'SGB_9': 'Соціальний кодекс IX (Інваліди)',
    'SGB_10': 'Соціальний кодекс X',
    'SGB_11': 'Соціальний кодекс XI (Догляд)',
    'SGB_12': 'Соціальний кодекс XII',
    'AO': 'Податковий кодекс (Abgabenordnung)',
    'AO_1977': 'Податковий кодекс 1977',
    'ZPO': 'Цивільний процесуальний кодекс',
    'StGB': 'Кримінальний кодекс',
    'StPO': 'Кримінальний процесуальний кодекс',
    'HGB': 'Торговельний кодекс',
    'GG': 'Основний закон (Конституція)',
    'VwVfG': 'Кодекс адміністративного судочинства',
    'FAMFG': 'Закон про сімейні справи',
}

def load_index():
    """Завантажити індекс законів."""
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_obsidian_file(law_name: str, paragraphs: list) -> str:
    """
    Створити Markdown файл для Obsidian.
    
    Args:
        law_name: Назва закону (напр. BGB, SGB_2)
        paragraphs: Список параграфів
    
    Returns:
        Текст файлу
    """
    # Отримуємо українську назву
    ua_name = CODES_UA.get(law_name, f'Закон: {law_name}')
    
    # Теги
    tags = ['#німецьке_право', '#закони']
    if 'SGB' in law_name:
        tags.append('#соціальне_право')
    if 'BGB' in law_name:
        tags.append('#цивільне_право')
    if 'AO' in law_name:
        tags.append('#податкове_право')
    if 'ZPO' in law_name:
        tags.append('#процесуальне_право')
    if 'StGB' in law_name or 'StPO' in law_name:
        tags.append('#кримінальне_право')
    
    # Формуємо контент
    content = []
    
    # Frontmatter
    content.append('---')
    content.append(f'title: "{law_name}"')
    content.append(f'ua_name: "{ua_name}"')
    content.append(f'paragraphs_count: {len(paragraphs)}')
    content.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    content.append(f'tags: {" ".join(tags)}')
    content.append('aliases: []')
    content.append('---')
    content.append('')
    
    # Заголовок
    content.append(f'# {law_name}')
    content.append(f'')
    content.append(f'**{ua_name}**')
    content.append('')
    content.append(f'---')
    content.append('')
    
    # Статистика
    content.append('## 📊 Статистика')
    content.append('')
    content.append(f'- **Всього параграфів:** {len(paragraphs)}')
    content.append(f'- **Перший параграф:** {paragraphs[0] if paragraphs else "N/A"}')
    content.append(f'- **Останній параграф:** {paragraphs[-1] if paragraphs else "N/A"}')
    content.append('')
    content.append('---')
    content.append('')
    
    # Зміст
    content.append('## 📑 Зміст параграфів')
    content.append('')
    
    # Групуємо параграфи по десятках
    para_groups = {}
    for para in paragraphs:
        # Витягуємо номер параграфа
        import re
        match = re.search(r'§\s*(\d+)', para)
        if match:
            num = int(match.group(1))
            decade = (num // 10) * 10
            if decade not in para_groups:
                para_groups[decade] = []
            para_groups[decade].append(para)
    
    # Виводимо групами
    for decade in sorted(para_groups.keys()):
        group = para_groups[decade]
        content.append(f'### Параграфи {decade}-{decade+9}')
        content.append('')
        for para in sorted(group, key=lambda x: int(re.search(r'§\s*(\d+)', x).group(1))):
            content.append(f'- {para}')
        content.append('')
    
    # Посилання
    content.append('---')
    content.append('')
    content.append('## 🔗 Посилання')
    content.append('')
    content.append(f'- [[німецьке_право]]')
    content.append(f'- [[закони_Німеччини]]')
    if 'SGB' in law_name:
        content.append(f'- [[соціальне_право]]')
        content.append(f'- [[Jobcenter]]')
    if 'BGB' in law_name:
        content.append(f'- [[цивільне_право]]')
    
    content.append('')
    content.append('---')
    content.append('')
    content.append(f'*Експортовано: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    
    return '\n'.join(content)

def export_to_obsidian():
    """Експорт всіх законів в Obsidian формат."""
    logger.info("="*70)
    logger.info("  📚 ЕКСПОРТ ЗАКОНІВ В OBSIDIAN")
    logger.info("="*70)
    
    # Завантажуємо індекс
    logger.info("\n📖 Завантаження індексу...")
    index = load_index()
    
    laws = index.get('laws', {})
    total_laws = len(laws)
    logger.info(f"   Знайдено законів: {total_laws:,}")
    
    # Створюємо директорію
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Створюємо файли
    logger.info(f"\n📝 Створення файлів в {OUTPUT_DIR}/...")
    
    created_files = []
    
    for i, (law_name, law_data) in enumerate(sorted(laws.items())):
        paragraphs = law_data.get('paragraphs', [])
        
        if not paragraphs:
            continue
        
        # Створюємо файл
        content = create_obsidian_file(law_name, paragraphs)
        
        # Ім'я файлу
        filename = f"{law_name}.md"
        file_path = OUTPUT_DIR / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        created_files.append(filename)
        
        # Прогрес
        if (i + 1) % 500 == 0:
            logger.info(f"   Створено: {i + 1}/{total_laws} файлів")
    
    # Створюємо index файл
    logger.info("\n📑 Створення індексного файлу...")
    create_index_file(laws)
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    logger.info(f"   Створено файлів: {len(created_files):,}")
    logger.info(f"   Директорія: {OUTPUT_DIR.absolute()}")
    
    # Топ 10
    logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ (за кількістю параграфів):")
    sorted_laws = sorted(laws.items(), key=lambda x: len(x[1].get('paragraphs', [])), reverse=True)[:10]
    for i, (law, data) in enumerate(sorted_laws, 1):
        count = len(data.get('paragraphs', []))
        ua_name = CODES_UA.get(law, law)
        logger.info(f"   {i}. {law} ({ua_name}): {count:,} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ЕКСПОРТ ЗАВЕРШЕНО!")
    logger.info("="*70)
    logger.info(f"\n📁 Відкрийте {OUTPUT_DIR}/ в Obsidian")
    logger.info("")

def create_index_file(laws: dict):
    """Створити індексний файл для всіх законів."""
    content = []
    
    content.append('---')
    content.append('title: "Індекс німецьких законів"')
    content.append('tags: [німецьке_право, закони, індекс]')
    content.append('---')
    content.append('')
    content.append('# 📚 Індекс німецьких законів')
    content.append('')
    content.append('Повний список всіх експортованих законів.')
    content.append('')
    content.append('---')
    content.append('')
    
    # Основні кодекси
    content.append('## 🏛️ Основні кодекси')
    content.append('')
    
    main_codes = ['BGB', 'SGB_1', 'SGB_2', 'SGB_3', 'SGB_4', 'SGB_5', 
                  'SGB_6', 'SGB_7', 'SGB_8', 'SGB_9', 'SGB_10', 'SGB_11', 'SGB_12',
                  'AO', 'AO_1977', 'ZPO', 'StGB', 'StPO', 'HGB', 'GG', 'FAMFG']
    
    for code in main_codes:
        if code in laws:
            count = len(laws[code].get('paragraphs', []))
            ua_name = CODES_UA.get(code, code)
            content.append(f'- [[{code}]] - {ua_name} ({count:,} §)')
    
    content.append('')
    content.append('---')
    content.append('')
    
    # Всі інші закони
    content.append('## 📋 Всі закони за абеткою')
    content.append('')
    
    for law_name in sorted(laws.keys()):
        count = len(laws[law_name].get('paragraphs', []))
        if count > 0:
            content.append(f'- [[{law_name}]] ({count} §)')
    
    content.append('')
    content.append('---')
    content.append('')
    content.append(f'*Створено: {datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    
    # Збереження
    with open(OUTPUT_DIR / '00_Індекс_законів.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

if __name__ == '__main__':
    export_to_obsidian()
