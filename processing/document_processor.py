"""
Main Document Processing Orchestrator
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .grammar import GrammarProcessor
from .tone import ToneAdjuster
from .formatting import FormattingProcessor
from .citation import CitationProcessor

class DocumentProcessor:
    def __init__(self):
        """Initialize document processor with all sub-processors"""
        self.grammar_processor = GrammarProcessor()
        self.tone_adjuster = ToneAdjuster()
        self.formatting_processor = FormattingProcessor()
        self.citation_processor = CitationProcessor()
    
    def process_document(self, 
                        original_path: str = None,
                        text: str = None,
                        mode: str = 'academic',
                        options: Dict = None) -> Dict[str, Any]:
        """
        Process document with all available processors
        
        Args:
            original_path: Path to original document (optional)
            text: Document text (optional, takes precedence over path)
            mode: Document mode (academic, cv, professional, personal)
            options: Processing options dictionary
            
        Returns:
            Dictionary with processed text and comprehensive metrics
        """
        start_time = datetime.now()
        
        # Default options
        default_options = {
            'grammar': True,
            'clarity': True,
            'tone': True,
            'formatting': True,
            'citations': True,
            'citation_style': 'apa'
        }
        
        if options:
            default_options.update(options)
        options = default_options
        
        # Get text (simulated for now - in production, extract from file)
        if text is None:
            # In production, extract text from file based on original_path
            text = self._extract_text_from_file(original_path) if original_path else ""
        
        if not text:
            return {
                'success': False,
                'error': 'No text provided or could not extract text',
                'processed_text': '',
                'metrics': {}
            }
        
        original_text = text
        all_changes = {}
        metrics = {
            'original_word_count': len(text.split()),
            'processing_time': 0,
            'steps_completed': []
        }
        
        # Step 1: Grammar and Clarity
        if options.get('grammar', True):
            grammar_result = self.grammar_processor.process(text)
            text = grammar_result['processed_text']
            all_changes['grammar'] = grammar_result.get('changes', [])
            metrics['grammar_fixes'] = grammar_result.get('fix_count', 0)
            metrics['steps_completed'].append('grammar')
            
            # Clarity improvement
            if options.get('clarity', True):
                clarity_result = self.grammar_processor.improve_clarity(text)
                text = clarity_result['processed_text']
                all_changes['clarity'] = clarity_result.get('changes', [])
                metrics['clarity_improvements'] = clarity_result.get('improvement_count', 0)
                metrics['steps_completed'].append('clarity')
        
        # Step 2: Tone Adjustment
        if options.get('tone', True):
            tone_result = self.tone_adjuster.adjust_tone(text, mode)
            text = tone_result['processed_text']
            all_changes['tone'] = tone_result.get('changes', [])
            metrics['tone_adjustments'] = tone_result.get('adjustment_count', 0)
            metrics['steps_completed'].append('tone')
            
            # Tone analysis
            tone_analysis = self.tone_adjuster.analyze_tone(text)
            metrics['tone_analysis'] = tone_analysis
        
        # Step 3: Formatting
        if options.get('formatting', True):
            formatting_result = self.formatting_processor.apply_formatting(text, mode)
            text = formatting_result['processed_text']
            all_changes['formatting'] = formatting_result.get('changes', [])
            metrics['formatting_changes'] = formatting_result.get('formatting_changes', 0)
            metrics['steps_completed'].append('formatting')
            
            # Formatting analysis
            formatting_analysis = self.formatting_processor.generate_formatting_report(text, mode)
            metrics['formatting_analysis'] = formatting_analysis
        
        # Step 4: Citations (for academic documents)
        if options.get('citations', True) and mode == 'academic':
            citation_style = options.get('citation_style', 'apa')
            citation_result = self.citation_processor.process_citations(text, citation_style)
            text = citation_result['processed_text']
            all_changes['citations'] = citation_result.get('changes', [])
            metrics['citation_fixes'] = citation_result.get('citation_count', 0)
            metrics['steps_completed'].append('citations')
            
            # Citation analysis
            citation_analysis = self.citation_processor.check_citation_consistency(text)
            metrics['citation_analysis'] = citation_analysis
        
        # Step 5: Final cleanup
        text = self._final_cleanup(text)
        
        # Calculate final metrics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        metrics.update({
            'processed_word_count': len(text.split()),
            'processing_time': round(processing_time, 2),
            'total_changes': sum([
                metrics.get('grammar_fixes', 0),
                metrics.get('clarity_improvements', 0),
                metrics.get('tone_adjustments', 0),
                metrics.get('formatting_changes', 0),
                metrics.get('citation_fixes', 0)
            ]),
            'improvement_percentage': self._calculate_improvement_percentage(original_text, text)
        })
        
        # Readability analysis
        readability = self.grammar_processor.check_readability(text)
        metrics['readability'] = readability
        
        return {
            'success': True,
            'processed_text': text,
            'original_text': original_text,
            'changes': all_changes,
            'metrics': metrics,
            'mode': mode,
            'options_used': options
        }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from document file
        
        Note: This is a simplified version. In production, implement proper
        extraction for DOCX, PDF, etc.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text
        """
        # This is a placeholder implementation
        # In production, use libraries like python-docx, PyPDF2, etc.
        
        try:
            # Simple text file reading
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # For now, return placeholder text
            # In production, implement proper extraction
            return "This is a placeholder for extracted document text. " \
                   "In production, implement proper extraction from DOCX/PDF files."
            
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _final_cleanup(self, text: str) -> str:
        """Perform final cleanup on processed text"""
        if not text:
            return text
        
        # Remove extra blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing spaces
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        text = '\n'.join(cleaned_lines)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _calculate_improvement_percentage(self, original: str, processed: str) -> float:
        """Calculate improvement percentage (simplified)"""
        if not original or not processed:
            return 0.0
        
        # This is a simplified calculation
        # In production, use more sophisticated metrics
        
        original_words = original.split()
        processed_words = processed.split()
        
        if not original_words:
            return 0.0
        
        # Calculate average word length difference
        avg_original = sum(len(w) for w in original_words) / len(original_words)
        avg_processed = sum(len(w) for w in processed_words) / len(processed_words)
        
        # Calculate sentence length (words per sentence)
        original_sentences = re.split(r'[.!?]+', original)
        processed_sentences = re.split(r'[.!?]+', processed)
        
        original_sentences = [s.strip() for s in original_sentences if s.strip()]
        processed_sentences = [s.strip() for s in processed_sentences if s.strip()]
        
        if not original_sentences:
            return 0.0
        
        avg_sent_original = len(original_words) / len(original_sentences)
        avg_sent_processed = len(processed_words) / len(processed_sentences)
        
        # Simplified improvement score
        # In production, use more sophisticated metrics
        word_improvement = min(1.0, abs(avg_processed - 5) / 5)  # Target 5 chars per word
        sentence_improvement = min(1.0, abs(avg_sent_processed - 20) / 20)  # Target 20 words per sentence
        
        improvement = (word_improvement + sentence_improvement) / 2 * 100
        
        return round(improvement, 1)
    
    def generate_report(self, processing_result: Dict) -> Dict[str, Any]:
        """
        Generate a comprehensive processing report
        
        Args:
            processing_result: Result from process_document()
            
        Returns:
            Comprehensive report dictionary
        """
        if not processing_result.get('success', False):
            return {
                'success': False,
                'error': processing_result.get('error', 'Unknown error')
            }
        
        metrics = processing_result.get('metrics', {})
        changes = processing_result.get('changes', {})
        
        report = {
            'summary': {
                'status': 'success',
                'mode': processing_result.get('mode', 'unknown'),
                'total_changes': metrics.get('total_changes', 0),
                'processing_time': metrics.get('processing_time', 0),
                'improvement_percentage': metrics.get('improvement_percentage', 0),
                'word_count_change': metrics.get('processed_word_count', 0) - metrics.get('original_word_count', 0)
            },
            'detailed_metrics': {
                'grammar': {
                    'fixes': metrics.get('grammar_fixes', 0),
                    'changes_count': len(changes.get('grammar', []))
                },
                'clarity': {
                    'improvements': metrics.get('clarity_improvements', 0),
                    'changes_count': len(changes.get('clarity', []))
                },
                'tone': {
                    'adjustments': metrics.get('tone_adjustments', 0),
                    'analysis': metrics.get('tone_analysis', {}),
                    'changes_count': len(changes.get('tone', []))
                },
                'formatting': {
                    'changes': metrics.get('formatting_changes', 0),
                    'analysis': metrics.get('formatting_analysis', {}),
                    'changes_count': len(changes.get('formatting', []))
                },
                'citations': {
                    'fixes': metrics.get('citation_fixes', 0),
                    'analysis': metrics.get('citation_analysis', {}),
                    'changes_count': len(changes.get('citations', []))
                }
            },
            'readability': metrics.get('readability', {}),
            'recommendations': self._generate_recommendations(metrics, changes)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict, changes: Dict) -> List[str]:
        """Generate recommendations based on processing results"""
        recommendations = []
        
        # Grammar recommendations
        grammar_fixes = metrics.get('grammar_fixes', 0)
        if grammar_fixes > 10:
            recommendations.append(
                f"Your document had {grammar_fixes} grammar issues. Consider using grammar "
                "checking tools regularly."
            )
        
        # Clarity recommendations
        clarity_improvements = metrics.get('clarity_improvements', 0)
        if clarity_improvements > 5:
            recommendations.append(
                f"We made {clarity_improvements} clarity improvements. Try to avoid wordy "
                "phrases and be more direct in your writing."
            )
        
        # Tone recommendations
        tone_analysis = metrics.get('tone_analysis', {})
        formality = tone_analysis.get('formality', 0.5)
        
        if formality < 0.3:
            recommendations.append(
                "Your writing tone is quite informal. For professional or academic documents, "
                "consider using more formal language."
            )
        elif formality > 0.8:
            recommendations.append(
                "Your writing is very formal. This is excellent for academic papers, "
                "but might be too formal for business emails or personal documents."
            )
        
        # Readability recommendations
        readability = metrics.get('readability', {})
        readability_level = readability.get('readability_level', 'Standard')
        
        if readability_level in ['Difficult', 'Very Difficult']:
            recommendations.append(
                f"Your document has a '{readability_level}' readability level. "
                "Consider using shorter sentences and simpler words for better comprehension."
            )
        
        # Citation recommendations (for academic)
        citation_analysis = metrics.get('citation_analysis', {})
        if citation_analysis.get('potential_issues'):
            for issue in citation_analysis['potential_issues'][:2]:
                recommendations.append(issue.get('description', ''))
        
        # Formatting recommendations
        formatting_analysis = metrics.get('formatting_analysis', {})
        if formatting_analysis.get('issues_found'):
            issues = formatting_analysis['issues_found']
            if issues:
                recommendations.append(
                    f"We found {len(issues)} formatting issue(s). Check the detailed report "
                    "for specific improvements."
                )
        
        return recommendations[:5]  # Return top 5 recommendations