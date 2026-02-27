import streamlit as st
import random
import copy
import streamlit.components.v1 as components

st.set_page_config(page_title="🎮 Game Arcade", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0a0f;
    color: #e0e0e0;
}
h1, h2, h3 { font-family: 'Orbitron', monospace; }
.stApp { background: radial-gradient(ellipse at top, #0d0d2b 0%, #0a0a0f 70%); }
.game-card {
    border: 2px solid #2a2a5a;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    background: linear-gradient(135deg, #0f0f2e, #1a1a3e);
    margin: 1rem 0;
}
.score-box {
    display: inline-block;
    background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
    border: 1px solid #5a3a8a;
    border-radius: 12px;
    padding: 0.6rem 1.5rem;
    margin: 0.3rem;
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    color: #c8a8ff;
}
div[data-testid="column"] .stButton > button {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    height: 90px;
    width: 100%;
    border-radius: 12px;
    border: 2px solid #2a2a5a;
    background: #0f0f2e;
    color: #e0e0e0;
    transition: all 0.2s ease;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #7b5ea7;
    background: #1a1a3e;
    box-shadow: 0 0 15px rgba(123,94,167,0.5);
}
.stButton > button {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    border-radius: 10px;
    border: 1px solid #5a3a8a;
    background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
    color: #c8a8ff;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a1a4e, #3a2a6e);
    box-shadow: 0 0 15px rgba(123,94,167,0.4);
    border-color: #9b7ec7;
}
.status-msg {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    text-align: center;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.win-msg  { background: linear-gradient(135deg, #0a2a0a, #1a4a1a); border: 1px solid #4aff4a; color: #4aff4a; }
.draw-msg { background: linear-gradient(135deg, #2a2a0a, #3a3a1a); border: 1px solid #ffcc00; color: #ffcc00; }
.turn-msg { background: linear-gradient(135deg, #0a0a2a, #1a1a3e); border: 1px solid #5a5aff; color: #aaaaff; }
.hint-msg {
    background: linear-gradient(135deg, #2a1a0a, #3a2a1a);
    border: 1px solid #ff9944;
    color: #ff9944;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    text-align: center;
    padding: 0.7rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ───
def init_state():
    defaults = {
        "screen": "menu",
        "ttt_board": [""] * 9,
        "ttt_turn": "X",
        "ttt_winner": None,
        "ttt_game_over": False,
        "score_x": 0,
        "score_o": 0,
        "score_draw": 0,
        "sudoku_puzzle": None,
        "sudoku_solution": None,
        "sudoku_user": None,
        "sudoku_hint_msg": "",
        "sudoku_locked": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── SUDOKU LOGIC ───
def is_valid(board, row, col, num):
    if num in board[row]: return False
    if num in [board[r][col] for r in range(9)]: return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num: return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if solve(board): return True
                        board[r][c] = 0
                return False
    return True

def generate_sudoku(clues=35):
    board = [[0] * 9 for _ in range(9)]
    solve(board)
    solution = copy.deepcopy(board)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:81 - clues]:
        board[r][c] = 0
    return board, solution

def new_sudoku_game():
    puzzle, solution = generate_sudoku()
    st.session_state.sudoku_puzzle = puzzle
    st.session_state.sudoku_solution = solution
    st.session_state.sudoku_user = copy.deepcopy(puzzle)
    st.session_state.sudoku_locked = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
    st.session_state.sudoku_hint_msg = ""


# ─── TIC TAC TOE LOGIC ───
WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_winner(board):
    for a, b, c in WINS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board): return "Draw"
    return None


def render_sudoku_board(puzzle, user, locked, solution, hint_cell=None):
    """Render a fully interactive sudoku board using HTML/JS."""

    # Flatten data for JS
    puzzle_flat = [puzzle[r][c] for r in range(9) for c in range(9)]
    user_flat   = [user[r][c]   for r in range(9) for c in range(9)]
    locked_flat = [1 if locked[r][c] else 0 for r in range(9) for c in range(9)]
    sol_flat    = [solution[r][c] for r in range(9) for c in range(9)]

    hint_idx = hint_cell[0] * 9 + hint_cell[1] if hint_cell else -1

    html = f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
      body {{ background: transparent; margin: 0; padding: 0; }}

      #sudoku-wrap {{
        display: flex;
        justify-content: center;
        padding: 10px 0;
      }}

      table.sudoku {{
        border-collapse: collapse;
        border: 3px solid #9b7ec7;
      }}

      table.sudoku td {{
        width: 52px;
        height: 52px;
        text-align: center;
        vertical-align: middle;
        padding: 0;
        border: 1px solid #3a3a6a;
        background: #0f0f2e;
        position: relative;
      }}

      /* Thick borders for 3x3 boxes */
      table.sudoku td.thick-top    {{ border-top: 3px solid #9b7ec7; }}
      table.sudoku td.thick-left   {{ border-left: 3px solid #9b7ec7; }}
      table.sudoku td.thick-bottom {{ border-bottom: 3px solid #9b7ec7; }}
      table.sudoku td.thick-right  {{ border-right: 3px solid #9b7ec7; }}

      table.sudoku td.selected {{ background: #1e1e4a !important; }}

      table.sudoku td span {{
        font-family: 'Orbitron', monospace;
        font-size: 1.2rem;
        font-weight: 700;
        user-select: none;
        cursor: default;
      }}
      table.sudoku td span.given  {{ color: #c8a8ff; }}
      table.sudoku td span.hint   {{ color: #ff9944; }}
      table.sudoku td span.user-val {{ color: #7adfff; cursor: pointer; }}
      table.sudoku td span.wrong  {{ color: #ff4a4a; cursor: pointer; }}

      table.sudoku td.editable {{ cursor: pointer; }}
      table.sudoku td.editable:hover {{ background: #1a1a3e; }}

      #numpad {{
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 14px;
        flex-wrap: wrap;
      }}
      #numpad button {{
        width: 46px;
        height: 46px;
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
        color: #c8a8ff;
        border: 2px solid #5a3a8a;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s;
      }}
      #numpad button:hover {{
        background: linear-gradient(135deg, #2a1a5e, #3a2a6e);
        border-color: #9b7ec7;
        box-shadow: 0 0 10px rgba(123,94,167,0.5);
      }}
      #numpad button.erase {{
        width: 60px;
        font-size: 0.85rem;
        color: #ff9944;
        border-color: #ff9944;
      }}

      #solve-status {{
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        margin-top: 12px;
        color: #4aff4a;
        min-height: 28px;
      }}
    </style>

    <div id="sudoku-wrap">
      <table class="sudoku" id="board"></table>
    </div>
    <div id="numpad">
      <button onclick="enterNum(1)">1</button>
      <button onclick="enterNum(2)">2</button>
      <button onclick="enterNum(3)">3</button>
      <button onclick="enterNum(4)">4</button>
      <button onclick="enterNum(5)">5</button>
      <button onclick="enterNum(6)">6</button>
      <button onclick="enterNum(7)">7</button>
      <button onclick="enterNum(8)">8</button>
      <button onclick="enterNum(9)">9</button>
      <button class="erase" onclick="enterNum(0)">✕ Erase</button>
    </div>
    <div id="solve-status"></div>

    <script>
      const puzzle  = {puzzle_flat};
      const userVal = {user_flat};
      const locked  = {locked_flat};
      const sol     = {sol_flat};
      const hintIdx = {hint_idx};

      let selected = -1;

      function buildBoard() {{
        const table = document.getElementById('board');
        table.innerHTML = '';
        for (let r = 0; r < 9; r++) {{
          const tr = document.createElement('tr');
          for (let c = 0; c < 9; c++) {{
            const idx = r * 9 + c;
            const td = document.createElement('td');

            // Thick border classes
            if (r % 3 === 0) td.classList.add('thick-top');
            if (c % 3 === 0) td.classList.add('thick-left');
            if (r === 8)     td.classList.add('thick-bottom');
            if (c === 8)     td.classList.add('thick-right');

            if (locked[idx]) {{
              const span = document.createElement('span');
              span.textContent = userVal[idx] || '';
              span.className = (idx === hintIdx) ? 'hint' : 'given';
              td.appendChild(span);
            }} else {{
              td.classList.add('editable');
              td.dataset.idx = idx;
              if (selected === idx) td.classList.add('selected');

              if (userVal[idx] !== 0) {{
                const span = document.createElement('span');
                span.textContent = userVal[idx];
                const isWrong = userVal[idx] !== sol[idx];
                span.className = isWrong ? 'wrong' : 'user-val';
                td.appendChild(span);
              }}

              td.addEventListener('click', () => {{
                selected = idx;
                buildBoard();
              }});
            }}
            tr.appendChild(td);
          }}
          table.appendChild(tr);
        }}
        checkSolved();
      }}

      function enterNum(n) {{
        if (selected === -1 || locked[selected]) return;
        userVal[selected] = n;
        buildBoard();
      }}

      document.addEventListener('keydown', (e) => {{
        if (selected === -1) return;
        if (e.key >= '1' && e.key <= '9') enterNum(parseInt(e.key));
        if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') enterNum(0);

        // Arrow key navigation
        let r = Math.floor(selected / 9);
        let c = selected % 9;
        if (e.key === 'ArrowRight') c = Math.min(8, c + 1);
        if (e.key === 'ArrowLeft')  c = Math.max(0, c - 1);
        if (e.key === 'ArrowDown')  r = Math.min(8, r + 1);
        if (e.key === 'ArrowUp')    r = Math.max(0, r - 1);
        selected = r * 9 + c;
        buildBoard();
      }});

      function checkSolved() {{
        const allFilled = userVal.every((v, i) => v !== 0);
        const allCorrect = userVal.every((v, i) => v === sol[i]);
        const status = document.getElementById('solve-status');
        if (allFilled && allCorrect) {{
          status.textContent = '🎉 Puzzle Solved! Congratulations!';
        }} else {{
          status.textContent = '';
        }}
      }}

      buildBoard();
    </script>
    """

    components.html(html, height=620, scrolling=False)


# ─── MENU ───
if st.session_state.screen == "menu":
    st.markdown("<h1 style='text-align:center; color:#c8a8ff; margin-bottom:0.2rem;'>🎮 GAME ARCADE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7a7aaa; margin-bottom:2rem;'>Choose your game</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='game-card'><div style='font-size:3rem'>⭕</div><h3 style='color:#c8a8ff;'>Tic Tac Toe</h3><p style='color:#7a7aaa;'>2 Players · Track scores · Classic fun</p></div>", unsafe_allow_html=True)
        if st.button("▶ Play Tic Tac Toe", key="go_ttt", use_container_width=True):
            st.session_state.screen = "ttt"
            st.rerun()
    with col2:
        st.markdown("<div class='game-card'><div style='font-size:3rem'>🔢</div><h3 style='color:#c8a8ff;'>Sudoku</h3><p style='color:#7a7aaa;'>Solo · Hints · Infinite puzzles</p></div>", unsafe_allow_html=True)
        if st.button("▶ Play Sudoku", key="go_sudoku", use_container_width=True):
            if st.session_state.sudoku_puzzle is None:
                new_sudoku_game()
            st.session_state.screen = "sudoku"
            st.rerun()


# ─── TIC TAC TOE ───
elif st.session_state.screen == "ttt":
    st.markdown("<h2 style='text-align:center; color:#c8a8ff;'>⭕ Tic Tac Toe</h2>", unsafe_allow_html=True)

    sx, so, sd = st.session_state.score_x, st.session_state.score_o, st.session_state.score_draw
    st.markdown(f"""
    <div style='text-align:center; margin-bottom:1rem;'>
        <span class='score-box'>✖ Player X &nbsp; {sx}</span>
        <span class='score-box'>🤝 Draws &nbsp; {sd}</span>
        <span class='score-box'>⭕ Player O &nbsp; {so}</span>
    </div>""", unsafe_allow_html=True)

    board = st.session_state.ttt_board
    winner = st.session_state.ttt_winner
    game_over = st.session_state.ttt_game_over

    if winner == "Draw":
        st.markdown("<div class='status-msg draw-msg'>🤝 It's a Draw!</div>", unsafe_allow_html=True)
    elif winner:
        st.markdown(f"<div class='status-msg win-msg'>🏆 Player {winner} Wins!</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='status-msg turn-msg'>Turn: Player {st.session_state.ttt_turn}</div>", unsafe_allow_html=True)

    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            label = board[idx] if board[idx] else " "
            with cols[col]:
                if st.button(label, key=f"ttt_{idx}", disabled=game_over or bool(board[idx])):
                    board[idx] = st.session_state.ttt_turn
                    result = check_winner(board)
                    if result:
                        st.session_state.ttt_winner = result
                        st.session_state.ttt_game_over = True
                        if result == "X": st.session_state.score_x += 1
                        elif result == "O": st.session_state.score_o += 1
                        else: st.session_state.score_draw += 1
                    else:
                        st.session_state.ttt_turn = "O" if st.session_state.ttt_turn == "X" else "X"
                    st.rerun()

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 New Round", use_container_width=True):
            st.session_state.ttt_board = [""] * 9
            st.session_state.ttt_turn = "X"
            st.session_state.ttt_winner = None
            st.session_state.ttt_game_over = False
            st.rerun()
    with c2:
        if st.button("🏠 Main Menu", use_container_width=True):
            st.session_state.screen = "menu"
            st.rerun()


# ─── SUDOKU ───
elif st.session_state.screen == "sudoku":
    st.markdown("<h2 style='text-align:center; color:#c8a8ff;'>🔢 Sudoku</h2>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 New Puzzle", use_container_width=True):
            new_sudoku_game()
            st.rerun()
    with c2:
        if st.button("💡 Hint", use_container_width=True):
            user = st.session_state.sudoku_user
            sol  = st.session_state.sudoku_solution
            locked = st.session_state.sudoku_locked
            empties = [(r, c) for r in range(9) for c in range(9) if not locked[r][c] and user[r][c] == 0]
            if empties:
                r, c = random.choice(empties)
                user[r][c] = sol[r][c]
                locked[r][c] = True
                st.session_state.sudoku_hint_msg = f"💡 Hint: Row {r+1}, Col {c+1} → {sol[r][c]}"
            else:
                st.session_state.sudoku_hint_msg = "✅ All cells are filled!"
            st.rerun()
    with c3:
        if st.button("🏠 Main Menu", use_container_width=True):
            st.session_state.screen = "menu"
            st.rerun()

    if st.session_state.sudoku_hint_msg:
        st.markdown(f"<div class='hint-msg'>{st.session_state.sudoku_hint_msg}</div>", unsafe_allow_html=True)

    # Find hint cell if any (most recently hinted)
    hint_cell = None
    if st.session_state.sudoku_hint_msg and "→" in st.session_state.sudoku_hint_msg:
        locked = st.session_state.sudoku_locked
        puzzle = st.session_state.sudoku_puzzle
        for r in range(9):
            for c in range(9):
                if locked[r][c] and puzzle[r][c] == 0:
                    hint_cell = (r, c)

    render_sudoku_board(
        st.session_state.sudoku_puzzle,
        st.session_state.sudoku_user,
        st.session_state.sudoku_locked,
        st.session_state.sudoku_solution,
        hint_cell=hint_cell
    )