import os
import uuid
import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify, session, flash
from app import app, db
from models import User, Conversation, Message, Mistake
from gemini_utils import (get_gemini_response, initialize_chat, 
                         process_user_message, generate_mistake_analysis)

# Add the now() function to templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@app.route('/')
def index():
    # Generate a session ID if it doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
        # Create a new user with this session ID
        user = User(session_id=session['session_id'])
        db.session.add(user)
        db.session.commit()
    
    # Clear any current conversation data
    if 'conversation_id' in session:
        del session['conversation_id']
    
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    # Get user inputs
    target_language = request.form.get('target_language')
    native_language = request.form.get('native_language')
    proficiency_level = request.form.get('proficiency_level')
    scene = request.form.get('scene')
    
    # Get the user based on session_id
    user = User.query.filter_by(session_id=session['session_id']).first()
    
    if not user:
        # Handle the case where the user doesn't exist
        flash('Session error. Please try again.')
        return redirect(url_for('index'))
    
    # Create a new conversation
    conversation = Conversation(
        user_id=user.id,
        target_language=target_language,
        native_language=native_language,
        proficiency_level=proficiency_level,
        scene=scene
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    # Store conversation ID in session
    session['conversation_id'] = conversation.id
    
    # Initialize the chat with Gemini API
    initial_bot_message = initialize_chat(target_language, native_language, proficiency_level, scene)
    
    # Save the bot's initial message
    message = Message(
        conversation_id=conversation.id,
        is_user=False,
        content=initial_bot_message
    )
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    # Ensure we have an active conversation
    if 'conversation_id' not in session:
        flash('No active conversation. Please start a new one.')
        return redirect(url_for('index'))
    
    conversation_id = session['conversation_id']
    conversation = Conversation.query.get(conversation_id)
    
    if not conversation:
        flash('Conversation not found. Please start a new one.')
        return redirect(url_for('index'))
    
    # Get all messages for this conversation
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    
    return render_template(
        'chat.html', 
        conversation=conversation,
        messages=messages
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'conversation_id' not in session:
        return jsonify({'error': 'No active conversation'}), 400
    
    conversation_id = session['conversation_id']
    conversation = Conversation.query.get(conversation_id)
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # Get user message from the request
    user_message = request.form.get('message')
    
    if not user_message or user_message.strip() == '':
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        is_user=True,
        content=user_message
    )
    db.session.add(user_msg)
    
    # Process the user message using Gemini API
    bot_response, mistakes = process_user_message(
        user_message, 
        conversation.target_language,
        conversation.native_language,
        conversation.proficiency_level
    )
    
    # Save bot response
    bot_msg = Message(
        conversation_id=conversation_id,
        is_user=False,
        content=bot_response
    )
    db.session.add(bot_msg)
    
    # Save any detected mistakes
    for mistake in mistakes:
        mistake_record = Mistake(
            conversation_id=conversation_id,
            original_text=mistake['original'],
            corrected_text=mistake['corrected'],
            explanation=mistake['explanation'],
            category=mistake.get('category', 'Uncategorized')
        )
        db.session.add(mistake_record)
    
    db.session.commit()
    
    return jsonify({
        'user_message': {
            'content': user_message,
            'timestamp': datetime.utcnow().strftime('%H:%M')
        },
        'bot_response': {
            'content': bot_response,
            'timestamp': datetime.utcnow().strftime('%H:%M')
        },
        'mistakes': mistakes
    })

@app.route('/end_conversation', methods=['POST'])
def end_conversation():
    if 'conversation_id' not in session:
        return jsonify({'error': 'No active conversation'}), 400
    
    conversation_id = session['conversation_id']
    
    # Get all mistakes for this conversation
    mistakes = Mistake.query.filter_by(conversation_id=conversation_id).all()
    
    # Generate summary and analysis using Gemini API
    conversation = Conversation.query.get(conversation_id)
    summary = generate_mistake_analysis(
        mistakes, 
        conversation.target_language,
        conversation.proficiency_level
    )
    
    # Store the summary as a bot message
    summary_msg = Message(
        conversation_id=conversation_id,
        is_user=False,
        content=summary['summary']
    )
    db.session.add(summary_msg)
    db.session.commit()
    
    # Redirect to summary page
    return jsonify({'redirect': url_for('summary')})

@app.route('/summary')
def summary():
    if 'conversation_id' not in session:
        flash('No active conversation. Please start a new one.')
        return redirect(url_for('index'))
    
    conversation_id = session['conversation_id']
    conversation = Conversation.query.get(conversation_id)
    
    if not conversation:
        flash('Conversation not found. Please start a new one.')
        return redirect(url_for('index'))
    
    # Get all mistakes for this conversation
    mistakes = Mistake.query.filter_by(conversation_id=conversation_id).all()
    
    # Get all messages for the conversation
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    
    # Generate or retrieve the summary
    summary_message = messages[-1] if messages and not messages[-1].is_user else None
    
    # Generate analysis with Gemini if needed
    if not summary_message:
        analysis = generate_mistake_analysis(
            mistakes, 
            conversation.target_language,
            conversation.proficiency_level
        )
        summary_text = analysis['summary']
        improvement_areas = analysis['improvement_areas']
    else:
        # Extract improvement areas from the existing summary
        summary_text = summary_message.content
        # This is a simple approach - in production we might want a more robust way to extract the improvement areas
        split_text = summary_text.split("Areas to focus on:")
        improvement_areas = split_text[1].strip() if len(split_text) > 1 else ""
    
    return render_template(
        'summary.html',
        conversation=conversation,
        mistakes=mistakes,
        summary=summary_text,
        improvement_areas=improvement_areas
    )

@app.route('/new_conversation', methods=['GET'])
def new_conversation():
    # Clear the current conversation
    if 'conversation_id' in session:
        del session['conversation_id']
    
    return redirect(url_for('index'))
