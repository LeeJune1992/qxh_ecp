#coding=utf-8
import os
from flask import abort,render_template,Blueprint,current_app,send_from_directory,request,flash,redirect,url_for
from analytics.forms import ProductForm,MediumForm,PlaceForm,ContentForm,ADForm
from analytics.models import AD_Product,AD_Medium,AD_Place,AD_Content,AD
from extensions import db
from sqlalchemy import func,create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from utils.decorator import admin_required
from datetime import datetime,timedelta
from collections import defaultdict

from global_settings import SQLALCHEMY_BINDS


engine = create_engine(SQLALCHEMY_BINDS['analytics'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


analytics = Blueprint('analytics',__name__,url_prefix='/analytics')

@analytics.route('/product/manage',methods = ['GET','POST'])
@admin_required
def product_manage():
    form = ProductForm()
    if form.validate_on_submit():
        product = AD_Product()
        form.populate_obj(product)
        db.session.add(product)
        db.session.commit()
        flash(u'产品《%s》已添加！' % form.name.data)
        return redirect(request.path)
    items = AD_Product.query.all()
    return render_template('analytics/product.html', form=form, items=items)


@analytics.route('/medium/manage',methods = ['GET','POST'])
@admin_required
def medium_manage():
    form = MediumForm()
    if form.validate_on_submit():
        medium = AD_Medium()
        form.populate_obj(medium)
        db.session.add(medium)
        db.session.commit()
        flash(u'媒体《%s》已添加！' % form.name.data)
        return redirect(request.path)
    items = AD_Medium.query.all()
    return render_template('analytics/medium.html', form=form, items=items)


@analytics.route('/place/manage',methods = ['GET','POST'])
@admin_required
def place_manage():
    form = PlaceForm()
    if form.validate_on_submit():
        place = AD_Place()
        place.medium_id = form.medium.data.id
        place.name = form.name.data
        place.url = form.url.data
        place.remark = form.remark.data
        db.session.add(place)
        db.session.commit()
        flash(u'广告位《%s》已添加！' % form.name.data)
        return redirect(request.path)
    items = AD_Place.query.join(AD_Medium,AD_Medium.id==AD_Place.medium_id).order_by(AD_Place.medium_id)
    return render_template('analytics/place.html', form=form, items=items)


@analytics.route('/content/list')
@admin_required
def content_list():
    page = int(request.args.get('page',1))
    q = request.args.get('q','')
    if q:
        pagination = AD_Content.query.filter(AD_Content.name.like('%'+q+'%')).order_by(db.desc(AD_Content.created)).paginate(page, per_page=20)
    else:
        pagination = AD_Content.query.order_by(db.desc(AD_Content.created)).paginate(page, per_page=20)
    return render_template('analytics/content_list.html',pagination=pagination)

@analytics.route('/content/add',methods = ['GET','POST'])
@admin_required
def content_add():
    form = ContentForm()
    if form.validate_on_submit():
        content = AD_Content()
        form.populate_obj(content)
        db.session.add(content)
        db.session.commit()
        flash(u'广告内容《%s》已添加！' % form.name.data)
        return redirect(url_for('.content_list'))
    return render_template('analytics/content_form.html', form=form)

@analytics.route('/content/edit/<int:content_id>',methods = ['GET','POST'])
@admin_required
def content_edit(content_id):
    content = AD_Content.query.get_or_404(content_id)
    form = ContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        db.session.commit()
        flash(u'广告内容《%s》已修改！' % form.name.data)
        return redirect(url_for('.content_list'))
    return render_template('analytics/content_form.html', form=form,is_edit=True)


@analytics.route('/code/<string:code>')
def ad_code(code):
    ad = AD.query.filter(AD.code==code).first()
    if not ad:abort(404)
    return render_template('analytics/code.html',ad=ad)

@analytics.route('/ad/add',methods = ['GET','POST'])
@admin_required
def ad_add():
    form = ADForm()
    if form.validate_on_submit():
        code = AD.generate_code(form.product.data.id,form.place.data.medium_id,form.place.data.id,form.content.data.id)
        if db.session.query(func.count(AD.id)).filter(AD.code==code).scalar()>0:
            flash(u'广告代码已存在！',category='error')
        else:
            ad = AD()
            ad.name = form.name.data
            ad.code = code
            product = form.product.data
            ad.product_id = product.id
            ad.product_name = product.name
            place = form.place.data
            medium = place.medium
            ad.medium_id = medium.id
            ad.medium_name = medium.name
            ad.place_id = place.id
            ad.place_name = place.name

            content = form.content.data
            ad.ad_id = content.id
            ad.ad_name = content.name
            ad.ad_mode = content.mode
            ad.ad_type = content.type
            ad.ad_img = content.img
            ad.ad_txt = content.txt
            ad.ad_url = place.url
            ad.to_url = content.to_url
            ad.remark = form.remark.data

            db.session.add(ad)
            db.session.commit()
            flash(u'广告内容《%s》已添加！' % form.name.data)
            return redirect(url_for('.ad_code',code=code))
    return render_template('analytics/ad_form.html', form=form)


@analytics.route('/ad/list')
@admin_required
def ad_list():
    page = int(request.args.get('page',1))
    q = request.args.get('q','')
    if q:
        pagination = AD.query.filter(AD.name.like('%'+q+'%')).order_by(db.desc(AD.created)).paginate(page, per_page=20)
    else:
     pagination = AD.query.order_by(db.desc(AD.created)).paginate(page, per_page=20)
    return render_template('analytics/ad_list.html',pagination=pagination)


@analytics.route('/ad/report/report_by_medium')
@admin_required
def analytics_report_by_medium():
    _conditions = []
    _start_date = request.args.get('start_date','')
    if _start_date:
        _conditions.append('`dt`>="%s"'%_start_date)

    _end_date = request.args.get('end_date','')
    if _end_date:
        _conditions.append('`dt`<="%s"'%_end_date)

    if not _start_date and not _end_date:
        _yestoday = (datetime.now()+timedelta(days=-1)).strftime('%Y-%m-%d')
        _conditions.append('`dt`>="%s 00:00:00"'%_yestoday)
        period = _yestoday
    else:
        period = '%s ~ %s'%(_start_date if _start_date else u'开始',_end_date if _end_date else u'现在')

    rows = db_session.execute('''
    SELECT
        code,name,product_name,product_id,medium_id,medium_name,place_id,place_name,ad_id,ad_name,action,action_name,
        SUM(`pv`) AS pvs,SUM(`ip`) AS ips,SUM(`uv`) AS uvs
    FROM `ad_report_view` WHERE %s
    GROUP BY code,name,product_name,product_id,medium_id,medium_name,place_id,place_name,ad_id,ad_name,action,action_name
    '''%' AND '.join(_conditions))

    data = {}
    for code,name,product_name,product_id,medium_id,medium_name,place_id,place_name,ad_id,ad_name,action,action_name,pvs,ips,uvs in rows:
        if not data.has_key(code):
            d = {'name':name,'product_name':product_name,'medium_name':medium_name,'place_name':place_name,'ad_name':ad_name,'actions':{},
                          'ip':0,'pv':0,'uv':0,'orders':0,'fee':0,'nums':0}
            data[code] = d
        else:
            d = data[code]

        if action == 'VISIT':
            d.update({'ip':ips,'pv':pvs,'uv':uvs})
        elif action == 'CLICK':
            d['actions'][action_name] = ips
            d['nums'] += 1
    return render_template('analytics/analytics_report_by_medium.html',period=period,data=data)


