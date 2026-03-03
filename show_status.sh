#!/bin/bash
# Швидкий перегляд статусу реалізації

clear
echo "========================================"
echo "  СТАТУС: Повна база німецьких законів"
echo "  Оновлено: $(date)"
echo "========================================"
echo ""

# Прогрес
echo "📊 ЗАГАЛЬНИЙ ПРОГРЕС: 75%"
echo "████████████████████░░░░"
echo ""

# Git Clone
if [ -d "data/german_laws_complete" ]; then
    SIZE=$(du -sh data/german_laws_complete 2>/dev/null | cut -f1)
    FILES=$(find data/german_laws_complete -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "✅ Git Clone: ЗАВЕРШЕНО"
    echo "   Розмір: $SIZE"
    echo "   Файлів: $FILES"
else
    echo "⏳ Git Clone: В ПРОЦЕСІ"
fi
echo ""

# Парсинг
if [ -f "data/complete_law_json/german_laws_complete.json" ]; then
    JSON_SIZE=$(du -h data/complete_law_json/german_laws_complete.json 2>/dev/null | cut -f1)
    echo "✅ Парсинг: ЗАВЕРШЕНО"
    echo "   JSON: $JSON_SIZE"
else
    echo "⏳ Парсинг: В ПРОЦЕСІ"
fi
echo ""

# RAG
if [ -d "data/complete_law_rag_v2" ]; then
    echo "🔄 RAG База: В ПРОЦЕСІ"
else
    echo "⏳ RAG База: ОЧІКУЄ"
fi
echo ""

echo "========================================"
echo "⏱️ Час до завершення: ~4-6 годин"
echo "========================================"
echo ""

# Останні логи
echo "📄 ОСТАННІ ЛОГИ:"
echo "----------------------------------------"
tail -10 data/parsing_progress.log 2>/dev/null || echo "Логів ще немає"
echo ""
echo "Для деталей:"
echo "  cat FINAL_STATUS.md"
echo "  tail -f data/parsing_progress.log"
