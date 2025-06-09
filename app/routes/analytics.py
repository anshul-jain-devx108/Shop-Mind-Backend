from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import ChatSession, Message, User
from .. import db
from datetime import datetime
import csv
import io
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/<user_id>', methods=['GET'])
@jwt_required()
def get_user_analytics(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    sessions = ChatSession.query.filter_by(user_id=user_id).all()
    total_sessions = len(sessions)
    total_messages = sum(session.message_count for session in sessions)

    return jsonify({
        'userId': user_id,
        'totalSessions': total_sessions,
        'totalMessages': total_messages
    })

@analytics_bp.route('/export/<user_id>', methods=['POST'])
@jwt_required()
def export_chat(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    export_format = data.get('format', 'json').lower()
    date_range = data.get('dateRange', {})

    start_date = datetime.fromisoformat(date_range.get('start')) if date_range.get('start') else None
    end_date = datetime.fromisoformat(date_range.get('end')) if date_range.get('end') else None

    messages_query = Message.query.join(ChatSession).filter(ChatSession.user_id == user_id)

    if start_date:
        messages_query = messages_query.filter(Message.timestamp >= start_date)
    if end_date:
        messages_query = messages_query.filter(Message.timestamp <= end_date)

    messages = messages_query.order_by(Message.timestamp.asc()).all()

    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'session_id', 'content', 'sender', 'timestamp', 'products'])
        for msg in messages:
            writer.writerow([
                msg.id, msg.session_id, msg.content, msg.sender,
                msg.timestamp.isoformat() + 'Z',
                json.dumps(msg.products)
            ])
        csv_data = output.getvalue()
        output.close()

        # Normally you'd upload CSV to storage and provide a URL.
        # For demo, return CSV content as string (not for prod)
        return jsonify({'data': csv_data})

    else:  # default json
        result = [{
            'id': msg.id,
            'sessionId': msg.session_id,
            'content': msg.content,
            'sender': msg.sender,
            'timestamp': msg.timestamp.isoformat() + 'Z',
            'products': msg.products
        } for msg in messages]
        return jsonify(result)
