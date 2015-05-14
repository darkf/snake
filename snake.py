# Copyright (c) 2015 darkf. Licensed under the terms of the MIT license

import operator, dis, sys

def compile_file(path):
	with open(path, "r") as f:
		return compile(f.read(), path, "exec")

class Function:
	def __init__(self, name, positional, code, interpreter):
		self.__name__ = name
		self.__positional = positional
		self.__code = code
		self.__interpreter = interpreter

	def __call__(self, *args, **kwargs):
		locals = self.__code.co_varnames
		xenv = {k:v for k,v in zip(locals, args)}
		return interpret_code(self.__code, interpreter=self.__interpreter, xenv=xenv)

class Return(BaseException):
	def __init__(self, retval):
		self.retval = retval

def log(*args): print(*args)

# to store the interpreter context as a closure for functions
def interpreter():
	env = {}
	env.update(__builtins__.__dict__) # add python builtins

	def interpret(code, indices, *, xenv=None):
			nonlocal env
			stack = []
			block_stack = []
			localenv = {}
			ip = 0
			if xenv: localenv.update(xenv)

			def offsetof(index): return {v:k for k,v in indices.items()}[index]

			def push(x): stack.append(x)
			def pop(): return stack.pop()

			def interp(ins):
				nonlocal stack, block_stack, ip, env

				if ins.opname == 'LOAD_CONST': push(ins.argval)
				elif ins.opname == 'LOAD_NAME': push(env[ins.argval]) # TODO: use locals or global
				elif ins.opname == 'STORE_NAME': env[ins.argval] = pop()
				elif ins.opname == 'DELETE_NAME': del env[ins.argval]
				elif ins.opname == 'LOAD_GLOBAL': push(env[ins.argval]) # TODO: global env
				elif ins.opname == 'LOAD_FAST': push(localenv[ins.argval])
				elif ins.opname == 'STORE_FAST': localenv[ins.argval] = pop()
				elif ins.opname == 'LOAD_ATTR': push(getattr(pop(), ins.argval))
				elif ins.opname == 'STORE_ATTR': setattr(pop(), ins.argval, pop())
				elif ins.opname == 'CALL_FUNCTION':
					# TODO: handle more than just positional arguments
					argc = ins.argval
					positional = argc & 0xFF
					args = [pop() for _ in range(positional)]
					args.reverse()
					log("args:", args)
					f = pop()
					push(f(*args))
				elif ins.opname == 'MAKE_FUNCTION':
					argc = ins.argval
					positional = argc & 0xFF
					name = pop()
					code = pop()
					default_args = [pop() for _ in range(positional)]
					log("make function:", name, positional, code)
					push(Function(name, positional, code, interpret))
				elif ins.opname == 'POP_TOP': pop()
				elif ins.opname == 'DUP_TOP': push(stack[-1])
				elif ins.opname == 'RETURN_VALUE': raise Return(pop())
				elif ins.opname == 'COMPARE_OP':
					opname = ins.argrepr
					rhs = pop()
					lhs = pop()
					push({'<': operator.lt, '>': operator.gt,
						  '==': operator.eq, '!=': operator.ne,
						  '<=': operator.le, '>=': operator.ge}[opname](lhs, rhs))
				elif ins.opname == 'UNARY_NOT': push(not pop())
				elif ins.opname == 'INPLACE_MULTIPLY': rhs = pop(); push(operator.imul(pop(), rhs))
				elif ins.opname == 'INPLACE_SUBTRACT': rhs = pop(); push(operator.isub(pop(), rhs))
				elif ins.opname == 'INPLACE_ADD': rhs = pop(); push(operator.iadd(pop(), rhs))
				elif ins.opname == 'BINARY_ADD': push(pop() + pop())
				elif ins.opname == 'BINARY_SUBTRACT': rhs = pop(); push(pop() - rhs)
				elif ins.opname == 'BINARY_MULTIPLY': rhs = pop(); push(pop() * rhs)
				elif ins.opname == 'BINARY_MODULO': rhs = pop(); push(pop() % rhs)
				elif ins.opname == 'BINARY_TRUE_DIVIDE': rhs = pop(); push(pop() / rhs)
				elif ins.opname == 'BINARY_OR': rhs = pop(); push(pop() or rhs)
				elif ins.opname == 'BINARY_SUBSCR': i = pop(); push(pop()[i])
				elif ins.opname == 'STORE_SUBSCR': i = pop(); lhs = pop(); lhs[i] = pop()
				elif ins.opname == 'STORE_MAP': k = pop(); v = pop(); stack[-1][k] = v
				elif ins.opname == 'UNPACK_SEQUENCE': stack.extend([x for x in reversed(pop())])
				elif ins.opname == 'LIST_APPEND': v = pop(); stack[-ins.argval].append(v)
				elif ins.opname == 'MAP_ADD': k = pop(); d = stack[-ins.argval-1]; d[k] = pop()
				elif ins.opname == 'BUILD_MAP': push({})
				elif ins.opname == 'BUILD_TUPLE':
					push(tuple(reversed([pop() for _ in range(ins.argval)])))
				elif ins.opname == 'BUILD_LIST':
					push(list(reversed([pop() for _ in range(ins.argval)])))
				elif ins.opname == 'BUILD_SLICE':
					argc = ins.argval
					if argc == 2: # x[i:]
						i = pop(); push(slice(pop(), i))
					elif argc == 3: # x[i:j]
						j = pop(); i = pop(); push(slice(pop(), i, j))
				elif ins.opname == 'SETUP_LOOP':
					# (start, end) indices
					block_stack.append((ip, indices[ins.argval]))
				elif ins.opname == 'POP_BLOCK': block_stack.pop()
				elif ins.opname == 'JUMP_ABSOLUTE':
					log("jmp to {0} ({1})".format(ins.argval, indices[ins.argval]))
					ip = indices[ins.argval]
				elif ins.opname == 'JUMP_FORWARD':
					log("jmp forward to {0} ({1})".format(ins.argval, indices[ins.argval]))
					ip = indices[ins.argval]
				elif ins.opname == 'POP_JUMP_IF_FALSE':
					log("jmpf to {0} ({1})".format(ins.argval, indices[ins.argval]))
					if not pop(): ip = indices[ins.argval]
				elif ins.opname == 'POP_JUMP_IF_TRUE':
					log("jmpt to {0} ({1})".format(ins.argval, indices[ins.argval]))
					if pop(): ip = indices[ins.argval]
				elif ins.opname == 'GET_ITER': push(iter(pop()))
				elif ins.opname == 'FOR_ITER':
					iterator = stack[-1]
					try: push(next(iterator))
					except StopIteration:
						pop()
						ip = indices[ins.argval]
				else:
					raise NotImplementedError("instruction: " + repr(ins))


			while ip < len(code):
				# fetch ins
				ins = code[ip]
				ip += 1

				try:
					interp(ins)
				except Return as e:
					return e.retval

	return interpret

def bytecode_to_list(bytecode):
	"Convert dis.Bytecode instructions into a flat list and a map of offsets to indices"

	instructions = []
	offset_indices = {}

	for i,ins in enumerate(bytecode):
		instructions.append(ins)
		offset_indices[ins.offset] = i

	return instructions, offset_indices

def interpret_code(code, *, interpreter=interpreter(), xenv=None):
	"Interprets a code object"
	bytecode = dis.Bytecode(code)
	log("code disassembly:")
	log(bytecode.dis())
	return interpreter(*bytecode_to_list(bytecode), xenv=xenv)

if __name__ == "__main__":
	interpret_code(compile_file(sys.argv[1]))
