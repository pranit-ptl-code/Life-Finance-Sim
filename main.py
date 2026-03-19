from player import Player
from events import random_event
from economy import invest_stocks


def monthly_decisions():
    while True:
        decision = input("Do you want to make a decision? (yes/no): ").lower()

        if decision == "no":
            print("No decisions made this month.")
            break
        elif decision == "yes":
            action = input(
                "Which decision? (job/vacation/entertainment/remove costs): ").lower()

            if action == "job":
                player.secondJob()
            elif action == "vacation":
                player.vacation()
            elif action == "entertainment":
                player.entertainment()
            elif action == "remove costs":
                category = input(
                    "Enter a category of cost you want to remove: ")
                player.removeCosts(category)
            else:
                print("Invalid decision. Try again.")
        else:
            print("Invalid input. Please type yes or no.")


player = Player(input("Enter your player name: "))

month_counter = 0

while player.stress < 10 and player.debt > 0:
    month_counter += 1

    print(f"Month: {month_counter}")

    player.displayStats()
    if month_counter % 12 == 0:
        player.savings *= 1.035

    random_event(player)

    player.monthlyCost()

    monthly_decisions()

    invest_stocks_question = input("Do you want to invest in stocks: ")
    invest_stocks_question = invest_stocks_question.lower()
    if invest_stocks_question == "no":
        continue
    else:
        invest_stocks(player)


print("Game Over")
