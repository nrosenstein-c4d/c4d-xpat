
# Automatically generated with c4ddev v1.7.0.

import os
import sys
import c4d

_frame = sys._getframe(1)
while _frame and not '__res__' in _frame.f_globals:
  _frame = _frame.f_back

project_path = os.path.dirname(_frame.f_globals['__file__'])
project_path = os.path.normpath(os.path.join(project_path, ''))
resource = __res__ = _frame.f_globals['__res__']

del _frame

def string(name, *subst, **kwargs):
  disable = kwargs.pop('disable', False)
  checked = kwargs.pop('checked', False)
  if kwargs:
    raise TypeError('unexpected keyword arguments: ' + ','.join(kwargs))

  if isinstance(name, str):
    name = globals()[name]
  elif not isinstance(name, (int, long)):
    raise TypeError('name must be str, int or long')

  result = resource.LoadString(name)
  for item in subst:
    result = result.replace('#', str(item), 1)

  if disable:
    result += '&d&'
  if checked:
    result += '&c&'
  return result

def tup(name, *subst, **kwargs):
  if isinstance(name, str):
    name = globals()[name]
  return (name, string(name, *subst))

def path(*parts):
  """
  Joins the path parts with the #project_path, which is initialized with the
  parent directory of the file that first imported this module (which is
  usually the Python plugin file).
  """
  path = os.path.join(*parts)
  if not os.path.isabs(path):
    path = os.path.join(project_path, path)
  return path

def localpath(*parts, **kwargs):
  """
  Joins the path parts with the parent directory of the Python file that
  called this function.
  """
  _stackdepth = kwargs.get('_stackdepth', 0)
  parent_dir = os.path.dirname(sys._getframe(_stackdepth+1).f_globals['__file__'])
  return os.path.normpath(os.path.join(parent_dir, *parts))

def bitmap(*parts):
  bitmap = c4d.bitmaps.BaseBitmap()
  result, ismovie = bitmap.InitWith(path(*parts))
  if result != c4d.IMAGERESULT_OK:
    return None
  return bitmap

BTN_SAVE = 10004
DLG_OPTIONS = 10001
EDT_HSPACE = 10002
EDT_VSPACE = 10003
XPAT_COMMAND_ALIGNHORIZONTAL = 10007
XPAT_COMMAND_ALIGNHORIZONTAL_HELP = 10008
XPAT_COMMAND_ALIGNVERTICAL = 10009
XPAT_COMMAND_ALIGNVERTICAL_HELP = 10010
XPAT_COMMAND_OPENOPTIONSDIALOG = 10005
XPAT_COMMAND_OPENOPTIONSDIALOG_HELP = 10006
