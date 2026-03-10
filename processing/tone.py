"""
Tone Adjustment Module
Adjusts document tone based on mode (academic, professional, CV, personal)
"""

import re
from typing import Dict, List, Any
from enum import Enum

class ToneMode(Enum):
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    CV = "cv"
    PERSONAL = "personal"

class ToneAdjuster:
    def __init__(self):
        """Initialize tone adjustment rules for each mode"""
        self.tone_rules = self._initialize_tone_rules()
        
        # Word replacements for different tones
        self.word_replacements = {
            ToneMode.ACADEMIC: {
                'get': 'obtain',
                'buy': 'purchase',
                'start': 'commence',
                'end': 'conclude',
                'show': 'demonstrate',
                'tell': 'inform',
                'help': 'assist',
                'use': 'utilize',
                'make': 'construct',
                'think': 'contemplate',
                'good': 'beneficial',
                'bad': 'detrimental',
                'big': 'substantial',
                'small': 'minimal',
            },
            ToneMode.PROFESSIONAL: {
                'get': 'acquire',
                'buy': 'procure',
                'start': 'initiate',
                'end': 'finalize',
                'show': 'present',
                'tell': 'advise',
                'help': 'support',
                'use': 'employ',
                'make': 'produce',
                'think': 'consider',
                'good': 'effective',
                'bad': 'ineffective',
                'big': 'significant',
                'small': 'modest',
            },
            ToneMode.CV: {
                'did': 'accomplished',
                'made': 'created',
                'helped': 'assisted',
                'worked on': 'contributed to',
                'responsible for': 'managed',
                'good at': 'skilled in',
                'know': 'proficient in',
                'like': 'passionate about',
                'want': 'aspire to',
            },
            ToneMode.PERSONAL: {
                'commence': 'start',
                'conclude': 'end',
                'demonstrate': 'show',
                'inform': 'tell',
                'assist': 'help',
                'utilize': 'use',
                'construct': 'make',
                'contemplate': 'think',
            }
        }
        
        # Sentence starters for different modes
        self.sentence_starters = {
            ToneMode.ACADEMIC: [
                "This study examines",
                "The research indicates",
                "Analysis reveals",
                "Evidence suggests",
                "Findings demonstrate",
            ],
            ToneMode.PROFESSIONAL: [
                "The report outlines",
                "Our analysis shows",
                "Based on the data",
                "We recommend",
                "The proposal includes",
            ],
            ToneMode.CV: [
                "Successfully implemented",
                "Effectively managed",
                "Significantly improved",
                "Collaborated on",
                "Led initiatives to",
            ]
        }
    
    def _initialize_tone_rules(self) -> Dict[ToneMode, List[tuple]]:
        """Initialize tone adjustment rules"""
        return {
            ToneMode.ACADEMIC: [
                (r'\bI\b', 'This study'),  # Avoid first person
                (r'\bwe\b', 'The research team'),
                (r'\byou\b', 'one'),
                (r'\bdon\'t\b', 'do not'),
                (r'\bcan\'t\b', 'cannot'),
                (r'\bwon\'t\b', 'will not'),
                (r'\bawesome\b', 'remarkable'),
                (r'\bcool\b', 'notable'),
                (r'\bgreat\b', 'significant'),
                (r'\breally\b', 'considerably'),
            ],
            ToneMode.PROFESSIONAL: [
                (r'\bawesome\b', 'impressive'),
                (r'\bcool\b', 'effective'),
                (r'\bgreat\b', 'excellent'),
                (r'\breally\b', 'highly'),
                (r'\bstuff\b', 'materials'),
                (r'\bthing\b', 'element'),
                (r'\bguy\b', 'colleague'),
                (r'\bkid\b', 'child'),
                (r'\bboss\b', 'supervisor'),
            ],
            ToneMode.CV: [
                (r'\bI did\b', ''),
                (r'\bMy job was\b', 'Responsible for'),
                (r'\bI was responsible for\b', 'Managed'),
                (r'\bI helped\b', 'Assisted with'),
                (r'\bI worked on\b', 'Contributed to'),
                (r'\bI made\b', 'Created'),
                (r'\bI know how to\b', 'Proficient in'),
                (r'\bgood at\b', 'skilled in'),
                (r'\blike to\b', 'passionate about'),
            ],
            ToneMode.PERSONAL: [
                (r'\bone\b', 'you'),
                (r'\bthe researcher\b', 'I'),
                (r'\bthe team\b', 'we'),
                (r'\bconsiderably\b', 'really'),
                (r'\bsignificant\b', 'great'),
                (r'\bremarkable\b', 'awesome'),
            ]
        }
    
    def adjust_tone(self, text: str, mode: str) -> Dict[str, Any]:
        """
        Adjust document tone based on specified mode
        """
        try:
            tone_mode = ToneMode(mode.lower())
        except ValueError:
            # Default to professional if invalid mode
            tone_mode = ToneMode.PROFESSIONAL
        
        original_text = text
        changes = []
        adjustment_count = 0
        
        # Apply tone-specific rules
        if tone_mode in self.tone_rules:
            for pattern, replacement in self.tone_rules[tone_mode]:
                def replace_func(match):
                    changes.append({
                        'type': 'tone',
                        'original': match.group(0),
                        'adjusted': replacement,
                        'mode': mode
                    })
                    return replacement
                
                text, count = re.subn(pattern, replace_func, text, flags=re.IGNORECASE)
                adjustment_count += count
        
        # Apply word replacements
        if tone_mode in self.word_replacements:
            for informal, formal in self.word_replacements[tone_mode].items():
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(informal) + r'\b'
                
                def replace_func(match):
                    changes.append({
                        'type': 'word_choice',
                        'original': match.group(0),
                        'adjusted': formal,
                        'mode': mode
                    })
                    return formal
                
                text, count = re.subn(pattern, replace_func, text, flags=re.IGNORECASE)
                adjustment_count += count
        
        # Adjust sentence structure based on mode
        if tone_mode in [ToneMode.ACADEMIC, ToneMode.PROFESSIONAL]:
            text = self._make_sentences_formal(text, tone_mode, changes)
            adjustment_count += len(changes) - adjustment_count
        
        # Remove contractions for formal modes
        if tone_mode in [ToneMode.ACADEMIC, ToneMode.PROFESSIONAL]:
            contraction_patterns = [
                (r"(\w+)n't\b", r"\1 not"),
                (r"'s\b", r" is"),
                (r"'re\b", r" are"),
                (r"'ll\b", r" will"),
                (r"'ve\b", r" have"),
                (r"'d\b", r" would"),
            ]
            
            for pattern, replacement in contraction_patterns:
                text, count = re.subn(pattern, replacement, text)
                adjustment_count += count
        
        # Ensure proper sentence capitalization
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            if sentence:
                # Capitalize first letter
                if sentence and sentence[0].islower():
                    sentence = sentence[0].upper() + sentence[1:]
                    adjustment_count += 1
                
                # Add appropriate starters for CV mode
                if tone_mode == ToneMode.CV and i == 0:
                    sentence = self._improve_cv_starter(sentence)
                
                formatted_sentences.append(sentence)
        
        text = ' '.join(formatted_sentences)
        
        return {
            "processed_text": text,
            "adjustment_count": adjustment_count,
            "changes": changes,
            "mode": mode,
            "original_text": original_text
        }
    
    def _make_sentences_formal(self, text: str, mode: ToneMode, changes: List) -> str:
        """Make sentences more formal for academic/professional writing"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formal_sentences = []
        
        for sentence in sentences:
            original_sentence = sentence
            
            # Remove informal starters
            informal_starters = [
                "So,",
                "Well,",
                "Anyway,",
                "Like,",
                "You know,",
                "I mean,",
            ]
            
            for starter in informal_starters:
                if sentence.startswith(starter):
                    sentence = sentence[len(starter):].lstrip()
                    changes.append({
                        'type': 'sentence_structure',
                        'original': original_sentence,
                        'adjusted': sentence,
                        'change': 'removed_informal_starter'
                    })
            
            # Avoid starting with conjunctions in formal writing
            conjunction_pattern = r'^(And|But|Or|So|Because)\s+'
            match = re.match(conjunction_pattern, sentence, re.IGNORECASE)
            if match:
                conjunction = match.group(1)
                sentence = re.sub(conjunction_pattern, '', sentence)
                # Capitalize new first letter
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:]
                
                changes.append({
                    'type': 'sentence_structure',
                    'original': original_sentence,
                    'adjusted': sentence,
                    'change': 'removed_initial_conjunction'
                })
            
            formal_sentences.append(sentence)
        
        return ' '.join(formal_sentences)
    
    def _improve_cv_starter(self, sentence: str) -> str:
        """Improve sentence starters for CVs"""
        # Check if sentence starts with weak verbs
        weak_starts = [
            r'^I\s+',
            r'^My\s+',
            r'^Responsible\s+for',
            r'^Duties\s+included',
        ]
        
        for pattern in weak_starts:
            if re.match(pattern, sentence, re.IGNORECASE):
                # Convert to action-oriented start
                action_verbs = [
                    "Managed",
                    "Implemented",
                    "Developed",
                    "Created",
                    "Led",
                    "Improved",
                    "Increased",
                    "Reduced",
                    "Optimized",
                    "Streamlined",
                ]
                
                # Simple transformation - in production, use NLP for better results
                sentence = re.sub(pattern, action_verbs[0] + ' ', sentence, flags=re.IGNORECASE)
                break
        
        return sentence
    
    def analyze_tone(self, text: str) -> Dict[str, float]:
        """
        Analyze the tone of the text
        Returns scores for formality, objectivity, etc.
        """
        doc = text.lower()
        
        # Calculate formality score
        formal_words = [
            'therefore', 'however', 'moreover', 'furthermore',
            'consequently', 'accordingly', 'nevertheless',
            'notwithstanding', 'subsequently'
        ]
        
        informal_words = [
            'awesome', 'cool', 'great', 'really', 'stuff',
            'thing', 'guy', 'kid', 'boss', 'like', 'totally'
        ]
        
        total_words = len(text.split())
        if total_words == 0:
            return {
                "formality": 0.5,
                "objectivity": 0.5,
                "confidence": 0.5
            }
        
        # Count formal and informal words
        formal_count = sum(1 for word in formal_words if word in doc)
        informal_count = sum(1 for word in informal_words if word in doc)
        
        # Calculate scores
        formality_score = formal_count / max(total_words, 1)
        informality_score = informal_count / max(total_words, 1)
        
        # Normalize formality score
        normalized_formality = 0.5 + (formality_score - informality_score) * 10
        normalized_formality = max(0, min(1, normalized_formality))
        
        # Calculate objectivity (avoid first person)
        personal_pronouns = ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours']
        personal_count = sum(1 for pronoun in personal_pronouns if pronoun in doc)
        objectivity_score = 1 - (personal_count / max(total_words, 1) * 5)
        objectivity_score = max(0, min(1, objectivity_score))
        
        # Calculate confidence score (based on strong language)
        weak_phrases = [
            'i think', 'i believe', 'in my opinion',
            'maybe', 'perhaps', 'might', 'could',
            'sort of', 'kind of', 'a bit'
        ]
        
        strong_phrases = [
            'clearly', 'evidently', 'undoubtedly',
            'definitely', 'certainly', 'obviously'
        ]
        
        weak_count = sum(1 for phrase in weak_phrases if phrase in doc)
        strong_count = sum(1 for phrase in strong_phrases if phrase in doc)
        
        confidence_score = 0.5 + (strong_count - weak_count) / max(total_words, 1) * 10
        confidence_score = max(0, min(1, confidence_score))
        
        return {
            "formality": round(normalized_formality, 3),
            "objectivity": round(objectivity_score, 3),
            "confidence": round(confidence_score, 3),
            "formal_word_count": formal_count,
            "informal_word_count": informal_count,
            "personal_pronoun_count": personal_count
        }
