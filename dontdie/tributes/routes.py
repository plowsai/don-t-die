from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from dontdie import db
from dontdie.models import Tribute, User
from dontdie.tributes.forms import TributeForm, TributeVisibilityForm

tributes = Blueprint('tributes', __name__)

@tributes.route('/tribute/new/<string:username>', methods=['GET', 'POST'])
@login_required
def new_tribute(username):
    recipient = User.query.filter_by(username=username).first_or_404()
    
    # Check if user is a friend
    if not current_user.is_friend(recipient) and current_user.id != recipient.id:
        flash('You can only write tributes for friends.', 'warning')
        return redirect(url_for('users.user_profile', username=username))
        
    form = TributeForm()
    if form.validate_on_submit():
        tribute = Tribute(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            recipient=recipient,
            is_visible=form.is_visible.data
        )
        db.session.add(tribute)
        db.session.commit()
        flash('Your tribute has been created!', 'success')
        return redirect(url_for('users.user_profile', username=username))
    return render_template('tributes/create_tribute.html', title='New Tribute',
                          form=form, recipient=recipient)

@tributes.route('/tribute/<int:tribute_id>')
@login_required
def tribute(tribute_id):
    tribute = Tribute.query.get_or_404(tribute_id)
    
    # Only author can see non-visible tributes
    if not tribute.is_visible and tribute.author_id != current_user.id:
        abort(403)
        
    # Only author and recipient can see tributes
    if tribute.author_id != current_user.id and tribute.recipient_id != current_user.id:
        abort(403)
        
    return render_template('tributes/tribute.html', title=tribute.title, tribute=tribute)

@tributes.route('/tribute/<int:tribute_id>/update', methods=['GET', 'POST'])
@login_required
def update_tribute(tribute_id):
    tribute = Tribute.query.get_or_404(tribute_id)
    
    # Only author can update
    if tribute.author_id != current_user.id:
        abort(403)
        
    form = TributeForm()
    if form.validate_on_submit():
        tribute.title = form.title.data
        tribute.content = form.content.data
        tribute.is_visible = form.is_visible.data
        db.session.commit()
        flash('Your tribute has been updated!', 'success')
        return redirect(url_for('tributes.tribute', tribute_id=tribute.id))
    elif request.method == 'GET':
        form.title.data = tribute.title
        form.content.data = tribute.content
        form.is_visible.data = tribute.is_visible
        
    return render_template('tributes/create_tribute.html', title='Update Tribute',
                          form=form, recipient=tribute.recipient, legend='Update Tribute')

@tributes.route('/tribute/<int:tribute_id>/delete', methods=['POST'])
@login_required
def delete_tribute(tribute_id):
    tribute = Tribute.query.get_or_404(tribute_id)
    
    # Only author can delete
    if tribute.author_id != current_user.id:
        abort(403)
        
    db.session.delete(tribute)
    db.session.commit()
    flash('Your tribute has been deleted!', 'success')
    return redirect(url_for('users.user_profile', username=tribute.recipient.username))

@tributes.route('/tribute/<int:tribute_id>/visibility', methods=['GET', 'POST'])
@login_required
def update_visibility(tribute_id):
    tribute = Tribute.query.get_or_404(tribute_id)
    
    # Only author can update visibility
    if tribute.author_id != current_user.id:
        abort(403)
        
    form = TributeVisibilityForm()
    if form.validate_on_submit():
        tribute.is_visible = form.is_visible.data
        db.session.commit()
        flash('Tribute visibility updated!', 'success')
        return redirect(url_for('tributes.tribute', tribute_id=tribute.id))
    elif request.method == 'GET':
        form.is_visible.data = tribute.is_visible
        
    return render_template('tributes/visibility.html', title='Update Visibility',
                          form=form, tribute=tribute)

@tributes.route('/my-tributes')
@login_required
def my_tributes():
    # Tributes I've written
    tributes_written = Tribute.query.filter_by(author_id=current_user.id).order_by(Tribute.created_at.desc()).all()
    
    # Tributes about me that are visible
    tributes_received = Tribute.query.filter_by(
        recipient_id=current_user.id, is_visible=True
    ).order_by(Tribute.created_at.desc()).all()
    
    return render_template('tributes/my_tributes.html', title='My Tributes',
                          tributes_written=tributes_written,
                          tributes_received=tributes_received) 