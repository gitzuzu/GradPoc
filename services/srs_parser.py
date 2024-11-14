import re
import language_tool_python
from spellchecker import SpellChecker

grammar_tool = language_tool_python.LanguageTool('en-US')
spell_checker = SpellChecker()

# List of custom terms to ignore
CUSTOM_TERMS = ['qanaa', 'srs']

def check_spelling_and_grammar(text):
    try:
        # Join split words with a hyphen if there is a space after the hyphen (e.g., "phar- macy" -> "pharmacy")
        text = re.sub(r'(\w)- (\w)', r'\1\2', text)  

        # Ensure no spaces between hyphenated words (e.g., "ever- evolving" -> "ever-evolving")
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  

        # Clean up punctuation from words (remove all non-word characters except whitespace and hyphen)
        clean_text = re.sub(r'[^\w\s\'-]', '', text)  # This removes punctuation except for hyphens and spaces
        
        # Spell Check (ignore custom terms)
        words = clean_text.split()
        misspelled = spell_checker.unknown(words)

        # Handle possessives: ignore words ending with 's to prevent possessive forms from being flagged
        misspelled = {
            word: spell_checker.correction(word) 
            for word in words 
            if word.lower() not in CUSTOM_TERMS and not re.match(r"\w+'s$", word)
            and word in spell_checker.unknown([word])
        }
        
        # Filter out custom terms from the misspelled list
        misspelled = {word: spell_checker.correction(word) for word in misspelled if word.lower() not in CUSTOM_TERMS}
        
        # Add back custom terms with no correction
        for term in CUSTOM_TERMS:
            if term in words:
                misspelled[term] = term
        
         # Filter out words with `null` suggestions from being displayed as misspelled
        misspelled = {word: correction for word, correction in misspelled.items() if correction is not None}
        print(f"Misspelled words: {misspelled}")
        print(f"Spell corrections: {misspelled}")

        # Grammar Check
        grammar_issues = grammar_tool.check(text)

         # Print full details of grammar issues
        for issue in grammar_issues:
            print(f"Grammar issue: {issue.message}")
            print(f"Context: {issue.context}")
            print(f"Replacements: {issue.replacements}")

          # Simplify the grammar issues output, only including the context (without suggestions)
        grammar_suggestions = [{"text": match.context} for match in grammar_issues]
        
        # Optionally filter out unwanted grammar issues
        for suggestion in grammar_suggestions:
            # Ignore suggestions for Qanaa or other terms we don't want corrected
            if "Qanaa" in suggestion['text']:
                suggestion['text'] = suggestion['text']  # Keep the text as is, no correction

        grammar_suggestions = [suggestion for suggestion in grammar_suggestions if "Qanaa" not in suggestion['text']]

        print(f"Grammar issues found: {len(grammar_issues)}")
        print(f"Grammar suggestions: {grammar_suggestions}")
        
        return misspelled, grammar_suggestions
    
    except Exception as e:
        print(f"Error in spelling/grammar check: {e}")
        return {}, []
    
sample_text = "Adherence to these requirements throughout development ensures user-friendly alignment with Qanaa Pharmacy’s healthcare"

misspelled, grammar_suggestions = check_spelling_and_grammar(sample_text)  
print("Misspelled:", misspelled)
print("Grammar suggestions:", grammar_suggestions)

   

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
            # Run spelling and grammar checks
                spelling, grammar = check_spelling_and_grammar(current_content)
                section_data = {"title": current_section, "content": current_content.strip(),"spelling_issues": spelling,"grammar_issues": grammar}
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
                # Run spelling and grammar checks
                spelling, grammar = check_spelling_and_grammar(current_content)
                section_data = {"title": current_section, "subtitle": current_subsection, "content": current_content.strip(),"spelling_issues": spelling,"grammar_issues": grammar}
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
        # Run spelling and grammar checks for the last section/subsection
        spelling, grammar = check_spelling_and_grammar(current_content)
        section_data = {"title": current_section, "content": current_content.strip(),"spelling_issues": spelling,"grammar_issues": grammar}
        if current_subsection:
            section_data["subtitle"] = current_subsection
        parsed_data.append(section_data)

    # Print the parsed data for debugging
    print("Parsed SRS Structure:", parsed_data)

    return parsed_data
