def validate_srs_structure(parsed_data, predefined_structure):
    """
    Validates if the parsed SRS document contains the required structure.

    :param parsed_data: List of parsed sections and subsections from the document.
    :param predefined_structure: Predefined structure dictionary.
    :return: Dictionary with missing and extra sections.
    """
    missing_sections = []
    extra_sections = []

    # Convert parsed data to a dictionary for easier lookup
    parsed_dict = {}
    for item in parsed_data:
        title = item["title"]
        subtitle = item.get("subtitle")
        if title not in parsed_dict:
            parsed_dict[title] = set()
        if subtitle:
            parsed_dict[title].add(subtitle)

    # Check for missing sections and subsections
    for section, subsections in predefined_structure.items():
        if section not in parsed_dict:
            # Entire section is missing
            missing_sections.append(section)
            # Add each subsection as missing under this section
            for subsection in subsections:
                missing_sections.append(f"{section} -> {subsection}")
        else:
            # Section found, now check each subsection
            found_subsections = parsed_dict[section]
            for subsection in subsections:
                if subsection not in found_subsections:
                    missing_sections.append(f"{section} -> {subsection}")

    # Check for extra sections by identifying any parsed sections not in the predefined structure
    predefined_sections = set(predefined_structure.keys())
    for section, found_subsections in parsed_dict.items():
        if section not in predefined_sections:
            # Entire section is extra
            extra_sections.append(section)
        else:
            # Section exists, check for any extra subsections
            predefined_subsections = set(predefined_structure[section].keys())
            extra_subsections = found_subsections - predefined_subsections
            for extra_subsection in extra_subsections:
                extra_sections.append(f"{section} -> {extra_subsection}")

    # Collect validation results
    validation_results = {
        "missing_sections": missing_sections,
        "extra_sections": extra_sections
    }

    return validation_results
