#!/usr/bin/env python3
"""
TELEGRAM BOT TESTER - Автоматичне тестування Gov.de Bot
Відправляє листи в Telegram бота та перехоплює відповіді

Використання:
python3 test_telegram_bot.py --token YOUR_BOT_TOKEN --chat_id YOUR_CHAT_ID
"""

import sys
import time
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime

# Кольори
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TelegramBotTester:
    """Автоматичне тестування Telegram бота."""
    
    def __init__(self, bot_token: str, chat_id: int):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.results = []
        
    def send_message(self, text: str) -> dict:
        """Відправити повідомлення."""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=data, timeout=30)
        return response.json()
    
    def send_document(self, file_path: str, caption: str = '') -> dict:
        """Відправити документ (лист)."""
        url = f"{self.base_url}/sendDocument"
        
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            response = requests.post(url, files=files, data=data, timeout=60)
        
        return response.json()
    
    def get_updates(self, offset: int = 0, timeout: int = 30) -> dict:
        """Отримати оновлення (відповіді бота)."""
        url = f"{self.base_url}/getUpdates"
        params = {
            'offset': offset,
            'timeout': timeout,
            'allowed_updates': ['message']
        }
        response = requests.get(url, params=params, timeout=timeout + 5)
        return response.json()
    
    def test_letter(self, letter_file: Path, letter_id: int) -> dict:
        """Тестування одного листа."""
        print(f"\n{Colors.BLUE}Тест {letter_id}: {letter_file.name}{Colors.END}")
        
        # Відправка листа
        print(f"  📤 Відправка...", end=" ")
        start_time = time.time()
        
        result = self.send_document(
            str(letter_file),
            caption=f"🧪 Тест {letter_id}"
        )
        
        if not result.get('ok'):
            print(f"{Colors.RED}❌ ПОМИЛКА: {result.get('description')}{Colors.END}")
            return {
                'id': letter_id,
                'success': False,
                'error': result.get('description'),
            }
        
        print(f"{Colors.GREEN}✅{Colors.END}")
        
        # Очікування відповіді
        print(f"  ⏳ Очікування відповіді...", end=" ")
        
        last_update_id = result.get('result', {}).get('message_id', 0) + 1
        bot_responses = []
        max_wait = 120  # 2 хвилини
        
        wait_start = time.time()
        while time.time() - wait_start < max_wait:
            updates = self.get_updates(offset=last_update_id, timeout=10)
            
            if updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    message = update.get('message', {})
                    if message.get('chat', {}).get('id') == self.chat_id:
                        bot_responses.append({
                            'text': message.get('text', ''),
                            'date': message.get('date'),
                            'message_id': message.get('message_id'),
                        })
                        last_update_id = message.get('message_id', 0) + 1
            
            # Якщо отримали хоча б одну відповідь - чекаємо ще трохи
            if bot_responses:
                time.sleep(2)
            else:
                time.sleep(1)
        
        elapsed = time.time() - start_time
        print(f"{Colors.GREEN}✅ ({elapsed:.2f}s, {len(bot_responses)} повідомлень){Colors.END}")
        
        # Аналіз відповідей
        analysis = self.analyze_responses(bot_responses)
        
        return {
            'id': letter_id,
            'success': True,
            'elapsed': elapsed,
            'responses': bot_responses,
            'analysis': analysis,
        }
    
    def analyze_responses(self, responses: list) -> dict:
        """Аналіз відповідей бота."""
        analysis = {
            'total_messages': len(responses),
            'total_length': sum(len(r['text']) for r in responses),
            'has_uk': False,
            'has_de': False,
            'has_repetitions': False,
            'has_placeholders': False,
            'has_paragraphs': False,
            'quality_score': 0,
            'issues': [],
        }
        
        full_text = '\n'.join(r['text'] for r in responses)
        
        # Перевірка на українську
        if any(c in full_text for c in ['і', 'ї', 'є', 'ґ', 'ь']):
            analysis['has_uk'] = True
        
        # Перевірка на німецьку
        if any(word in full_text.lower() for word in ['sehr', 'geehrte', 'mit', 'freundlichen']):
            analysis['has_de'] = True
        
        # Перевірка на повторення
        words = full_text.split()
        if len(words) > 100:
            for i in range(len(words) - 20):
                phrase = ' '.join(words[i:i+10])
                if words.count(phrase) > 3:
                    analysis['has_repetitions'] = True
                    analysis['issues'].append(f'Повторення: "{phrase[:50]}..."')
                    break
        
        # Перевірка на placeholder'и
        placeholders = ['[', ']', 'Ha3ba', 'Homep', 'Fpiaenue']
        for ph in placeholders:
            if ph in full_text:
                analysis['has_placeholders'] = True
                analysis['issues'].append(f'Placeholder: {ph}')
        
        # Перевірка на параграфи
        if '§' in full_text or 'BGB' in full_text or 'SGB' in full_text:
            analysis['has_paragraphs'] = True
        
        # Розрахунок quality score
        score = 0
        if analysis['total_length'] > 1000:
            score += 20
        if analysis['has_uk']:
            score += 20
        if analysis['has_de']:
            score += 20
        if not analysis['has_repetitions']:
            score += 20
        if not analysis['has_placeholders']:
            score += 10
        if analysis['has_paragraphs']:
            score += 10
        
        analysis['quality_score'] = score
        
        return analysis
    
    def run_tests(self, letters_dir: Path, max_letters: int = 50) -> list:
        """Запуск тестів."""
        print_header("🧪 АВТОМАТИЧНЕ ТЕСТУВАННЯ TELEGRAM БОТА")
        print(f"Директорія: {letters_dir.absolute()}")
        print(f"Максимум листів: {max_letters}")
        print(f"Chat ID: {self.chat_id}")
        
        # Отримання списку листів
        letter_files = sorted(letters_dir.glob('letter_*.txt'))[:max_letters]
        
        print(f"\nЗнайдено {len(letter_files)} листів\n")
        
        # Тестування
        for i, letter_file in enumerate(letter_files, 1):
            result = self.test_letter(letter_file, i)
            self.results.append(result)
            
            # Пауза між тестами
            if i < len(letter_files):
                time.sleep(3)
        
        # Збереження результатів
        self.save_results()
        
        # Підсумки
        self.print_summary()
        
        return self.results
    
    def save_results(self):
        """Збереження результатів."""
        output_file = Path(f'telegram_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        # Статистика
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('success'))
        avg_quality = sum(r.get('analysis', {}).get('quality_score', 0) for r in self.results if r.get('success')) / max(passed, 1)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'total_letters': total,
                'passed': passed,
                'failed': total - passed,
                'avg_quality': avg_quality,
                'results': self.results,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результати збережено: {output_file.absolute()}")
    
    def print_summary(self):
        """Друк підсумків."""
        print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('success'))
        avg_quality = sum(r.get('analysis', {}).get('quality_score', 0) for r in self.results if r.get('success')) / max(passed, 1)
        avg_time = sum(r.get('elapsed', 0) for r in self.results if r.get('success')) / max(passed, 1)
        
        print(f"\nЗагальна точність: {Colors.BOLD}{passed}/{total} ({passed/total*100:.1f}%){Colors.END}")
        print(f"Середня якість: {Colors.BOLD}{avg_quality:.1f}/100{Colors.END}")
        print(f"Середній час: {Colors.BOLD}{avg_time:.2f}s{Colors.END}")
        
        if avg_quality >= 80:
            print(f"\n{Colors.GREEN}✅ ВІДМІННО{Colors.END}")
        elif avg_quality >= 60:
            print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END}")
        else:
            print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END}")
        
        # Проблеми
        all_issues = []
        for r in self.results:
            if r.get('success'):
                all_issues.extend(r.get('analysis', {}).get('issues', []))
        
        if all_issues:
            print(f"\n{Colors.RED}⚠️ ПРОБЛЕМИ:{Colors.END}")
            for issue in all_issues[:10]:
                print(f"  - {issue}")


def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}\n")

def main():
    parser = argparse.ArgumentParser(description='Автоматичне тестування Telegram бота')
    parser.add_argument('--token', required=True, help='Telegram Bot Token')
    parser.add_argument('--chat-id', type=int, required=True, help='Chat ID для тестування')
    parser.add_argument('--dir', default='test_letters_500', help='Директорія з листами')
    parser.add_argument('--max', type=int, default=50, help='Максимум листів для тесту')
    
    args = parser.parse_args()
    
    letters_dir = Path(args.dir)
    if not letters_dir.exists():
        print(f"❌ Директорія {letters_dir} не знайдена!")
        return
    
    tester = TelegramBotTester(args.token, args.chat_id)
    tester.run_tests(letters_dir, args.max)

if __name__ == '__main__':
    main()
