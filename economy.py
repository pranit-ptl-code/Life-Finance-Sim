import random


def invest_stocks(player):
    stock_price = round(random.uniform(10.00, 250.00), 2)
    print(f"Current stock price is ${stock_price:,}")

    confirm = ""
    while confirm.lower() != "yes":
        shares = int(
            input("How many shares of the stock do you want to buy: "))
        buy_price = round(stock_price * shares, 2)

        print(f"Current stock price is ${stock_price:,}")
        print(f"You will have to pay ${buy_price:,}")

        while buy_price > player.savings:
            print("You do not have enough in savings to buy this many shares.")
            print(f"You have ${player.savings:,} in savings.")
            print(f"Current stock price is ${stock_price:,}")
            shares = int(
                input("How many shares of the stock do you want to buy: "))
            buy_price = round(stock_price * shares, 2)
            print(f"You will have to pay ${buy_price:,}")

        confirm = input("Do you want to buy the stock at this price? ")

    player.savings -= buy_price


def stock_change(player):
    while change == 0:
        change = random.randint(0, 2)

    if change < 1:
        print("Your stock decreased in value")
        buy_price *= change
    else:
        print("Your stock increased in value")
        buy_price += change

    print(f"This is now your new stock price: ${buy_price:,}")
    sell_question = input("Do you want to sell your stock: ")
    if sell_question.lower() == "yes":
        print(f"Your current stock price is ${buy_price:,}")
        player.savings += buy_price
