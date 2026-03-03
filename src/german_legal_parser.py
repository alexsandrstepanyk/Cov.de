#!/usr/bin/env python3
"""
German Legal Reference Parser v8.2
Інтеграція з lavis-nlp/german-legal-reference-parser

Парсить посилання на німецькі закони з тексту:
- Simple LawRef: § 811 Abs. 1 Nr. 11 ZPO
- Multi LawRef: §§ 3, 4 Nr. 3a) UWG
- IVM LawRef: § 291 S. 1 i.V.m § 288 Abs. 1 S. 2 BGB
- File Ref: 7 L 3645/97

Джерело: https://github.com/lavis-nlp/german-legal-reference-parser
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SimpleLawRef:
    """Просте посилання на закон."""
    paragraph: str  # Параграф (§ 19)
    abs: Optional[str] = None  # Absatz (Abs. 1)
    satz: Optional[str] = None  # Satz (S. 1)
    nr: Optional[str] = None  # Nummer (Nr. 11)
    vorschrift: Optional[str] = None  # Закон (BGB, ZPO, SGB)
    buch: Optional[str] = None  # Buch (для SGB)
    
    def __str__(self):
        result = f"§ {self.paragraph}"
        if self.abs:
            result += f" Abs. {self.abs}"
        if self.satz:
            result += f" S. {self.satz}"
        if self.nr:
            result += f" Nr. {self.nr}"
        if self.vorschrift:
            result += f" {self.vorschrift}"
        return result


@dataclass
class MultiLawRef:
    """Множинне посилання на закони (§§)."""
    paragraphs: List[str]
    abs: Optional[str] = None
    satz: Optional[str] = None
    nr: Optional[str] = None
    vorschrift: Optional[str] = None
    
    def __str__(self):
        result = f"§§ {', '.join(self.paragraphs)}"
        if self.abs:
            result += f" Abs. {self.abs}"
        if self.satz:
            result += f" S. {self.satz}"
        if self.nr:
            result += f" Nr. {self.nr}"
        if self.vorschrift:
            result += f" {self.vorschrift}"
        return result


@dataclass
class IVMLawRef:
    """Посилання з i.V.m. (in Verbindung mit)."""
    left: SimpleLawRef
    right: SimpleLawRef
    
    def __str__(self):
        return f"{self.left} i.V.m {self.right}"


@dataclass
class FileRef:
    """Посилання на файл справи."""
    kammer: str  # Kammer (7 L)
    nr: str  # Номер (3645)
    jahr: str  # Рік (97)
    
    def __str__(self):
        return f"{self.kammer} {self.nr}/{self.jahr}"


class GermanLegalReferenceParser:
    """
    Парсер посилань на німецькі закони.
    
    Інтеграція з lavis-nlp/german-legal-reference-parser
    """
    
    def __init__(self):
        # Завантаження назв законів з laws.txt
        self.law_names = self._load_law_names()
        
        # Компіляція regex patterns
        self.patterns = self._compile_patterns()
    
    def _load_law_names(self) -> List[str]:
        """Завантаження назв законів."""
        # Вбудований список найпоширеніших законів
        return [
            # Кодекси
            'BGB', 'ZPO', 'AO', 'SGB', 'SGG', 'VwVfG', 'VwGO', 'FGO', 'SGV',
            'StGB', 'StPO', 'OWiG', 'JGG', 'BtMG', 'WpHG', 'KWG',
            'HGB', 'AktG', 'GmbHG', 'InsO', 'ZVG',
            'GG', 'BVerfGG', 'BGBL', 'GVBL',
            'UWG', 'BGB-InfoV', 'TMG', 'DSGVO', 'BDSG',
            'ArbG', 'ArbGG', 'BUrlG', 'EFZG', 'KSchG', 'TzBfG',
            'SozGG', 'Soz ArbG',
            # Соціальні кодекси
            'SGB I', 'SGB II', 'SGB III', 'SGB IV', 'SGB V',
            'SGB VI', 'SGB VII', 'SGB VIII', 'SGB IX', 'SGB X',
            'SGB XI', 'SGB XII', 'SGB XIII',
            # Податкові
            'EStG', 'KStG', 'GewStG', 'UStG', 'ErbStG', 'GrEStG',
            'BewG', 'AO', 'FGO',
            # Цивільні
            'BGB', 'ZPO', 'GVGA', 'GBO', 'VersZG',
            # Адміністративні
            'VwVfG', 'VwGO', 'SGB X',
            # Кримінальні
            'StGB', 'StPO', 'OWiG', 'JGG',
            # Інші
            'FamFG', 'BeurkG', 'ZPO', 'EGZPO', 'GVGA',
        ]
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Компіляція regex patterns."""
        patterns = {}
        
        # Simple LawRef: § 811 Abs. 1 Nr. 11 ZPO
        patterns['simple'] = re.compile(
            r'§\s*'
            r'(\d+[a-z]?)'  # Параграф
            r'(?:\s*(?:Abs\.?|Absatz)\s*(\d+(?:[a-z])?))?'  # Absatz
            r'(?:\s*(?:S\.?|Satz)\s*(\d+))?'  # Satz
            r'(?:\s*(?:Nr\.?|Nummer)\s*(\d+(?:[a-z])?))?'  # Nummer
            r'(?:\s*([A-Z]{2,}(?:\s*[IVX]+)?))?'  # Закон (BGB, ZPO, SGB II)
        )
        
        # Multi LawRef: §§ 3, 4 Nr. 3a) UWG
        patterns['multi'] = re.compile(
            r'§§\s*'
            r'(\d+(?:[a-z])?(?:\s*,\s*\d+(?:[a-z])?)*)'  # Параграфи
            r'(?:\s*(?:Abs\.?|Absatz)\s*(\d+(?:[a-z])?))?'  # Absatz
            r'(?:\s*(?:S\.?|Satz)\s*(\d+))?'  # Satz
            r'(?:\s*(?:Nr\.?|Nummer)\s*(\d+(?:[a-z])?))?'  # Nummer
            r'(?:\s*([A-Z]{2,}(?:\s*[IVX]+)?))?'  # Закон
        )
        
        # IVM LawRef: § 291 S. 1 i.V.m § 288 Abs. 1 S. 2 BGB
        patterns['ivm'] = re.compile(
            r'(§\s*\d+[a-z]?(?:\s*[A-Z]{2,})?)\s*'
            r'(?:i\.?V\.?m\.?|in Verbindung mit)\s*'
            r'(§\s*\d+[a-z]?(?:\s*[A-Z]{2,})?)'
        )
        
        # File Ref: 7 L 3645/97
        patterns['file'] = re.compile(
            r'(\d+)\s*([A-Z])\s*(\d+)/(\d{2})'
        )
        
        return patterns
    
    def parse_simple(self, text: str) -> List[Tuple[SimpleLawRef, int]]:
        """Парсинг простих посилань."""
        results = []
        
        for match in self.patterns['simple'].finditer(text):
            ref = SimpleLawRef(
                paragraph=match.group(1),
                abs=match.group(2),
                satz=match.group(3),
                nr=match.group(4),
                vorschrift=match.group(5),
            )
            results.append((ref, match.start()))
        
        return results
    
    def parse_multi(self, text: str) -> List[Tuple[MultiLawRef, int]]:
        """Парсинг множинних посилань."""
        results = []
        
        for match in self.patterns['multi'].finditer(text):
            paragraphs = [p.strip() for p in match.group(1).split(',')]
            ref = MultiLawRef(
                paragraphs=paragraphs,
                abs=match.group(2),
                satz=match.group(3),
                nr=match.group(4),
                vorschrift=match.group(5),
            )
            results.append((ref, match.start()))
        
        return results
    
    def parse_ivm(self, text: str) -> List[Tuple[IVMLawRef, int]]:
        """Парсинг i.V.m. посилань."""
        results = []
        
        for match in self.patterns['ivm'].finditer(text):
            left_text = match.group(1)
            right_text = match.group(2)
            
            # Парсинг лівої частини
            left_match = self.patterns['simple'].search(left_text)
            if left_match:
                left = SimpleLawRef(
                    paragraph=left_match.group(1),
                    abs=left_match.group(2),
                    satz=left_match.group(3),
                    nr=left_match.group(4),
                    vorschrift=left_match.group(5),
                )
            else:
                continue
            
            # Парсинг правої частини
            right_match = self.patterns['simple'].search(right_text)
            if right_match:
                right = SimpleLawRef(
                    paragraph=right_match.group(1),
                    abs=right_match.group(2),
                    satz=right_match.group(3),
                    nr=right_match.group(4),
                    vorschrift=right_match.group(5),
                )
            else:
                continue
            
            ref = IVMLawRef(left=left, right=right)
            results.append((ref, match.start()))
        
        return results
    
    def parse_file(self, text: str) -> List[Tuple[FileRef, int]]:
        """Парсинг посилань на файли справ."""
        results = []
        
        for match in self.patterns['file'].finditer(text):
            ref = FileRef(
                kammer=f"{match.group(1)} {match.group(2)}",
                nr=match.group(3),
                jahr=match.group(4),
            )
            results.append((ref, match.start()))
        
        return results
    
    def parse_all(self, text: str) -> Dict:
        """
        Повний парсинг всіх посилань з тексту.
        
        Args:
            text: Текст з юридичними посиланнями
            
        Returns:
            Dict з всіма типами посилань
        """
        return {
            'simples': self.parse_simple(text),
            'multis': self.parse_multi(text),
            'ivms': self.parse_ivm(text),
            'files': self.parse_file(text),
        }
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """
        Витягування всіх параграфів з тексту у форматі string.
        
        Args:
            text: Текст з юридичними посиланнями
            
        Returns:
            Список параграфів як strings
        """
        results = self.parse_all(text)
        paragraphs = []
        
        # Simple references
        for ref, _ in results['simples']:
            paragraphs.append(str(ref))
        
        # Multi references
        for ref, _ in results['multis']:
            paragraphs.append(str(ref))
        
        # IVM references
        for ref, _ in results['ivms']:
            paragraphs.append(str(ref))
        
        # File references
        for ref, _ in results['files']:
            paragraphs.append(str(ref))
        
        return paragraphs


# Глобальний екземпляр
_parser = None

def get_parser() -> GermanLegalReferenceParser:
    """Отримати або створити парсер."""
    global _parser
    if _parser is None:
        _parser = GermanLegalReferenceParser()
    return _parser

def parse_legal_references(text: str) -> Dict:
    """
    Парсинг юридичних посилань з тексту.
    
    Args:
        text: Текст з юридичними посиланнями
        
    Returns:
        Dict з всіма посиланнями
    """
    parser = get_parser()
    return parser.parse_all(text)

def extract_legal_paragraphs(text: str) -> List[str]:
    """
    Витягування параграфів з тексту.
    
    Args:
        text: Текст з юридичними посиланнями
        
    Returns:
        Список параграфів
    """
    parser = get_parser()
    return parser.extract_paragraphs(text)


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  📚 GERMAN LEGAL REFERENCE PARSER v8.2")
    print("="*80)
    
    test_texts = [
        "Gemäß § 811 Abs. 1 Nr. 11 ZPO ist...",
        "Nach §§ 3, 4 Nr. 3a) UWG verboten...",
        "Gemäß § 291 S. 1 i.V.m § 288 Abs. 1 S. 2 BGB...",
        "Urteil des 7 L 3645/97 vom...",
        "§ 59 SGB II verpflichtet zur Teilnahme...",
        "§§ 19, 20 SGB II regeln die Leistungen...",
    ]
    
    for text in test_texts:
        print(f"\nТекст: {text}")
        print("-"*80)
        
        parser = GermanLegalReferenceParser()
        results = parser.parse_all(text)
        
        if results['simples']:
            print(f"  Simple: {[str(ref) for ref, _ in results['simples']]}")
        if results['multis']:
            print(f"  Multi: {[str(ref) for ref, _ in results['multis']]}")
        if results['ivms']:
            print(f"  IVM: {[str(ref) for ref, _ in results['ivms']]}")
        if results['files']:
            print(f"  File: {[str(ref) for ref, _ in results['files']]}")
        
        # Витягування параграфів
        paragraphs = parser.extract_paragraphs(text)
        print(f"  Всі параграфи: {paragraphs}")
