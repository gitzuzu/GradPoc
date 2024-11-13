import re

def parse_srs(text):
    parsed_data = []
    
    # Regular expressions for matching titles, subtitles, and page numbers
    section_pattern = r"^\d+ [A-Za-z ]+"  # Matches main section titles
    subsection_pattern = r"^\d+\.\d+ [A-Za-z ]+"  # Matches subsection titles
    page_number_pattern = r"^\d+$"  # Matches standalone page numbers
    dots_pattern = r"\.{2,}"  # Matches rows of dots, often used in TOCs
    
    current_section = None
    current_subsection = None
    current_content = ""
    
    # Split text into lines and clean up formatting issues
    lines = text.replace(" .", ".").replace(" ,", ",").replace(" :", ":").replace(" ;", ";").splitlines()
    
    # Separate the TOC section and ignore it until the actual content begins
    content_lines = []
    content_started = False
    abstract_section = None

    for line in lines:
        line = line.strip()
        
        # Skip page numbers and dot lines
        if re.match(page_number_pattern, line) or re.match(dots_pattern, line):
            continue
        
        # Start capturing content after "Abstract" line is found
        if "Abstract" in line:
            content_started = True
            abstract_section = {"title": "Abstract", "content": ""}
            # Skip adding "Abstract" itself to the content
            continue
        
        if content_started and line:
            content_lines.append(line)

    # Parse content_lines after TOC
    for line in content_lines:
        # Separate Abstract content until Introduction
        if abstract_section and re.match(section_pattern, line) and "Introduction" in line:
            # Save the Abstract section
            parsed_data.append(abstract_section)
            abstract_section = None
            current_section = line
            current_subsection = None
            current_content = ""
        elif abstract_section:
            abstract_section["content"] += line + " "
        
        # Check if line matches a main section title
        elif re.match(section_pattern, line):  # Main section titles
            # Save current section if content exists
            if current_section and current_content:
                section_data = {"title": current_section, "content": current_content.strip()}
                if current_subsection:
                    section_data["subtitle"] = current_subsection
                parsed_data.append(section_data)
                current_content = ""
            
            # Start a new section
            current_section = line
            current_subsection = None
            
        # Check for subsection titles within the current section
        elif current_section and re.match(subsection_pattern, line):  # Subsection titles
            # Save current subsection if content exists
            if current_subsection and current_content:
                section_data = {"title": current_section, "subtitle": current_subsection, "content": current_content.strip()}
                parsed_data.append(section_data)
                current_content = ""
            
            # Start a new subsection
            current_subsection = line
            
        else:
            # Append line to current content
            current_content += line + " "
            # Clean up whitespace and ensure proper spacing
            current_content = re.sub(r'\s+', ' ', current_content)  # Remove extra spaces
            current_content = re.sub(r'([.,;])([A-Za-z])', r'\1 \2', current_content)  # Ensure space after punctuation
    
    # Save the last section or subsection if any content exists
    if current_section and current_content:
        section_data = {"title": current_section, "content": current_content.strip()}
        if current_subsection:
            section_data["subtitle"] = current_subsection
        parsed_data.append(section_data)

    # Print the parsed data for debugging
    print("Parsed SRS Structure:", parsed_data)

    return parsed_data
