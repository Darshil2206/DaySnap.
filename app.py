"""
DaySnap – Plan your day in a snap
A minimal, fast daily productivity app built with Streamlit.
"""

import streamlit as st
import json
import os
from datetime import date, timedelta

# ─────────────────────────────────────────────
# CONFIG & PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DaySnap – Plan your day in a snap",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# DATA PERSISTENCE – JSON FILES
# ─────────────────────────────────────────────
DATA_FILE = "daysnap_data.json"

def load_data() -> dict:
    """Load persisted data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_data(data: dict) -> None:
    """Persist data to JSON file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass

# ─────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────
def init_state() -> None:
    """Bootstrap all session-state keys from persisted JSON + defaults."""
    persisted = load_data()
    today_str = date.today().isoformat()

    # ---------- dark mode ----------
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = persisted.get("dark_mode", False)

    # ---------- daily reset (always read last_date from JSON – source of truth) ----------
    # Using JSON instead of session_state here so date changes are always detected,
    # even within the same browser session (e.g. when testing by editing the JSON).
    saved_date   = persisted.get("last_date", today_str)
    saved_streak = persisted.get("streak", 0)

    if "last_date" not in st.session_state:
        st.session_state.last_date = saved_date

    # Auto-reset tasks & routines when a new day begins
    if saved_date != today_str:
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()
        was_consecutive = saved_date == yesterday_str   # exactly 1 day gap

        old_tasks    = persisted.get("tasks", [])
        old_routines = persisted.get("routines", {})

        # BUG FIX: all([]) == True, so require at least one task to exist
        tasks_completed    = len(old_tasks) > 0 and all(t.get("done") for t in old_tasks)
        # Routines: at least one habit must be checked (not all-False)
        routines_completed = any(old_routines.values()) if old_routines else False

        previous_day_done = tasks_completed or routines_completed

        if was_consecutive and previous_day_done:
            new_streak = saved_streak + 1
        else:
            # Either missed a day, or had a consecutive day but did nothing
            new_streak = 0

        st.session_state.streak    = new_streak
        st.session_state.tasks     = []
        st.session_state.routines  = {h: False for h in DEFAULT_HABITS}
        st.session_state.last_date = today_str

        save_data({
            "streak":    new_streak,
            "tasks":     [],
            "routines":  st.session_state.routines,
            "last_date": today_str,
            "dark_mode": st.session_state.dark_mode,
        })
        return

    # ---------- load today's data (same day) ----------
    if "tasks" not in st.session_state:
        st.session_state.tasks = persisted.get("tasks", [])

    if "streak" not in st.session_state:
        st.session_state.streak = saved_streak

    if "routines" not in st.session_state:
        saved_routines = persisted.get("routines", {})
        st.session_state.routines = {
            h: saved_routines.get(h, False) for h in DEFAULT_HABITS
        }

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
DEFAULT_HABITS = [
    "🌅  Wake up early",
    "🏃  Exercise",
    "📚  Study",
    "💧  Drink water",
]

MOTIVATIONAL = {
    (0, 0):   ("Let's crush today! ⚡", ""),
    (1, 25):  ("Good start 🚀", ""),
    (26, 50): ("You're rolling! 💪", ""),
    (51, 75): ("Over halfway there 🎯", ""),
    (76, 99): ("Almost done 🔥", ""),
    (100, 100): ("All done! You're amazing 🏆", ""),
}

def motivational_message(pct: int) -> str:
    for (lo, hi), (msg, _) in MOTIVATIONAL.items():
        if lo <= pct <= hi:
            return msg
    return ""

# ─────────────────────────────────────────────
# PERSIST HELPER
# ─────────────────────────────────────────────
def persist() -> None:
    save_data({
        "streak":    st.session_state.streak,
        "tasks":     st.session_state.tasks,
        "routines":  st.session_state.routines,
        "last_date": st.session_state.last_date,
        "dark_mode": st.session_state.dark_mode,
    })

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
def inject_css(dark: bool) -> None:
    if dark:
        bg        = "#0f0f13"
        surface   = "#1a1a24"
        card      = "#22223a"
        text      = "#e8e8f0"
        sub_text  = "#8888aa"
        accent    = "#7c6af7"
        accent2   = "#a78bfa"
        done_col  = "#4ade80"
        border    = "#2e2e4a"
        input_bg  = "#1a1a2e"
        btn_bg    = "#7c6af7"
        btn_hover = "#6b5ce7"
        del_col   = "#f87171"
        bar_bg    = "#2e2e4a"
    else:
        bg        = "#f5f5fb"
        surface   = "#ffffff"
        card      = "#ffffff"
        text      = "#1e1e2e"
        sub_text  = "#6b7280"
        accent    = "#6d5fff"
        accent2   = "#a78bfa"
        done_col  = "#16a34a"
        border    = "#e5e7eb"
        input_bg  = "#f9f9ff"
        btn_bg    = "#6d5fff"
        btn_hover = "#5b4de8"
        del_col   = "#ef4444"
        bar_bg    = "#e5e7eb"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* ── main background ── */
        .stApp {{
            background: {bg};
            color: {text};
        }}

        /* ── hide streamlit chrome ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 680px;
        }}

        /* ── card component ── */
        .ds-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 20px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 16px rgba(0,0,0,{0.18 if dark else 0.06});
            transition: box-shadow .2s ease;
        }}

        /* ── header area ── */
        .ds-header {{
            text-align: center;
            margin-bottom: 0.5rem;
        }}
        .ds-logo {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, {accent}, {accent2});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }}
        .ds-tagline {{
            font-size: 0.85rem;
            color: {sub_text};
            margin-top: -4px;
        }}
        .ds-date {{
            font-size: 1rem;
            font-weight: 600;
            color: {sub_text};
            text-align: center;
            margin-top: 0.4rem;
        }}

        /* ── streak badge ── */
        .ds-streak {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: linear-gradient(135deg, {accent}, {accent2});
            color: #fff;
            padding: 6px 18px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 1rem;
            justify-content: center;
            width: 100%;
            margin: 0.6rem 0;
            box-shadow: 0 4px 14px rgba(109,95,255,0.35);
        }}

        /* ── section titles ── */
        .ds-section-title {{
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: {sub_text};
            margin-bottom: 0.75rem;
        }}

        /* ── task items ── */
        .ds-task {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 12px;
            margin-bottom: 6px;
            background: {surface};
            border: 1px solid {border};
            transition: background .15s ease, opacity .15s ease;
        }}
        .ds-task.done-task {{
            opacity: 0.55;
        }}
        .ds-task-text {{
            flex: 1;
            font-size: 0.97rem;
            color: {text};
            word-break: break-word;
        }}
        .ds-task-text.done-text {{
            text-decoration: line-through;
            color: {sub_text};
        }}

        /* ── progress bar ── */
        .ds-prog-wrap {{
            background: {bar_bg};
            border-radius: 999px;
            height: 8px;
            overflow: hidden;
            margin: 0.5rem 0 0.3rem;
        }}
        .ds-prog-bar {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, {accent}, {accent2});
            transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
        }}
        .ds-prog-label {{
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: {sub_text};
            margin-top: 4px;
        }}

        /* ── motivational message ── */
        .ds-motiv {{
            text-align: center;
            font-size: 0.88rem;
            font-weight: 600;
            color: {accent2};
            padding: 4px 0 8px;
        }}

        /* ── routine items ── */
        .ds-habit {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 12px;
            border-radius: 12px;
            margin-bottom: 6px;
            background: {surface};
            border: 1px solid {border};
            font-size: 0.95rem;
        }}
        .ds-habit.done-habit {{
            background: {'#1a2e1a' if dark else '#f0fdf4'};
            border-color: {'#2d6a2d' if dark else '#bbf7d0'};
            color: {done_col};
            font-weight: 500;
        }}

        /* ── empty state ── */
        .ds-empty {{
            text-align: center;
            color: {sub_text};
            font-size: 0.9rem;
            padding: 1.2rem 0;
        }}

        /* ── button overrides ── */
        .stButton > button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(109,95,255,0.3) !important;
        }}

        /* ── text input ── */
        .stTextInput > div > div > input {{
            background: {input_bg} !important;
            border: 1.5px solid {border} !important;
            border-radius: 12px !important;
            color: {text} !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.97rem !important;
            padding: 0.6rem 1rem !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px {'rgba(124,106,247,0.25)' if dark else 'rgba(109,95,255,0.15)'} !important;
        }}

        /* ── checkbox style ── */
        .stCheckbox label span {{
            font-size: 0.95rem !important;
            color: {text} !important;
        }}

        /* ── divider ── */
        hr {{
            border-color: {border} !important;
            margin: 1.2rem 0 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────

def render_header() -> None:
    """Top section: logo, tagline, date, streak, dark-mode toggle."""
    col_left, col_right = st.columns([4, 1])
    with col_left:
        st.markdown(
            '<div class="ds-logo">⚡ DaySnap</div>'
            '<div class="ds-tagline">Plan your day in a snap</div>',
            unsafe_allow_html=True,
        )
    with col_right:
        icon = "☀️" if st.session_state.dark_mode else "🌙"
        if st.button(icon, key="toggle_dark", help="Toggle dark/light mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            persist()
            st.rerun()

    today = date.today()
    day_name  = today.strftime("%A")
    full_date = today.strftime("%B %d, %Y")
    st.markdown(f'<div class="ds-date">📅 {day_name}, {full_date}</div>', unsafe_allow_html=True)

    # ── Real-time streak: check if today is already "complete" ──────────────
    tasks         = st.session_state.tasks
    routines      = st.session_state.routines
    tasks_done    = len(tasks) > 0 and all(t.get("done") for t in tasks)
    routines_done = any(routines.values())
    today_complete = tasks_done or routines_done

    # Display streak = previous streak + 1 if today is done, else base streak
    base_streak    = st.session_state.streak
    display_streak = base_streak + 1 if today_complete else base_streak

    if today_complete:
        label = f"🔥 {display_streak} Day Streak  ✅ Today Complete!"
    elif display_streak > 0:
        label = f"🔥 {display_streak} Day Streak"
    else:
        label = "🌱 Start your streak today!"

    st.markdown(f'<div class="ds-streak">{label}</div>', unsafe_allow_html=True)


def render_task_section() -> None:
    """Middle section: task input + task list."""
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">📝 Today\'s Tasks</div>', unsafe_allow_html=True)

    # ── add task form ──────────────────────────
    with st.form("add_task_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            new_task = st.text_input(
                "task",
                placeholder="What do you want to get done? ✍️",
                label_visibility="collapsed",
                key="task_input",
            )
        with col_btn:
            submitted = st.form_submit_button("＋", use_container_width=True)

    if submitted:
        task_text = new_task.strip()
        if task_text:
            existing = [t["text"].lower() for t in st.session_state.tasks]
            if task_text.lower() not in existing:
                st.session_state.tasks.append({"text": task_text, "done": False})
                persist()
                st.rerun()
            else:
                st.warning("This task already exists!", icon="⚠️")
        else:
            st.warning("Please enter a task first!", icon="✏️")

    # ── task list ──────────────────────────────
    tasks = st.session_state.tasks
    if not tasks:
        st.markdown(
            '<div class="ds-empty">No tasks yet – add one above to get started! 👆</div>',
            unsafe_allow_html=True,
        )
    else:
        to_delete = None
        for i, task in enumerate(tasks):
            done_cls  = "done-task"  if task["done"] else ""
            text_cls  = "done-text"  if task["done"] else ""
            check_sym = "✅" if task["done"] else "⬜"

            col_chk, col_txt, col_del = st.columns([1, 8, 1])
            with col_chk:
                checked = st.checkbox(
                    " ",
                    value=task["done"],
                    key=f"chk_{i}",
                    label_visibility="collapsed",
                )
                if checked != task["done"]:
                    st.session_state.tasks[i]["done"] = checked
                    persist()
                    st.rerun()
            with col_txt:
                style = "text-decoration:line-through;opacity:0.55;" if task["done"] else ""
                st.markdown(
                    f'<div style="padding-top:6px;font-size:0.97rem;{style}">{task["text"]}</div>',
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("🗑️", key=f"del_{i}", help="Delete task"):
                    to_delete = i

        if to_delete is not None:
            st.session_state.tasks.pop(to_delete)
            persist()
            st.rerun()

    # ── progress ───────────────────────────────
    total = len(tasks)
    done  = sum(1 for t in tasks if t.get("done"))
    pct   = int(done / total * 100) if total else 0

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ds-prog-wrap">
            <div class="ds-prog-bar" style="width:{pct}%"></div>
        </div>
        <div class="ds-prog-label">
            <span>{done}/{total} tasks completed</span>
            <span>{pct}%</span>
        </div>
        <div class="ds-motiv">{motivational_message(pct)}</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)   # close ds-card


def render_routine_section() -> None:
    """Bottom section: daily habit checklist."""
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">🌿 Daily Routine</div>', unsafe_allow_html=True)

    habits = st.session_state.routines
    changed = False

    for habit in DEFAULT_HABITS:
        done = habits.get(habit, False)
        col_chk, col_lbl = st.columns([1, 9])
        with col_chk:
            new_val = st.checkbox(
                " ",
                value=done,
                key=f"habit_{habit}",
                label_visibility="collapsed",
            )
        with col_lbl:
            style = "text-decoration:line-through;opacity:0.6;" if new_val else ""
            st.markdown(
                f'<div style="padding-top:6px;font-size:0.95rem;{style}">{habit}</div>',
                unsafe_allow_html=True,
            )
        if new_val != done:
            st.session_state.routines[habit] = new_val
            changed = True

    if changed:
        # Persist the updated routine state; streak is calculated at day-rollover only
        persist()
        st.rerun()

    # ── routine progress ───────────────────────
    total   = len(DEFAULT_HABITS)
    done_ct = sum(1 for v in habits.values() if v)
    pct     = int(done_ct / total * 100) if total else 0

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ds-prog-wrap">
            <div class="ds-prog-bar" style="width:{pct}%"></div>
        </div>
        <div class="ds-prog-label">
            <span>{done_ct}/{total} habits checked</span>
            <span>{pct}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)   # close ds-card


def render_clear_button() -> None:
    """Utility: clear all tasks for the day."""
    with st.expander("⚙️ Options"):
        if st.button("🗑️  Clear all tasks", use_container_width=True):
            st.session_state.tasks = []
            persist()
            st.rerun()
        if st.button("🔄  Reset routine", use_container_width=True):
            st.session_state.routines = {h: False for h in DEFAULT_HABITS}
            persist()
            st.rerun()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    init_state()
    inject_css(st.session_state.dark_mode)

    render_header()
    st.markdown("<br>", unsafe_allow_html=True)
    render_task_section()
    render_routine_section()
    render_clear_button()

    # Footer
    st.markdown(
        "<br><div style='text-align:center;font-size:0.78rem;opacity:0.4;'>Made with ⚡ DaySnap</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
