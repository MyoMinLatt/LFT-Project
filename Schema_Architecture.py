from graphviz import Digraph

# Create the main directed graph
G = Digraph('G', filename='schema_architecture', format='png')
G.attr(rankdir='LR')  # Layout left-to-right
G.attr('node', shape='box', style='filled', fontsize='10')

# --- Database folder ---
with G.subgraph(name='cluster_database') as c:
    c.attr(label='Database', color='lightblue')
    c.node('db_connection.py')
    c.node('queries.py')
    c.node('models.py')

# --- Services folder ---
with G.subgraph(name='cluster_services') as c:
    c.attr(label='Services', color='lightgreen')
    c.node('auth_service.py')
    c.node('data_service.py')

# --- Routes folder ---
with G.subgraph(name='cluster_routes') as c:
    c.attr(label='Routes', color='yellow')
    c.node('main_route.py')
    c.node('user_route.py')

# --- Templates folder ---
with G.subgraph(name='cluster_templates') as c:
    c.attr(label='Templates', color='orange')
    c.node('index.html')
    c.node('dashboard.html')

# --- Static folder ---
with G.subgraph(name='cluster_static') as c:
    c.attr(label='Static', color='pink')
    c.node('style.css')
    c.node('script.js')

# --- Example connections (dependencies) ---
G.edge('main_route.py', 'auth_service.py')
G.edge('main_route.py', 'data_service.py')
G.edge('auth_service.py', 'db_connection.py')
G.edge('data_service.py', 'queries.py')
G.edge('dashboard.html', 'style.css')
G.edge('dashboard.html', 'script.js')

# Render diagram
G.render(view=True)