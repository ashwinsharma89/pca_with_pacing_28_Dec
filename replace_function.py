"""
Script to replace render_deep_dive_page() function in streamlit_modular.py
"""

# Read the new function
with open('render_deep_dive_page_NEW.py', 'r', encoding='utf-8') as f:
    new_function_content = f.read()

# Remove the comment lines at the top
new_function_lines = new_function_content.split('\n')
# Skip first 3 lines (comments)
new_function = '\n'.join(new_function_lines[3:])

# Read the original file
with open('streamlit_modular.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the function boundaries
start_line = None
end_line = None

for i, line in enumerate(lines):
    if line.strip().startswith('def render_deep_dive_page():'):
        start_line = i
    elif start_line is not None and line.strip().startswith('def render_visualizations_page():'):
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"ERROR: Could not find function boundaries")
    print(f"start_line: {start_line}, end_line: {end_line}")
    exit(1)

print(f"Found function at lines {start_line+1} to {end_line}")
print(f"Replacing {end_line - start_line} lines with new function")

# Replace the function
new_lines = lines[:start_line] + [new_function + '\n\n'] + lines[end_line:]

# Write back
with open('streamlit_modular.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Successfully replaced render_deep_dive_page() function!")
print(f"   Old: {end_line - start_line} lines")
print(f"   New: {len(new_function.split(chr(10)))} lines")
