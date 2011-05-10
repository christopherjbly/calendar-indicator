#
# encoderapi.py
# 
# An api for encoder
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$23/03/2011'
__copyright__ = 'Copyright (c) 2011 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'

from Crypto.Cipher import AES
import base64

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '&'

MK = 'YlF1YfNqaLpgRQ21rlyOpM1RpHztgKhi9t7YAB9+3i8=CDYU/qPgmqo4bzeqqvG86GeXgZYrPFc0RgkjEx2NCaE=GAfPmvXMxZrh1sBwnM4QbRF65EcOirhjU0lAFJWhe+I=4SnMYszjwos5XUCTxDp7a5pe4fcxt/EWP/iQ96h1WNA=/g689L9NBj0wNdSSu48jEL5bGpsoDv6JlIxi0cJ3LGI='
def convertStr(s):
	"""Convert string to either int"""
	try:
		ret = int(s)
	except:
		ret = 0
	return ret

class Encoder:
	def __init__(self):
		AE=MK[30:80]
		self.cipher = AES.new(self.pad(AE[10:41]))
	
	def encode(self,cadena):
		return base64.b64encode(self.cipher.encrypt(self.pad(cadena)))
	
	def decode(self,cadena):
		return self.cipher.decrypt(base64.b64decode(cadena)).rstrip(PADDING)
	
	def pad(self,cadena):
		return cadena + (BLOCK_SIZE - len(cadena) % BLOCK_SIZE) * PADDING

if __name__ == "__main__":
	encoder = Encoder()
	key = encoder.encode('prueba')
	print key
	print encoder.decode(key)
	
