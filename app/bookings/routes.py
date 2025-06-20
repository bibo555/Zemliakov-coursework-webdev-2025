from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime
from ..models import db, Booking, Flight, Passenger
from flask import current_app

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings')
@login_required
def bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', bookings=user_bookings)

@bookings_bp.route('/add_booking', methods=['POST'])
@login_required
def add_booking():
    ticket_data = request.get_json()
    
    new_booking = Booking(
        user_id=current_user.id,
        flight_id=ticket_data['flight_id'],
        booking_number=f"BK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        booking_date=datetime.utcnow(),
        status='confirmed',
        price=ticket_data['price']
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@bookings_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Вы не можете отменить это бронирование', 'danger')
        return redirect(url_for('bookings.bookings'))
    
    try:
        Passenger.query.filter_by(booking_id=booking.id).delete()
        db.session.delete(booking)
        db.session.commit()
        flash('Бронирование успешно отменено', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при отмене бронирования', 'danger')
        current_app.logger.error(f"Error canceling booking: {str(e)}")
    
    return redirect(url_for('bookings.bookings'))