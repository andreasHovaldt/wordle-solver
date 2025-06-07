import numpy as np
import requests
import os
from pathlib import Path
import json

class WordleGame:
    def __init__(self, seed: int | None = None) -> None:
        self.random_gen = np.random.default_rng(seed=seed)
        self.word_list_path = Path("word_lists/words.json")
        self.word_list_api = "https://cheaderthecoder.github.io/5-Letter-words/words.json"
        self.secret_word = self._generate_word()
        self.guesses = []
        
    
    def _generate_word(self):
        
        if self.word_list_path.exists():
            with open(self.word_list_path, 'r') as file:
                word_list = json.load(file)["words"]
        
        else:
            response = requests.get(self.word_list_api)
            if response.status_code == 200:
                print("Fetched word list from API")
                word_list_json = response.json()
                
                with open(self.word_list_path, "w") as file:
                    json.dump(word_list_json, file, indent=4)
                word_list = word_list_json["words"]
            else:
                raise ValueError("Failed to fetch word list")
        
        return word_list[self.random_gen.integers(low=0, high=len(word_list))]
    
    
    def restart_game(self):
        response = {
            "message": "Game restarted.",
            "secret_word": self.secret_word,
            "guesses": self.guesses,
        }
        self.secret_word = self._generate_word()
        self.guesses = []
        return response
    
    
    def make_guess(self, guess: str):
        if len(guess) != 5:
            raise ValueError("Guess must be exactly 5 letters!")
        
        # Save guess
        self.guesses.append(guess)
        
        # Compute feedback
        feedback = []
        for guess_letter, secret_letter in zip(guess, self.secret_word):
            if guess_letter == secret_letter:
                feedback.append("2")
            elif guess_letter in self.secret_word:
                feedback.append("1")
            else:
                feedback.append("0")
        
        # Return response
        response = {
            "guess": guess,
            "feedback": "".join(feedback),
            "guesses_used": len(self.guesses),
            "is_correct": guess == self.secret_word,
            "out_of_guesses": len(self.guesses) >= 6,
            "game_summary": None,
        }
        
        if response["is_correct"]: # Check if guess is correct
            response["game_summary"] = self.restart_game()
            return response
            
        elif response["out_of_guesses"]: # Check if player has run out of guesses
            response["game_summary"] = self.restart_game()
            return response
            
        else: # Return response if game is not over
            return response
    
    
    def status(self):
        return {
            "guesses": self.guesses,
            "guesses_used": len(self.guesses),
            "secret_word": self.secret_word,
        }