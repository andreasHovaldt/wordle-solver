from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from wordle_game import WordleGame

# Init api instance
app = FastAPI()

# Init game object
game = WordleGame()
#game = WordleGame(seed=42)

# Create model for the guess message
class WordleGuess(BaseModel):
    guess: str

# Create root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Wordle API!"}

# Create guessing endpoint
@app.post("/wordle")
async def wordle(guess: WordleGuess):
    
    try:
        game_response = game.make_guess(guess=guess.guess.lower())
        return game_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Create status endpoint
@app.get("/wordle")
async def wordle_status():
    return game.status()

# Create restart endpoint
@app.post("/wordle/restart")
async def wordle_restart():
    return game.restart_game()




        





