#!/usr/bin/env python3
"""
Export RAG Database to Obsidian
Експорт RAG бази в Obsidian для візуалізації зв'язків
"""

import chromadb
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('export_to_obsidian')

# Шляхи
CHROMA_DB_PATH = Path('data/legal_database_chroma')
OBSIDIAN_OUTPUT = Path('obsidian_rag_export')

def export_to_obsidian():
    """Експорт RAG бази в Obsidian."""
    print("\n" + "="*80)
    print("  📚 ЕКСПОРТ RAG БАЗИ В OBSIDIAN")
    print("="*80)
    
    # Підключення до ChromaDB
    print(f"\n🔌 Підключення до ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Створення вихідної папки
    OBSIDIAN_OUTPUT.mkdir(parents=True, exist_ok=True)
    (OBSIDIAN_OUTPUT / '.obsidian').mkdir(parents=True, exist_ok=True)
    
    # Отримуємо всі колекції
    collections = ['german_laws_general', 'german_laws_full']
    
    all_laws_data = {}
    total_exported = 0
    
    for coll_name in collections:
        print(f"\n📖 Обробка колекції '{coll_name}'...")
        
        try:
            collection = client.get_collection(coll_name)
            count = collection.count()
            print(f"   Знайдено {count:,} записів")
            
            # Отримуємо всі дані
            results = collection.get(
                include=['documents', 'metadatas'],
                limit=None
            )
            
            documents = results['documents']
            metadatas = results['metadatas']
            
            # Групуємо по законах
            laws_by_name = {}
            
            for i, (doc, meta) in enumerate(zip(documents, metadatas)):
                law_name = meta.get('law_name', 'Unknown')
                
                if law_name not in laws_by_name:
                    laws_by_name[law_name] = {
                        'chunks': [],
                        'source': meta.get('source', 'unknown'),
                        'files': set()
                    }
                
                laws_by_name[law_name]['chunks'].append({
                    'index': meta.get('chunk_index', 0),
                    'total': meta.get('total_chunks', 1),
                    'content': doc,
                    'file': meta.get('file_name', ''),
                })
                
                if meta.get('file_name'):
                    laws_by_name[law_name]['files'].add(meta.get('file_name'))
                
                total_exported += 1
            
            # Зберігаємо в all_laws_data
            for law_name, data in laws_by_name.items():
                if law_name not in all_laws_data:
                    all_laws_data[law_name] = data
                else:
                    # Об'єднуємо chunk'и
                    all_laws_data[law_name]['chunks'].extend(data['chunks'])
                    all_laws_data[law_name]['files'].update(data['files'])
            
            print(f"   Законів: {len(laws_by_name)}")
            
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    # Створення файлів Obsidian
    print(f"\n📝 Створення файлів Obsidian...")
    
    # Індексний файл
    index_content = f"""---
title: "RAG База - Індекс Законів"
created: {datetime.now().strftime('%Y-%m-%d')}
tags: [rag, індекс, закони]
---

# 📚 RAG База - Індекс Законів

**Експортовано:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Статистика

- **Всього законів:** {len(all_laws_data)}
- **Всього чанків:** {total_exported:,}

---

## 📋 Закони за абеткою

"""
    
    # Сортуємо закони
    sorted_laws = sorted(all_laws_data.items())
    
    for law_name, data in sorted_laws:
        chunk_count = len(data['chunks'])
        files = ', '.join(sorted(data['files'])) if data['files'] else 'N/A'
        index_content += f"- [[{law_name}]] ({chunk_count} чанків) - Файли: {files}\n"
    
    index_content += f"""
---

## 🔗 Джерела

- **german_laws_general:** PDF кодекси з папки general
- **german_laws_full:** Повна база німецьких законів

---

## 🎯 Як використовувати

1. Відкрийте будь-який закон зі списку вище
2. Перегляньте Graph View для візуалізації зв'язків
3. Використовуйте пошук (Ctrl/Cmd+Shift+F) для пошуку по всій базі

"""
    
    # Зберігаємо індекс
    index_file = OBSIDIAN_OUTPUT / '00_RAG_Index.md'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"   ✅ Створено індекс: {index_file}")
    
    # Створення файлів для кожного закону
    export_progress = 0
    
    for law_name, data in sorted_laws:
        try:
            # Сортуємо chunk'и по індексу
            sorted_chunks = sorted(data['chunks'], key=lambda x: x['index'])
            
            # Об'єднуємо контент
            full_content = "\n\n---\n\n".join([
                f"### Частина {chunk['index'] + 1}/{chunk['total']}\n\n{chunk['content']}"
                for chunk in sorted_chunks
            ])
            
            # Створюємо файл
            file_content = f"""---
title: "{law_name}"
created: {datetime.now().strftime('%Y-%m-%d')}
tags: [rag, закон, {data['source']}]
files: {', '.join(sorted(data['files'])) if data['files'] else 'N/A'}
chunks: {len(sorted_chunks)}
---

# {law_name}

**Джерело:** {data['source']}

**Файли:** {', '.join(sorted(data['files'])) if data['files'] else 'N/A'}

**Кількість чанків:** {len(sorted_chunks)}

---

## 📄 Повний текст

{full_content}

---

## 🔗 Посилання

- [[00_RAG_Index|← Повернутися до індексу]]

"""
            
            # Зберігаємо файл
            file_path = OBSIDIAN_OUTPUT / f'{law_name}.md'
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            export_progress += 1
            
            if export_progress % 100 == 0:
                print(f"   Прогрес: {export_progress}/{len(sorted_laws)}")
                
        except Exception as e:
            print(f"   ❌ Помилка експорту {law_name}: {e}")
    
    print(f"   ✅ Експортовано законів: {export_progress}")
    
    # Створення конфігурації Obsidian
    print(f"\n⚙️  Створення конфігурації Obsidian...")
    
    # app.json
    app_json = {
        "alwaysUpdateLinks": True,
        "newLinkFormat": "relative",
        "useMarkdownLinks": True,
        "showLineNumber": True
    }
    
    import json
    with open(OBSIDIAN_OUTPUT / '.obsidian' / 'app.json', 'w', encoding='utf-8') as f:
        json.dump(app_json, f, indent=2)
    
    # appearance.json
    appearance_json = {
        "accentColor": "#7c3aed",
        "baseFontSize": 16
    }
    
    with open(OBSIDIAN_OUTPUT / '.obsidian' / 'appearance.json', 'w', encoding='utf-8') as f:
        json.dump(appearance_json, f, indent=2)
    
    # core-plugins.json
    core_plugins = {
        "core-plugins": {
            "file-explorer": True,
            "graph": True,
            "search": True,
            "backlink": True,
            "outgoing-link": True,
            "tag-pane": True,
            "page-preview": True,
            "daily-notes": False,
            "templates": True,
            "note-composer": True
        }
    }
    
    with open(OBSIDIAN_OUTPUT / '.obsidian' / 'core-plugins.json', 'w', encoding='utf-8') as f:
        json.dump(core_plugins, f, indent=2)
    
    print(f"   ✅ Конфігурацію створено")
    
    # Фінальна статистика
    print("\n" + "="*80)
    print("  📊 СТАТИСТИКА ЕКСПОРТУ")
    print("="*80)
    print(f"Законів експортовано:    {export_progress:,}")
    print(f"Всього чанків:           {total_exported:,}")
    print(f"Шлях до бази:            {OBSIDIAN_OUTPUT.absolute()}")
    
    print("\n" + "="*80)
    print("  ✅ ЕКСПОРТ В OBSIDIAN ЗАВЕРШЕНО!")
    print("="*80)
    print(f"\n📁 Відкрийте папку: {OBSIDIAN_OUTPUT.absolute()}")
    print("\n📊 Для візуалізації зв'язків:")
    print("   1. Відкрийте папку в Obsidian")
    print("   2. Натисніть Graph View (Ctrl/Cmd+G)")
    print("   3. Перегляньте зв'язки між законами")
    print("")


if __name__ == '__main__':
    try:
        export_to_obsidian()
    except KeyboardInterrupt:
        print("\n\n⚠️  Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
