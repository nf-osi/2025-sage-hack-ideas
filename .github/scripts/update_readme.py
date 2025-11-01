#!/usr/bin/env python3
"""
Update README.md with issue information when an issue with 'idea:' prefix is created or edited.
"""

import os
import re

def get_preview_text(body, max_length=100):
    """Extract a preview from the issue body."""
    if not body:
        return "No description provided"
    
    # Remove markdown formatting for cleaner preview
    preview = body.strip()
    # Remove multiple newlines
    preview = re.sub(r'\n+', ' ', preview)
    # Remove markdown headers
    preview = re.sub(r'#+\s*', '', preview)
    # Remove markdown links but keep text
    preview = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', preview)
    # Remove bold/italic markers
    preview = re.sub(r'[*_]{1,2}', '', preview)
    
    # Truncate to max_length
    if len(preview) > max_length:
        preview = preview[:max_length].rsplit(' ', 1)[0] + '...'
    
    return preview.strip()

def escape_pipe(text):
    """Escape pipe characters for markdown table."""
    return text.replace('|', '\\|')

def update_readme():
    """Update the README.md file with issue information."""
    issue_title = os.environ.get('ISSUE_TITLE', '')
    issue_number = os.environ.get('ISSUE_NUMBER', '')
    issue_body = os.environ.get('ISSUE_BODY', '')
    repo_url = os.environ.get('REPO_URL', '')
    
    if not all([issue_title, issue_number, repo_url]):
        print("Missing required environment variables")
        return
    
    # Read the current README
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prepare the new row
    issue_link = f"{repo_url}/issues/{issue_number}"
    preview = get_preview_text(issue_body)
    
    # Escape special characters for markdown table
    title_text = escape_pipe(issue_title)
    preview_text = escape_pipe(preview)
    
    new_row = f"| [{title_text}]({issue_link}) | {preview_text} |"
    
    # Find the table markers
    start_marker = "<!-- IDEAS_TABLE_START -->"
    end_marker = "<!-- IDEAS_TABLE_END -->"
    
    if start_marker not in content or end_marker not in content:
        print("Table markers not found in README.md")
        return
    
    # Extract the table content
    start_idx = content.find(start_marker) + len(start_marker)
    end_idx = content.find(end_marker)
    
    table_content = content[start_idx:end_idx].strip()
    
    # Parse existing rows and check if this issue is already in the table
    existing_rows = []
    if table_content:
        for line in table_content.split('\n'):
            line = line.strip()
            if line and line.startswith('|'):
                existing_rows.append(line)
    
    # Check if this issue already exists in the table
    issue_pattern = f"/issues/{issue_number}"
    issue_exists = any(issue_pattern in row for row in existing_rows)
    
    if issue_exists:
        # Update the existing row
        updated_rows = []
        for row in existing_rows:
            if issue_pattern in row:
                updated_rows.append(new_row)
            else:
                updated_rows.append(row)
        existing_rows = updated_rows
    else:
        # Add the new row
        existing_rows.append(new_row)
    
    # Rebuild the table content
    new_table_content = '\n' + '\n'.join(existing_rows) + '\n'
    
    # Update the README content
    new_content = (
        content[:start_idx] +
        new_table_content +
        content[end_idx:]
    )
    
    # Write the updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated README.md with issue #{issue_number}")

if __name__ == '__main__':
    update_readme()
