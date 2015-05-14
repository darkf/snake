import dis

def compile_file(path):
	with open(path, "r") as f:
		return compile(f.read(), path, "exec")

class Function:
	def __init__(self, name, positional, code):
		self.__name__ = name
		self.__positional = positional
		self.__code = code

	def __call__(self, *args, **kwargs):
		locals = self.__code.co_varnames
		xenv = {k:v for k,v in zip(locals, args)}
		return interpret_code(self.__code, xenv=xenv)

class Return(BaseException):
	def __init__(self, retval):
		self.retval = retval

def interpret(code, indices, *, xenv=None):
	stack = []
	ip = 0
	env = {'print': print, 'sum': sum}
	if xenv: env.update(xenv)

	def push(x): stack.append(x)
	def pop(): return stack.pop()

	def interp(ins):
		nonlocal ip, env, stack

		if ins.opname == 'LOAD_CONST': stack.append(ins.argval)
		elif ins.opname == 'LOAD_NAME': stack.append(env[ins.argval]) # TODO: envs
		elif ins.opname == 'STORE_NAME': env[ins.argval] = pop()
		elif ins.opname == 'LOAD_GLOBAL': stack.append(env[ins.argval]) # TODO: global env
		elif ins.opname == 'LOAD_FAST': stack.append(env[ins.argval]) # TODO: locals
		elif ins.opname == 'CALL_FUNCTION':
			# TODO: handle more than just positional arguments
			argc = ins.argval
			positional = argc & 0xFF
			args = [pop() for _ in range(positional)] # stack[-positional:]
			args.reverse()
			#stack = stack[:-positional]
			print("args:", args)
			f = pop()
			push(f(*args))
		elif ins.opname == 'MAKE_FUNCTION':
			argc = ins.argval
			positional = argc & 0xFF
			name = pop()
			code = pop()
			default_args = [pop() for _ in range(positional)]
			print("make function:", name, positional, code)
			push(Function(name, positional, code))
		elif ins.opname == 'POP_TOP': pop()
		elif ins.opname == 'RETURN_VALUE': raise Return(pop())
		elif ins.opname == 'BINARY_ADD': push(pop() + pop())
		elif ins.opname == 'BINARY_SUBSCR': i = pop(); push(pop()[i])
		elif ins.opname == 'BUILD_LIST':
			push(list(reversed([pop() for _ in range(ins.argval)])))
		elif ins.opname == 'BUILD_SLICE':
			argc = ins.argval
			if argc == 2: # x[i:]
				i = pop(); push(slice(pop(), i))
			elif argc == 3: # x[i:j]
				j = pop(); i = pop(); push(slice(pop(), i, j))
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

def bytecode_to_list(bytecode):
	"Convert dis.Bytecode instructions into a flat list and a map of offsets to indices"

	instructions = []
	offset_indices = {}

	for i,ins in enumerate(bytecode):
		instructions.append(ins)
		offset_indices[ins.offset] = i

	return instructions, offset_indices

def interpret_code(code, *, xenv=None):
	"Interprets a code object"
	bytecode = dis.Bytecode(code)
	print("code disassembly:")
	print(bytecode.dis())
	return interpret(*bytecode_to_list(bytecode), xenv=xenv)

interpret_code(compile_file("testmod.py"))
