import random

events = [

    {"text": "You found $200 on the ground.", "savings": 200},
    {"text": "Your boss gave you a bonus.", "savings": 500},
    {"text": "You won a small lottery prize.", "savings": 1000},
    {"text": "A friend paid you back money they owed.", "savings": 300},
    {"text": "A relative gave you a gift of cash.", "savings": 250},
    {"text": "Your side hustle made extra money.", "savings": 400},
    {"text": "You received a tax refund.", "savings": 700},
    {"text": "You sold some old items online.", "savings": 150},
    {"text": "You received a cashback reward.", "savings": 100},
    {"text": "You got a refund from a purchase.", "savings": 120},

    {"text": "You lost your wallet.", "savings": -250},
    {"text": "Your phone broke and needed replacing.", "savings": -400},
    {"text": "You had to pay an unexpected bill.", "savings": -350},
    {"text": "You got a parking ticket.", "savings": -100},
    {"text": "Your car needed repairs.", "savings": -600},
    {"text": "You forgot to cancel a subscription.", "savings": -80},
    {"text": "You had a medical expense.", "savings": -500},
    {"text": "You paid for a friend's birthday gift.", "savings": -150},
    {"text": "You accidentally damaged something and had to pay for it.", "savings": -300},
    {"text": "Your laptop needed repairs.", "savings": -450}

]


def random_event(player):

    event = random.choice(events)

    print("\n--- Random Event ---")
    print(event["text"])

    player.savings += event["savings"]

    print(f"Savings change: ${event['savings']}")
