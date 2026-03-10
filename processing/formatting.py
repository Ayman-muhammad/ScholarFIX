"""
Document Formatting Processor
"""

import re
from typing import Dict, List, Any
from enum import Enum

class FormattingMode(Enum):
    """Document formatting modes"""
    ACADEMIC = "academic"
    CV = "cv"
    PROFESSIONAL = "professional"
    PERSONAL = "personal"

class FormattingProcessor:
    def __init__(self):
        """Initialize formatting processor"""
        self.formatting_rules = self._initialize_formatting_rules()
        
    def _initialize_formatting_rules(self) -> Dict[FormattingMode, Dict[str, Any]]:
        """Initialize formatting rules for each mode"""
        return {
            FormattingMode.ACADEMIC: {
                'font_family': 'Times New Roman',
                'font_size': 12,
                'line_spacing': 2.0,
                'margins': {'top': 1, 'right': 1, 'bottom': 1, 'left': 1.5},
                'paragraph_spacing': '12pt',
                'header_levels': 3,
                'justification': 'left',
            },
            FormattingMode.CV: {
                'font_family': 'Arial',
                'font_size': 11,
                'line_spacing': 1.15,
                'margins': {'top': 0.5, 'right': 0.5, 'bottom': 0.5, 'left': 0.5},
                'paragraph_spacing': '6pt',
                'header_levels': 2,
                'justification': 'left',
                'section_order': ['contact', 'summary', 'experience', 'education', 'skills'],
            },
            FormattingMode.PROFESSIONAL: {
                'font_family': 'Calibri',
                'font_size': 11,
                'line_spacing': 1.5,
                'margins': {'top': 1, 'right': 1, 'bottom': 1, 'left': 1},
                'paragraph_spacing': '10pt',
                'header_levels': 3,
                'justification': 'justify',
            },
            FormattingMode.PERSONAL: {
                'font_family': 'Georgia',
                'font_size': 12,
                'line_spacing': 1.5,
                'margins': {'top': 1, 'right': 1, 'bottom': 1, 'left': 1},
                'paragraph_spacing': '12pt',
                'header_levels': 2,
                'justification': 'left',
            }
        }
    
    def apply_formatting(self, text: str, mode: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Apply formatting to text based on mode
        
        Args:
            text: Input text
            mode: Formatting mode (academic, cv, professional, personal)
            metadata: Optional document metadata
            
        Returns:
            Dictionary with formatted text and changes
        """
        try:
            formatting_mode = FormattingMode(mode.lower())
        except ValueError:
            formatting_mode = FormattingMode.ACADEMIC
        
        original_text = text
        changes = []
        formatting_changes = 0
        
        # Get formatting rules for mode
        rules = self.formatting_rules.get(formatting_mode, self.formatting_rules[FormattingMode.ACADEMIC])
        
        # Apply formatting based on mode
        if formatting_mode == FormattingMode.ACADEMIC:
            text, academic_changes = self._format_academic(text, rules)
            changes.extend(academic_changes)
            formatting_changes += len(academic_changes)
        
        elif formatting_mode == FormattingMode.CV:
            text, cv_changes = self._format_cv(text, rules)
            changes.extend(cv_changes)
            formatting_changes += len(cv_changes)
        
        elif formatting_mode == FormattingMode.PROFESSIONAL:
            text, professional_changes = self._format_professional(text, rules)
            changes.extend(professional_changes)
            formatting_changes += len(professional_changes)
        
        elif formatting_mode == FormattingMode.PERSONAL:
            text, personal_changes = self._format_personal(text, rules)
            changes.extend(personal_changes)
            formatting_changes += len(personal_changes)
        
        # Apply common formatting
        text, common_changes = self._apply_common_formatting(text, rules)
        changes.extend(common_changes)
        formatting_changes += len(common_changes)
        
        return {
            'processed_text': text,
            'formatting_changes': formatting_changes,
            'changes': changes,
            'mode': mode,
            'rules_applied': rules,
            'original_text': original_text
        }
    
    def _format_academic(self, text: str, rules: Dict) -> tuple:
        """Format text for academic documents"""
        changes = []
        
        # Ensure proper heading structure
        lines = text.split('\n')
        formatted_lines = []
        heading_level = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Detect headings (lines that might be headings)
            if self._is_potential_heading(line, i, lines):
                heading_level += 1
                if heading_level <= rules['header_levels']:
                    # Format as heading
                    formatted_line = f"\n{line.upper()}\n"
                    changes.append({
                        'type': 'heading',
                        'original': line,
                        'formatted': formatted_line.strip(),
                        'level': heading_level
                    })
                    formatted_lines.append(formatted_line)
                    continue
            
            formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        # Ensure proper paragraph spacing
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            if para.strip():
                # Remove extra spaces
                para = re.sub(r'\s+', ' ', para).strip()
                # Capitalize first letter
                if para and para[0].islower():
                    para = para[0].upper() + para[1:]
                    changes.append({
                        'type': 'capitalization',
                        'original': para[0],
                        'formatted': para[0].upper()
                    })
                formatted_paragraphs.append(para)
        
        text = '\n\n'.join(formatted_paragraphs)
        
        return text, changes
    
    def _format_cv(self, text: str, rules: Dict) -> tuple:
        """Format text for CV/resume"""
        changes = []
        
        # Identify and format CV sections
        lines = text.split('\n')
        formatted_lines = []
        
        section_keywords = {
            'contact': ['contact', 'address', 'phone', 'email', 'linkedin'],
            'summary': ['summary', 'objective', 'profile'],
            'experience': ['experience', 'work', 'employment', 'career'],
            'education': ['education', 'qualification', 'degree', 'university'],
            'skills': ['skills', 'competencies', 'expertise', 'technical'],
            'projects': ['projects', 'portfolio', 'achievements'],
            'certifications': ['certifications', 'certificates', 'licenses'],
            'languages': ['languages', 'language'],
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Check if line is a section header
            line_lower = line.lower()
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    if line_lower in keywords or f"{line_lower}:" in [f"{k}:" for k in keywords]:
                        current_section = section
                        # Format section header
                        formatted_line = f"\n{line.upper()}\n{'-' * len(line)}"
                        changes.append({
                            'type': 'cv_section',
                            'section': section,
                            'original': line,
                            'formatted': formatted_line
                        })
                        formatted_lines.append(formatted_line)
                        break
            else:
                # Format content based on section
                if current_section == 'experience' or current_section == 'education':
                    # Format as bullet points or timeline
                    if not line.startswith(('-', '•', '*', '→')):
                        line = f"• {line}"
                        changes.append({
                            'type': 'bullet_point',
                            'original': line[2:],
                            'formatted': line
                        })
                
                formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        # Ensure consistent date formatting
        date_patterns = [
            (r'(\d{4})\s*[-–]\s*(\d{4})', r'\1 – \2'),  # 2019-2020 -> 2019 – 2020
            (r'(\w+)\s+(\d{4})\s*[-–]\s*(\w+)\s+(\d{4})', r'\1 \2 – \3 \4'),  # Jan 2019-Dec 2020
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', r'\1/\2/\4'),  # 01-01-2020 -> 01/01/2020
        ]
        
        for pattern, replacement in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                text = re.sub(pattern, replacement, text)
                changes.extend([{
                    'type': 'date_format',
                    'original': match[0] if isinstance(match, tuple) else match,
                    'formatted': replacement
                } for match in matches])
        
        return text, changes
    
    def _format_professional(self, text: str, rules: Dict) -> tuple:
        """Format text for professional documents"""
        changes = []
        
        # Ensure proper paragraph structure
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                # Remove extra spaces
                para = re.sub(r'\s+', ' ', para).strip()
                
                # Ensure proper capitalization
                if para and para[0].islower():
                    para = para[0].upper() + para[1:]
                    changes.append({
                        'type': 'capitalization',
                        'position': f'paragraph_{i+1}',
                        'original': para[0],
                        'formatted': para[0].upper()
                    })
                
                formatted_paragraphs.append(para)
        
        text = '\n\n'.join(formatted_paragraphs)
        
        # Format bullet points
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not any(stripped.startswith(char) for char in ['#', '*', '-', '•', '→']):
                # Check if this looks like a list item
                if re.match(r'^\d+[\.\)]', stripped) or re.match(r'^[a-z][\.\)]', stripped.lower()):
                    # Already formatted as list
                    formatted_lines.append(line)
                elif len(stripped.split()) < 20 and not stripped.endswith(('.', ':', ';')):
                    # Might be a list item, add bullet
                    formatted_line = f"• {stripped}"
                    changes.append({
                        'type': 'bullet_point',
                        'original': stripped,
                        'formatted': formatted_line
                    })
                    formatted_lines.append(formatted_line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        return text, changes
    
    def _format_personal(self, text: str, rules: Dict) -> tuple:
        """Format text for personal documents"""
        changes = []
        
        # Ensure proper letter formatting if detected
        if text.lower().startswith(('dear', 'to whom it may concern')):
            lines = text.split('\n')
            formatted_lines = []
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Format salutation
                if i == 0 and stripped.lower().startswith('dear'):
                    formatted_line = stripped.title()
                    if formatted_line != stripped:
                        changes.append({
                            'type': 'salutation',
                            'original': stripped,
                            'formatted': formatted_line
                        })
                    formatted_lines.append(formatted_line)
                
                # Format closing
                elif stripped.lower().startswith(('sincerely', 'best regards', 'kind regards', 'yours truly')):
                    formatted_line = f"\n{stripped.title()},"
                    if formatted_line.strip() != stripped:
                        changes.append({
                            'type': 'closing',
                            'original': stripped,
                            'formatted': formatted_line.strip()
                        })
                    formatted_lines.append(formatted_line)
                
                else:
                    formatted_lines.append(line)
            
            text = '\n'.join(formatted_lines)
        
        # Ensure paragraph spacing
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text, changes
    
    def _apply_common_formatting(self, text: str, rules: Dict) -> tuple:
        """Apply common formatting rules"""
        changes = []
        
        # Remove multiple spaces
        original = text
        text = re.sub(r' {2,}', ' ', text)
        if text != original:
            changes.append({
                'type': 'spacing',
                'issue': 'multiple_spaces',
                'formatted': 'single_spaces'
            })
        
        # Ensure proper line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing spaces
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        text = '\n'.join(cleaned_lines)
        
        # Ensure text ends with proper punctuation if it's a sentence
        if text and text[-1] not in ['.', '!', '?', ':']:
            # Check if last line looks like a sentence
            last_line = text.split('\n')[-1].strip()
            if last_line and len(last_line.split()) > 3:
                text += '.'
                changes.append({
                    'type': 'punctuation',
                    'issue': 'missing_ending_punctuation',
                    'formatted': 'added_period'
                })
        
        return text, changes
    
    def _is_potential_heading(self, line: str, index: int, all_lines: List[str]) -> bool:
        """Check if a line is likely a heading"""
        if not line:
            return False
        
        # Check length (headings are usually short)
        if len(line.split()) > 10:
            return False
        
        # Check if line ends without punctuation (common for headings)
        if line and line[-1] in ['.', ',', ';', ':']:
            return False
        
        # Check if next line is empty or content (headings often followed by content)
        if index + 1 < len(all_lines):
            next_line = all_lines[index + 1].strip()
            if not next_line:
                return True
            if len(next_line.split()) > 5:
                return True
        
        # Check common heading patterns
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]{1,50}$',  # Title case, reasonable length
            r'^\d+\.\s+',  # Numbered heading: "1. Introduction"
            r'^[IVXLCDM]+\.\s+',  # Roman numerals
            r'^[A-Z][A-Za-z\s]*:$',  # Ending with colon
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def generate_formatting_report(self, text: str, mode: str) -> Dict[str, Any]:
        """
        Generate formatting analysis report
        
        Args:
            text: Input text
            mode: Document mode
            
        Returns:
            Dictionary with formatting analysis
        """
        try:
            formatting_mode = FormattingMode(mode.lower())
        except ValueError:
            formatting_mode = FormattingMode.ACADEMIC
        
        rules = self.formatting_rules.get(formatting_mode, self.formatting_rules[FormattingMode.ACADEMIC])
        
        analysis = {
            'mode': mode,
            'expected_rules': rules,
            'issues_found': [],
            'suggestions': []
        }
        
        # Analyze text
        lines = text.split('\n')
        
        # Check for long lines
        long_lines = []
        for i, line in enumerate(lines):
            if len(line) > 100:  # Assuming 100 chars is too long for a line
                long_lines.append({
                    'line_number': i + 1,
                    'length': len(line),
                    'content': line[:50] + '...' if len(line) > 50 else line
                })
        
        if long_lines:
            analysis['issues_found'].append({
                'type': 'long_lines',
                'count': len(long_lines),
                'examples': long_lines[:3]
            })
            analysis['suggestions'].append(
                f"Consider breaking {len(long_lines)} long line(s) into shorter ones for better readability."
            )
        
        # Check paragraph length
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        long_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            word_count = len(para.split())
            if word_count > 200:  # Long paragraph
                long_paragraphs.append({
                    'paragraph_number': i + 1,
                    'word_count': word_count
                })
        
        if long_paragraphs:
            analysis['issues_found'].append({
                'type': 'long_paragraphs',
                'count': len(long_paragraphs),
                'examples': long_paragraphs[:3]
            })
            analysis['suggestions'].append(
                f"Consider splitting {len(long_paragraphs)} long paragraph(s) for better readability."
            )
        
        # Check heading structure
        heading_candidates = []
        for i, line in enumerate(lines):
            if self._is_potential_heading(line.strip(), i, lines):
                heading_candidates.append({
                    'line_number': i + 1,
                    'content': line[:50] + '...' if len(line) > 50 else line
                })
        
        analysis['headings_found'] = len(heading_candidates)
        analysis['heading_examples'] = heading_candidates[:5]
        
        # Check consistency
        if formatting_mode == FormattingMode.CV:
            # Check for common CV sections
            section_keywords = ['experience', 'education', 'skills', 'summary', 'contact']
            found_sections = []
            for keyword in section_keywords:
                if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                    found_sections.append(keyword)
            
            analysis['cv_sections_found'] = found_sections
            if len(found_sections) < 3:
                analysis['suggestions'].append(
                    "Consider adding more sections to your CV (e.g., Experience, Education, Skills)."
                )
        
        return analysis
