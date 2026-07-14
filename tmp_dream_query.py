import sqlite3, json, sys

DB = r'C:\Users\sinch\.local\share\mimocode\mimocode.db'
SESSION = 'ses_09f6aeb20ffeAwOhKIl4ohZ01L'

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute('''
    SELECT m.id, json_extract(m.data, '$.role') as role
    FROM message m 
    WHERE m.session_id = ?
    ORDER BY m.time_created
''', (SESSION,))
msgs = c.fetchall()
print(f'=== Session: {len(msgs)} messages ===')

for msg_id, role in msgs:
    c.execute('''
        SELECT id, json_extract(data, '$.type') as ptype, 
               json_extract(data, '$.text') as text,
               json_extract(data, '$.tool') as tool,
               substr(data, 1, 800) as preview
        FROM part 
        WHERE message_id = ?
        ORDER BY time_created
    ''', (msg_id,))
    parts = c.fetchall()
    print(f'\n--- {role} (msg {msg_id}) ---')
    for pid, ptype, text, tool, preview in parts:
        if ptype == 'text':
            t = text or ''
            print(f'  TEXT: {t[:500]}')
        elif ptype == 'tool':
            print(f'  TOOL: {tool}')
            try:
                pd = json.loads(preview)
                state = pd.get('state', {})
                inp = str(state.get('input', ''))[:300]
                out = str(state.get('output', ''))[:500]
                print(f'    INPUT: {inp}')
                print(f'    OUTPUT: {out}')
            except:
                print(f'    (parse failed)')
        elif ptype in ('step-start', 'step-finish'):
            if ptype == 'step-finish':
                try:
                    pd = json.loads(preview)
                    tokens = pd.get('tokens', '')
                    print(f'  STEP-FINISH tokens={tokens}')
                except:
                    print(f'  {ptype}')
            else:
                print(f'  {ptype}')
        else:
            print(f'  {ptype}: {str(preview)[:300]}')
conn.close()
