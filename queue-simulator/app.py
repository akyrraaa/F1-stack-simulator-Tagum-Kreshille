from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
import os
import secrets
from queue_model import Queue

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_NAME'] = 'queue_session'  # keeps it apart from the stack app's session


@app.route('/')
def index():
    queue = Queue(session.get('items', []))
    items = queue.items  # not reversed: the front stays first
    size = queue.size()
    removed = session.get('removed', [])
    highlight = request.args.get('peek') == '1'
    return render_template('index.html', items=items, size=size,
                           removed=removed, highlight=highlight)


@app.route('/queue', methods=['POST'])
def operate():
    action = request.form.get('action')
    value = request.form.get('value', '').strip()

    queue = Queue(session.get('items', []))
    removed = session.get('removed', [])
    highlight = False

    if action == 'enqueue':
        if not value or len(value) > 24:
            flash('Enter 1 to 24 characters.', 'error')
        elif queue.size() >= 20:
            flash('Limit is 20 items.', 'error')
        else:
            queue.enqueue(value)
            flash(f'Enqueued {value}', 'success')
    elif action == 'dequeue':
        front = queue.dequeue()
        if front is None:
            flash('Queue is empty.', 'error')
        else:
            removed.insert(0, front)
            removed = removed[:20]  # keep the 20 most recently removed values
            flash(f'Dequeued {front}', 'success')
    elif action == 'peek':
        front = queue.peek()
        if front is None:
            flash('Queue is empty.', 'error')
        else:
            flash(f'Front is {front}', 'success')
            highlight = True
    elif action == 'clear':
        queue.clear()
        removed = []
        flash('Queue and removed history cleared.', 'success')
    else:
        flash('Unknown operation.', 'error')

    session['items'] = queue.items
    session['removed'] = removed
    if highlight:
        return redirect(url_for('index', peek=1))
    return redirect(url_for('index'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(port=5001)  # Local development only. Stop with Ctrl+C.