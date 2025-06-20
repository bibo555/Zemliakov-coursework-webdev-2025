from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from datetime import datetime
from ..models import db, User, Flight, Airport, Airline, Passport, Booking
from flask import current_app

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

@admin_bp.route('/admin/tickets')
@login_required
def admin_tickets():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    flights = Flight.query.join(Airline).join(Airport, Flight.origin_id == Airport.id).all()
    
    tickets = []
    for flight in flights:
        tickets.append({
            'id': flight.id,
            'airline': flight.airline.name,
            'origin': f"{flight.origin.code} ({flight.origin.city})",
            'destination': f"{flight.destination.code} ({flight.destination.city})",
            'departure_date': flight.departure_time.strftime('%Y-%m-%d'),
            'price': flight.price
        })
    
    return render_template('admin_tickets.html', tickets=tickets)

@admin_bp.route('/admin/tickets/add', methods=['GET', 'POST'])
@login_required
def add_ticket():
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    airports = Airport.query.all()
    airlines = Airline.query.all()
    
    if request.method == 'POST':
        try:
            airline_id = request.form.get('airline')
            origin_id = request.form.get('origin_id')
            destination_id = request.form.get('destination_id')
            flight_number = request.form.get('flight_number')
            departure_date = request.form.get('departure_date')
            departure_time = request.form.get('departure_time')
            arrival_time = request.form.get('arrival_time')
            duration = request.form.get('duration')
            price = request.form.get('price')

            if not all([airline_id, origin_id, destination_id, flight_number, 
                        departure_date, departure_time, arrival_time, duration, price]):
                flash('Заполните все обязательные поля', 'danger')
                return redirect(url_for('admin.add_ticket'))

            try:
                hours, minutes = map(int, duration.replace('ч', '').replace('м', '').split())
                duration_minutes = hours * 60 + minutes
            except Exception as e:
                flash('Некорректный формат длительности. Используйте "2ч 30м"', 'danger')
                return redirect(url_for('admin.add_ticket'))

            new_flight = Flight(
                airline_id=airline_id,
                flight_number=flight_number,
                origin_id=origin_id,
                destination_id=destination_id,
                departure_time=datetime.strptime(departure_time, '%H:%M').time(),
                arrival_time=datetime.strptime(arrival_time, '%H:%M').time(),
                duration=duration_minutes,
                price=int(price),
                departure_date=datetime.strptime(departure_date, '%Y-%m-%d').date()
            )

            db.session.add(new_flight)
            db.session.commit()
            flash('Билет успешно добавлен!', 'success')
            return redirect(url_for('admin.admin_tickets'))

        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка в формате данных: {str(e)}', 'danger')
            return redirect(url_for('admin.add_ticket'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении: {str(e)}', 'danger')
            current_app.logger.error(f"Error in add_ticket: {str(e)}")
            return redirect(url_for('admin.add_ticket'))

    return render_template('add_ticket.html', airports=airports, airlines=airlines)

@admin_bp.route('/admin/tickets/edit/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    flight = Flight.query.get_or_404(ticket_id)
    
    if request.method == 'POST':
        try:
            flight.departure_time = datetime.strptime(request.form.get('departure_time'), '%H:%M').time()
            flight.arrival_time = datetime.strptime(request.form.get('arrival_time'), '%H:%M').time()
            flight.duration = (int(request.form.get('duration').split('ч')[0]) * 60 + 
                              int(request.form.get('duration').split('ч')[1].split('м')[0]))
            flight.price = int(request.form.get('price'))
            flight.departure_date = datetime.strptime(request.form.get('departure_date'), '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Билет успешно обновлен!', 'success')
            return redirect(url_for('admin.admin_tickets'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
            current_app.logger.error(f"Error editing ticket {ticket_id}: {str(e)}")
    
    return render_template('edit_ticket.html', ticket=flight)

@admin_bp.route('/admin/tickets/delete/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    flight = Flight.query.get(ticket_id)
    if not flight:
        flash('Билет не найден', 'danger')
    else:
        try:
            db.session.delete(flight)
            db.session.commit()
            flash('Билет успешно удален!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_tickets'))

@admin_bp.route('/admin/user/<int:user_id>')
@login_required
def view_user(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    user = User.query.get_or_404(user_id)
    passports = Passport.query.filter_by(user_id=user_id).all()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    
    return render_template('admin_user_view.html', 
                         user=user, 
                         passports=passports, 
                         bookings=bookings)

@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.home'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin and user.id != current_user.id:
        flash('Нельзя удалить другого администратора', 'danger')
        return redirect(url_for('admin.admin'))
    
    try:
        # Удаляем связанные паспорта пользователя
        Passport.query.filter_by(user_id=user_id).delete()
        
        # Удаляем бронирования пользователя (без Passenger)
        bookings = Booking.query.filter_by(user_id=user_id).all()
        for booking in bookings:
            db.session.delete(booking)
        
        # Удаляем самого пользователя
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении пользователя', 'danger')
        current_app.logger.error(f"Error deleting user {user_id}: {str(e)}")
    
    return redirect(url_for('admin.admin'))