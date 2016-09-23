from __future__ import absolute_import

#from celery import app

from celery import Celery

app = Celery('tasks',
             broker='amqp://',
             #backend='rpc://')
app = Celery('tasks',
             broker='amqp://')
# Optional configuration, see the application user guide.



@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
@app.task(ignore_result=True)

def print_hello():
    print 'hello there'
    
@app.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i*i, x+1, i):
                multiples.append(j)
    return results