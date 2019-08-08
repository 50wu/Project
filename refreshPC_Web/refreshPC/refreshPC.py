#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 18:39:14 2019

@author: nwu
"""
import datetime, dateutil.parser
import time
from flask import Flask, render_template, redirect, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired
import logging


logging.basicConfig()
logger = logging.getLogger('logger')
logger.warning('The system may break down')


app = Flask(__name__)
app.config.from_pyfile('config.py')


class SnForm(FlaskForm):
    serial_number = StringField('Serial Number', validators=[DataRequired()])

class RefForm(FlaskForm):
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    choice = RadioField('Label', choices=[('yes','Refresh'),('no','No need')], validators=[DataRequired()])
    
def apple_year_offset(dateobj, years=0):
    # Convert to a maleable format
    mod_time = dateobj.timetuple()
    # Offset year by number of years
    mod_time = time.struct_time(tuple([mod_time[0]+years]) + mod_time[1:])
    # Convert back to a datetime obj
    return datetime.datetime.fromtimestamp(int(time.mktime(mod_time)))    
    
def getEndDateFromsn(serial_number):
    # http://www.macrumors.com/2010/04/16/apple-tweaks-serial-number-format-with-new-macbook-pro/
    est_date = u''
    if 10 < len(serial_number) < 13:
        if len(serial_number) == 11:
            # Old format
            year = serial_number[2].lower()
            est_year = 2000 + '   3456789012'.index(year)
            week = int(serial_number[3:5]) - 1
            year_time = datetime.date(year=est_year, month=1, day=1)
            if (week):
                week_dif = datetime.timedelta(weeks=week)
                year_time += week_dif
            est_date = u'' + year_time.strftime('%Y-%m-%d')
        else:
            # New format
            alpha_year = 'cdfghjklmnpqrstvwxyz'
            year = serial_number[3].lower()
            est_year = int(2010 + (alpha_year.index(year) / 2))
            # 1st or 2nd half of the year
            est_half = alpha_year.index(year) % 2
            week = serial_number[4].lower()
            alpha_week = ' 123456789cdfghjklmnpqrtvwxy'
            est_week = alpha_week.index(week) + (est_half * 26) - 1
            year_time = datetime.date(year=est_year, month=1, day=1)
            if (est_week):
                week_dif = datetime.timedelta(weeks=est_week)
                year_time += week_dif
            est_date = u'' + year_time.strftime('%Y-%m-%d')
            end_date =  u'' + apple_year_offset(dateutil.parser.parse(est_date), 3).strftime('%Y-%m-%d')
    return end_date

@app.route('/check', methods=('GET', 'POST'))
def check():
    form = RefForm()
    if form.validate_on_submit():
        refresh = form.choice.data
        if refresh.lower() == 'yes':
            google_form_url = app.config['GOOGLE_FORM_URL']
            return redirect(google_form_url)
        return redirect('/finish')
    return render_template('check.html', form=form, serial_number=session.get('serial_number', ''),\
                           end_date=session.get('end_date', ''), current_date=session.get('current_date', ''))

@app.route("/", methods=('GET', 'POST'))
def refreshPC():
    form = SnForm()
    if form.validate_on_submit():
        serial_number = request.form['serial_number']
        end_date = getEndDateFromsn(serial_number)
        if end_date:
            current_date = time.strftime("%Y-%m-%d", time.localtime())
            session['current_date'] = current_date
            session['end_date'] = end_date
            session['serial_number'] = serial_number
            return redirect('/check')
        return redirect('/norecord')
    return render_template('home.html', form=form)

@app.route("/norecord")
def norecord():
    return render_template('message.html')

@app.route("/finish")
def finish():
    return render_template('finish.html')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

