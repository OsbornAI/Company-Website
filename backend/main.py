from flask import Flask, jsonify, request
import stripe
import os
from database import Database
import json

app = Flask(__name__)

db = Database()

stripe.api_key = os.getenv('STRIPE_SECRET')

# -------------------------- Payment routes -----------------------------

@app.route('/load_payment_id', methods=['POST'], strict_slashes=False)
def validateId():
    form_json = request.get_json()
    payment_id = form_json['payment_id']

    payment_info = db.admin_view_payment_id_details(payment_id)
    if payment_info == False:
        return jsonify({'success': False})

    return jsonify({**{'success': True}, **payment_info}) # This has to return more

# Ill need another function for creating these payment_id's

@app.route('/pay', methods=['POST'], strict_slashes=False)
def pay():
    form_json = request.get_json()
    first = form_json['first']
    last = form_json['last']
    email = form_json['email']
    payment_id = form_json['payment_id']

    payment_info = db.admin_view_payment_id_details(payment_id)
    if payment_info == False:
        return jsonify({'success': False})

    amount = payment_info['amount'] * 100
    currency = payment_info['currency']

    # I'll have to check to make sure stripe doesnt send strange receipts
    desc_json = json.dumps({
        'payment_id': payment_id,
        'first': first,
        'last': last,
        'email': email,
        'purchase': payment_info['purchase'],
        'amount': amount,
        'currency': currency
    })

    intent = stripe.PaymentIntent.create(
        amount=amount,
        description=desc_json,
        currency=currency,
        receipt_email=email
    )

    return jsonify({'success': True, 'client_secret': intent['client_secret']})

@app.route('/payment_webook', methods=['POST'], strict_slashes=False)
def paymentWebhook():
    form_json = request.get_json()

    if form_json['type'] == 'payment_intent.succeeded':
        data_object = form_json['data']['object']
        receipt_info_json = data_object['description']
        receipt_info = json.loads(receipt_info_json)

        payment_id = receipt_info['payment_id']
        first = receipt_info['first']
        last = receipt_info['last']
        email = receipt_info['email']
        purchase = receipt_info['purchase']
        amount = receipt_info['amount']
        currency = receipt_info['currency']

        db.add_payment(first, last, email, payment_id, purchase, amount, currency)

        db.admin_delete_payment_id(payment_id) 

        return jsonify({'success': True})

    else:
        # What am I going to do if this is false?

        return jsonify({'success': False})

# ------------------- Inquiry routes -----------------------

@app.route('/add_inquiry', methods=['POST'], strict_slashes=False)
def addInquiry():
    form_json = request.json()

    first = form_json['first']
    last = form_json['last']
    email = form_json['email']
    inquiry = form_json['inquiry']

    success = db.add_inquiry(first, last, email, inquiry)

    return jsonify({'success': success})

@app.route('/view_inquiry_notifications', methods=['POST'], strict_slashes=False)
def viewInquiryNotifications():
    inquiries = db.admin_view_inquiry_notifications()

    if inquiries == False:
        return jsonify({'success': False})

    return jsonify({'success': True, 'inquiries': inquiries})

@app.route('/delete_inquiry_notification', methods=['POST'], strict_slashes=False)
def deleteInquiryNotification():
    form_json = request.get_json()

    inquiry_notification_id = form_json['inquiry_notification_id'] # This will come from the '_id'

    success = db.admin_delete_inquiry_notification(inquiry_notification_id)

    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)