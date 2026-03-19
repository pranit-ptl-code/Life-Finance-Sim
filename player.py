import random


class Player:
    def __init__(self, name, stress=5, savings=0):

        random_income = (2500, 2750, 3000, 3250, 3500, 3750, 4000)
        random_debt = (5000, 10000, 15000, 20000, 25000)
        random_rent = (250, 500, 750, 1000, 1250)

        self.name = name.capitalize()
        self.debt = random.choice(random_debt)
        self.income = random.choice(random_income)
        self.rent = random.choice(random_rent)
        self.stress = stress
        self.savings = savings

        self.foodCostHome = 250
        self.foodCostOut = 250
        self.transportationCost = 250
        self.utilitesCost = 250
        self.miscCost = 200

    def displayStats(self):
        print("Name:", self.name)
        print(f"Debt: ${self.debt:,}")
        print(f"Income: ${self.income:,}")
        print(f"Rent: ${self.rent:,}")
        print(f"Stress level: {self.stress}/10")
        print(f"Savings: ${self.savings:,}")

    def monthlyCost(self):
        totalExpenses = [self.foodCostHome, self.foodCostOut,
                         self.transportationCost, self.utilitesCost, self.miscCost]
        totalExpenseSum = sum(totalExpenses)
        print(f"You have ${totalExpenseSum:,} in total expenses.")

        amountRemaining = (self.income - totalExpenseSum - self.rent)
        print(f"You have ${amountRemaining:,} remaining after your bills.")

        if amountRemaining < 0:
            print(
                "You have a negative money after costs. The extra amount spent will go into debt.")
            self.debt += abs(amountRemaining)
            print(f"You are now ${self.debt:,} in debt.")

        if amountRemaining > 0:
            amountRemainingChoice = (input(
                "Where do you want the rest of your money to go (Savings or Debt): ")).lower()

            if amountRemainingChoice == "savings":
                self.savings += amountRemaining
                print(f"You now have ${self.savings:,} in savings.")
            elif amountRemainingChoice == "debt":
                self.debt -= abs(amountRemaining)
                print(f"You are now ${self.debt:,} in debt.")

    def secondJob(self):
        secondJobIncomeRandom = (300, 350, 400, 450, 500, 550, 600)
        secondJobIncome = random.choice(secondJobIncomeRandom)
        self.income += secondJobIncome
        print(f"Your new job pays ${secondJobIncome:,}.")
        print(f"Your total income is now ${self.income:,}.")

        self.adjustStress(1)
        print(f"Your stress level is now {self.stress}/10.")

    def vacation(self):
        print("vacation")
        if self.savings >= 500:
            print("You can go on a vacation!")
            self.adjustStress(-1)
            print(f"Your stress level is {self.stress}/10.")
            self.savings -= 500
            print(f"You now have ${self.savings:,} left in savings.")
        else:
            print("You do not have enough to go on vacation.")

    def entertainment(self):
        if self.savings >= 150:
            print("You can get more entertainment.")
            self.adjustStress(-1)
            print(f"Your stress level is {self.stress}/10.")
            self.savings -= 150
            print(f"You now have ${self.savings:,} left in savings.")
        else:
            print("You do not have enough money to get more entertainment.")

    def removeCosts(self, category):
        if category == "food":
            if self.foodCostOut > 0:
                self.foodCostOut = 0
                self.adjustStress(1)
                print("You cut your eating out expense.")
            else:
                print("You already cut your eating out expense.")
        elif category == "transportation":
            if self.transportationCost > 0:
                self.transportationCost = 0
                self.adjustStress(1)
                print("You cut your transportation cost.")
            else:
                print("You already cut your transportation cost.")
        elif category == "miscellaneous":
            if self.miscCost > 0:
                self.miscCost = 0
                self.adjustStress(1)
                print("You cut your miscellaneous costs.")
            else:
                print("You already cut your food costs.")

    def adjustStress(self, amount):
        self.stress += amount
        self.stress = max(0, min(10, self.stress))
