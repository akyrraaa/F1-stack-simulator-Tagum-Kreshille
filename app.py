from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
import os
import secrets
from stack_model import Stack

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))


@app.route('/')
def index():
    stack = Stack(session.get('items', []))
    items = list(reversed(stack.items))  # last pushed is shown on top
    size = stack.size()
    popped = session.get('popped', [])
    highlight = request.args.get('peek') == '1'
    return render_template('index.html', items=items, size=size,
                           popped=popped, highlight=highlight)


@app.route('/stack', methods=['POST'])
def operate():
    action = request.form.get('action')
    value = request.form.get('value', '').strip()

    stack = Stack(session.get('items', []))
    popped = session.get('popped', [])
    highlight = False

    if action == 'push':
        if not value or len(value) > 24:
            flash('Enter 1 to 24 characters.', 'error')
        elif stack.size() >= 20:
            flash('Limit is 20 items.', 'error')
        else:
            stack.push(value)
            flash(f'Pushed {value}', 'success')
    elif action == 'pop':
        removed = stack.pop()
        if removed is None:
            flash('Stack is empty.', 'error')
        else:
            popped.insert(0, removed)
            popped = popped[:20]  # keep the 20 most recently removed values
            flash(f'Popped {removed}', 'success')
    elif action == 'peek':
        top = stack.peek()
        if top is None:
            flash('Stack is empty.', 'error')
        else:
            flash(f'Top is {top}', 'success')
            highlight = True
    elif action == 'clear':
        stack.clear()
        popped = []
        flash('Stack and deleted history cleared.', 'success')
    else:
        flash('Unknown operation.', 'error')

    session['items'] = stack.items
    session['popped'] = popped
    if highlight:
        return redirect(url_for('index', peek=1))  # peek flag highlights the top item
    return redirect(url_for('index'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run()  # Local development only. Stop with Ctrl+C.