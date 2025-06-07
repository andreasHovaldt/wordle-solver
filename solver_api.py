import requests
import json
import numpy as np
from copy import deepcopy
from pathlib import Path

class WordleSolver:
    def __init__(self,
                 seed_word_strategy: int = 1 ,
                 guessed_words: None | list[str] = None,
                 wordle_game_api: str = "http://127.0.0.1:8000/wordle",
                 word_list_api: str = "https://cheaderthecoder.github.io/5-Letter-words/words.json",
                 seed=None,
                 ):
        
        # Init some class vars
        self.wordle_game_api = wordle_game_api
        self.word_list_path = Path("word_lists/words.json")
        self.word_list_api = word_list_api
        self.guesses_used = 0
        self.random_gen = np.random.default_rng(seed=seed)
        
        # Define the first tried out words
        # https://www.sfi.ie/research-news/news/wordle-data-analytics/
        if guessed_words is not None: self.seed_words = guessed_words                # If initialized with already guessed words
        elif seed_word_strategy == 1: self.seed_words = ["tales",]                   # 95% success w/ 3.66 avg rounds 
        elif seed_word_strategy == 2: self.seed_words = ["cones", "trial",]          # 96% success w/ 3.68 avg rounds 
        elif seed_word_strategy == 3: self.seed_words = ["hates", "round", "climb",] # 97% success w/ 4.20 avg rounds 
        else: 
            print("Using no seed words")
            self.seed_words = []
        
        # Init letter dict, recording the knowledge gained from guessing
        self.letter_dict = {
            "gray": [],
            "yellow": [],
            "green": [],
        }
        
        # Obtain a word list of all english 5 letter words
        self.word_list = self._get_word_list()
        
    
    def reset(self):
        self.guesses_used = 0
        self.word_list = self._get_word_list()
        self.letter_dict = {
            "gray": [],
            "yellow": [],
            "green": [],
        }
        return True
        
        
    def _get_word_list(self):
        
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
        
        return word_list


    @staticmethod
    def _update_letter_dict(letter_dict: dict, word: str, feedback: str) -> dict:
        """Updates the letter dict based on a tested word and the received feedback"""
        # feedback -> '00120' -> gray, gray, yellow, green, gray
        
        assert len(word) == len(feedback), "The feedback must be same length as the word (5)"
        
        for i, (letter, result) in enumerate(zip(word, feedback)):
            
            match result:
                case "0": letter_dict["gray"].append(letter)
                case "1": letter_dict["yellow"].append([letter, i])
                case "2": letter_dict["green"].append([letter, i])
                case _: raise Exception(f"The feedback had an unknown charactor: {result}")
        
        return letter_dict


    @staticmethod
    def _update_word_list(word_list: list[str], letter_dict: dict, verbose=False) -> list[str]:
        """Removes invalid words based on the letter_dict"""
        
        # Init a word list for filtering
        filtered_word_list = deepcopy(word_list)
        
        for word in word_list:
            
            for green_letter, letter_idx in letter_dict["green"]:
                # Remove word if it does not contain the green letter at the correct idx
                if word[letter_idx] is not green_letter: 
                    filtered_word_list.remove(word)
                    break
            
            else: # Executes if the previous for loop didn't break
                for yellow_letter, letter_idx in letter_dict["yellow"]:
                    # Remove word if it contains a yellow letter in the idx known to not be correct or if the word doesn't contain the yellow letter
                    if (word[letter_idx] is yellow_letter) or (yellow_letter not in word): 
                        filtered_word_list.remove(word)
                        break
            
                else:
                    confirmed_letters = [l for l, _ in letter_dict["green"] + letter_dict["yellow"]]
                    for gray_letter in letter_dict["gray"]:
                        # Remove word only if it contains a gray letter and the gray letter does not appear in the green or yellow list (relates to words with multiple of the same char)
                        # Kind of a shitty work around method since if the char is also added to the gray list, it is known how many of that specific char the target word contains.
                        # This info is not utilized for the sorting, yet :)
                        if (gray_letter in word) and (gray_letter not in confirmed_letters):
                            filtered_word_list.remove(word)
                            break
        
        if verbose: print("Current filtered word list length:", len(filtered_word_list))
        
        return filtered_word_list
    
    
    def _guess_word(self, guess: str, verbose=False):
        
        # Guess a word
        if verbose: print(f"WordleSolver guesses: '{guess}'...")
        response = requests.post(url=self.wordle_game_api, json={"guess": guess})
        if response.status_code == 200:
            feedback = response.json()["feedback"]
            if verbose: 
                print(f"Received guess feedback: {feedback}")
                summary = response.json()["game_summary"]
                if summary is not None:
                    print(summary)
        else:
            raise ValueError("Failed to fetch feedback from wordle game api...")
        
        self.guesses_used += 1
        
        # Check if feedback says it is solved
        if feedback == "22222":
            return True
        
        # Update the letter dict based on feedback
        self.letter_dict = self._update_letter_dict(
            letter_dict=self.letter_dict,
            word=guess,
            feedback=feedback,
        )
        
        # Update the word list based on letter dict
        self.word_list = self._update_word_list(
            word_list=self.word_list,
            letter_dict=self.letter_dict,
        )
        
        return False
        
      
    def solve(self, verbose=False):
        
        # Try out seed words first
        for seed_word in self.seed_words:
            if self._guess_word(guess=seed_word): 
                if verbose: print(f"Wordle puzzle solved in {self.guesses_used} guesses!\nThe word was '{seed_word}'")
                return True
        
        # Choose random word from word list
        solved = False
        guess = ""
        while (not solved) and (self.guesses_used < 6):
            guess = self.word_list[self.random_gen.integers(low=0, high=len(self.word_list))]
            solved = self._guess_word(guess=guess)
        
        # Catch the result of the solving process
        if solved:
            if verbose: print(f"Wordle puzzle solved in {self.guesses_used} guesses!\nThe word was '{guess}'")
            return True
        else:
            if verbose: print(f"WordleSolver ran out of guess ;(")
            return False

        
        
        
        
def main():
    ### When words have already been guess ###
    # guessed_words = ["kicky", "issue", "remix", "grief", "tried"]
    # solver = WordleSolver(seed_word_strategy=0, seed=42, guessed_words=guessed_words)
    
    ### When starting from scratch ###
    strat = int(input(f"Enter the number of seed words to use (0,1,2,3): "))
    solver = WordleSolver(seed_word_strategy=strat, seed=123)
    
    for _ in range(10):
        solver.solve()
        solver.reset()
        
    

if __name__ == "__main__":
    main()