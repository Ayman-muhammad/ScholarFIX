"""
Grammar and Spelling Processing Module
"""

import re
import spacy
import language_tool_python
from typing import Dict, List, Any, Tuple

class GrammarProcessor:
    def __init__(self):
        """Initialize grammar processor"""
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model not found, use basic tokenizer
            self.nlp = None
        
        # Initialize LanguageTool
        self.language_tool = language_tool_python.LanguageTool('en-US')
        
        # Custom grammar rules
        self.grammar_rules = self._initialize_grammar_rules()
        
    def _initialize_grammar_rules(self) -> Dict[str, List[Tuple]]:
        """Initialize custom grammar rules"""
        return {
            'contractions': [
                (r'\bdo not\b', "don't"),
                (r'\bdoes not\b', "doesn't"),
                (r'\bdid not\b', "didn't"),
                (r'\bhave not\b', "haven't"),
                (r'\bhas not\b', "hasn't"),
                (r'\bhad not\b', "hadn't"),
                (r'\bcannot\b', "can't"),
                (r'\bcould not\b', "couldn't"),
                (r'\bshould not\b', "shouldn't"),
                (r'\bwill not\b', "won't"),
                (r'\bwould not\b', "wouldn't"),
            ],
            'common_errors': [
                (r'\btheir\s+are\b', 'there are'),
                (r'\byour\s+welcome\b', "you're welcome"),
                (r'\balot\b', 'a lot'),
                (r'\bcould of\b', 'could have'),
                (r'\bshould of\b', 'should have'),
                (r'\bwould of\b', 'would have'),
                (r'\bloose\b', 'lose'),
                (r'\beffect\b', 'affect'),  # Context-dependent
                (r'\bprinciple\b', 'principal'),  # Context-dependent
            ]
        }
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text for grammar and spelling corrections
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary with processed text and metrics
        """
        if not text or not isinstance(text, str):
            return {
                'processed_text': text,
                'fix_count': 0,
                'changes': [],
                'original_text': text
            }
        
        original_text = text
        changes = []
        fix_count = 0
        
        # Step 1: LanguageTool corrections
        try:
            matches = self.language_tool.check(text)
            for match in matches:
                if match.replacements:
                    replacement = match.replacements[0]
                    start_pos = match.offset
                    end_pos = match.offset + match.errorLength
                    
                    # Store change
                    changes.append({
                        'type': 'grammar',
                        'original': text[start_pos:end_pos],
                        'corrected': replacement,
                        'rule': match.ruleId,
                        'message': match.message
                    })
                    
                    # Apply replacement
                    text = text[:start_pos] + replacement + text[end_pos:]
                    fix_count += 1
        except Exception as e:
            # If LanguageTool fails, continue with other corrections
            pass
        
        # Step 2: Apply custom grammar rules
        for rule_type, rules in self.grammar_rules.items():
            for pattern, replacement in rules:
                def replace_func(match):
                    return replacement
                
                # Count replacements
                count = len(re.findall(pattern, text, re.IGNORECASE))
                if count > 0:
                    text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                    fix_count += count
        
        # Step 3: Fix sentence capitalization
        sentences = re.split(r'(?<=[.!?])\s+', text)
        corrected_sentences = []
        
        for sentence in sentences:
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
                fix_count += 1
            corrected_sentences.append(sentence)
        
        text = ' '.join(corrected_sentences)
        
        # Step 4: Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return {
            'processed_text': text,
            'fix_count': fix_count,
            'changes': changes,
            'original_text': original_text
        }
    
    def improve_clarity(self, text: str) -> Dict[str, Any]:
        """
        Improve text clarity by removing wordiness
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with improved text and metrics
        """
        if not text:
            return {
                'processed_text': text,
                'improvement_count': 0,
                'changes': [],
                'original_text': text
            }
        
        original_text = text
        changes = []
        improvement_count = 0
        
        # Wordiness patterns
        wordy_patterns = [
            (r'\bdue to the fact that\b', 'because'),
            (r'\bin order to\b', 'to'),
            (r'\bat this point in time\b', 'now'),
            (r'\bwith regard to\b', 'regarding'),
            (r'\bin the event that\b', 'if'),
            (r'\bfor the purpose of\b', 'for'),
            (r'\bas a matter of fact\b', 'in fact'),
            (r'\bit is important to note that\b', ''),
            (r'\bit should be pointed out that\b', ''),
            (r'\bwhat I mean to say is\b', ''),
            (r'\bvery\s+(\w+)\b', lambda m: self._strengthen_word(m.group(1))),
            (r'\breally\s+(\w+)\b', lambda m: self._strengthen_word(m.group(1))),
        ]
        
        for pattern, replacement in wordy_patterns:
            if callable(replacement):
                # Count matches before replacement
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    for match in matches:
                        original = match.group(0)
                        improved = replacement(match)
                        changes.append({
                            'type': 'clarity',
                            'original': original,
                            'improved': improved
                        })
                    
                    # Apply replacement
                    text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                    improvement_count += len(matches)
            else:
                # Count matches
                count = len(re.findall(pattern, text, re.IGNORECASE))
                if count > 0:
                    # Record changes
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        changes.append({
                            'type': 'clarity',
                            'original': match,
                            'improved': replacement
                        })
                    
                    # Apply replacement
                    text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                    improvement_count += count
        
        # Remove redundant phrases at sentence start
        sentences = re.split(r'(?<=[.!?])\s+', text)
        improved_sentences = []
        
        for sentence in sentences:
            # Remove "There is/are" when possible
            if re.match(r'^(There is|There are)\s+', sentence, re.IGNORECASE):
                # Try to rephrase
                words = sentence.split()
                if len(words) > 3:
                    # Simple rephrasing: "There are many people" -> "Many people exist"
                    pass
            
            improved_sentences.append(sentence)
        
        text = ' '.join(improved_sentences)
        
        return {
            'processed_text': text,
            'improvement_count': improvement_count,
            'changes': changes,
            'original_text': original_text
        }
    
    def _strengthen_word(self, word: str) -> str:
        """Replace weak words with stronger alternatives"""
        strengthening_map = {
            'good': 'excellent',
            'bad': 'poor',
            'big': 'substantial',
            'small': 'modest',
            'important': 'crucial',
            'interesting': 'compelling',
            'hard': 'challenging',
            'easy': 'straightforward',
            'many': 'numerous',
            'few': 'limited',
            'old': 'aged',
            'new': 'recent',
            'fast': 'rapid',
            'slow': 'gradual',
        }
        return strengthening_map.get(word.lower(), word)
    
    def check_readability(self, text: str) -> Dict[str, float]:
        """
        Calculate readability scores
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with readability metrics
        """
        if not text:
            return {
                'flesch_reading_ease': 0,
                'average_sentence_length': 0,
                'average_word_length': 0,
                'readability_level': 'Unknown'
            }
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return {
                'flesch_reading_ease': 0,
                'average_sentence_length': 0,
                'average_word_length': 0,
                'readability_level': 'Unknown'
            }
        
        # Calculate metrics
        num_sentences = len(sentences)
        num_words = len(words)
        num_syllables = sum(self._count_syllables(word) for word in words)
        
        # Average sentence length
        avg_sentence_length = num_words / num_sentences
        
        # Average word length (in characters)
        avg_word_length = sum(len(word) for word in words) / num_words
        
        # Flesch Reading Ease
        # 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        flesch_score = 206.835 - (1.015 * (num_words / num_sentences)) - (84.6 * (num_syllables / num_words))
        
        # Determine readability level
        if flesch_score >= 90:
            level = "Very Easy"
        elif flesch_score >= 80:
            level = "Easy"
        elif flesch_score >= 70:
            level = "Fairly Easy"
        elif flesch_score >= 60:
            level = "Standard"
        elif flesch_score >= 50:
            level = "Fairly Difficult"
        elif flesch_score >= 30:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            'flesch_reading_ease': round(flesch_score, 2),
            'average_sentence_length': round(avg_sentence_length, 2),
            'average_word_length': round(avg_word_length, 2),
            'readability_level': level
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximate)"""
        word = word.lower()
        
        # Remove final 'e'
        if word.endswith('e'):
            word = word[:-1]
        
        # Count vowel groups
        vowels = 'aeiouy'
        count = 0
        prev_char_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_vowel:
                count += 1
            prev_char_vowel = is_vowel
        
        # Ensure at least one syllable
        return max(1, count)