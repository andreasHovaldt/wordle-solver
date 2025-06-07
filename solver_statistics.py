from solver_api import WordleSolver
from tqdm import tqdm

def main():
    strat = int(input(f"Enter the number of seed words to use (0,1,2,3): "))
    solver = WordleSolver(seed_word_strategy=strat, seed=42)
    
    num_runs = int(input(f"Enter the number of runs to do: "))
    
    n_solves = 0
    solves_guesses = 0
    for _ in tqdm(range(num_runs)):
        if solver.solve(): 
            n_solves += 1
            solves_guesses += solver.guesses_used
        solver.reset()
    
    print(f"Solving success with {strat} seed words for {num_runs} runs:")
    print(f"   {(n_solves/num_runs)*100:3f}%")
    print(f"Avg. guesses for solves")
    print(f"   {solves_guesses/n_solves:3f}")


def test_solver(num_runs: int = 10_000):
    
    for strat in range(4):
        print(f"Testing using {strat} seed words...")
        solver = WordleSolver(seed_word_strategy=strat, seed=42)
        
        n_solves = 0
        solves_guesses = 0
        for _ in tqdm(range(num_runs)):
            if solver.solve(): 
                n_solves += 1
                solves_guesses += solver.guesses_used
            solver.reset()
        
        print(f"Solving success with {strat} seed words for {num_runs} runs:")
        print(f"   {(n_solves/num_runs)*100:3f}%")
        print(f"Avg. guesses for solves")
        print(f"   {solves_guesses/n_solves:3f}")
    



if __name__ == "__main__":
    #main()
    test_solver(1000)