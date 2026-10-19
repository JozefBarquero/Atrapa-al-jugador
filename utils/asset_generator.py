import os
from config import ASSETS_DIR, COLOR_PLAYER, COLOR_PLAYER_2, COLOR_COMPUTER, COLOR_GOAL, COLOR_NODE

def create_svg_circle(color, path_file, inner_type="none"):
    inner_svg = ""
    if inner_type == "player":
        inner_svg = '<circle cx="50" cy="50" r="15" fill="#ffffff" opacity="0.6"/>'
    elif inner_type == "player2":
        inner_svg = '<rect x="35" y="35" width="30" height="30" fill="#ffffff" opacity="0.6"/>'
    elif inner_type == "computer":
        inner_svg = '<line x1="35" y1="35" x2="65" y2="65" stroke="#ffffff" stroke-width="8" opacity="0.6" stroke-linecap="round"/><line x1="35" y1="65" x2="65" y2="35" stroke="#ffffff" stroke-width="8" opacity="0.6" stroke-linecap="round"/>'
        
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="45" fill="{color}" stroke="#4a4238" stroke-width="4"/>
    {inner_svg}
    </svg>"""
    with open(path_file, "w") as f:
        f.write(svg_content)

def create_svg_star(color, path_file):
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35" fill="{color}" stroke="#4a4238" stroke-width="4"/>
    </svg>"""
    with open(path_file, "w") as f:
        f.write(svg_content)

def create_svg_sound_on(path_file):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <polygon points="20,40 40,40 60,20 60,80 40,60 20,60" fill="#e1ebf5"/>
    <path d="M 70 30 Q 85 50 70 70" fill="none" stroke="#e1ebf5" stroke-width="6" stroke-linecap="round"/>
    <path d="M 80 20 Q 100 50 80 80" fill="none" stroke="#e1ebf5" stroke-width="6" stroke-linecap="round"/>
    </svg>"""
    with open(path_file, "w") as f:
        f.write(svg_content)

def create_svg_sound_off(path_file):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <polygon points="20,40 40,40 60,20 60,80 40,60 20,60" fill="#a0b4c8"/>
    <line x1="70" y1="30" x2="90" y2="70" stroke="#e17888" stroke-width="6" stroke-linecap="round"/>
    <line x1="90" y1="30" x2="70" y2="70" stroke="#e17888" stroke-width="6" stroke-linecap="round"/>
    </svg>"""
    with open(path_file, "w") as f:
        f.write(svg_content)

def generate_assets():
    nodes_dir = os.path.join(ASSETS_DIR, "nodes")
    icons_dir = os.path.join(ASSETS_DIR, "icons")
    os.makedirs(nodes_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    
    c_player = f"rgb({COLOR_PLAYER[0]},{COLOR_PLAYER[1]},{COLOR_PLAYER[2]})"
    c_player2 = f"rgb({COLOR_PLAYER_2[0]},{COLOR_PLAYER_2[1]},{COLOR_PLAYER_2[2]})"
    c_computer = f"rgb({COLOR_COMPUTER[0]},{COLOR_COMPUTER[1]},{COLOR_COMPUTER[2]})"
    c_goal = f"rgb({COLOR_GOAL[0]},{COLOR_GOAL[1]},{COLOR_GOAL[2]})"
    c_node = f"rgb({COLOR_NODE[0]},{COLOR_NODE[1]},{COLOR_NODE[2]})"
    
    create_svg_circle(c_node, os.path.join(nodes_dir, "node.svg"))
    create_svg_circle(c_player, os.path.join(nodes_dir, "player.svg"), "player")
    create_svg_circle(c_player2, os.path.join(nodes_dir, "player2.svg"), "player2")
    create_svg_circle(c_computer, os.path.join(nodes_dir, "computer.svg"), "computer")
    create_svg_star(c_goal, os.path.join(nodes_dir, "goal.svg"))
    
    create_svg_sound_on(os.path.join(icons_dir, "sound_on.svg"))
    create_svg_sound_off(os.path.join(icons_dir, "sound_off.svg"))