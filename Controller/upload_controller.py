from flask import Blueprint, request, jsonify, current_app
from models.document_parser import extract_text_from_pdf
from services.srs_parser import parse_srs
from services.srs_validator import validate_srs_structure
from models.srs_structure import PREDEFINED_STRUCTURE
import os

upload_blueprint = Blueprint('upload', __name__)

@upload_blueprint.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdfFile' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files['pdfFile']
    filename = pdf_file.filename
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # Save the uploaded file
    pdf_file.save(save_path)
    

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(save_path)
     # Debug: Print the extracted text
  

    # Parse the extracted text for SRS structure
    parsed_srs = parse_srs(pdf_text)
 # Validate the SRS structure
    validation_results = validate_srs_structure(parsed_srs, PREDEFINED_STRUCTURE)

    return jsonify({
        "parsed_srs": parsed_srs,
        "validation": validation_results
    })


