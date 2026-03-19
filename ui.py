from economy import invest_stocks
from events import random_event, events
from player import Player
import pygame
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

pygame.init()

W, H = 1100, 720
FPS = 60
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Life Finance Sim")
clock = pygame.time.Clock()

BG = (10,  10,  20)
SURFACE = (22,  22,  40)
SURFACE2 = (32,  32,  54)
BORDER = (55,  55,  90)
ACCENT = (124, 106, 255)
TEAL = (40, 180, 160)
TEXT = (232, 232, 240)
MUTED = (110, 110, 150)
DANGER = (255,  70, 100)
SUCCESS = (60, 220, 140)
WARN = (255, 190,  60)
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)

f_title = pygame.font.SysFont("Segoe UI", 42, bold=True)
f_head = pygame.font.SysFont("Segoe UI", 22, bold=True)
f_body = pygame.font.SysFont("Segoe UI", 17)
f_small = pygame.font.SysFont("Segoe UI", 14)
f_mono = pygame.font.SysFont("Courier New", 15)
f_big = pygame.font.SysFont("Segoe UI", 52, bold=True)


def rr(surf, col, rect, r=10, bw=0, bc=None):
    pygame.draw.rect(surf, col, rect, border_radius=r)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=r)


def txt(surf, text, font, col, cx=None, cy=None, x=None, y=None):
    s = font.render(text, True, col)
    if cx is not None and cy is not None:
        surf.blit(s, s.get_rect(center=(cx, cy)))
    else:
        surf.blit(s, (x, y))
    return s


def button(surf, rect, label, col, font, text_col=WHITE, mouse=None):
    r = pygame.Rect(rect)
    hover = r.collidepoint(mouse) if mouse else False
    c = tuple(min(255, v + 25) for v in col) if hover else col
    rr(surf, c, r, r=8)
    txt(surf, label, font, text_col, cx=r.centerx, cy=r.centery)
    return r


def modal(surf):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    surf.blit(ov, (0, 0))
    card = pygame.Rect(W//2 - 280, H//2 - 200, 560, 400)
    rr(surf, SURFACE, card, r=16, bw=2, bc=BORDER)
    return card


STATE_NAME = 0
STATE_INSTRUCTIONS = 1
STATE_EVENT = 2
STATE_ALLOC = 3
STATE_MONTHLY = 4
STATE_STOCKS = 5
STATE_GAMEOVER = 6

state = STATE_NAME
player = None
month = 0
pending_event = None
stock_price = 0.0
stock_shares = 0
stock_bought = 0.0
stock_new = 0.0
stock_stage = "ask"
portfolio = []   # list of {"shares": int, "bought": float, "price_per": float}
name_text = ""
notifs = []
log_lines = []
win = False
used_second_job = False
used_leisure = False  # vacation or entertainment


def push_notif(text, col=SUCCESS):
    notifs.append([text, col, 200])


def push_log(text, col=TEXT):
    log_lines.append((text, col))
    if len(log_lines) > 60:
        log_lines.pop(0)


def clamp_savings():
    """If savings go negative, move the deficit into debt and zero savings."""
    if player.savings < 0:
        player.debt += abs(player.savings)
        push_notif(
            f"Savings went negative! ${abs(player.savings):,.0f} added to debt.", DANGER)
        push_log(f"Negative savings ${player.savings:,.0f} → debt", DANGER)
        player.savings = 0


def start_month():
    global month, pending_event, state, used_second_job, used_leisure
    used_second_job = False
    used_leisure = False
    month += 1
    if month % 12 == 0:
        bonus = round(player.savings * 0.035, 2)
        player.savings += bonus
        clamp_savings()
        push_log(f"Annual savings interest: +${bonus:,.0f}", SUCCESS)
    if player.debt > 5000 and random.random() < 0.5:
        player.adjustStress(1)
        push_notif("Debt is weighing on you. Stress +1", DANGER)
        push_log("High debt — stress +1", DANGER)
    ev = random.choice(events)
    player.savings += ev["savings"]
    clamp_savings()
    pending_event = ev
    state = STATE_EVENT


def check_gameover():
    global state, win
    if player.stress >= 10:
        state = STATE_GAMEOVER
        win = False
        return True
    if player.debt <= 0:
        state = STATE_GAMEOVER
        win = True
        return True
    return False


def draw_stat_panel():
    p = player
    rr(screen, SURFACE, (20, 20, 240, 680), r=14, bw=1, bc=BORDER)

    rr(screen, ACCENT, (20, 20, 240, 54), r=14)
    txt(screen, p.name, f_head, WHITE, cx=140, cy=47)
    txt(screen, f"Month {month}", f_small, WHITE, x=28, cy=None, y=32)

    rows = [
        ("DEBT",     f"${p.debt:,.0f}",     DANGER),
        ("SAVINGS",  f"${p.savings:,.0f}",  SUCCESS),
        ("INCOME",   f"${p.income:,.0f}",   TEAL),
        ("RENT",     f"${p.rent:,.0f}",     WARN),
        ("EXPENSES",
         f"${p.foodCostHome+p.foodCostOut+p.transportationCost+p.utilitesCost+p.miscCost:,.0f}", WARN),
    ]
    y = 90
    for label, value, col in rows:
        txt(screen, label, f_small, MUTED, x=32, y=y)
        txt(screen, value, f_head,  col,   x=32, y=y + 16)
        y += 56

    txt(screen, "STRESS", f_small, MUTED, x=32, y=375)
    rr(screen, SURFACE2, (32, 394, 208, 16), r=8)
    fw = int(208 * p.stress / 10)
    if fw > 0:
        sc = SUCCESS if p.stress < 4 else (WARN if p.stress < 7 else DANGER)
        rr(screen, sc, (32, 394, fw, 16), r=8)
    txt(screen, f"{p.stress}/10", f_small, WHITE, cx=136, cy=402)

    txt(screen, "COSTS ACTIVE", f_small, MUTED, x=32, y=422)
    cost_items = [
        ("Food Out",     p.foodCostOut > 0),
        ("Transport",    p.transportationCost > 0),
        ("Misc",         p.miscCost > 0),
    ]
    y2 = 440
    for label, active in cost_items:
        col = SUCCESS if active else DANGER
        mark = "ON" if active else "OFF"
        txt(screen, f"  {label}: {mark}", f_small, col, x=32, y=y2)
        y2 += 18

    txt(screen, "ACTIVITY", f_small, MUTED, x=32, y=502)
    recent = log_lines[-12:]
    y3 = 520
    for line, col in recent:
        short = line[:26] + ".." if len(line) > 28 else line
        txt(screen, short, f_small, col, x=32, y=y3)
        y3 += 16


def draw_event_screen(mouse):
    modal(screen)
    ev = pending_event
    col = SUCCESS if ev["savings"] > 0 else DANGER
    arrow = "▲" if ev["savings"] > 0 else "▼"
    cx = W // 2

    txt(screen, f"Month {month}  —  Random Event",
        f_small, MUTED, cx=cx, cy=H//2 - 140)
    txt(screen, ev["text"], f_head, TEXT, cx=cx, cy=H//2 - 90)
    txt(screen, f"{arrow}  ${abs(ev['savings']):,.0f}",
        f_big, col, cx=cx, cy=H//2 - 30)

    return button(screen, (cx-75, H//2+70, 150, 44), "Continue", ACCENT, f_body, mouse=mouse)


def draw_alloc_screen(mouse):
    modal(screen)
    p = player
    exp = p.foodCostHome + p.foodCostOut + \
        p.transportationCost + p.utilitesCost + p.miscCost
    rem = p.income - exp - p.rent
    cx = W // 2

    txt(screen, "Monthly Budget", f_head, TEXT, cx=cx, cy=H//2 - 155)

    lines = [
        (f"Income:             ${p.income:>9,.0f}",       TEAL),
        (f"Rent:              -${p.rent:>9,.0f}",         WARN),
        (f"Expenses:          -${exp:>9,.0f}",            WARN),
        ("─" * 36,                                         BORDER),
        (f"Remaining:          ${rem:>9,.0f}",
         SUCCESS if rem >= 0 else DANGER),
    ]
    y = H//2 - 110
    for line, col in lines:
        txt(screen, line, f_mono, col, cx=cx, cy=y)
        y += 28

    if rem < 0:
        txt(screen, f"Deficit of ${abs(rem):,.0f} added to debt.",
            f_body, DANGER, cx=cx, cy=H//2+30)
        return button(screen, (cx-75, H//2+70, 150, 44), "Continue", DANGER, f_body, mouse=mouse), None
    else:
        txt(screen, "Where does the surplus go?",
            f_body, MUTED, cx=cx, cy=H//2+30)
        s = button(screen, (cx-165, H//2+65, 145, 44),
                   "→ Savings", SUCCESS, f_body, BLACK, mouse)
        d = button(screen, (cx+20,  H//2+65, 145, 44),
                   "→ Pay Debt", DANGER, f_body, WHITE, mouse)
        return s, d


def draw_monthly_screen(mouse):
    draw_stat_panel()
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 120))
    screen.blit(ov, (0, 0))
    rr(screen, SURFACE, (W//2-320, 130, 640, 460), r=16, bw=2, bc=BORDER)

    txt(screen, "Monthly Decisions", f_head, ACCENT, cx=W//2, cy=168)
    txt(screen, "Take actions before ending the month",
        f_small, MUTED, cx=W//2, cy=194)

    p = player
    actions = [
        # (label, colour, greyed_out)
        ("Second Job" if not used_second_job else "Job Taken ✓",
         TEAL,   used_second_job),
        ("Vacation" if not used_leisure else "Leisure Used ✓",
         SUCCESS, used_leisure),
        ("Entertainment" if not used_leisure else "Leisure Used ✓",
         ACCENT,  used_leisure),
        ("Food Out: ON" if p.foodCostOut > 0 else "Food Out: OFF",
         WARN,   False),
        ("Transport: ON" if p.transportationCost > 0 else "Transport: OFF",
         WARN,   False),
        ("Misc: ON" if p.miscCost > 0 else "Misc: OFF",
         WARN,   False),
    ]
    bw, bh, gap = 170, 52, 14
    sx = W//2 - (3*(bw+gap)-gap)//2
    sy = 222
    rects = []
    for i, (label, col, greyed) in enumerate(actions):
        bx = sx + (i % 3) * (bw + gap)
        by = sy + (i // 3) * (bh + gap)
        draw_col = SURFACE2 if greyed else col
        text_col = MUTED if greyed else (
            BLACK if col in (SUCCESS, TEAL, WARN) else WHITE)
        r = button(screen, (bx, by, bw, bh), label,
                   draw_col, f_body, text_col, mouse)
        if greyed:
            pygame.draw.rect(screen, BORDER, (bx, by, bw, bh),
                             1, border_radius=8)
        rects.append(r)

    done = button(screen, (W//2-80, 415, 160, 48),
                  "Done ▶", ACCENT, f_body, mouse=mouse)
    return rects, done


def draw_stocks_screen(mouse):
    draw_stat_panel()
    modal(screen)
    cx, cy = W//2, H//2

    if stock_stage == "ask":
        txt(screen, "Invest in Stocks?", f_head, ACCENT, cx=cx, cy=cy-110)
        txt(screen, f"Your savings: ${player.savings:,.2f}",
            f_body, TEXT, cx=cx, cy=cy-65)
        portfolio_label = f"Portfolio: {len(portfolio)} holding(s)" if portfolio else "Portfolio: empty"
        txt(screen, portfolio_label, f_small, MUTED, cx=cx, cy=cy-38)
        yes = button(screen, (cx-165, cy-10, 145, 44),
                     "Yes, Invest!", ACCENT, f_body, mouse=mouse)
        no = button(screen, (cx+20,  cy-10, 145, 44), "Skip",
                    SURFACE2, f_body, MUTED, mouse)
        pygame.draw.rect(screen, BORDER, (cx+20, cy-10,
                         145, 44), 1, border_radius=8)
        view = button(screen, (cx-75, cy+50, 150, 44), "View Portfolio",
                      SURFACE2, f_body, WARN if portfolio else MUTED, mouse)
        pygame.draw.rect(screen, BORDER, (cx-75, cy+50,
                         150, 44), 1, border_radius=8)
        return yes, no, None, None, None, None, None, view

    elif stock_stage == "input":
        txt(screen, "Stock Market", f_head, ACCENT, cx=cx, cy=cy-130)
        txt(screen, f"Share price:  ${stock_price:,.2f}",
            f_body, TEXT, cx=cx, cy=cy-90)
        txt(screen, f"Savings:  ${player.savings:,.2f}",
            f_small, MUTED, cx=cx, cy=cy-62)
        txt(screen, f"Shares: {stock_shares}  (cost: ${stock_price*stock_shares:,.2f})",
            f_body, WARN, cx=cx, cy=cy-30)
        minus = button(screen, (cx-130, cy+10, 52, 52),
                       "-", SURFACE2, f_title, MUTED, mouse)
        rr(screen, BORDER, (cx-130, cy+10, 52, 52), r=8, bw=1, bc=BORDER)
        txt(screen, str(stock_shares), f_head, TEXT, cx=cx, cy=cy+36)
        plus = button(screen, (cx+78,  cy+10, 52, 52), "+",
                      SURFACE2, f_title, SUCCESS, mouse)
        rr(screen, BORDER, (cx+78, cy+10, 52, 52), r=8, bw=1, bc=BORDER)
        buy = button(screen, (cx-75,  cy+80, 150, 44),
                     "Buy", ACCENT, f_body, mouse=mouse)
        return None, None, buy, None, None, minus, plus, None

    elif stock_stage == "change":
        gain = stock_new >= stock_bought
        col = SUCCESS if gain else DANGER
        arrow = "\u25b2" if gain else "\u25bc"
        txt(screen, "Stock Market", f_head, ACCENT, cx=cx, cy=cy-130)
        txt(screen, f"You paid: ${stock_bought:,.2f}",
            f_body, TEXT, cx=cx, cy=cy-85)
        txt(screen, f"New value: ${stock_new:,.2f}  {arrow} ${abs(stock_new-stock_bought):,.2f}",
            f_head, col, cx=cx, cy=cy-45)
        txt(screen, "Sell now for cash, or Hold to sell later from your portfolio.",
            f_small, MUTED, cx=cx, cy=cy-5)
        sell = button(screen, (cx-170, cy+30, 150, 44),
                      "Sell Now", SUCCESS, f_body, BLACK, mouse)
        hold = button(screen, (cx+20,  cy+30, 150, 44),
                      "Hold", SURFACE2, f_body, MUTED, mouse)
        pygame.draw.rect(screen, BORDER, (cx+20, cy+30,
                         150, 44), 1, border_radius=8)
        return None, None, None, sell, hold, None, None, None

    elif stock_stage == "portfolio":
        txt(screen, "Your Portfolio", f_head, ACCENT, cx=cx, cy=cy-150)
        if not portfolio:
            txt(screen, "No held stocks.", f_body, MUTED, cx=cx, cy=cy-90)
        else:
            y = cy - 110
            for pos in portfolio:
                gain = pos["current"] >= pos["bought"]
                col = SUCCESS if gain else DANGER
                arrow = "\u25b2" if gain else "\u25bc"
                shares_val = pos["shares"]
                bought_val = pos["bought"]
                current_val = pos["current"]
                line = f"{shares_val} share(s) — paid ${bought_val:,.2f}  {arrow}  now ${current_val:,.2f}"
                txt(screen, line, f_body, col, cx=cx, cy=y)
                y += 30
        sell_all = button(screen, (cx-75, cy+50, 150, 44), "Sell All",
                          SUCCESS, f_body, BLACK, mouse) if portfolio else None
        close = button(screen, (cx-75, cy+110, 150, 44),
                       "Close", SURFACE2, f_body, MUTED, mouse)
        pygame.draw.rect(screen, BORDER, (cx-75, cy+110,
                         150, 44), 1, border_radius=8)
        return None, None, None, sell_all, close, None, None, None


def draw_instructions_screen(mouse):
    screen.fill(BG)
    cx = W // 2

    txt(screen, "How to Play", f_title, ACCENT, cx=cx, cy=60)

    sections = [
        ("🎯  GOAL",         SUCCESS, [
            "Pay off ALL your debt to win the game.",
            "Each month you earn income and pay rent + expenses.",
            "Route any leftover money to savings or debt repayment.",
        ]),
        ("💀  LOSE CONDITION", DANGER, [
            "If your stress level reaches 10/10, you burn out — game over.",
            "Each month with debt over $5,000: 50% chance stress rises by 1.",
            "Selling or holding a stock that lost value: 50% chance stress rises by 1.",
            "Stress also rises when you take a second job.",
            "Reduce stress by taking a vacation or buying entertainment.",
        ]),
        ("📅  EACH MONTH", TEAL, [
            "1. A random event fires — good or bad — affecting your savings.",
            "2. Your budget is calculated: income − rent − expenses.",
            "3. Surplus goes to savings or debt; a deficit grows your debt.",
            "4. Take optional decisions: second job, vacation, cut costs.",
            "5. Optionally invest in stocks — buy shares, then sell or hold.",
        ]),
        ("📈  STOCKS", WARN, [
            "Buy shares at a random price with money from savings.",
            "The price changes — sell for profit or hold (no payout).",
        ]),
    ]

    y = 120
    for title, col, lines in sections:
        rr(screen, SURFACE, (cx - 420, y, 840, 24 +
           len(lines) * 22 + 16), r=10, bw=1, bc=BORDER)
        txt(screen, title, f_head, col, x=cx - 408, y=y + 6)
        for i, line in enumerate(lines):
            txt(screen, line, f_body, TEXT, x=cx - 400, y=y + 30 + i * 22)
        y += 24 + len(lines) * 22 + 16 + 10

    return button(screen, (cx - 100, H - 70, 200, 50), "Let's Play!", ACCENT, f_head, mouse=mouse)


def draw_gameover_screen(mouse):
    screen.fill(BG)
    col = SUCCESS if win else DANGER
    msg = "DEBT FREE — YOU WIN!" if win else "BURNED OUT — GAME OVER"
    txt(screen, msg, f_big, col, cx=W//2, cy=H//2-120)
    txt(screen, f"Survived {month} month(s)",
        f_body, MUTED, cx=W//2, cy=H//2-40)
    txt(screen, f"Final debt:     ${player.debt:,.0f}",
        f_head, DANGER,  cx=W//2, cy=H//2+10)
    txt(screen, f"Final savings:  ${player.savings:,.0f}",
        f_head, SUCCESS, cx=W//2, cy=H//2+50)
    return button(screen, (W//2-90, H//2+110, 180, 50), "Play Again", ACCENT, f_head, mouse=mouse)


running = True
while running:
    clock.tick(FPS)
    mouse = pygame.mouse.get_pos()
    clicks = []
    kdowns = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicks.append(event.pos)
        if event.type == pygame.KEYDOWN:
            kdowns.append(event)

    screen.fill(BG)

    if state == STATE_NAME:
        cx, cy = W//2, H//2
        txt(screen, "Life Finance Sim", f_title, ACCENT, cx=cx, cy=cy-130)
        txt(screen, "Manage debt, savings, and stress. Survive each month.",
            f_body, MUTED, cx=cx, cy=cy-80)
        rr(screen, SURFACE2, (cx-180, cy-30, 360, 46), r=8, bw=2, bc=ACCENT)
        display = name_text if name_text else "Enter your name..."
        col = TEXT if name_text else MUTED
        txt(screen, display, f_body, col, x=cx-168, y=cy-14)
        if pygame.time.get_ticks() % 1000 < 500 and name_text is not None:
            cw = f_body.size(name_text)[0]
            pygame.draw.line(screen, TEXT, (cx-168+cw, cy-12),
                             (cx-168+cw, cy+12), 2)
        start_btn = button(screen, (cx-90, cy+38, 180, 48),
                           "Start Game", ACCENT, f_head, mouse=mouse)

        for k in kdowns:
            if k.key == pygame.K_BACKSPACE:
                name_text = name_text[:-1]
            elif k.key == pygame.K_RETURN and name_text.strip():
                player = Player(name_text.strip())
                state = STATE_INSTRUCTIONS
            elif len(name_text) < 20 and k.unicode.isprintable() and k.unicode != "":
                name_text += k.unicode
        for pos in clicks:
            if start_btn.collidepoint(pos) and name_text.strip():
                player = Player(name_text.strip())
                state = STATE_INSTRUCTIONS

    elif state == STATE_INSTRUCTIONS:
        play_btn = draw_instructions_screen(mouse)
        for pos in clicks:
            if play_btn.collidepoint(pos):
                start_month()

    elif state == STATE_EVENT:
        draw_stat_panel()
        cont = draw_event_screen(mouse)
        for pos in clicks:
            if cont.collidepoint(pos):
                push_log(pending_event["text"],
                         SUCCESS if pending_event["savings"] > 0 else DANGER)
                state = STATE_ALLOC

    elif state == STATE_ALLOC:
        draw_stat_panel()
        p = player
        exp = p.foodCostHome + p.foodCostOut + \
            p.transportationCost + p.utilitesCost + p.miscCost
        rem = p.income - exp - p.rent
        result = draw_alloc_screen(mouse)

        for pos in clicks:
            if rem < 0:
                btn = result[0]
                if btn.collidepoint(pos):
                    player.debt += abs(rem)
                    push_notif(
                        f"Deficit! +${abs(rem):,.0f} added to debt.", DANGER)
                    push_log(f"Deficit ${abs(rem):,.0f} → debt", DANGER)
                    state = STATE_MONTHLY
            else:
                sav_btn, debt_btn = result
                if sav_btn.collidepoint(pos):
                    player.savings += rem
                    clamp_savings()
                    push_notif(f"Added ${rem:,.0f} to savings!", SUCCESS)
                    push_log(f"+${rem:,.0f} to savings", SUCCESS)
                    state = STATE_MONTHLY
                if debt_btn.collidepoint(pos):
                    player.debt = max(0, player.debt - rem)
                    push_notif(f"Paid ${rem:,.0f} off debt!", WARN)
                    push_log(f"-${rem:,.0f} from debt", WARN)
                    if not check_gameover():
                        state = STATE_MONTHLY

    elif state == STATE_MONTHLY:
        rects, done = draw_monthly_screen(mouse)
        for pos in clicks:
            if done.collidepoint(pos):
                stock_stage = "ask"
                stock_shares = 0
                state = STATE_STOCKS
            for i, r in enumerate(rects):
                if r.collidepoint(pos):
                    if i == 0:
                        if used_second_job:
                            push_notif(
                                "Already took a second job this month.", MUTED)
                        else:
                            extra = player.secondJob()
                            used_second_job = True
                            push_notif(
                                f"Second job! +${extra}/mo income.", TEAL)
                            push_log(f"Second job: +${extra}/mo", TEAL)
                    elif i == 1:
                        if used_leisure:
                            push_notif(
                                "Already used leisure this month.", MUTED)
                        elif player.savings < 500:
                            push_notif(
                                "Not enough savings for vacation. (need $500)", DANGER)
                        else:
                            player.savings -= 500
                            player.adjustStress(-2)
                            clamp_savings()
                            used_leisure = True
                            push_notif("Vacation! Stress -2  (-$500)", SUCCESS)
                            push_log("Vacation (-$500, stress -2)", SUCCESS)
                    elif i == 2:
                        if used_leisure:
                            push_notif(
                                "Already used leisure this month.", MUTED)
                        elif player.savings < 150:
                            push_notif(
                                "Not enough savings for entertainment. (need $150)", DANGER)
                        else:
                            player.savings -= 150
                            player.adjustStress(-1)
                            clamp_savings()
                            used_leisure = True
                            push_notif(
                                "Entertainment! Stress -1  (-$150)", ACCENT)
                            push_log(
                                "Entertainment (-$150, stress -1)", ACCENT)
                    elif i == 3:
                        if player.foodCostOut > 0:
                            player.foodCostOut = 0
                            player.adjustStress(1)
                            push_notif("Cut food out costs. Stress +1", WARN)
                            push_log("Cut food out costs", WARN)
                        else:
                            player.foodCostOut = 250
                            player.adjustStress(-1)
                            push_notif(
                                "Turned food out back on. Stress -1", WARN)
                            push_log("Re-enabled food out costs", WARN)
                    elif i == 4:
                        if player.transportationCost > 0:
                            player.transportationCost = 0
                            player.adjustStress(1)
                            push_notif(
                                "Cut transportation costs. Stress +1", WARN)
                            push_log("Cut transportation costs", WARN)
                        else:
                            player.transportationCost = 250
                            player.adjustStress(-1)
                            push_notif(
                                "Turned transport back on. Stress -1", WARN)
                            push_log("Re-enabled transportation costs", WARN)
                    elif i == 5:
                        if player.miscCost > 0:
                            player.miscCost = 0
                            player.adjustStress(1)
                            push_notif("Cut misc costs. Stress +1", WARN)
                            push_log("Cut misc costs", WARN)
                        else:
                            player.miscCost = 200
                            player.adjustStress(-1)
                            push_notif(
                                "Turned misc costs back on. Stress -1", WARN)
                            push_log("Re-enabled misc costs", WARN)
                    check_gameover()

    elif state == STATE_STOCKS:
        result = draw_stocks_screen(mouse)
        yes_btn, no_btn, buy_btn, sell_btn, hold_btn, minus_btn, plus_btn, view_btn = result
        for pos in clicks:
            if stock_stage == "ask":
                if yes_btn and yes_btn.collidepoint(pos):
                    stock_price = round(random.uniform(10, 250), 2)
                    stock_shares = 0
                    stock_stage = "input"
                if no_btn and no_btn.collidepoint(pos):
                    if not check_gameover():
                        start_month()
                if view_btn and view_btn.collidepoint(pos):
                    # refresh current prices for all holdings
                    for holding in portfolio:
                        holding["current"] = round(
                            holding["bought"] * random.uniform(0.6, 1.6), 2)
                    stock_stage = "portfolio"
            elif stock_stage == "input":
                max_s = int(player.savings //
                            stock_price) if stock_price > 0 else 0
                if plus_btn and plus_btn.collidepoint(pos):
                    stock_shares = min(stock_shares + 1, max_s)
                if minus_btn and minus_btn.collidepoint(pos):
                    stock_shares = max(0, stock_shares - 1)
                if buy_btn and buy_btn.collidepoint(pos) and stock_shares > 0:
                    cost = round(stock_price * stock_shares, 2)
                    if cost <= player.savings:
                        player.savings -= cost
                        stock_bought = cost
                        change = 0
                        while change == 0:
                            change = round(random.uniform(-0.5, 1.0), 2)
                        stock_new = round(stock_bought * (1 + change), 2)
                        stock_stage = "change"
                        push_log(
                            f"Bought {stock_shares} shares @ ${stock_price:.2f}", WARN)
                    else:
                        push_notif("Not enough savings!", DANGER)
            elif stock_stage == "change":
                if sell_btn and sell_btn.collidepoint(pos):
                    profit = stock_new - stock_bought
                    player.savings += stock_new
                    clamp_savings()
                    if profit < 0 and random.random() < 0.5:
                        player.adjustStress(1)
                        push_notif(
                            f"Stock loss hurts. Stress +1. Sold for ${stock_new:,.2f} ({profit:,.2f})", DANGER)
                        push_log(f"Stock loss — stress +1", DANGER)
                    else:
                        push_notif(f"Sold for ${stock_new:,.2f}! ({'+'if profit >= 0 else ''}${profit:,.2f})",
                                   SUCCESS if profit >= 0 else DANGER)
                    push_log(f"Sold stock: ${stock_new:,.2f} ({'+'if profit >= 0 else ''}${profit:,.0f})",
                             SUCCESS if profit >= 0 else DANGER)
                    if not check_gameover():
                        start_month()
                if hold_btn and hold_btn.collidepoint(pos):
                    if stock_new < stock_bought and random.random() < 0.5:
                        player.adjustStress(1)
                        push_notif(
                            f"Holding a losing stock is stressful. Stress +1", DANGER)
                        push_log(f"Held losing stock — stress +1", DANGER)
                    portfolio.append({"shares": stock_shares, "bought": stock_bought,
                                      "price_per": stock_price, "current": stock_new})
                    push_notif(
                        f"Held {stock_shares} share(s). Added to portfolio.", WARN)
                    push_log(
                        f"Held {stock_shares} share(s) in portfolio", WARN)
                    if not check_gameover():
                        start_month()
            elif stock_stage == "portfolio":
                if sell_btn and sell_btn.collidepoint(pos) and portfolio:
                    total = sum(p["current"] for p in portfolio)
                    paid = sum(p["bought"] for p in portfolio)
                    player.savings += total
                    clamp_savings()
                    profit = total - paid
                    push_notif(f"Sold all holdings for ${total:,.2f}! ({'+'if profit >= 0 else ''}${profit:,.2f})",
                               SUCCESS if profit >= 0 else DANGER)
                    push_log(
                        f"Sold portfolio: ${total:,.2f}", SUCCESS if profit >= 0 else DANGER)
                    portfolio.clear()
                    stock_stage = "ask"
                if hold_btn and hold_btn.collidepoint(pos):
                    stock_stage = "ask"

    elif state == STATE_GAMEOVER:
        restart = draw_gameover_screen(mouse)
        for pos in clicks:
            if restart.collidepoint(pos):
                state = STATE_NAME
                player = None
                month = 0
                pending_event = None
                name_text = ""
                notifs = []
                log_lines = []
                stock_stage = "ask"
                stock_shares = 0
                stock_price = 0.0
                stock_bought = 0.0
                stock_new = 0.0
                win = False
                used_second_job = False
                used_leisure = False
                portfolio.clear()

    notifs = [[t, c, ttl-1] for t, c, ttl in notifs if ttl > 1]
    for i, (t, col, ttl) in enumerate(notifs[-4:]):
        alpha = int(230 * ttl / 200)
        s = pygame.Surface((400, 38), pygame.SRCALPHA)
        r2, g2, b2 = col
        pygame.draw.rect(s, (r2, g2, b2, int(alpha*0.2)),
                         (0, 0, 400, 38), border_radius=8)
        pygame.draw.rect(s, (r2, g2, b2, alpha),
                         (0, 0, 400, 38), 2, border_radius=8)
        rendered = f_body.render(t, True, (*col, alpha))
        s.blit(rendered, (12, 9))
        screen.blit(s, (W//2 - 200, H - 50 - i * 46))

    pygame.display.flip()

pygame.quit()
sys.exit()
