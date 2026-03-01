import streamlit as st
import random
import copy
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Arcade", layout="centered")

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
    border: 2px solid #2a2a5a; border-radius: 16px; padding: 2rem;
    text-align: center; background: linear-gradient(135deg, #0f0f2e, #1a1a3e);
    margin: 1rem 0; height: 220px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.score-box {
    display: inline-block; background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
    border: 1px solid #5a3a8a; border-radius: 12px; padding: 0.6rem 1.5rem;
    margin: 0.3rem; font-family: 'Orbitron', monospace; font-size: 1rem; color: #c8a8ff;
}
div[data-testid="column"] .stButton > button {
    font-family: 'Orbitron', monospace; font-size: 2rem; font-weight: 900;
    height: 90px; width: 100%; border-radius: 12px; border: 2px solid #2a2a5a;
    background: #0f0f2e; color: #e0e0e0; transition: all 0.2s ease;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #7b5ea7; background: #1a1a3e; box-shadow: 0 0 15px rgba(123,94,167,0.5);
}
.stButton > button {
    font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1rem;
    border-radius: 10px; border: 1px solid #5a3a8a;
    background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
    color: #c8a8ff; padding: 0.5rem 1.5rem; transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a1a4e, #3a2a6e);
    box-shadow: 0 0 15px rgba(123,94,167,0.4); border-color: #9b7ec7;
}
.status-msg {
    font-family: 'Orbitron', monospace; font-size: 1.2rem; text-align: center;
    padding: 1rem; border-radius: 10px; margin: 1rem 0;
}
.win-msg  { background: linear-gradient(135deg,#0a2a0a,#1a4a1a); border:1px solid #4aff4a; color:#4aff4a; }
.draw-msg { background: linear-gradient(135deg,#2a2a0a,#3a3a1a); border:1px solid #ffcc00; color:#ffcc00; }
.turn-msg { background: linear-gradient(135deg,#0a0a2a,#1a1a3e); border:1px solid #5a5aff; color:#aaaaff; }
.hint-msg {
    background: linear-gradient(135deg,#2a1a0a,#3a2a1a); border:1px solid #ff9944;
    color:#ff9944; font-family:'Rajdhani',sans-serif; font-size:1rem;
    text-align:center; padding:0.7rem; border-radius:8px; margin:0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


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
        "sudoku_hints": [],
        "sudoku_selected": -1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def is_valid(board, row, col, num):
    if num in board[row]: return False
    if num in [board[r][col] for r in range(9)]: return False
    br, bc = (row//3)*3, (col//3)*3
    for r in range(br, br+3):
        for c in range(bc, bc+3):
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
    board = [[0]*9 for _ in range(9)]
    solve(board)
    solution = copy.deepcopy(board)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    for r, c in cells[:81-clues]:
        board[r][c] = 0
    return board, solution

def new_sudoku_game():
    puzzle, solution = generate_sudoku()
    st.session_state.sudoku_puzzle   = puzzle
    st.session_state.sudoku_solution = solution
    st.session_state.sudoku_user     = copy.deepcopy(puzzle)
    st.session_state.sudoku_locked   = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
    st.session_state.sudoku_hint_msg = ""
    st.session_state.sudoku_hints    = []
    st.session_state.sudoku_selected = -1

WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_winner(board):
    for a, b, c in WINS:
        if board[a] and board[a] == board[b] == board[c]: return board[a]
    if all(board): return "Draw"
    return None


def render_sudoku(user, locked, sol, hints, selected_idx):
    u  = [user[r][c]               for r in range(9) for c in range(9)]
    lk = [1 if locked[r][c] else 0 for r in range(9) for c in range(9)]
    s  = [sol[r][c]                for r in range(9) for c in range(9)]
    h  = [1 if (r,c) in hints else 0 for r in range(9) for c in range(9)]

    u_js   = "[" + ",".join(str(x) for x in u)  + "]"
    lk_js  = "[" + ",".join(str(x) for x in lk) + "]"
    s_js   = "[" + ",".join(str(x) for x in s)  + "]"
    h_js   = "[" + ",".join(str(x) for x in h)  + "]"
    sel_js = str(selected_idx)

    html = (
        '<!DOCTYPE html><html><head><meta charset="UTF-8">'
        '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">'
        '<style>'
        '* { box-sizing:border-box; margin:0; padding:0; }'
        'body { background:transparent; display:flex; flex-direction:column; align-items:center; padding:10px 0; font-family:Rajdhani,sans-serif; }'
        '.wrap { background:linear-gradient(135deg,#0a0a1e,#0f0f2e); border-radius:16px; padding:16px;'
        '  box-shadow:0 0 60px rgba(123,94,167,0.25),0 0 120px rgba(123,94,167,0.1); }'
        'table.sudoku { border-collapse:collapse; border:3px solid #9b7ec7; }'
        'table.sudoku td { width:54px; height:54px; text-align:center; vertical-align:middle;'
        '  font-family:Orbitron,monospace; font-size:1.25rem; font-weight:700;'
        '  border:1px solid #2a2a5a; background:#0c0c22; cursor:pointer; padding:0;'
        '  user-select:none; transition:background 0.12s,box-shadow 0.12s; }'
        'table.sudoku td:hover { background:#1a1a3e; }'
        'table.sudoku td.bt { border-top:3px solid #9b7ec7; }'
        'table.sudoku td.bl { border-left:3px solid #9b7ec7; }'
        'table.sudoku td.given  { color:#c8a8ff; cursor:default; }'
        'table.sudoku td.given:hover { background:#0c0c22; }'
        'table.sudoku td.hinted { color:#ff9944; background:#180e00; cursor:default; }'
        'table.sudoku td.hinted:hover { background:#180e00; }'
        'table.sudoku td.correct { color:#4aff4a; background:#001800; }'
        'table.sudoku td.wrong   { color:#ff4a4a; background:#1a0000; }'
        'table.sudoku td.selected { background:#1e1e4a !important; box-shadow:inset 0 0 0 2px #9b7ec7; color:#ffffff; }'
        '#numpad { display:flex; gap:8px; margin-top:16px; justify-content:center; flex-wrap:wrap; }'
        '#numpad button { width:48px; height:48px; font-family:Orbitron,monospace; font-size:1.1rem; font-weight:700;'
        '  background:linear-gradient(135deg,#1a1a3e,#2a1a4e); color:#c8a8ff; border:2px solid #5a3a8a;'
        '  border-radius:10px; cursor:pointer; transition:all 0.15s; }'
        '#numpad button:hover { background:linear-gradient(135deg,#2a1a5e,#3a2a6e); border-color:#9b7ec7;'
        '  box-shadow:0 0 12px rgba(123,94,167,0.5); transform:translateY(-1px); }'
        '#numpad button.erase { width:62px; font-size:0.75rem; letter-spacing:0.5px; color:#ff9944; border-color:#ff9944; }'
        '#numpad button.erase:hover { background:linear-gradient(135deg,#2a1000,#3a1500); box-shadow:0 0 12px rgba(255,153,68,0.4); }'
        '#info { font-family:Rajdhani,sans-serif; font-size:0.92rem; color:#7a7aaa; text-align:center; margin-top:12px; min-height:22px; }'
        '#solved-msg { font-family:Orbitron,monospace; font-size:1.1rem; color:#4aff4a; text-align:center;'
        '  margin-top:10px; min-height:26px; text-shadow:0 0 10px rgba(74,255,74,0.5); }'
        '</style></head><body>'
        '<div class="wrap"><table class="sudoku" id="board"></table></div>'
        '<div id="numpad">'
        '<button onclick="enterNum(1)">1</button>'
        '<button onclick="enterNum(2)">2</button>'
        '<button onclick="enterNum(3)">3</button>'
        '<button onclick="enterNum(4)">4</button>'
        '<button onclick="enterNum(5)">5</button>'
        '<button onclick="enterNum(6)">6</button>'
        '<button onclick="enterNum(7)">7</button>'
        '<button onclick="enterNum(8)">8</button>'
        '<button onclick="enterNum(9)">9</button>'
        '<button class="erase" onclick="enterNum(0)">ERASE</button>'
        '</div>'
        '<div id="info">Click any empty cell to select it</div>'
        '<div id="solved-msg"></div>'
        '<script>'
        'var U='   + u_js   + ';'
        'var LK='  + lk_js  + ';'
        'var S='   + s_js   + ';'
        'var H='   + h_js   + ';'
        'var sel=' + sel_js + ';'
        'function build(){'
        '  var tbl=document.getElementById("board");'
        '  tbl.innerHTML="";'
        '  for(var r=0;r<9;r++){'
        '    var tr=document.createElement("tr");'
        '    for(var c=0;c<9;c++){'
        '      var i=r*9+c;'
        '      var td=document.createElement("td");'
        '      var cl=[];'
        '      if(r%3===0)cl.push("bt");'
        '      if(c%3===0)cl.push("bl");'
        '      if(H[i]){'
        '        cl.push("hinted");'
        '        td.textContent=U[i]||"";'
        '      } else if(LK[i]){'
        '        cl.push("given");'
        '        td.textContent=U[i]||"";'
        '      } else {'
        '        if(i===sel)cl.push("selected");'
        '        if(U[i]!==0){td.textContent=U[i];cl.push(U[i]===S[i]?"correct":"wrong");}'
        '        (function(idx){td.addEventListener("click",function(){sel=idx;build();info();push();});})(i);'
        '      }'
        '      td.className=cl.join(" ");'
        '      tr.appendChild(td);'
        '    }'
        '    tbl.appendChild(tr);'
        '  }'
        '}'
        'function enterNum(n){'
        '  if(sel<0||LK[sel]||H[sel])return;'
        '  U[sel]=n;build();push();checkSolved();'
        '}'
        'function info(){'
        '  var el=document.getElementById("info");'
        '  if(sel<0){el.textContent="Click any empty cell to select it";return;}'
        '  if(LK[sel]||H[sel]){el.textContent="This cell is fixed";return;}'
        '  var r=Math.floor(sel/9)+1,c=(sel%9)+1;'
        '  el.textContent="Row "+r+", Col "+c+" selected  |  type or click a number below";'
        '}'
        'function push(){'
        '  try{'
        '    var url=new URL(window.parent.location.href);'
        '    url.searchParams.set("sv",U.join(","));'
        '    url.searchParams.set("ss",sel);'
        '    window.parent.history.replaceState({},"",url.toString());'
        '  }catch(e){}'
        '}'
        'function checkSolved(){'
        '  if(U.every(function(v,i){return v===S[i];}))'
        '    document.getElementById("solved-msg").textContent="Puzzle Solved!";'
        '}'
        'document.addEventListener("keydown",function(e){'
        '  if(e.key>="1"&&e.key<="9"){enterNum(parseInt(e.key));return;}'
        '  if(e.key==="Backspace"||e.key==="Delete"){enterNum(0);return;}'
        '  if(sel<0)return;'
        '  var r=Math.floor(sel/9),c=sel%9;'
        '  if(e.key==="ArrowRight")c=Math.min(8,c+1);'
        '  if(e.key==="ArrowLeft")c=Math.max(0,c-1);'
        '  if(e.key==="ArrowDown")r=Math.min(8,r+1);'
        '  if(e.key==="ArrowUp")r=Math.max(0,r-1);'
        '  sel=r*9+c;build();info();push();'
        '});'
        'build();info();'
        '</script></body></html>'
    )
    components.html(html, height=660, scrolling=False)


# ══════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════

if st.session_state.screen == "menu":
    st.markdown("""
    <div style='text-align:center; margin-bottom:0.2rem;'>
        <div style='font-size:2.5rem; margin-bottom:6px;'>&#x1F3AE;</div>
        <h1 style='font-family:Orbitron,monospace; color:#c8a8ff; font-size:2rem; margin:0;'>GAME ARCADE</h1>
    </div>
    <p style='text-align:center; color:#7a7aaa; margin-bottom:2rem;'>Choose your game and let the fun begin!</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='game-card'>
            <div style='font-size:2.8rem; margin-bottom:8px;'>&#x274C;&#x2B55;</div>
            <h3 style='color:#c8a8ff; margin:0 0 8px 0;'>Tic Tac Toe</h3>
            <p style='color:#7a7aaa; font-size:0.9rem;'>&#x1F465; 2 Players &middot; &#x1F3C6; Track scores &middot; &#x2694;&#xFE0F; Classic fun</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("&#x25B6; Play Tic Tac Toe", key="go_ttt", use_container_width=True):
            st.session_state.screen = "ttt"
            st.rerun()
    with col2:
        st.markdown("""
        <div class='game-card'>
            <div style='font-size:2.8rem; margin-bottom:8px;'>&#x1F9E9;</div>
            <h3 style='color:#c8a8ff; margin:0 0 8px 0;'>Sudoku</h3>
            <p style='color:#7a7aaa; font-size:0.9rem;'>&#x1F9D1; Solo &middot; &#x1F4A1; Hints &middot; &#x267E;&#xFE0F; Infinite puzzles</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("&#x25B6; Play Sudoku", key="go_sudoku", use_container_width=True):
            if st.session_state.sudoku_puzzle is None:
                new_sudoku_game()
            st.session_state.screen = "sudoku"
            st.rerun()


elif st.session_state.screen == "ttt":
    st.markdown("""
    <div style='text-align:center; margin-bottom:0.8rem;'>
        <div style='font-size:2rem; margin-bottom:4px;'>&#x274C; &amp; &#x2B55;</div>
        <h2 style='font-family:Orbitron,monospace; color:#c8a8ff; font-size:1.6rem; margin:0;'>Tic Tac Toe</h2>
    </div>
    """, unsafe_allow_html=True)

    sx = st.session_state.score_x
    so = st.session_state.score_o
    sd = st.session_state.score_draw
    st.markdown(f"""
    <div style='text-align:center; margin-bottom:1rem;'>
        <span class='score-box'>&#x274C; &nbsp; {sx}</span>
        <span class='score-box'>&#x1F91D; Draw &nbsp; {sd}</span>
        <span class='score-box'>&#x2B55; &nbsp; {so}</span>
    </div>""", unsafe_allow_html=True)

    board     = st.session_state.ttt_board
    winner    = st.session_state.ttt_winner
    game_over = st.session_state.ttt_game_over

    if winner == "Draw":
        st.markdown("<div class='status-msg draw-msg'>&#x1F91D; It's a Draw!</div>", unsafe_allow_html=True)
    elif winner:
        emoji = "&#x274C;" if winner == "X" else "&#x2B55;"
        st.markdown(f"<div class='status-msg win-msg'>{emoji} Player {winner} Wins! &#x1F3C6;</div>", unsafe_allow_html=True)
    else:
        emoji = "&#x274C;" if st.session_state.ttt_turn == "X" else "&#x2B55;"
        st.markdown(f"<div class='status-msg turn-msg'>&#x1F3AF; Turn: {emoji} Player {st.session_state.ttt_turn}</div>", unsafe_allow_html=True)

    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx   = row*3+col
            label = board[idx] if board[idx] else " "
            with cols[col]:
                if st.button(label, key=f"ttt_{idx}", disabled=game_over or bool(board[idx])):
                    board[idx] = st.session_state.ttt_turn
                    result = check_winner(board)
                    if result:
                        st.session_state.ttt_winner    = result
                        st.session_state.ttt_game_over = True
                        if result == "X":   st.session_state.score_x    += 1
                        elif result == "O": st.session_state.score_o    += 1
                        else:               st.session_state.score_draw += 1
                    else:
                        st.session_state.ttt_turn = "O" if st.session_state.ttt_turn == "X" else "X"
                    st.rerun()

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("&#x1F504; New Round", use_container_width=True):
            st.session_state.ttt_board     = [""] * 9
            st.session_state.ttt_turn      = "X"
            st.session_state.ttt_winner    = None
            st.session_state.ttt_game_over = False
            st.rerun()
    with c2:
        if st.button("&#x1F3E0; Main Menu", use_container_width=True):
            st.session_state.screen = "menu"
            st.rerun()


elif st.session_state.screen == "sudoku":
    st.markdown("""
    <div style='text-align:center; margin-bottom:0.5rem;'>
        <div style='font-size:1.8rem; margin-bottom:4px;'>&#x1F9E9;</div>
        <h2 style='font-family:Orbitron,monospace; color:#c8a8ff; font-size:1.6rem; margin:0;'>Sudoku</h2>
    </div>
    """, unsafe_allow_html=True)

    params = st.query_params
    if "sv" in params and st.session_state.sudoku_locked is not None:
        try:
            vals = [int(x) for x in params["sv"].split(",")]
            if len(vals) == 81:
                for r in range(9):
                    for c in range(9):
                        if not st.session_state.sudoku_locked[r][c]:
                            st.session_state.sudoku_user[r][c] = vals[r*9+c]
        except: pass
    if "ss" in params:
        try:
            st.session_state.sudoku_selected = int(params["ss"])
        except: pass

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("&#x1F504; New Puzzle", use_container_width=True):
            new_sudoku_game()
            st.query_params.clear()
            st.rerun()
    with c2:
        if st.button("&#x1F4A1; Hint", use_container_width=True):
            sel    = st.session_state.sudoku_selected
            user   = st.session_state.sudoku_user
            sol    = st.session_state.sudoku_solution
            locked = st.session_state.sudoku_locked
            if sel < 0:
                st.session_state.sudoku_hint_msg = "&#x26A0;&#xFE0F; Select a cell first, then click Hint"
            else:
                sr, sc = sel//9, sel%9
                if locked[sr][sc]:
                    st.session_state.sudoku_hint_msg = "&#x26A0;&#xFE0F; That cell is already filled in"
                elif user[sr][sc] == sol[sr][sc] and user[sr][sc] != 0:
                    st.session_state.sudoku_hint_msg = "&#x2705; That cell is already correct"
                else:
                    user[sr][sc]   = sol[sr][sc]
                    locked[sr][sc] = True
                    st.session_state.sudoku_hints.append((sr, sc))
                    st.session_state.sudoku_hint_msg = (
                        "&#x1F4A1; Hint: Row " + str(sr+1) + ", Col " + str(sc+1) + " = " + str(sol[sr][sc])
                    )
            st.rerun()
    with c3:
        if st.button("&#x1F3E0; Main Menu", use_container_width=True):
            st.session_state.screen = "menu"
            st.query_params.clear()
            st.rerun()

    if st.session_state.sudoku_hint_msg:
        st.markdown(
            "<div class='hint-msg'>" + st.session_state.sudoku_hint_msg + "</div>",
            unsafe_allow_html=True
        )

    render_sudoku(
        st.session_state.sudoku_user,
        st.session_state.sudoku_locked,
        st.session_state.sudoku_solution,
        st.session_state.sudoku_hints,
        st.session_state.sudoku_selected,
    )
