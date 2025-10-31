# streamlit_gm_league_app.py
import streamlit as st
import pandas as pd
from copy import deepcopy
import io

# --------------------------- Helper functions ---------------------------

def default_data():
    """Return initial default groups with teams and stats."""
    return {
        "Group A": [
            {"Team": "OG HINATA GAMING", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "RVS GAMING", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "LRP ESPORTS", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "TSS GAMING", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
        ],
        "Group B": [
            {"Team": "WAR GOD", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "AURA ACES", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "RV SQUAD", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "NAMMA RIVALS", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
        ],
        "Group C": [
            {"Team": "RK GAM", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "V CHAMPS", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "TEAM X", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "SQUAD LEGENDS", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
        ],
        "Group D": [
            {"Team": "NINJA FORCE", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "STEALTH", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "PHOENIX", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
            {"Team": "RISING SUN", "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0},
        ],
    }

def compute_pd(wins, losses):
    return int(wins) - int(losses)

def compute_pdt(pd, rounds_won):
    return int(pd) + int(rounds_won)

def compute_total(pd, pdt, rounds_won):
    # Per Option A: Total = PD + PDT + RoundsWon
    return int(pd) + int(pdt) + int(rounds_won)

def df_from_group(teams_list):
    """Create DataFrame with the requested columns: Rank, Team Name, Matches Played, Win, Loss, Rounds Won, PD, PDT, Total"""
    if not teams_list:
        df = pd.DataFrame(columns=["Rank","Team Name","Matches Played","Win","Loss","Rounds Won","PD","PDT","Total"])
        return df
    rows = []
    for t in teams_list:
        team = {
            "Team Name": t.get("Team",""),
            "Matches Played": int(t.get("Matches",0)),
            "Win": int(t.get("Wins",0)),
            "Loss": int(t.get("Losses",0)),
            "Rounds Won": int(t.get("RoundsWon",0))
        }
        pd_val = compute_pd(team["Win"], team["Loss"])
        pdt_val = compute_pdt(pd_val, team["Rounds Won"])
        total_val = compute_total(pd_val, pdt_val, team["Rounds Won"])
        team["PD"] = pd_val
        team["PDT"] = pdt_val
        team["Total"] = total_val
        rows.append(team)
    df = pd.DataFrame(rows)
    # sort by Total desc, then PD desc, then Rounds Won desc
    df = df.sort_values(by=["Total","PD","Rounds Won"], ascending=[False, False, False]).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df)+1))
    return df

def render_table_with_badges(df):
    """Return HTML for a neon-styled table with gold/silver/bronze badges."""
    css = """
    <style>
    .gm-wrap { overflow-x:auto; padding:6px; }
    .neon-table { width:100%; border-collapse: collapse; font-family: 'Inter', Arial, sans-serif; color:#e6eef8; }
    .neon-table th, .neon-table td { padding:10px 12px; text-align:left; border-bottom:1px solid rgba(255,255,255,0.03); }
    .neon-table thead th { color:#9be7ff; font-weight:700; font-size:14px; }
    .badge { padding:6px 10px; border-radius:14px; font-weight:800; display:inline-block; min-width:34px; text-align:center; box-shadow: 0 4px 18px rgba(0,0,0,0.6); }
    .gold { background: linear-gradient(90deg,#ffd700,#ffdf6a); color:#111; box-shadow: 0 8px 30px rgba(255,215,0,0.18); }
    .silver { background: linear-gradient(90deg,#c0c0c0,#d6d6d6); color:#111; box-shadow: 0 8px 30px rgba(192,192,192,0.12); }
    .bronze { background: linear-gradient(90deg,#cd7f32,#d99a6b); color:#111; box-shadow: 0 8px 30px rgba(205,127,50,0.12); }
    .row-highlight { background: linear-gradient(90deg, rgba(125,211,252,0.03), transparent); }
    .neon-header { text-align:center; padding:14px 0; }
    .brand { font-size:22px; color:#ffd700; font-weight:900; text-shadow: 0 0 14px rgba(255, 215, 0, 0.25); }
    .lead { font-size:18px; color:#7dd3fc; font-weight:800; text-shadow: 0 0 8px rgba(125,211,252,0.10); }
    @media (max-width: 700px) {
        .neon-table th, .neon-table td { padding:6px 8px; font-size:12px; }
        .badge { min-width:28px; padding:4px 8px; }
    }
    </style>
    """
    html = css + '<div class="gm-wrap"><table class="neon-table" border="0">'
    html += "<thead><tr>"
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        rank = int(row["Rank"])
        badge = f"<span class='badge'>{rank}</span>"
        if rank == 1:
            badge = f"<span class='badge gold'>1</span>"
        elif rank == 2:
            badge = f"<span class='badge silver'>2</span>"
        elif rank == 3:
            badge = f"<span class='badge bronze'>3</span>"
        html += "<tr>"
        html += f"<td>{badge}</td>"
        for col in df.columns[1:]:
            html += f"<td>{row[col]}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    return html

def apply_match_result(group_name, match_results):
    """
    Apply match results to teams in a group.
    match_results: list of dicts: [{'Team': name, 'PlacementRank': int, 'RoundsWon': int}]
    Rules:
    - If PlacementRank == 1 => count as Win, else if PlacementRank > 1 => Loss
    - Matches increments by 1 for any team with placed rank or rounds entered
    - RoundsWon increments by provided
    """
    group = st.session_state.groups.get(group_name, [])
    name_to_idx = {t['Team']: i for i, t in enumerate(group)}
    for res in match_results:
        name = res.get('Team')
        if name not in name_to_idx:
            continue
        idx = name_to_idx[name]
        # increment matches only if there's meaningful data
        st.session_state.groups[group_name][idx]['Matches'] += 1
        pr = res.get('PlacementRank', 0)
        if pr == 1:
            st.session_state.groups[group_name][idx]['Wins'] += 1
        elif pr > 1:
            st.session_state.groups[group_name][idx]['Losses'] += 1
        # update rounds
        st.session_state.groups[group_name][idx]['RoundsWon'] += int(res.get('RoundsWon', 0))

def group_to_csv_bytes(group_name):
    df = df_from_group(st.session_state.groups.get(group_name, []))
    buf = io.StringIO()
    # export columns in the requested order for persistence/import
    export_df = df.rename(columns={
        "Team Name": "Team",
        "Matches Played": "Matches",
        "Win": "Wins",
        "Loss": "Losses",
        "Rounds Won": "RoundsWon",
        "PD": "PD",
        "PDT": "PDT",
        "Total": "Total"
    })
    export_df.to_csv(buf, index=False)
    return buf.getvalue().encode('utf-8')

# --------------------------- Session State Init ---------------------------
if 'groups' not in st.session_state:
    st.session_state.groups = default_data()

if 'pending_delete' not in st.session_state:
    st.session_state.pending_delete = None

# --------------------------- Page styling & header ---------------------------
st.set_page_config(page_title="GM League S-1 — Points Manager", layout='wide')
page_css = """
<style>
body { background: #03060a; color: #e6eef8; }
.app-shell { padding: 10px 18px; }
.neon-top { text-align:center; margin-bottom:8px; }
.small-note { color: #9fbfdc; font-size:12px; opacity:0.9; }
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

# Neon header
st.markdown("""
<div class="neon-header">
  <div class="brand">GAMING MARVEL PRESENTS</div>
  <div class="lead">GM LEAGUE S-1 — Interactive Points Manager</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# --------------------------- Sidebar: persistence ---------------------------
st.sidebar.header("Persistence & Export/Import")
if st.session_state.groups:
    export_group = st.sidebar.selectbox("Choose group to export CSV", options=list(st.session_state.groups.keys()))
    csv_bytes = group_to_csv_bytes(export_group)
    st.sidebar.download_button(label=f"Download {export_group} CSV", data=csv_bytes, file_name=f"{export_group.replace(' ','_')}_points.csv", mime='text/csv')

st.sidebar.markdown("---")
st.sidebar.markdown("**Import CSV into Group** (replace group's teams)\n\nCSV columns expected: Team, Matches, Wins, Losses, RoundsWon")
if st.session_state.groups:
    import_group = st.sidebar.selectbox("Select group to import into", options=list(st.session_state.groups.keys()))
else:
    import_group = None

uploaded = st.sidebar.file_uploader("Upload CSV for selected group", type=['csv'])
if uploaded and import_group:
    try:
        df_in = pd.read_csv(uploaded)
        required = set(["Team","Matches","Wins","Losses","RoundsWon"])
        if not required.issubset(df_in.columns):
            st.sidebar.error("CSV missing required columns. Required: Team, Matches, Wins, Losses, RoundsWon")
        else:
            new_list = []
            for _, r in df_in.iterrows():
                new_list.append({
                    'Team': str(r['Team']),
                    'Matches': int(r.get('Matches',0)),
                    'Wins': int(r.get('Wins',0)),
                    'Losses': int(r.get('Losses',0)),
                    'RoundsWon': int(r.get('RoundsWon',0)),
                })
            st.session_state.groups[import_group] = new_list
            st.sidebar.success(f"Imported {len(new_list)} teams into {import_group}.")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to parse CSV: {e}")

st.sidebar.markdown("---")
if st.sidebar.button("Reset All to Default"):
    st.session_state.groups = default_data()
    st.rerun()

# --------------------------- Add new group UI ---------------------------
with st.expander("Add New Group"):
    with st.form("add_group_form"):
        new_group_name = st.text_input("Group Name (e.g. Group E)")
        teams_text = st.text_area("Team Names (one per line)", help="Enter each team name on its own line")
        submitted = st.form_submit_button("Create Group")
        if submitted:
            if not new_group_name.strip():
                st.error("Please enter a group name.")
            elif new_group_name.strip() in st.session_state.groups:
                st.error("A group with that name already exists.")
            else:
                team_names = [t.strip() for t in teams_text.splitlines() if t.strip()]
                if not team_names:
                    st.error("Please provide at least one team name (one per line).")
                else:
                    st.session_state.groups[new_group_name.strip()] = [
                        {"Team": tn, "Matches": 0, "Wins": 0, "Losses": 0, "RoundsWon": 0}
                        for tn in team_names
                    ]
                    st.success(f"Group '{new_group_name.strip()}' created with {len(team_names)} teams.")
                    st.rerun()

# --------------------------- Tabs for groups ---------------------------
if not st.session_state.groups:
    st.info("No groups yet. Add a group using the form above.")
else:
    tabs = st.tabs(list(st.session_state.groups.keys()))
    for tab, group_name in zip(tabs, list(st.session_state.groups.keys())):
        with tab:
            st.subheader(group_name)
            group = st.session_state.groups.get(group_name, [])

            # Render points table
            df = df_from_group(group)
            html = render_table_with_badges(df)
            st.markdown(html, unsafe_allow_html=True)

            st.markdown("---")
            left, right = st.columns([2,1])

            # Left: Match-level input & manual edit
            with left:
                st.markdown("### Record Match Result (auto-update stats)")
                st.markdown("Enter each participating team's **Placement Rank** and **Rounds Won**. Placement Rank == 1 counts as a Win; >1 counts as Loss.")
                if group:
                    with st.form(f"match_form_{group_name}"):
                        match_entries = []
                        for t in group:
                            cols = st.columns([1,1])
                            with cols[0]:
                                rank = st.number_input(f"Rank - {t['Team']}", min_value=0, value=0, key=f"rank_{group_name}_{t['Team']}")
                            with cols[1]:
                                rwon = st.number_input(f"RoundsWon - {t['Team']}", min_value=0, value=0, key=f"r_{group_name}_{t['Team']}")
                            match_entries.append({'Team': t['Team'], 'PlacementRank': int(rank), 'RoundsWon': int(rwon)})
                        apply_match = st.form_submit_button("Apply Match Result")
                        if apply_match:
                            filtered = [m for m in match_entries if (m['PlacementRank']>0 or m['RoundsWon']>0)]
                            if not filtered:
                                st.warning("No match data entered — nothing to apply.")
                            else:
                                apply_match_result(group_name, filtered)
                                st.success("Match applied. Table updated.")
                                st.rerun()
                else:
                    st.info("No teams in this group.")

                st.markdown("---")
                st.markdown("### Manual Team Edit")
                team_names = [t['Team'] for t in group]
                if team_names:
                    selected = st.selectbox("Select Team to Edit", team_names, key=f"select_{group_name}_edit")
                    team_idx = next((i for i, t in enumerate(group) if t['Team'] == selected), None)
                    if team_idx is not None:
                        team = deepcopy(group[team_idx])
                        with st.form(f"edit_form_{group_name}"):
                            matches = st.number_input("Matches Played", min_value=0, value=int(team.get("Matches", 0)), step=1)
                            wins = st.number_input("Wins", min_value=0, value=int(team.get("Wins", 0)), step=1)
                            losses = st.number_input("Losses", min_value=0, value=int(team.get("Losses", 0)), step=1)
                            rounds = st.number_input("Rounds Won", min_value=0, value=int(team.get("RoundsWon", 0)), step=1)
                            update = st.form_submit_button("Update Team")
                            if update:
                                st.session_state.groups[group_name][team_idx]['Matches'] = int(matches)
                                st.session_state.groups[group_name][team_idx]['Wins'] = int(wins)
                                st.session_state.groups[group_name][team_idx]['Losses'] = int(losses)
                                st.session_state.groups[group_name][team_idx]['RoundsWon'] = int(rounds)
                                st.success(f"Updated '{selected}'. Table recalculated.")
                                st.rerun()
                else:
                    st.info("No teams to edit in this group.")

            # Right column: delete group and CSV download
            with right:
                st.markdown("### Group Actions")
                if st.button("Delete Group", key=f"del_{group_name}"):
                    st.session_state.pending_delete = group_name
                if st.session_state.pending_delete == group_name:
                    st.warning(f"Confirm deletion of '{group_name}' — this cannot be undone.")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirm Delete", key=f"confirm_{group_name}"):
                        del st.session_state.groups[group_name]
                        st.session_state.pending_delete = None
                        st.rerun()
                    if c2.button("Cancel", key=f"cancel_{group_name}"):
                        st.session_state.pending_delete = None

                st.markdown("---")
                st.markdown("**Export Points CSV**")
                csv_bytes = group_to_csv_bytes(group_name)
                st.download_button(
    label=f"Download {group_name} CSV",
    data=csv_bytes,
    file_name=f"{group_name.replace(' ','_')}_points.csv",
    mime="text/csv",
    key=f"download_{group_name}"
)


st.markdown("---")
st.caption("Neon UI active. Table columns: Rank, Team Name, Matches Played, Win, Loss, Rounds Won, PD, PDT, Total. PD = Wins - Losses; PDT = PD + RoundsWon; Total = PD + PDT + RoundsWon.")
