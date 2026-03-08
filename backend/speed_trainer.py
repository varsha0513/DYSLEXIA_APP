"""
Speed Trainer Module for Dyslexia Reading Assistance

This module provides functionality for guided pace reading training.
Users can improve their reading speed by following highlighted words
that advance at a controlled pace (measured in Words Per Minute).

Features:
- Text splitting into individual words
- WPM calculation and millisecond interval conversion
- Multiple training rounds with progressive speed increases
- Reading statistics tracking
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class ReadingRound:
    """Represents a single training round with its configuration"""
    round_number: int
    wpm: int
    interval_ms: int
    duration_seconds: float
    status: str = "pending"  # pending, in_progress, completed
    

@dataclass
class SpeedTrainerSession:
    """Represents a complete speed training session"""
    text: str
    words: List[str]
    total_words: int
    rounds: List[ReadingRound]
    current_round: int = 0
    current_word_index: int = 0
    is_paused: bool = False
    is_completed: bool = False
    session_id: str = ""


class SpeedTrainer:
    """
    Main class for managing guided pace reading training.
    
    This trainer helps users improve reading speed by displaying text
    word-by-word at a controlled pace based on WPM (Words Per Minute).
    """
    
    # Default speed progression for training rounds
    DEFAULT_SPEEDS = [60, 75, 90]  # WPM values
    
    def __init__(self, text: str = "", speeds: List[int] = None):
        """
        Initialize the speed trainer with text and speed progression.
        
        Args:
            text: The paragraph or text to use for training
            speeds: List of WPM values for each round (default: [60, 75, 90])
        """
        self.text = text
        self.speeds = speeds or self.DEFAULT_SPEEDS
        self.words = []
        self.session = None
        
    def prepare_text(self, text: str) -> List[str]:
        """
        Split text into words for pace reading.
        
        Args:
            text: Raw text input
            
        Returns:
            List of individual words with punctuation handled appropriately
        """
        if not text or not text.strip():
            return []
        
        # Remove extra whitespace and normalize
        text = text.strip()
        
        # Split by whitespace, removing empty strings
        words = text.split()
        
        # Clean each word: remove leading/trailing punctuation but keep in-word punctuation
        cleaned_words = []
        for word in words:
            # Remove leading punctuation (quotes, brackets, etc.)
            word = re.sub(r'^[\"\'\(\[\{«]+', '', word)
            # Remove trailing punctuation except apostrophes (for contractions)
            word = re.sub(r'[\"\')\]\}»\.!?,;:\-]+$', '', word)
            
            if word:  # Only add non-empty words
                cleaned_words.append(word)
        
        self.words = cleaned_words
        return cleaned_words
    
    def calculate_interval(self, wpm: int) -> int:
        """
        Calculate the time interval between words based on WPM.
        
        Formula: interval (ms) = 60000 / WPM
        
        Args:
            wpm: Words per minute reading speed
            
        Returns:
            Interval in milliseconds
        """
        if wpm <= 0:
            raise ValueError("WPM must be greater than 0")
        
        interval_ms = round(60000 / wpm)
        return interval_ms
    
    def calculate_round_duration(self, wpm: int, word_count: int) -> float:
        """
        Calculate how long a round will take based on WPM and word count.
        
        Args:
            wpm: Words per minute
            word_count: Number of words in the text
            
        Returns:
            Duration in seconds
        """
        if wpm <= 0:
            raise ValueError("WPM must be greater than 0")
        
        duration_seconds = (word_count / wpm) * 60
        return duration_seconds
    
    def create_session(self, text: str, speeds: List[int] = None, session_id: str = "") -> SpeedTrainerSession:
        """
        Create a new speed training session.
        
        Args:
            text: The text to train on
            speeds: WPM values for each round
            session_id: Optional session identifier
            
        Returns:
            SpeedTrainerSession object representing the session
        """
        self.text = text
        self.words = self.prepare_text(text)
        
        if not self.words:
            raise ValueError("Text must contain at least one word")
        
        speeds = speeds or self.speeds
        
        # Create rounds with calculated intervals
        rounds = []
        for idx, wpm in enumerate(speeds, 1):
            interval_ms = self.calculate_interval(wpm)
            duration = self.calculate_round_duration(wpm, len(self.words))
            
            round_data = ReadingRound(
                round_number=idx,
                wpm=wpm,
                interval_ms=interval_ms,
                duration_seconds=duration
            )
            rounds.append(round_data)
        
        # Create session
        self.session = SpeedTrainerSession(
            text=text,
            words=self.words,
            total_words=len(self.words),
            rounds=rounds,
            session_id=session_id
        )
        
        return self.session
    
    def get_current_round(self) -> ReadingRound | None:
        """Get the current training round"""
        if not self.session or self.session.current_round >= len(self.session.rounds):
            return None
        return self.session.rounds[self.session.current_round]
    
    def get_current_word(self) -> str | None:
        """Get the current word being highlighted"""
        if not self.session or self.session.current_word_index >= len(self.session.words):
            return None
        return self.session.words[self.session.current_word_index]
    
    def advance_to_next_word(self) -> bool:
        """
        Advance to the next word in the current round.
        
        Returns:
            True if advanced, False if reached end of text
        """
        if not self.session:
            return False
        
        self.session.current_word_index += 1
        
        # Check if round is complete
        if self.session.current_word_index >= len(self.session.words):
            return self._complete_round()
        
        return True
    
    def _complete_round(self) -> bool:
        """
        Complete the current round and advance to the next.
        
        Returns:
            True if advanced to next round, False if all rounds complete
        """
        if not self.session:
            return False
        
        current_round = self.get_current_round()
        if current_round:
            current_round.status = "completed"
        
        # Check if there are more rounds
        if self.session.current_round + 1 >= len(self.session.rounds):
            self.session.is_completed = True
            return False
        
        # Advance to next round
        self.session.current_round += 1
        self.session.current_word_index = 0
        
        current_round = self.get_current_round()
        if current_round:
            current_round.status = "in_progress"
        
        return True
    
    def pause(self) -> bool:
        """Pause the current training session"""
        if self.session:
            self.session.is_paused = True
            return True
        return False
    
    def resume(self) -> bool:
        """Resume a paused training session"""
        if self.session:
            self.session.is_paused = False
            return True
        return False
    
    def reset(self) -> bool:
        """Reset the session to the beginning"""
        if self.session:
            self.session.current_round = 0
            self.session.current_word_index = 0
            self.session.is_paused = False
            self.session.is_completed = False
            
            # Reset all rounds
            for round_data in self.session.rounds:
                round_data.status = "pending"
            
            # Mark first round as in progress
            if self.session.rounds:
                self.session.rounds[0].status = "in_progress"
            
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
            "words": self.session.words,
            "total_words": self.session.total_words,
            "current_round": self.session.current_round,
            "current_word_index": self.session.current_word_index,
            "current_word": self.get_current_word(),
            "is_paused": self.session.is_paused,
            "is_completed": self.session.is_completed,
            "rounds": [asdict(round_data) for round_data in self.session.rounds],
            "current_round_data": asdict(self.get_current_round()) if self.get_current_round() else None,
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
        
        completed_rounds = sum(1 for r in self.session.rounds if r.status == "completed")
        total_time = sum(r.duration_seconds for r in self.session.rounds)
        
        return {
            "total_words": self.session.total_words,
            "total_rounds": len(self.session.rounds),
            "completed_rounds": completed_rounds,
            "current_round": self.session.current_round + 1,
            "total_duration_seconds": total_time,
            "average_wpm": sum(r.wpm for r in self.session.rounds) / len(self.session.rounds) if self.session.rounds else 0,
            "min_wpm": min(r.wpm for r in self.session.rounds) if self.session.rounds else 0,
            "max_wpm": max(r.wpm for r in self.session.rounds) if self.session.rounds else 0,
            "is_completed": self.session.is_completed
        }


# Convenience functions for API usage
def prepare_pace_reading(text: str) -> Dict:
    """
    Prepare text for pace reading training.
    
    Args:
        text: The text to prepare
        
    Returns:
        Dictionary with prepared data
    """
    trainer = SpeedTrainer()
    words = trainer.prepare_text(text)
    
    return {
        "original_text": text,
        "words": words,
        "total_words": len(words),
        "speeds": SpeedTrainer.DEFAULT_SPEEDS,
        "intervals": [trainer.calculate_interval(wpm) for wpm in SpeedTrainer.DEFAULT_SPEEDS]
    }


def calculate_speed_intervals(wpm_list: List[int]) -> Dict[int, int]:
    """
    Calculate millisecond intervals for a list of WPM values.
    
    Args:
        wpm_list: List of words per minute values
        
    Returns:
        Dictionary mapping WPM to interval in milliseconds
    """
    trainer = SpeedTrainer()
    return {wpm: trainer.calculate_interval(wpm) for wpm in wpm_list}


if __name__ == "__main__":
    # Example usage
    sample_text = """The quick brown fox jumps over the lazy dog. 
    This is a sample paragraph for testing the speed trainer module."""
    
    trainer = SpeedTrainer()
    session = trainer.create_session(sample_text)
    
    print("Session created successfully!")
    print(f"Total words: {session.total_words}")
    print(f"Number of rounds: {len(session.rounds)}")
    print(f"Words: {session.words[:5]}...")
    
    print("\nRound details:")
    for round_data in session.rounds:
        print(f"  Round {round_data.round_number}: {round_data.wpm} WPM, "
              f"Interval: {round_data.interval_ms}ms, "
              f"Duration: {round_data.duration_seconds:.1f}s")
    
    print(f"\nSession data: {json.dumps(trainer.get_session_stats(), indent=2)}")
