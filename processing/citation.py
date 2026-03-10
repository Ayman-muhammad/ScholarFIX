"""
Citation and Reference Processing Module
"""

import re
from typing import Dict, List, Any, Optional
from enum import Enum

class CitationStyle(Enum):
    """Citation styles"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    IEEE = "ieee"

class CitationProcessor:
    def __init__(self):
        """Initialize citation processor"""
        self.citation_patterns = self._initialize_citation_patterns()
        self.reference_patterns = self._initialize_reference_patterns()
        
    def _initialize_citation_patterns(self) -> Dict[CitationStyle, List[tuple]]:
        """Initialize citation patterns for each style"""
        return {
            CitationStyle.APA: [
                (r'\(([A-Za-z]+),?\s*(\d{4})\)', r'(\1, \2)'),  # (Smith, 2020)
                (r'\(([A-Za-z]+)\s+&\s+([A-Za-z]+),?\s*(\d{4})\)', r'(\1 & \2, \3)'),  # (Smith & Jones, 2020)
            ],
            CitationStyle.MLA: [
                (r'\(([A-Za-z]+)\s+(\d+)\)', r'(\1 \2)'),  # (Smith 45)
                (r'\(([A-Za-z]+)\s+and\s+([A-Za-z]+)\s+(\d+)\)', r'(\1 and \2 \3)'),  # (Smith and Jones 45)
            ],
            CitationStyle.CHICAGO: [
                (r'\[(\d+)\]', r'[\1]'),  # [1]
                (r'\(([A-Za-z]+)\s+(\d{4}),?\s*(\d+)\)', r'(\1 \2, \3)'),  # (Smith 2020, 45)
            ],
            CitationStyle.HARVARD: [
                (r'\(([A-Za-z]+)\s+(\d{4})\)', r'(\1 \2)'),  # (Smith 2020)
                (r'\(([A-Za-z]+)\s+and\s+([A-Za-z]+)\s+(\d{4})\)', r'(\1 and \2 \3)'),  # (Smith and Jones 2020)
            ],
            CitationStyle.IEEE: [
                (r'\[(\d+)\]', r'[\1]'),  # [1]
            ]
        }
    
    def _initialize_reference_patterns(self) -> Dict[CitationStyle, Dict[str, Any]]:
        """Initialize reference formatting patterns"""
        return {
            CitationStyle.APA: {
                'book': '{author_last}, {author_first_initial}. ({year}). *{title}*. {publisher}.',
                'article': '{author_last}, {author_first_initial}. ({year}). {title}. *{journal}*, *{volume}*({issue}), {pages}.',
                'website': '{author_last}, {author_first_initial}. ({year}, {month} {day}). {title}. {site_name}. {url}',
            },
            CitationStyle.MLA: {
                'book': '{author_last}, {author_first}. *{title}*. {publisher}, {year}.',
                'article': '{author_last}, {author_first}. "{title}." *{journal}*, vol. {volume}, no. {issue}, {year}, pp. {pages}.',
                'website': '{author_last}, {author_first}. "{title}." *{site_name}*, {day} {month} {year}, {url}.',
            },
            CitationStyle.CHICAGO: {
                'book': '{author_last}, {author_first}. {year}. *{title}*. {location}: {publisher}.',
                'article': '{author_last}, {author_first}. "{title}." *{journal}* {volume}, no. {issue} ({year}): {pages}.',
                'website': '{author_last}, {author_first}. "{title}." *{site_name}*. Last modified {month} {day}, {year}. {url}.',
            }
        }
    
    def process_citations(self, text: str, style: str = 'apa') -> Dict[str, Any]:
        """
        Process and format citations in text
        
        Args:
            text: Input text
            style: Citation style (apa, mla, chicago, harvard, ieee)
            
        Returns:
            Dictionary with processed text and citation info
        """
        try:
            citation_style = CitationStyle(style.lower())
        except ValueError:
            citation_style = CitationStyle.APA
        
        original_text = text
        changes = []
        citation_count = 0
        
        # Apply citation formatting patterns
        if citation_style in self.citation_patterns:
            for pattern, replacement in self.citation_patterns[citation_style]:
                # Find all matches
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    original = match.group(0)
                    formatted = re.sub(pattern, replacement, original, flags=re.IGNORECASE)
                    
                    if original != formatted:
                        changes.append({
                            'type': 'citation_format',
                            'style': style,
                            'original': original,
                            'formatted': formatted
                        })
                        citation_count += 1
                
                # Apply replacement to entire text
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Extract citations for analysis
        citations_found = self.extract_citations(text)
        
        return {
            'processed_text': text,
            'citation_count': citation_count,
            'citations_found': citations_found,
            'style': style,
            'changes': changes,
            'original_text': original_text
        }
    
    def extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract citations from text
        
        Args:
            text: Input text
            
        Returns:
            List of citations found
        """
        citations = []
        
        # Common citation patterns
        patterns = [
            # (Author, Year)
            (r'\(([A-Z][a-z]+(?:,?\s+[A-Z][a-z]+)*),?\s*(\d{4})\)', 'author_year'),
            # [Number]
            (r'\[(\d+)\]', 'numbered'),
            # Author (Year)
            (r'([A-Z][a-z]+(?:,?\s+[A-Z][a-z]+)*)\s*\((\d{4})\)', 'author_year_text'),
        ]
        
        for pattern, citation_type in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    'type': citation_type,
                    'match': match.group(0),
                    'position': match.start(),
                    'details': match.groups()
                })
        
        return citations
    
    def generate_reference(self, reference_type: str, data: Dict[str, str], style: str = 'apa') -> str:
        """
        Generate a formatted reference
        
        Args:
            reference_type: Type of reference (book, article, website)
            data: Reference data
            style: Citation style
            
        Returns:
            Formatted reference
        """
        try:
            citation_style = CitationStyle(style.lower())
        except ValueError:
            citation_style = CitationStyle.APA
        
        if citation_style not in self.reference_patterns:
            return ""
        
        style_patterns = self.reference_patterns[citation_style]
        
        if reference_type not in style_patterns:
            return ""
        
        template = style_patterns[reference_type]
        
        # Fill template with data
        formatted = template
        for key, value in data.items():
            placeholder = f'{{{key}}}'
            formatted = formatted.replace(placeholder, value)
        
        return formatted
    
    def check_citation_consistency(self, text: str) -> Dict[str, Any]:
        """
        Check citation consistency in text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with consistency analysis
        """
        analysis = {
            'total_citations': 0,
            'citation_styles_found': [],
            'potential_issues': [],
            'suggestions': []
        }
        
        # Extract all citations
        citations = self.extract_citations(text)
        analysis['total_citations'] = len(citations)
        
        if not citations:
            analysis['suggestions'].append("No citations found. Consider adding references to support your claims.")
            return analysis
        
        # Analyze citation styles
        style_patterns = {
            'apa': r'\([A-Za-z]+,\s*\d{4}\)',
            'mla': r'\([A-Za-z]+\s+\d+\)',
            'numbered': r'\[\d+\]',
            'chicago': r'\([A-Za-z]+\s+\d{4}[,\s]+\d+\)',
        }
        
        found_styles = set()
        for citation in citations:
            for style_name, pattern in style_patterns.items():
                if re.match(pattern, citation['match']):
                    found_styles.add(style_name)
                    break
        
        analysis['citation_styles_found'] = list(found_styles)
        
        # Check for consistency
        if len(found_styles) > 1:
            analysis['potential_issues'].append({
                'type': 'mixed_styles',
                'description': f'Multiple citation styles detected: {", ".join(found_styles)}',
                'severity': 'warning'
            })
            analysis['suggestions'].append(
                "Use a consistent citation style throughout your document."
            )
        
        # Check for missing citations in paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraphs_without_citations = []
        
        for i, para in enumerate(paragraphs):
            # Skip short paragraphs
            if len(para.split()) < 20:
                continue
            
            # Check if paragraph contains citations
            has_citation = any(
                pattern[0] for pattern in [
                    (r'\([A-Za-z]+', 'author citation'),
                    (r'\[\d+\]', 'numbered citation'),
                    (r'\d{4}', 'year reference'),
                ] if re.search(pattern[0], para)
            )
            
            if not has_citation:
                paragraphs_without_citations.append({
                    'paragraph_number': i + 1,
                    'word_count': len(para.split()),
                    'preview': para[:100] + '...' if len(para) > 100 else para
                })
        
        if paragraphs_without_citations:
            analysis['potential_issues'].append({
                'type': 'missing_citations',
                'count': len(paragraphs_without_citations),
                'description': f'{len(paragraphs_without_citations)} substantial paragraph(s) without citations',
                'examples': paragraphs_without_citations[:3],
                'severity': 'info'
            })
            analysis['suggestions'].append(
                f"Consider adding citations to {len(paragraphs_without_citations)} paragraph(s) that make factual claims."
            )
        
        return analysis
    
    def format_reference_list(self, references: List[Dict], style: str = 'apa') -> List[str]:
        """
        Format a list of references
        
        Args:
            references: List of reference dictionaries
            style: Citation style
            
        Returns:
            List of formatted references
        """
        formatted_references = []
        
        for i, ref in enumerate(references):
            ref_type = ref.get('type', 'unknown')
            data = ref.get('data', {})
            
            # Generate reference
            formatted = self.generate_reference(ref_type, data, style)
            
            if formatted:
                # Add numbering if needed
                if style.lower() in ['ieee', 'numbered']:
                    formatted = f"[{i + 1}] {formatted}"
                
                formatted_references.append(formatted)
        
        return formatted_references
