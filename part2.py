import random
from enum import Enum
from math import comb, factorial

class CombinationCoef(Enum):
    BALUT = 4
    STRAIGHT = 5
    FULL_HOUSE = 3
    PAIR = 2
    OTHER = 0

class DiceGameLogic:
    def roll_dice(self) -> list:
        return [random.randint(1, 6) for _ in range(5)]

    def determine_result(self, dice_values: list) -> CombinationCoef:
        counts = {x: dice_values.count(x) for x in set(dice_values)}
        unique_values = len(counts)
        max_count = max(counts.values())

        if unique_values == 1:
            return CombinationCoef.BALUT
        if unique_values == 5 and (1 not in counts or 6 not in counts):
            return CombinationCoef.STRAIGHT
        if unique_values == 2 and (max_count == 3 or max_count == 2):
            return CombinationCoef.FULL_HOUSE
        if max_count >= 2:
            return CombinationCoef.PAIR
        return CombinationCoef.OTHER

def simulate_balut_game(num_simulations: int, bet_amount: int = 1) -> float:
    game_logic = DiceGameLogic()
    total_bets = 0
    total_wins = 0

    for _ in range(num_simulations):
        dice = game_logic.roll_dice()
        result = game_logic.determine_result(dice)

        total_bets += bet_amount
        total_wins += bet_amount * result.value

    rtp = (total_wins / total_bets) * 100
    return rtp


def task_one():
    simulations = [1000, 10000, 100000, 1000000]
    
    for num_sims in simulations:
        rtp = simulate_balut_game(num_sims)
        print(f"RTP after {num_sims} simulations: {rtp:.2f}%")

def task_two():
    total_outcomes = 6**5
    balut_chance = 6 / total_outcomes
    straight_chance = (factorial(5) + factorial(5)) / total_outcomes
    full_house_chance = comb(5, 3) * 6 * 5 / total_outcomes
    pair_chance = 1 - (1 / total_outcomes) * ((6 * 5 * 4 * 3 * 2) + (6 * 10 * 5 * 4) + (6 * 5 * 5) + 6 + (comb(5, 3) * 6 * 5))
    
    coeff = 0.95 / (sum([balut_chance * total_outcomes * CombinationCoef.BALUT.value, straight_chance * total_outcomes * CombinationCoef.STRAIGHT.value, full_house_chance * total_outcomes * CombinationCoef.FULL_HOUSE.value, pair_chance * total_outcomes * CombinationCoef.PAIR.value]) / total_outcomes)

    print("New odds: ")
    print(f"Balut: {CombinationCoef.BALUT.value * coeff}")
    print(f"Straight: {CombinationCoef.STRAIGHT.value * coeff}")
    print(f"Full house: {CombinationCoef.FULL_HOUSE.value * coeff}")
    print(f"Pair: {CombinationCoef.PAIR.value * coeff}")


if __name__ == "__main__":
    task_one()
    task_two()

