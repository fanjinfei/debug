from functools import partial
def ori_func():
	print('real')

def pd_dec(func):
    def wrap_f(*args, **kwargs):
	print("dec")
        return func(*args, **kwargs)
    func.is_deced = True
    return func

@pd_dec
def f1(chained_f):
   def wrap_f():
	print('a1')
	r = chained_f()
	print('a2')
	return r
   return wrap_f

@pd_dec
def f2(chained_f):
   def wrap_f():
	print('b')
	chained_f()
	print('b2')
   return wrap_f

print(f1.__name__,f1.is_deced, getattr(ori_func,'is_deced', False), f2.__name__)

ori_func = f1(ori_func)
ori_func = f2(ori_func)
print (ori_func())

def f3(a, b, c):
	print(a,b,c)

f4 = partial(f3,1)
print( f4(3, 4) )
