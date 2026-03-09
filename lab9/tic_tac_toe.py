import tkinter as tk
from tkinter import messagebox

def check_winner(board):
    
    win_conditions = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != "":
            return board[condition[0]]
    if "" not in board:
        return "Draw"
    return None


def minimax(board, is_maximizing):
    result = check_winner(board)

    if result == "O":
        return 1
    elif result == "X":
        return -1
    elif result == "Draw":
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                score = minimax(board, False)
                board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                score = minimax(board, True)
                board[i] = ""
                best_score = min(score, best_score)
        return best_score


def best_move():
    best_score = -float("inf")
    move = None
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            score = minimax(board, False)
            board[i] = ""
            if score > best_score:
                best_score = score
                move = i
    return move


def on_click(i):
    if board[i] == "" and not check_winner(board):
        board[i] = "X"
        buttons[i].config(text="X")

        winner = check_winner(board)
        if winner:
            show_result(winner)
            return

        ai_move = best_move()
        if ai_move is not None:
            board[ai_move] = "O"
            buttons[ai_move].config(text="O")

        winner = check_winner(board)
        if winner:
            show_result(winner)


def show_result(winner):
    if winner == "Draw":
        messagebox.showinfo("Game Over", "It's a Draw!")
    else:
        messagebox.showinfo("Game Over", f"{winner} Wins!")
    reset_game()


def reset_game():
    global board
    board = [""] * 9
    for button in buttons:
        button.config(text="")

root = tk.Tk()
root.title("Tic Tac Toe - Minimax AI")
root.geometry("400x500")
root.configure(bg="#F5F7FA")

board = [""] * 9
buttons = []

title = tk.Label(root, text="Tic Tac Toe", font=("Helvetica", 24, "bold"), bg="#F5F7FA")
title.pack(pady=20)

frame = tk.Frame(root, bg="#F5F7FA")
frame.pack()

for i in range(9):
    button = tk.Button(
        frame,
        text="",
        font=("Helvetica", 32),
        width=5,
        height=2,
        bg="white",
        fg="#333",
        relief="ridge",
        command=lambda i=i: on_click(i)
    )
    button.grid(row=i//3, column=i%3, padx=5, pady=5)
    buttons.append(button)

reset_btn = tk.Button(root, text="Reset Game", font=("Helvetica", 14), command=reset_game)
reset_btn.pack(pady=20)

root.mainloop()
