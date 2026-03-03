#!/bin/bash
# Моніторинг прогресу Git Clone

LOG_FILE="data/clone_progress.log"
REPO_DIR="data/german_laws_complete"

echo "========================================" > "$LOG_FILE"
echo "  МОНІТОРИНГ GIT CLONE" >> "$LOG_FILE"
echo "  Початок: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

while true; do
    # Перевірка чи процес ще триває
    if ps aux | grep "[g]it clone" > /dev/null; then
        STATUS="⏳ В ПРОЦЕСІ"
        
        # Розмір директорії
        if [ -d "$REPO_DIR" ]; then
            SIZE=$(du -sh "$REPO_DIR" 2>/dev/null | cut -f1)
            FILES=$(find "$REPO_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
        else
            SIZE="0"
            FILES="0"
        fi
        
        # Прогрес (приблизно, бо Git не показує %)
        # Очікуваний розмір ~500MB
        if [ "$SIZE" != "0" ]; then
            SIZE_NUM=$(echo "$SIZE" | sed 's/[^0-9.]//g')
            if [[ "$SIZE" == *"G"* ]]; then
                PROGRESS="100%"
            elif [[ "$SIZE" == *"M"* ]]; then
                PERCENT=$(echo "scale=0; $SIZE_NUM * 100 / 500" | bc 2>/dev/null || echo "N/A")
                PROGRESS="${PERCENT}%"
            else
                PROGRESS="<1%"
            fi
        else
            PROGRESS="0%"
        fi
    else
        STATUS="✅ ЗАВЕРШЕНО"
        PROGRESS="100%"
        if [ -d "$REPO_DIR" ]; then
            SIZE=$(du -sh "$REPO_DIR" 2>/dev/null | cut -f1)
            FILES=$(find "$REPO_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
        fi
    fi
    
    # Запис в лог
    cat > "$LOG_FILE" << LOGEOF
========================================
  МОНІТОРИНГ GIT CLONE
  Оновлено: $(date)
========================================

Статус: $STATUS
Прогрес: $PROGRESS
Розмір: $SIZE
Файлів: $FILES

Очікується: ~500MB, ~12,000+ файлів
Час початку: $(date -v-1H +%H:%M 2>/dev/null || date +%H:%M)

========================================
LOGEOF
    
    # Вивід на екран
    clear
    cat "$LOG_FILE"
    
    # Якщо завершено - вихід
    if [ "$STATUS" == "✅ ЗАВЕРШЕНО" ]; then
        echo ""
        echo "🎉 GIT CLONE ЗАВЕРШЕНО!"
        echo ""
        echo "Наступний крок: python3 src/parse_and_build_rag.py"
        break
    fi
    
    sleep 5
done
