from flask import request, jsonify, render_template
from ..functions.search import rag_pipeline
import logging
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*NumPy: _ARRAY_API not found.*")

logger = logging.getLogger("clinical_assistant.api")


def setup_routes(app):
    """Configure all routes for the Flask application"""

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/query', methods=['POST'])
    def api_query():
        try:
            data = request.json
            query = data.get('query', '')

            if not query:
                return jsonify({'error': 'Query is required'}), 400

            # Process query with RAG pipeline
            response, sources = rag_pipeline(query)

            return jsonify({
                'response': response,
                'sources': [
                    {
                        'patient_id': s.get('patient_id', 'Unknown'),
                        'note_id': s['note_id'],
                        'score': round(s['score'], 3)
                    }
                    for s in sources
                ]
            })

        except Exception as e:
            logger.exception("Error processing query")
            return jsonify({'error': str(e)}), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error=str(e)), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error=str(e)), 500

    @app.route('/api/patients', methods=['GET'])
    def get_patients():
        from app.functions.iris import get_patient_list

        try:
            patients = get_patient_list()
            return jsonify({
                'patients': patients,
                'count': len(patients)
            })
        except Exception as e:
            logger.exception("Error retrieving patient list")
            return jsonify({'error': str(e)}), 500

