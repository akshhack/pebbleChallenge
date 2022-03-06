from flask import Blueprint, request, render_template
from api.models import db, User, Quote
from api.core import create_response, serialize_list, logger
from api.views.utils import *
import enum
from sqlalchemy import inspect

main = Blueprint("main", __name__)  # initialize blueprint


class ObjKeys(enum.Enum):
    DOB = 'dob'
    DATE = 'date'
    NAME = 'name'
    QUOTE = 'quote'
    ZIP = 'zip'
    AMOUNT = 'amount'
    COMPARE = 'compare'
    LESS = 'less'
    GREATER = 'greater'


# function that is called when you visit /
@main.route("/")
def index():
    # you are now in the current application context with the main.route decorator
    # access the logger with the logger from api.core and uses the standard logging module
    # try using ipdb here :) you can inject yourself
    logger.info("Hello World!")
    return render_template('index.html')


# function that is called when you visit /users
@main.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return create_response(data={"users": serialize_list(users)})


# function that is called when you visit /quotes with ability to filter by indicating zip field or amount field
# with an additional field of compare = less or compare = greater if amount is indicated.
# ex: http://localhost:5000/quotes --> will return last 24 hours quotes
# ex: http://localhost:5000/quotes?zip=94085 --> will return last 24 hours quotes whose users have zip = 94085
# ex: ex: http://localhost:5000/quotes?amount=600&compare=less --> will return last 24 hours quotes with quotes less
# than 600
# filters can be compounded and compare will take less as precedence.
@main.route("/quotes", methods=["GET"])
def get_quotes():
    data = request.args
    quotes = Quote.query.filter_by(Quote.date.between(date_yday(), date_now()))

    if ObjKeys.ZIP in data:
        logger.info("Zip filter requested.")
        user_ids_with_zip = User.query.with_entities(User.id).filter_by(zip=data[ObjKeys.ZIP]).all()
        quotes = quotes.filter_by(Quote.user.in_(user_ids_with_zip))
    if ObjKeys.AMOUNT in data:
        logger.info("Amount filter requested.")
        if ObjKeys.COMPARE not in data or data[ObjKeys.COMPARE] is not ObjKeys.LESS or \
                data[ObjKeys.COMPARE] is not ObjKeys.GREATER:
            logger.info("Compare field malformed.")
            return render_template('error.html', msg="Amount mentioned without proper compare field")
        if data[ObjKeys.COMPARE] == ObjKeys.LESS:
            logger.info("Requested less.")
            quotes = quotes.filter_by(Quote.quote <= float(data[ObjKeys.AMOUNT]))
        elif data[ObjKeys.COMPARE] == ObjKeys.GREATER:
            logger.info("Requested greater.")
            quotes = quotes.filter_by(Quote.quote >= float(data[ObjKeys.AMOUNT]))

    return create_response(data={"quotes": serialize_list(quotes.all())})


# function to get quote for specific user, when you visit quote,
# ex: http://localhost:5000/quote?name=Ack&zip=94085&dob=1998-02-01
@main.route("/quote", methods=["GET"])
def get_quote():
    data = request.args
    logger.info("Data received: %s", data)

    error_msg = check_fields(data)
    if error_msg is not None:
        return render_template('error.html', msg=msg)

    # Get quote which matches user info
    user_id = User.query.filter_by(name=data[ObjKeys.NAME], dob=string_to_date(data[ObjKeys.DOB]),
                                   zip=data[ObjKeys.ZIP]).first().id
    quote = Quote.query.filter_by(user=user_id).first().to_dict()

    logger.info("Quote found", quote)
    return create_response(data={"quote": quote})


@main.route("/premium", methods=["GET"])
def get_premium():
    now = date_now()
    current_month = now.date().month()
    current_year = now.date().year()
    quotes = Quote.query.filter_by(Quote.date.date().month() == current_month).all()

    total_premium_collected = 0
    for quoteObj in quotes:
        quote_issuance_date = quoteObj[ObjKeys.DATE]
        total_days_in_current_month = days_in_month(current_month, current_year)
        quote_remaining_days_in_current_month = (last_day_of_month(now.date()) - quote_issuance_date.date()).days + 1

        total_premium_collected += (1.0 * quote_remaining_days_in_current_month) / total_days_in_current_month * \
                                   quoteObj[ObjKeys.QUOTE]

    return create_response(data={"quotes": quotes, "current_month_premium_collected": total_premium_collected})


# POST request for /persons
@main.route("/success", methods=["POST"])
def create_person_and_quote():
    data = request.form
    logger.info("Data received: %s", data)

    error_msg = check_fields(data)
    if error_msg is not None:
        return render_template('error.html', msg=msg)

    # Create new user and quote
    quote = calculate_premium(data[ObjKeys.DOB])
    new_user = User(name=data[ObjKeys.NAME], dob=string_to_date(data[ObjKeys.DOB]), zip=data[ObjKeys.ZIP])
    new_quote = Quote(quote=quote, date=date_now())
    new_user.quotes.append(new_quote)

    db.session.add_all([new_user, new_quote])
    db.session.commit()

    return render_template('quote.html', data=data)


def check_fields(data):
    fields = [ObjKeys.NAME, ObjKeys.DOB, ObjKeys.ZIP]
    for field in fields:
        if field not in data or data[field] == '':
            msg = 'No %s provided for user.' % field
            logger.info(msg)
            return msg
    return None
