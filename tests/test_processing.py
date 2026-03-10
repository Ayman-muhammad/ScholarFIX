"""
Unit tests for ScholarFix processing modules
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processing.grammar import GrammarProcessor
from processing.tone import ToneAdjuster
from processing.formatting import FormattingProcessor
from processing.citation import CitationProcessor
from processing.document_processor import DocumentProcessor

class TestGrammarProcessor(unittest.TestCase):
    """Test grammar processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = GrammarProcessor()
    
    def test_process_basic_grammar(self):
        """Test basic grammar correction"""
        text = "he go to school everyday. its good."
        result = self.processor.process(text)
        
        self.assertIn('processed_text', result)
        self.assertIn('fix_count', result)
        self.assertGreater(result['fix_count'], 0)
        
        # Should fix basic grammar issues
        processed = result['processed_text']
        self.assertNotIn('its good', processed.lower())
    
    def test_improve_clarity(self):
        """Test clarity improvement"""
        text = "Due to the fact that it was raining, we decided to not go outside."
        result = self.processor.improve_clarity(text)
        
        self.assertIn('processed_text', result)
        self.assertIn('improvement_count', result)
        
        # Should remove wordiness
        processed = result['processed_text'].lower()
        self.assertNotIn('due to the fact that', processed)
    
    def test_check_readability(self):
        """Test readability scoring"""
        text = "This is a simple sentence. It has good readability."
        result = self.processor.check_readability(text)
        
        self.assertIn('flesch_reading_ease', result)
        self.assertIn('average_sentence_length', result)
        self.assertIn('readability_level', result)
        
        # Simple text should have good readability
        self.assertGreater(result['flesch_reading_ease'], 60)
    
    def test_empty_text(self):
        """Test handling of empty text"""
        text = ""
        result = self.processor.process(text)
        
        self.assertEqual(result['processed_text'], "")
        self.assertEqual(result['fix_count'], 0)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text = "This text has special chars: @#$%^&*()"
        result = self.processor.process(text)
        
        self.assertIn('processed_text', result)
        self.assertIn('@#$%^&*()', result['processed_text'])


class TestToneAdjuster(unittest.TestCase):
    """Test tone adjustment functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.adjuster = ToneAdjuster()
    
    def test_academic_tone(self):
        """Test academic tone adjustment"""
        text = "I think this is a really awesome study. It's got cool results."
        result = self.adjuster.adjust_tone(text, 'academic')
        
        self.assertIn('processed_text', result)
        self.assertIn('adjustment_count', result)
        
        # Should make text more formal
        processed = result['processed_text'].lower()
        self.assertNotIn('awesome', processed)
        self.assertNotIn('cool', processed)
    
    def test_professional_tone(self):
        """Test professional tone adjustment"""
        text = "Hey guys, this stuff is great! Let's do it."
        result = self.adjuster.adjust_tone(text, 'professional')
        
        self.assertIn('processed_text', result)
        
        # Should remove informal language
        processed = result['processed_text'].lower()
        self.assertNotIn('hey guys', processed)
        self.assertNotIn('stuff', processed)
    
    def test_cv_tone(self):
        """Test CV tone adjustment"""
        text = "I did coding and made apps. I helped with the project."
        result = self.adjuster.adjust_tone(text, 'cv')
        
        self.assertIn('processed_text', result)
        
        # Should make more action-oriented
        processed = result['processed_text']
        self.assertNotIn('I did', processed)
    
    def test_personal_tone(self):
        """Test personal tone adjustment"""
        text = "One must consider the implications of such actions."
        result = self.adjuster.adjust_tone(text, 'personal')
        
        self.assertIn('processed_text', result)
        
        # Should make more personal
        processed = result['processed_text'].lower()
        self.assertNotIn('one must', processed)
    
    def test_analyze_tone(self):
        """Test tone analysis"""
        text = "This is a formal document. The researcher conducted experiments."
        result = self.adjuster.analyze_tone(text)
        
        self.assertIn('formality', result)
        self.assertIn('objectivity', result)
        self.assertIn('confidence', result)
        
        # Formal text should have high formality
        self.assertGreater(result['formality'], 0.5)


class TestFormattingProcessor(unittest.TestCase):
    """Test document formatting functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = FormattingProcessor()
    
    def test_academic_formatting(self):
        """Test academic document formatting"""
        text = """introduction\nThis is the introduction.\n\nmethods\nWe used methods."""
        result = self.processor.apply_formatting(text, 'academic')
        
        self.assertIn('processed_text', result)
        self.assertIn('formatting_changes', result)
        
        # Should format headings
        processed = result['processed_text']
        self.assertIn('INTRODUCTION', processed)
    
    def test_cv_formatting(self):
        """Test CV formatting"""
        text = """experience\nWorked at company\neducation\nStudied at university"""
        result = self.processor.apply_formatting(text, 'cv')
        
        self.assertIn('processed_text', result)
        
        # Should format sections
        processed = result['processed_text']
        self.assertIn('EXPERIENCE', processed)
        self.assertIn('EDUCATION', processed)
    
    def test_generate_formatting_report(self):
        """Test formatting report generation"""
        text = "This is a test document.\n\nIt has multiple paragraphs."
        result = self.processor.generate_formatting_report(text, 'academic')
        
        self.assertIn('mode', result)
        self.assertIn('issues_found', result)
        self.assertIn('suggestions', result)
    
    def test_common_formatting(self):
        """Test common formatting rules"""
        text = "This  has   multiple   spaces.  "
        result = self.processor.apply_formatting(text, 'professional')
        
        self.assertIn('processed_text', result)
        
        # Should remove multiple spaces
        processed = result['processed_text']
        self.assertNotIn('  ', processed)


class TestCitationProcessor(unittest.TestCase):
    """Test citation processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = CitationProcessor()
    
    def test_apa_citations(self):
        """Test APA citation formatting"""
        text = "According to (Smith, 2020), this is important."
        result = self.processor.process_citations(text, 'apa')
        
        self.assertIn('processed_text', result)
        self.assertIn('citation_count', result)
        
        # Should properly format APA citation
        self.assertIn('(Smith, 2020)', result['processed_text'])
    
    def test_mla_citations(self):
        """Test MLA citation formatting"""
        text = "This is discussed (Smith 45)."
        result = self.processor.process_citations(text, 'mla')
        
        self.assertIn('processed_text', result)
        
        # Should properly format MLA citation
        self.assertIn('(Smith 45)', result['processed_text'])
    
    def test_extract_citations(self):
        """Test citation extraction"""
        text = "Some text (Smith, 2020) and more [1]."
        result = self.processor.extract_citations(text)
        
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)
    
    def test_check_citation_consistency(self):
        """Test citation consistency check"""
        text = "First citation (Smith, 2020). Second citation [1]."
        result = self.processor.check_citation_consistency(text)
        
        self.assertIn('total_citations', result)
        self.assertIn('citation_styles_found', result)
        self.assertIn('potential_issues', result)
    
    def test_generate_reference(self):
        """Test reference generation"""
        data = {
            'author_last': 'Smith',
            'author_first_initial': 'J',
            'year': '2020',
            'title': 'Test Book',
            'publisher': 'Test Publisher'
        }
        result = self.processor.generate_reference('book', data, 'apa')
        
        self.assertIsInstance(result, str)
        self.assertIn('Smith', result)
        self.assertIn('2020', result)


class TestDocumentProcessor(unittest.TestCase):
    """Test main document processor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    def test_process_document_basic(self):
        """Test basic document processing"""
        text = "This is a test document. It has some issues."
        result = self.processor.process_document(text=text, mode='academic')
        
        self.assertIn('success', result)
        self.assertIn('processed_text', result)
        self.assertIn('metrics', result)
        self.assertTrue(result['success'])
    
    def test_process_document_with_options(self):
        """Test document processing with specific options"""
        text = "Test document for processing."
        options = {
            'grammar': True,
            'clarity': True,
            'tone': True,
            'formatting': True,
            'citations': False
        }
        
        result = self.processor.process_document(
            text=text,
            mode='professional',
            options=options
        )
        
        self.assertIn('success', result)
        self.assertIn('processed_text', result)
        self.assertIn('options_used', result)
        self.assertTrue(result['success'])
    
    def test_generate_report(self):
        """Test report generation"""
        # First process a document
        text = "Test document."
        processing_result = self.processor.process_document(text=text, mode='academic')
        
        # Generate report
        report = self.processor.generate_report(processing_result)
        
        self.assertIn('summary', report)
        self.assertIn('detailed_metrics', report)
        self.assertIn('recommendations', report)
    
    def test_empty_document(self):
        """Test processing empty document"""
        result = self.processor.process_document(text="")
        
        self.assertIn('success', result)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_final_cleanup(self):
        """Test final cleanup method"""
        text = "  This  has   extra   spaces.  \n\n\nAnd extra lines.  "
        cleaned = self.processor._final_cleanup(text)
        
        # Should remove extra spaces and lines
        self.assertNotIn('  ', cleaned)
        self.assertNotIn('\n\n\n', cleaned)


class TestIntegration(unittest.TestCase):
    """Test integration between modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    def test_full_pipeline(self):
        """Test full processing pipeline"""
        text = """
        introduction
        This paper look at how social media effect young people.
        
        methods
        We did surveys with 100 students.
        
        results
        The results show that social media can have negative effects.
        """
        
        result = self.processor.process_document(
            text=text,
            mode='academic',
            options={
                'grammar': True,
                'clarity': True,
                'tone': True,
                'formatting': True,
                'citation_style': 'apa'
            }
        )
        
        self.assertTrue(result['success'])
        self.assertIn('processed_text', result)
        self.assertIn('changes', result)
        self.assertIn('metrics', result)
        
        # Check metrics
        metrics = result['metrics']
        self.assertIn('processing_time', metrics)
        self.assertIn('total_changes', metrics)
        self.assertIn('steps_completed', metrics)
    
    def test_different_modes(self):
        """Test processing with different modes"""
        text = "I worked on a project. I made good results."
        
        modes = ['academic', 'cv', 'professional', 'personal']
        
        for mode in modes:
            result = self.processor.process_document(text=text, mode=mode)
            self.assertTrue(result['success'])
            self.assertEqual(result['mode'], mode)


class TestPerformance(unittest.TestCase):
    """Test performance aspects"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    def test_large_document(self):
        """Test processing large document"""
        # Create a large document
        text = "Sentence. " * 1000
        
        result = self.processor.process_document(text=text, mode='academic')
        
        self.assertTrue(result['success'])
        self.assertLess(result['metrics']['processing_time'], 10)  # Should complete within 10 seconds
    
    def test_special_characters_handling(self):
        """Test handling of special characters"""
        text = """
        Normal text with special chars: @#$%^&*()
        Unicode: αβγδε ζηθ ικλμν
        Emoji: 😀 👍 🎉
        Math: E = mc²
        HTML: <div>test</div>
        """
        
        result = self.processor.process_document(text=text, mode='professional')
        
        self.assertTrue(result['success'])
        # Should preserve most special characters
        self.assertIn('@#$%^&*()', result['processed_text'])


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor()
    
    def test_invalid_mode(self):
        """Test processing with invalid mode"""
        text = "Test document."
        
        # Invalid mode should default to academic
        result = self.processor.process_document(text=text, mode='invalid_mode')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['mode'], 'invalid_mode')
    
    def test_none_text(self):
        """Test processing None text"""
        result = self.processor.process_document(text=None)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_invalid_options(self):
        """Test processing with invalid options"""
        text = "Test document."
        
        result = self.processor.process_document(
            text=text,
            mode='academic',
            options='invalid'  # Should be dict
        )
        
        # Should handle gracefully
        self.assertTrue(result['success'])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when script is executed directly
    success = run_tests()
    sys.exit(0 if success else 1)
