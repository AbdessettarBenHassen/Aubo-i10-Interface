import sqlite3

DB_PATH = "/root/AuboRobotWorkSpace/teachpendant/share/teachpendant/database/tool_coord_param.db"

def fetch_all_tool_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tool_name FROM tool_param")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

def get_full_tool_data(tool_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get related kinematics & dynamics
    cursor.execute("SELECT kinematics_name, dynamics_name FROM tool_param WHERE tool_name = ?", (tool_name,))
    kin_name, dyn_name = cursor.fetchone()

    cursor.execute("SELECT * FROM tool_kinematics_param WHERE kinematics_name = ?", (kin_name,))
    kin_data = cursor.fetchone()
    kin_columns = [desc[0] for desc in cursor.description]

    cursor.execute("SELECT * FROM tool_dynamics_param WHERE dynamics_name = ?", (dyn_name,))
    dyn_data = cursor.fetchone()
    dyn_columns = [desc[0] for desc in cursor.description]

    conn.close()
    return {
        'tool_name': tool_name,
        'kinematics': dict(zip(kin_columns, kin_data)),
        'dynamics': dict(zip(dyn_columns, dyn_data))
    }
