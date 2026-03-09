"""
Phrase Trainer Module for Dyslexia Reading Assistance

This module provides functionality for chunk reading (phrase training).
Users improve reading speed and comprehension by reading in meaningful phrases
(2-4 words) instead of individual words.

Features:
- Text splitting into meaningful phrase chunks
- Configurable phrase length (2-4 words)
- Progress tracking through phrases
- Session management for phrase training
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class PhraseChunk:
    """Represents a single phrase chunk"""
    phrase: str
    word_count: int
    position: int


@dataclass
class ChunkReadingSession:
    """Represents a phrase training session"""
    text: str
    phrases: List[str]
    total_phrases: int
    current_phrase_index: int = 0
    is_paused: bool = False
    is_completed: bool = False
    session_id: str = ""


class PhraseTrainer:
    """
    Main class for managing phrase-based reading training.
    
    Helps users improve reading speed and comprehension by displaying
    and highlighting text in meaningful phrase chunks (2-4 words each).
    """
    
    # Default phrase length configuration
    MIN_PHRASE_LENGTH = 2  # Minimum words per phrase
    MAX_PHRASE_LENGTH = 4  # Maximum words per phrase
    
    def __init__(self, text: str = "", min_length: int = 2, max_length: int = 4):
        """
        Initialize the phrase trainer.
        
        Args:
            text: The paragraph to train on
            min_length: Minimum words per phrase (default: 2)
            max_length: Maximum words per phrase (default: 4)
        """
        self.text = text
        self.min_length = max(1, min_length)
        self.max_length = max(self.min_length, max_length)
        self.phrases = []
        self.session = None
    
    def split_into_words(self, text: str) -> List[str]:
        """
        Split text into individual words with basic punctuation handling.
        
        Args:
            text: Raw text input
            
        Returns:
            List of words
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()
        
        # Split by whitespace
        words = text.split()
        
        # Clean each word: remove leading/trailing punctuation
        cleaned_words = []
        for word in words:
            # Remove leading punctuation
            word = re.sub(r'^[\"\'\(\[\{«]+', '', word)
            # Remove trailing punctuation (keep apostrophes for contractions)
            word = re.sub(r'[\"\')\]\}»\.!?,;:\-]+$', '', word)
            
            if word:  # Only add non-empty words
                cleaned_words.append(word)
        
        return cleaned_words
    
    def chunk_words_into_phrases(self, words: List[str]) -> List[str]:
        """
        Group words into meaningful phrase chunks.
        
        Strategy: Try to create balanced chunks of 2-4 words each.
        This helps maintain natural reading flow while grouping related words.
        
        Args:
            words: List of individual words
            
        Returns:
            List of phrase strings
        """
        if not words:
            return []
        
        phrases = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            
            # Check if chunk is ready to be converted to phrase
            chunk_len = len(current_chunk)
            
            # If we hit max length, finalize phrase
            if chunk_len >= self.max_length:
                phrases.append(' '.join(current_chunk))
                current_chunk = []
            # If we hit min length and next word would exceed max, finalize
            elif chunk_len >= self.min_length and chunk_len < self.max_length:
                # Look ahead logic: if adding more would exceed max, finalize
                # For now, we continue accumulating
                pass
        
        # Add remaining words as final phrase
        if current_chunk:
            phrases.append(' '.join(current_chunk))
        
        return phrases
    
    def analyze_sentence_boundaries(self, words: List[str]) -> List[int]:
        """
        Identify punctuation marks that suggest phrase boundaries.
        
        Args:
            words: List of words (some may contain trailing punctuation)
            
        Returns:
            List of indices where phrase boundaries should occur
        """
        boundaries = []
        
        for idx, word in enumerate(words):
            # Check for common phrase-ending punctuation
            if word.endswith((',', ':', ';')) or word.endswith('.'):
                boundaries.append(idx + 1)
        
        return boundaries
    
    def smart_chunk_words(self, words: List[str]) -> List[str]:
        """
        Intelligently chunk words into phrases respecting sentence structure.
        
        This method tries to:
        1. Respect natural phrase boundaries (punctuation)
        2. Keep phrase lengths between min and max
        3. Create readable, meaningful chunks
        
        Args:
            words: List of words
            
        Returns:
            List of phrase chunks
        """
        if not words:
            return []
        
        if len(words) <= self.max_length:
            return [' '.join(words)]
        
        phrases = []
        current_chunk = []
        
        for idx, word in enumerate(words):
            current_chunk.append(word)
            chunk_len = len(current_chunk)
            
            # Always finalize if we reach max length
            should_finalize = chunk_len >= self.max_length
            
            # Check for natural boundaries (punctuation)
            has_terminal_punctuation = word.endswith(('.', '!', '?', ',', ':', ';'))
            
            # Finalize if we have terminal punctuation and minimum length
            if has_terminal_punctuation and chunk_len >= self.min_length:
                should_finalize = True
            
            # Check if we're at the last word
            is_last_word = idx == len(words) - 1
            
            # Finalize if minimum length reached and next chunk would be short
            remaining_words = len(words) - (idx + 1)
            if chunk_len >= self.min_length and remaining_words > 0:
                if remaining_words <= 2 and chunk_len < self.max_length:
                    # Might combine later words
                    pass
            
            if should_finalize or is_last_word:
                if current_chunk:
                    phrases.append(' '.join(current_chunk))
                    current_chunk = []
        
        # Handle any remaining words
        if current_chunk:
            if phrases and len(current_chunk) < self.min_length:
                # Append remaining short chunk to previous phrase
                phrases[-1] = phrases[-1] + ' ' + ' '.join(current_chunk)
            else:
                phrases.append(' '.join(current_chunk))
        
        # Ensure no phrase exceeds max length
        final_phrases = []
        for phrase in phrases:
            phrase_words = phrase.split()
            if len(phrase_words) <= self.max_length:
                final_phrases.append(phrase)
            else:
                # Split long phrase into max-length chunks
                for i in range(0, len(phrase_words), self.max_length):
                    chunk = ' '.join(phrase_words[i:i + self.max_length])
                    final_phrases.append(chunk)
        
        return final_phrases if final_phrases else [' '.join(words)]
    
    def prepare_text(self, text: str) -> List[str]:
        """
        Prepare text by splitting into intelligently chunked phrases.
        
        Args:
            text: Raw text input
            
        Returns:
            List of phrase chunks
        """
        # Step 1: Split into words
        words = self.split_into_words(text)
        
        if not words:
            return []
        
        # Step 2: Group into meaningful phrases
        self.phrases = self.smart_chunk_words(words)
        
        return self.phrases
    
    def create_session(self, text: str, session_id: str = "") -> ChunkReadingSession:
        """
        Create a new phrase training session.
        
        Args:
            text: The text to train on
            session_id: Optional session identifier
            
        Returns:
            ChunkReadingSession object
        """
        self.text = text
        self.phrases = self.prepare_text(text)
        
        if not self.phrases:
            raise ValueError("Text must contain at least one word")
        
        # Create session
        self.session = ChunkReadingSession(
            text=text,
            phrases=self.phrases,
            total_phrases=len(self.phrases),
            session_id=session_id
        )
        
        return self.session
    
    def get_current_phrase(self) -> Optional[str]:
        """Get the currently highlighted phrase"""
        if not self.session or self.session.current_phrase_index >= len(self.session.phrases):
            return None
        return self.session.phrases[self.session.current_phrase_index]
    
    def advance_to_next_phrase(self) -> bool:
        """
        Advance to the next phrase.
        
        Returns:
            True if advanced, False if reached end
        """
        if not self.session:
            return False
        
        self.session.current_phrase_index += 1
        
        # Check if we've completed the session
        if self.session.current_phrase_index >= len(self.session.phrases):
            self.session.is_completed = True
            return False
        
        return True
    
    def pause(self) -> bool:
        """Pause the training session"""
        if self.session:
            self.session.is_paused = True
            return True
        return False
    
    def resume(self) -> bool:
        """Resume a paused session"""
        if self.session:
            self.session.is_paused = False
            return True
        return False
    
    def reset(self) -> bool:
        """Reset the session to the beginning"""
        if self.session:
            self.session.current_phrase_index = 0
            self.session.is_paused = False
            self.session.is_completed = False
            return True
        return False
    
    def get_session_data(self) -> Dict:
        """
        Get the current session data as a dictionary.
        
        Returns:
            Dictionary containing session information
        """
        if not self.session:
            return {}
        
        return {
            "text": self.session.text,
            "phrases": self.session.phrases,
            "total_phrases": self.session.total_phrases,
            "current_phrase_index": self.session.current_phrase_index,
            "current_phrase": self.get_current_phrase(),
            "is_paused": self.session.is_paused,
            "is_completed": self.session.is_completed,
            "session_id": self.session.session_id
        }
    
    def get_session_stats(self) -> Dict:
        """
        Get statistics about the training session.
        
        Returns:
            Dictionary containing session statistics
        """
        if not self.session:
            return {}
        
        return {
            "total_phrases": self.session.total_phrases,
            "current_phrase_index": self.session.current_phrase_index,
            "phrases_completed": min(self.session.current_phrase_index, 
                                    self.session.total_phrases),
            "progress_percent": (self.session.current_phrase_index / 
                                self.session.total_phrases * 100) if self.session.total_phrases > 0 else 0,
            "is_completed": self.session.is_completed
        }


# Convenience functions for API usage
def prepare_phrase_reading(text: str, min_length: int = 2, 
                          max_length: int = 4) -> Dict:
    """
    Prepare text for phrase reading training.
    
    Args:
        text: The text to prepare
        min_length: Minimum words per phrase
        max_length: Maximum words per phrase
        
    Returns:
        Dictionary with prepared phrase data
    """
    trainer = PhraseTrainer(min_length=min_length, max_length=max_length)
    phrases = trainer.prepare_text(text)
    
    return {
        "original_text": text,
        "phrases": phrases,
        "total_phrases": len(phrases),
        "min_phrase_length": min_length,
        "max_phrase_length": max_length
    }


if __name__ == "__main__":
    # Example usage
    sample_text = """The quick brown fox jumps over the lazy dog.
    This is a sample paragraph for testing the phrase trainer."""
    
    trainer = PhraseTrainer()
    session = trainer.create_session(sample_text)
    
    print("Session created successfully!")
    print(f"Total phrases: {session.total_phrases}")
    print(f"Phrases: {session.phrases}")
    
    print("\nSession stats:", json.dumps(trainer.get_session_stats(), indent=2))
