#!/bin/bash
# Запуск RAG будівництва з логуванням
cd /Users/alex/Desktop/project/Gov.de
python3 src/build_chroma_rag.py 2>&1 | tee logs/build_rag_progress.log
