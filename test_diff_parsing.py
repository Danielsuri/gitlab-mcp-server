#!/usr/bin/env python3
"""
Simple test for diff parsing functionality
"""
import re

def parse_diff_for_line_numbers(diff_content):
    """Parse diff content to extract valid line numbers for comments"""
    lines = diff_content.split('\n')
    valid_lines = []
    
    current_new_line = 0
    current_old_line = 0
    
    for line in lines:
        if line.startswith('@@'):
            # Parse hunk header to get starting line numbers
            # Format: @@ -old_start,old_count +new_start,new_count @@
            match = re.match(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
            if match:
                current_old_line = int(match.group(1))
                current_new_line = int(match.group(2))
            continue
            
        if line.startswith('+') and not line.startswith('+++'):
            # This is a new line that can be commented on
            valid_lines.append({
                'type': 'new',
                'line_number': current_new_line,
                'content': line[1:]  # Remove the + prefix
            })
            current_new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            # This is a deleted line that can be commented on
            valid_lines.append({
                'type': 'old', 
                'line_number': current_old_line,
                'content': line[1:]  # Remove the - prefix
            })
            current_old_line += 1
        elif line.startswith(' '):
            # Context line - both line numbers advance
            current_new_line += 1
            current_old_line += 1
            
    return valid_lines

def test_parse_diff():
    """Test parsing diff content"""
    sample_diff = """@@ -10,5 +10,6 @@ def hello():
     print("hello world")
-    return "old line"
+    return "new line"
+    print("added line")
     print("context line")
"""
    
    result = parse_diff_for_line_numbers(sample_diff)
    
    # Should find one old line and two new lines
    old_lines = [line for line in result if line['type'] == 'old']
    new_lines = [line for line in result if line['type'] == 'new']
    
    print(f"Found {len(old_lines)} old lines and {len(new_lines)} new lines")
    
    for line in old_lines:
        print(f"Old line {line['line_number']}: {line['content']}")
    for line in new_lines:
        print(f"New line {line['line_number']}: {line['content']}")
    
    # Check the old line
    assert len(old_lines) == 1
    assert old_lines[0]['line_number'] == 11  # Fixed: starts at 10, then context line makes it 11
    assert old_lines[0]['content'] == '    return "old line"'
    
    # Check the new lines
    assert len(new_lines) == 2
    assert new_lines[0]['line_number'] == 11  # Fixed: starts at 10, then context line makes it 11
    assert new_lines[0]['content'] == '    return "new line"'
    assert new_lines[1]['line_number'] == 12  # Then increments
    assert new_lines[1]['content'] == '    print("added line")'
    
    print("All diff parsing tests passed!")

if __name__ == '__main__':
    test_parse_diff()