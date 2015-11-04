# -*- mode: python -*-

block_cipher = None


a = Analysis(['gimp2acv.py'],
             pathex=['C:\\Users\\kolbe\\Desktop\\gimp2acv'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.binaries = a.binaries - TOC([
	('sqlite3.dll', None, None),
	('tcl85.dll', None, None),
	('tk85.dll', None, None),
	('_sqlite3', None, None),
	('_ssl', None, None),
	('bz2', None, None),
	('_multiprocessing', None, None),
	('_hashlib', None, None),
	('mfc90.dll', None, None),
	('mfc90u.dll', None, None),
	('mfcm90.dll', None, None),
	('mfcm90u.dll', None, None),
	('msvcr90.dll', None, None),
	('msvcm90.dll', None, None),
	('msvcp90.dll', None, None),
	('_tkinter', None, None)])


a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]
for i in a.binaries:
	print i[0]#, i[1], i[2]
	

for d in a.datas:
	if d[0].startswith('tk') or d[0].startswith('tcl'):
		#print d[0]
		#a.excludes += d
		a.datas.remove(d)
	
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='gimp2acv',
          debug=False,
          strip=None,
          upx=True,
          console=True )
