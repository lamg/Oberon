# Translation of ORS.Mod.txt

import sys,os

IdLen = 32
NKW = 34 #number of keywords
maxExp = 38; stringBufSize = 256

#lexical symbols
null = 0; times = 1; rdiv = 2; div = 3; mod = 4
And  = 5; plus = 6; minus = 7; Or = 8; eql = 9
neq = 10; lss = 11; leq = 12; gtr = 13; geq = 14
In  = 15; Is = 16; arrow = 17; period = 18
char = 20; Int = 21; real = 22; false = 23; true = 24
nil = 25; string = 26; Not = 27; lparen = 28; lbrak = 29
lbrace = 30; ident = 31
If = 32; While = 34; repeat = 35; Case = 36; For = 37
comma = 40; colon = 41; becomes = 42; upto = 43; rparen = 44
rbrak = 45; rbrace = 46; then = 47; of = 48; do = 49
to = 50; by = 51; semicolon = 52; end = 53; bar = 54
Else = 55; elsif = 56; until = 57; Return = 58
array = 60; record = 61; pointer = 62; const = 63; Type = 64
var = 65; procedure = 66; begin = 67; Import = 68; module = 69;
eof = 70# This symbol was added by me because it was
#needed a symbol for denoting the end of file, that made
#the loop in the Get procedure terminate. In Compiler Construction,
#Wirth uses it.

class Ident:
	def __init__(self, chl):
		"""chl must be a list of char of at most 32 elements"""
		self.chl  = chl

class KTElm:
	def __init__(self,sym,Id):
		self.sym,self.id = sym, Id
		
ival, slen = 0, 0 #results of get
rval = 0.0
Id = ['']*IdLen #for identifiers
Str = ['']*stringBufSize
errcnt = 0

ch = '' #last character read
errpos = 0
R = None #file reader
W = None #file writer
k = 0
KWX = [0]*10 #for all i in [0,10] 'the amount of keywords in the
#language with i letters = KWX[i] except for i = 8 which is equals
#to KWX[7] (I don't know why)'
keyTab =  [KTElm(0,['']*12)]*NKW #element: KTElm

def CopyId(ident):
	global Id
	ident = Id

#the semantics of Oberon's Texts.Pos is not clear to me
#therefore this translation may be not accurate
def Pos():
	return R.seek(0,os.SEEK_CUR) - 1

def Mark(msg):
	global errpos,errcnt
	p = Pos()
	if p > errpos and errcnt < 25:
		W.write('\n')
		W.write(" pos ")
		W.write(str(p))
		W.write(" ")
		W.write(msg)
	errcnt += 1
	errpos = p + 4

def Identifier(sym):
	global ch,R,IdLen,KWX,Id,keyTab,ident
	i,k,b = 0,0,True
	while b:
		if i < IdLen-1:
			Id[i] = ch
			i += 1
		ch = R.read(1)
		b = not (ch < "0" or (ch > "9" and ch < "A") or (ch > "Z" and ch < "a") or ch > "z")
	Id[i] = 0
	if i < 10:
		k = KWX[i-1] #search for keyword
		while (Id != keyTab[k].id) and (k < KWX[i]):
			k += 1
		if k < KWX[i]:
			sym = keyTab[k].sym
		else:
			sym = ident
	else:
		sym = ident

def String():
	global R,ch,stringBufSize,Str,slen
	i = 0
	ch = R.read(1)
	#is the loop guard equivalent to the source?
	while ch != '' and ch != chr(0x22):
		if ch >= ' ':
			if i < stringBufSize-1:
				Str[i] = ch
				i += 1
			else:
				Mark('String too long')
		ch = R.read(1)
	Str[i] = 0
	i += 1
	ch = R.read(1)
	slen = i

def HexString():
	global ch,R,stringBufSize
	i,m,n = 0,0,0
	ch = R.Read(1)
	while ch != '' and ch != '$':
		while ch == ' ' or ch == chr(0x9) or ch == chr(0xD):
			ch = R.read(1)
		#spaces and other characters skipped
		if '0' <= ch and ch <= '9':
			n = ord(ch) - 0x30
		elif 'A' <= ch and ch <= 'F':
			n = ord(ch) - 0x37
		else:
			n = 0
			Mark('hexdig expected')
		ch = R.read(1)
		if '0' <= ch and ch <= '9':
			n = ord(ch) - 0x30
		elif 'A' <= ch and ch <= 'F':
			n = ord(ch) - 0x37
		else:
			n = 0
			Mark('hexdig expected')
		if i < stringBufSize:
			Str[i] = chr(m*0x10 + n)
			i += 1
		else:
			Mark('string too long')
		ch = R.read(1)
	ch = R.read(1)
	slen = i

def Ten(e):
	x, t = 1.0, 10.0
	while e > 0:
		if e % 2 == 1:
			x = t * x
		t = t * t
		e = e // 2
	return x

def Number(sym):
	global ch, R, ival, rval, Int, real, maxExp
	max, maxM = 2**31, 2**24
	i, k, e, n, s, h, x = 0, 0, 0, 0, 0, 0, 0.0
	ival = 0
	d = [0]*16
	negE, b = False, True
	while b:
		if n < 16:
			d[n] = ord(ch)-0x30
			n += 1
		else:
			Mark('too many digits')
			n = 0
		ch = R.read(1)
		b = not (ch < '0' or (ch > '9' and ch < 'A') or ch > 'F')
	if ch == 'H' or ch == 'R' or ch == 'X':
		#hex
		b = True
		while b:
			h = d[i]
			if h >= 10:
				h = h - 7
			k = k*0x10 + h
			i += 1
			b = i != n
		if ch == 'X':
			sym = char
			if k < 0x100:
				ival = k
			else:
				Mark('illegal value')
				ival = 0
		elif ch == 'R':
			sym = real
			rval = k #I guess SYSTEM.VAL(REAL, k) converts INTEGER to REAL
		else:
			sym = Int
			ival = k
		ch = R.read(1)
	elif ch == ".":
		ch = R.read(1)
		if ch == '.':
			#double dot
			ch = chr(0x7F)
			#decimal integer
			b = True
			while b:
				if d[i] < 10:
					h = k*10 + d[i]
					if h < max:
						k = h
					else:
						Mark('too large')
				else:
					Mark('bad integer')
				i += 1
				b = i != n
			sym = Int
			ival = k
		else: #real number
			x, e, b = 0.0, 0, True
			while b:
				h = k*10 + d[i]
				if h < maxM:
					k = h
				else:
					Mark('too many digits')
				i += 1
				b = i != n
			while ch >= '0' and ch <= '9': #fraction
				h = k*10 + ord(ch) - 0x30
				if h < maxM:
					k = h
				else:
					Mark('too many digits')
				e -= 1
				ch = R.read(1)
			x = k*1.0 #FLT(k)
			if ch == 'E' or ch == 'D': #scale factor
				ch = R.read(1)
				s = 0
				if ch == '-':
					negE = True
					ch = R.read(1)
				else:
					negE = False
					if ch == '+':
						ch = R.read(1)
				if ch >= '0' and ch <= '9':
					b = True
					while b:
						s = s*10 + ord(ch)-0x30
						ch = R.read(1)
						b = not (ch < '0' or ch > '9')
					if negE:
						e = e-s
					else:
						e = e + s
				else:
					Mark('digit?')
				if e < 0:
					if e >= -maxExp:
						x = x/Ten(-e)
					else:
						x = 0.0
				elif e > 0:
					if e <= maxExp:
						x = Ten(e) * x
					else:
						x = 0.0
						Mark('too large')
				sym = real
				rval = x
			else: #decimal integer
				while i != n:
					if d[i] < 10:
						if k <= (max - d[i]) // 10:
							k = k*10 + d[i]
						else:
							Mark("too large"); k = 0
					else:
						Mark("bad integer")
					i += 1
				sym = int
				ival = k

def comment():
	global ch, R
	ch = R.read(1)
	while ch != ')' and ch != '':
		while ch != '' and ch != '*':
			if ch == '(':
				ch = R.read(1)
				if ch == '*':
					comment()
			else:
				ch = R.read(1)
		while ch == '*':
			ch = R.read(1)
	if ch != '':
		ch = R.read(1)
	else:
		Mark('unterminated comment')

def Get(sym):
	global null, ch, R, string, neq, And, lparen, rparen, \
	times, plus, comma, minus, upto, period, rdiv, becomes, \
	colon, semicolon, leq, lss, eql, geq, gtr, lbrak, rbrak, arrow, \
	lbrace, rbrace, bar, Not, upto
	b = True
	while b:
		while ch != '' and ch <= ' ':
			ch = R.read(1)
		if ch == '':
			sym = eof
		elif ch < 'A':
			if ch < '0':
				if ch == chr(0x22):
					String()
					sym = string
				elif ch == '#':
					ch = R.read(1)
					sym = neq
				elif ch == '&':
					ch = R.read(1)
					sym = And
				elif ch == '(':
					ch = R.read(1)
					if ch == '*':
						sym = null
						comment()
					else:
						sym = lparen
				elif ch == ')':
					ch = R.read(1)
					sym = rparen
				elif ch == '*':
					ch = R.read(1)
					sym = times
				elif ch == '+':
					ch = R.read(1)
				elif ch == ',':
					ch = R.read(1)
					sym = comma
				elif ch == '-':
					ch = R.read(1)
					sym = minus
				elif ch == '.':
					ch = R.read(1)
					if ch == '.':
						sym = upto
					else:
						sym = period
				elif ch == '/':
					ch = R.read(1)
					sym = rdiv
				else:
					ch = R.read(1)# ! % ' 
					sym = null
			elif ch < ':':
				Number(sym)
			elif ch == ':':
				ch = R.read(1)
				if ch == '=':
					ch = R.read(1)
					sym = becomes
				else :
					sym = colon
			elif ch == ';':
				ch = R.read(1)
				sym = semicolon
			elif ch == '<':
				ch = R.read(1)
				if ch == '=':
					ch = R.read(1)
					sym = leq
				else:
					sym = lss
			elif ch == '>':
				ch = R.read(1)
				sym = eql
			elif ch == '>':
				ch = R.read(1)
				if ch == '=':
					ch = R.read(1)
					sym = geq
				else:
					sym = gtr
			else: # ? @ 
				ch = R.read(1)
				sym = null
		elif ch < '[':
			Identifier(sym)
		elif ch < 'a':
			if ch == '[':
				sym = lbrak
			elif ch == ']':
				sym = rbrak
			elif ch == '^':
				sym = arrow
			else:# _ ` 
				sym = null
			ch = R.read(1)
		elif ch < '{':
			Identifier(sym)
		else:
			if ch == '{':
				sym = lbrace
			elif ch == '}':
				sym = rbrace
			elif ch == '|':
				sym = bar
			elif ch == '~':
				sym = Not
			elif ch == chr(0x7F):
				#explained in Project Oberon
				#the use of the character 7FX
				sym = upto
			else:
				sym = null
			ch = R.read(1)
		b = sym == null
		#having b ≡ sym = null the loop doesn't
		#end when the file reader reaches the end
		#of the file
	return sym


def Init(t,pos):
	global errpos, errcnt, R, ch
	errpos = pos
	errcnt = 0
	R = open(t)
	R.seek(pos)
	ch = R.read(1)
	
def EnterKW(sym, name):
	global keyTab, k
	keyTab[k].id = name
	keyTab[k].sym = sym
	k += 1
	
W = sys.stderr
k = 0 # I already wrote this because declaration and
#initialization of variables in Python are the same thing
EnterKW(If,'IF')
EnterKW(do,'DO')
EnterKW(of,'OF')
EnterKW(Or,'OR')
EnterKW(to,'TO')
EnterKW(In,'IN')
EnterKW(Is,'IS')
EnterKW(by,'BY')
KWX[2] = k
EnterKW(end, 'END')
EnterKW(nil, 'NIL')
EnterKW(var,'VAR')
EnterKW(div,'DIV')
EnterKW(mod,'MOD')
EnterKW(For,'FOR')
KWX[3] = k
EnterKW(Else,'ELSE')
EnterKW(then,'THEN')
EnterKW(true,'TRUE')
EnterKW(Type,'TYPE')
EnterKW(Case,'CASE')
KWX[4] = k
EnterKW(elsif,'ELSIF')
EnterKW(false,'FALSE')
EnterKW(array,'ARRAY')
EnterKW(begin,'BEGIN')
EnterKW(const,'CONST')
EnterKW(const,'UNTIL')
EnterKW(until,'WHILE')
KWX[5] = k
EnterKW(record,'RECORD')
EnterKW(repeat,'REPEAT')
EnterKW(Return,'RETURN')
EnterKW(Import,'IMPORT')
EnterKW(module,'MODULE')
KWX[6] = k
EnterKW(pointer,'POINTER')
KWX[7] = k
KWX[8] = k
EnterKW(procedure,'PROCEDURE')
KWX[9] = k
