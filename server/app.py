import logging
import os
import sys
from collections import defaultdict
from datetime import datetime

import click
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import local_settings as conf

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_url_path=os.path.join(basedir, 'static'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, conf.DBFILE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

logger = logging.getLogger('gunicorn.error')

class ThingCounter(db.Model):
    __tablename__ = 'thing_counter'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SinglePress(db.Model):
    __tablename__ = 'single_press'

    id = db.Column(db.Integer, primary_key=True)
    thing_id = db.Column(db.Integer, db.ForeignKey('thing_counter.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ThingSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'count')


class PressSchema(ma.Schema):
    class Meta:
        fields = ('thing_id', 'created_at')


thing_schema = ThingSchema()
things_schema = ThingSchema(many=True)
press_schema = PressSchema(many=True)


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(APIError, self).__init__()
        self.message = message
        self.status_code = status_code or 500
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(APIError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route("/tallymebanana", methods=["GET"])
def tallybanana():
    """ tallybanana -- this just returns json of what's in the db no processing """
    all_the_things = ThingCounter.query.all()
    result = things_schema.dump(all_the_things)
    return jsonify(result.data)


@app.route('/daylightcome', methods=['GET'])
def daylightcome():
    """ Return the SinglePresses table with no processing """
    all_the_things = SinglePress.query.all()
    result = press_schema.dump(all_the_things)
    return jsonify(result.data)


@app.route('/iwannagohome', methods=['GET'])
def iwannagohome():
    """ Return the SinglePresses table with some light processing """
    all_the_things = db.engine.execute("""
        SELECT p.created_at, t.name
          FROM single_press p
          JOIN thing_counter t
            ON p.thing_id = t.id;
    """)
    output = defaultdict(list)
    for row in all_the_things:
        output[row[1]].append(row[0])
    return jsonify([{'name': key, 'presses': value, 'count': len(value)} for key, value in output.items()])


@app.route("/tally", methods=["GET"])
def tally():
    """ tally -- returns a json that graph lib can deal with """
    all_the_things = ThingCounter.query.all()
    result = things_schema.dump(all_the_things)
    names = list()
    counts = list()
    for res in result.data:
        names.append(res['name'])
        counts.append(res['count'])
    ans = {'data': [{'x': names, 'y': counts, 'type': 'bar'}]}

    return jsonify(ans)


def check_auth():
    client_sekrit = request.headers.get(conf.AUTH_HDR)
    if (client_sekrit != conf.AUTH_SEKRIT):
        raise APIError('Say ‘friend’ and enter.', status_code=401)
    return True


@app.route("/thing/<thing>", methods=["PUT", "DELETE", "PURGE"])
def manipulate_thingie(thing):
    """ manipulate_thingie -- either
        - deletes an object from DB;
        - sets it's count=0;
        - or count += 1
        depending on request.method
        silently cuts off <thing> at conf.MAX_THINGIE_NAME_LENGTH bc i'm a bastard """
    thing_name = ''.join([*filter(str.isalnum, thing)])
    thing_name = thing_name[:conf.MAX_THINGIE_NAME_LENGTH]
    q = db.session.query(ThingCounter)
    r = q.filter(ThingCounter.name == thing_name)

    if r.count() not in [0, 1]:
        raise APIError('number of things name %s:%d is neither {0,1}' % (thing, r.count()), status_code=520)

    thing = r.first()
    if not thing:
        if request.method != "PUT":
            raise APIError('{} does not exist to {}'.format(thing, request.method), status_code=409)
        thing = ThingCounter(name=thing_name, count=0)
        db.session.add(thing)
        db.session.flush()  # Get id of new thing

    if request.method == "PURGE":
        check_auth()
        thing.count = 0
    elif request.method == "DELETE":
        check_auth()
        db.session.delete(thing)
    elif request.method == "PUT":
        thing.count = thing.count + 1
        db.session.add(SinglePress(thing_id=thing.id))
    else:
        # Should never get here; should be filtered by flask
        raise APIError('unallowed method: %s' % (request.method), status_code=405)
    db.session.commit()

    return thing_schema.jsonify(thing)


@click.group()
def cli():
    """ Count things """
    pass


@cli.command('run')
def run_command():
    """ Start the server """
    app.run(debug=True)


@cli.command('create')
def create_command():
    """ Create the database """
    db.create_all()


if __name__ == '__main__':
    cli()
