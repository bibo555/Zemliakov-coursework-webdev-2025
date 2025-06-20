from flask import Blueprint, render_template, request, jsonify, flash, url_for, current_app
from flask_login import current_user, login_required
from datetime import datetime
# Стало:
from ..models import db, Flight, Airport, Airline
from ..models import User, Booking, Passenger, Passport
from sqlalchemy.orm import aliased
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

import os

main_bp = Blueprint('main', __name__)

def get_tickets(origin=None, destination=None, date=None, min_price=None, max_price=None, airline=None):
    origin_alias = aliased(Airport, name='origin_airport')
    destination_alias = aliased(Airport, name='destination_airport')
    
    query = db.session.query(
        Flight,
        Airline,
        origin_alias,
        destination_alias
    ).join(
        Airline, Flight.airline_id == Airline.id
    ).join(
        origin_alias, Flight.origin_id == origin_alias.id
    ).join(
        destination_alias, Flight.destination_id == destination_alias.id
    )
    
    if origin:
        # Обрабатываем как "Город (КОД)" или просто город
        origin_parts = origin.split('(')
        origin_city = origin_parts[0].strip()
        query = query.filter(origin_alias.city.ilike(f"%{origin_city}%"))
    
    if destination:
        dest_parts = destination.split('(')
        dest_city = dest_parts[0].strip()
        query = query.filter(destination_alias.city.ilike(f"%{dest_city}%"))
    
    if date:
        try:
            query = query.filter(Flight.departure_date == datetime.strptime(date, '%Y-%m-%d').date())
        except ValueError:
            pass  # Игнорируем неверный формат даты
    
    if min_price is not None:
        query = query.filter(Flight.price >= min_price)
    if max_price is not None:
        query = query.filter(Flight.price <= max_price)
    
    if airline:
        query = query.filter(Airline.name.ilike(f"%{airline}%"))
    
    flights = query.all()
    
    tickets = []
    for flight in flights:
        flight_obj, airline, origin_airport, dest_airport = flight
        tickets.append({
            'id': flight_obj.id,
            'airline': airline.name,
            'origin': f"{origin_airport.city} ({origin_airport.code})",
            'destination': f"{dest_airport.city} ({dest_airport.code})",
            'departure_time': flight_obj.departure_time.strftime('%H:%M'),
            'arrival_time': flight_obj.arrival_time.strftime('%H:%M'),
            'duration': f"{flight_obj.duration // 60}ч {flight_obj.duration % 60}м",
            'price': flight_obj.price,
            'departure_date': flight_obj.departure_date.strftime('%Y-%m-%d')
        })
    
    return tickets

@main_bp.route('/', endpoint='home')
def home():
    return render_template('home.html', tickets=get_tickets())

@main_bp.route('/search')
def search():
    try:
        origin = request.args.get('origin', '')
        origin = origin.split('(')[0].strip() if origin else None
        
        destination = request.args.get('destination', '')
        destination = destination.split('(')[0].strip() if destination else None
        
        departure_date = request.args.get('departure_date')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        airline = request.args.get('airline')
        
        sort_by = request.args.get('sort', 'price')
        sort_direction = request.args.get('direction', 'asc')

        tickets = get_tickets(
            origin=origin,
            destination=destination,
            date=departure_date,
            min_price=min_price,
            max_price=max_price,
            airline=airline
        )

        # Улучшенная сортировка с обработкой ошибок
        if sort_by == 'price':
            tickets.sort(key=lambda x: x.get('price', 0), reverse=(sort_direction == 'desc'))
        elif sort_by == 'duration':
            def parse_duration(dur):
                try:
                    if not isinstance(dur, str):
                        return 0
                    parts = dur.replace('м', '').split('ч')
                    hours = int(parts[0].strip()) if parts[0].strip() else 0
                    minutes = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
                    return hours * 60 + minutes
                except (ValueError, AttributeError) as e:
                    current_app.logger.error(f"Duration parsing failed for '{dur}': {str(e)}")
                    return 0
                    
            tickets.sort(key=lambda x: parse_duration(x.get('duration', '0ч 0м')), 
                         reverse=(sort_direction == 'desc'))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('_tickets_list.html', tickets=tickets)
        
        airports = Airport.query.all()
        airlines = Airline.query.all()
        
        return render_template(
            'search.html',
            tickets=tickets,
            airports=airports,
            airlines=airlines,
            origin=request.args.get('origin', ''),
            destination=request.args.get('destination', ''),
            departure_date=departure_date,
            min_price=min_price,
            max_price=max_price,
            airline=airline
        )
    except Exception as e:
        current_app.logger.error(f"Search route error: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
        return render_template('error.html', error="Произошла ошибка при поиске билетов"), 500

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.fullname = request.form.get('fullname')
            current_user.email = request.form.get('email')
            current_user.phone = request.form.get('phone')
            
            passport_data = {
                'series': request.form.get('passport_series'),
                'number': request.form.get('passport_number'),
                'issued_by': request.form.get('passport_issued_by'),
                'issue_date': request.form.get('passport_issue_date')
            }
            
            if current_user.passports:
                passport = current_user.passports[0]
                passport.series = passport_data['series']
                passport.number = passport_data['number']
                passport.issued_by = passport_data['issued_by']
                passport.issue_date = datetime.strptime(passport_data['issue_date'], '%Y-%m-%d').date()
            else:
                new_passport = Passport(
                    user_id=current_user.id,
                    series=passport_data['series'],
                    number=passport_data['number'],
                    issued_by=passport_data['issued_by'],
                    issue_date=datetime.strptime(passport_data['issue_date'], '%Y-%m-%d').date()
                )
                db.session.add(new_passport)
            
            db.session.commit()
            flash('Данные успешно сохранены!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении данных: {str(e)}', 'danger')
    
    passport_data = current_user.passports[0] if current_user.passports else None
    
    return render_template(
        'profile.html', 
        user=current_user,
        passport_data=passport_data
    )

@main_bp.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'})
    
    if file and allowed_file(file.filename):
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = f"user_{current_user.id}_photo.{file.filename.rsplit('.', 1)[1].lower()}"
        filename = secure_filename(filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        current_user.photo = f"uploads/{filename}"
        db.session.commit()
        
        return jsonify({
            'success': True,
            'photo_url': url_for('static', filename=current_user.photo)
        })
    
    return jsonify({'success': False, 'error': 'Недопустимый формат файла'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']