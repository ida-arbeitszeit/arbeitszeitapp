from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from arbeitszeit.errors import CompanyAlreadyExists, MemberAlreadyExists
from arbeitszeit.use_cases import RegisterCompany, RegisterMember
from project import database
from project.database import with_injection

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
def start():
    # not sure if this is the best place to create database instance
    session["user_type"] = None
    return render_template("start.html")


@auth.route("/help")
def help():
    return render_template("start_hilfe.html")


# Member
@auth.route("/member/signup")
def signup_member():
    return render_template("signup_member.html")


@auth.route("/member/signup", methods=["POST"])
@with_injection
def signup_member_post(register_member: RegisterMember):
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    assert email and name and password

    try:
        register_member(email, name, password)
    except MemberAlreadyExists:
        flash("Email address already exists")
        return redirect(url_for("auth.signup_member"))

    return redirect(url_for("auth.login_member"))


@auth.route("/member/login")
def login_member():
    return render_template("login_member.html")


@auth.route("/member/login", methods=["POST"])
def login_member_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    member = database.get_user_by_mail(email)

    if not member or not check_password_hash(member.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login_member"))

    session["user_type"] = "member"
    login_user(member, remember=remember)
    return redirect(url_for("main_member.profile"))


# Company
@auth.route("/company/login")
def login_company():
    return render_template("login_company.html")


@auth.route("/company/login", methods=["POST"])
def login_company_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    company = database.get_company_by_mail(email)

    if not company or not check_password_hash(company.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login_company"))

    session["user_type"] = "company"
    login_user(company, remember=remember)
    return redirect(url_for("main_company.profile"))


@auth.route("/company/signup")
def signup_company():
    return render_template("signup_company.html")


@auth.route("/company/signup", methods=["POST"])
@with_injection
def signup_company_post(register_company: RegisterCompany):
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    assert email and name and password
    try:
        register_company(email, name, password)
    except CompanyAlreadyExists:
        flash("Email address already exists")
        return redirect(url_for("auth.signup_company"))
    return redirect(url_for("auth.login_company"))


# logout
@auth.route("/zurueck")
def zurueck():
    session["user_type"] = None
    logout_user()
    return redirect(url_for("auth.start"))


@auth.route("/logout")
@login_required
def logout():
    session["user_type"] = None
    logout_user()
    return redirect(url_for("auth.start"))
