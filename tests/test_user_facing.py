#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import Teams, Solves, WrongKeys
import json
from CTFd import utils


def test_index():
    """Does the index page return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_register_user():
    """Can a user can be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_register_duplicate_teamname():
    """A user shouldn't be able to use an already registered team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_register_duplicate_email():
    """A user shouldn't be able to use an already registered email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user2", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_user_bad_login():
    """A user should not be able to login with an incorrect password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user", password="wrong_password")
        r = client.get('/profile')
        assert r.location.startswith("http://localhost/login")  # We got redirected to login
    destroy_ctfd(app)


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.location != "http://localhost/login"  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_isnt_admin():
    """A registered user cannot access admin pages"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/admin/graphs')
        assert r.location == "http://localhost/login"
        assert r.status_code == 302
    destroy_ctfd(app)


def test_user_get_teams():
    """Can a registered user load /teams"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/teams')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scoreboard():
    """Can a registered user load /scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scores():
    """Can a registered user load /scores"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scores')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_topteams():
    """Can a registered user load /top/10"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/top/10')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_challenges():
    """Can a registered user load /challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_chals():
    """Can a registered user load /chals"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_solves_per_chal():
    """Can a registered user load /chals/solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_solves():
    """Can a registered user load /solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_team_page():
    """Can a registered user load their public profile (/team/2)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/team/2')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_profile():
    """Can a registered user load their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_logout():
    """Can a registered user load /logout"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        client.get('/logout', follow_redirects=True)
        r = client.get('/challenges')
        assert r.location == "http://localhost/login?next=challenges"
        assert r.status_code == 302
    destroy_ctfd(app)


def test_user_get_reset_password():
    """Can an unregistered user load /reset_password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = app.test_client()
        r = client.get('/reset_password')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_viewing_challenges():
    """Test that users can see added challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get('/chals')
        chals = json.loads(r.get_data(as_text=True))
        assert len(chals['game']) == 1
    destroy_ctfd(app)


def test_submitting_correct_flag():
    """Test that correct flags are correct"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_incorrect_flag():
    """Test that incorrect flags are incorrect"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'notflag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
    destroy_ctfd(app)


def test_submitting_unicode_flag():
    """Test that users can submit a unicode flag"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag=u'你好')
        with client.session_transaction() as sess:
            data = {
                "key": '你好',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_flags_with_large_ips():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)

        # SQLite doesn't support BigInteger well so we can't test it properly
        ip_addresses = ['172.18.0.1', '255.255.255.255', '2001:0db8:85a3:0000:0000:8a2e:0370:7334']
        for ip_address in ip_addresses:
            # Monkeypatch get_ip
            utils.get_ip = lambda: ip_address

            # Generate challenge and flag
            chal = gen_challenge(app.db)
            chal_id = chal.id
            flag = gen_flag(app.db, chal=chal.id, flag=u'correct_key')

            # Submit wrong_key
            with client.session_transaction() as sess:
                data = {
                    "key": 'wrong_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
            assert WrongKeys.query.filter_by(ip=ip_address).first()

            # Submit correct key
            with client.session_transaction() as sess:
                data = {
                    "key": 'correct_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 1 and resp.get('message') == "Correct"
            assert Solves.query.filter_by(ip=ip_address).first()
    destroy_ctfd(app)


def test_pages_routing_and_rendering():
    """Test that pages are routing and rendering"""
    app = create_ctfd()
    with app.app_context():
        html = '''##The quick brown fox jumped over the lazy dog'''
        route = 'test'
        page = gen_page(app.db, route, html)

        with app.test_client() as client:
            r = client.get('/test')
            output = r.get_data(as_text=True)
            assert "<h2>The quick brown fox jumped over the lazy dog</h2>" in output
    destroy_ctfd(app)


def test_themes_handler():
    """Test that the themes handler is working properly"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/themes/original/static/css/style.css')
            assert r.status_code == 200
            r = client.get('/themes/original/static/css/404_NOT_FOUND')
            assert r.status_code == 404
            r = client.get('/themes/original/static/%2e%2e/%2e%2e/%2e%2e/utils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/%2e%2e%2f%2e%2e%2f%2e%2e%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/..%2f..%2f..%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/../../../utils.py')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_ctfd_setup_redirect():
    """Test that a fresh CTFd instance redirects to /setup"""
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/teams')
            assert r.status_code == 302
            assert r.location == "http://localhost/setup"

            # Files in /themes load properly
            r = client.get('/themes/original/static/css/style.css')
            assert r.status_code == 200
    destroy_ctfd(app)
