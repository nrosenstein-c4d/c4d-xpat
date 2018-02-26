# The MIT License (MIT)
#
# Copyright (c) 2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import json
import c4d
import itertools
from c4d.modules import graphview as gv
from nr.c4d import gv as graphnode
from . import res
from .res import __res__

OPTIONS_FILENAME = res.localpath('../config.json')

def align_nodes(nodes, mode, spacing):
    r"""
    Aligns the passed nodes horizontally and apply the minimum spacing
    between them.
    """

    modes = ['horizontal', 'vertical']
    if not nodes:
        return
    if mode not in modes:
        raise ValueError('invalid mode, choices are: ' + ', '.join(modes))

    get_0 = lambda x: x.x
    get_1 = lambda x: x.y
    set_0 = lambda x, v: setattr(x, 'x', v)
    set_1 = lambda x, v: setattr(x, 'y', v)

    if mode == 'vertical':
        get_0, get_1 = get_1, get_0
        set_0, set_1 = set_1, set_0

    nodes = [graphnode.GraphNode(n) for n in nodes]
    nodes.sort(key=lambda n: get_0(n.position))
    midpoint = graphnode.find_nodes_mid(nodes)

    # Apply the spacing between the nodes relative to the coordinate-systems
    # origin. We can offset them later because we now the nodes' midpoint
    # already.
    first_position = nodes[0].position
    new_positions = []
    prev_offset = 0
    for node in nodes:
        # Compute the relative position of the node.
        position = node.position
        set_0(position, get_0(position) - get_0(first_position))

        # Obtain it's size and check if the node needs to be re-placed.
        size = node.size
        if get_0(position) < prev_offset:
            set_0(position, prev_offset)
            prev_offset += spacing + get_0(size)
        else:
            prev_offset = get_0(position) + get_0(size) + spacing

        set_1(position, get_1(midpoint))
        new_positions.append(position)

    # Center the nodes again.
    bbox_size = prev_offset - spacing
    bbox_size_2 = bbox_size * 0.5
    for node, position in itertools.izip(nodes, new_positions):
        # TODO: Here is some issue with offsetting the nodes. Some value
        # dependent on the spacing must be added here to not make the nodes
        # move horizontally/vertically although they have already been
        # aligned.
        set_0(position, get_0(midpoint) + get_0(position) - bbox_size_2 + spacing)
        node.position = position

def align_nodes_shortcut(mode, spacing):
    master = gv.GetMaster(0)
    if not master:
        return

    root = master.GetRoot()
    if not root:
        return

    nodes = graphnode.find_selected_nodes(root)
    if nodes:
        master.AddUndo()
        align_nodes(nodes, mode, spacing)
        c4d.EventAdd()

    return True

def register_command(cmd):
    c4d.plugins.RegisterCommandPlugin(cmd.PLUGIN_ID, cmd.PLUGIN_NAME,
        getattr(cmd, 'PLUGIN_INFO', 0), getattr(cmd, 'PLUGIN_ICON', None),
        getattr(cmd, 'PLUGIN_HELP', ''), cmd)

class XPAT_Options(object):
    r"""
    This class organizes the options for the XPAT plugin, i.e.
    validating, loading and saving.
    """

    hspace = 50
    vspace = 20

    def __init__(self, filename=None):
        super(XPAT_Options, self).__init__()
        self.load(filename)

    def load(self, filename=None):
        r"""
        Load the options from file pointed to by filename. If filename
        is None, it defaults to the filename defined in options in the
        global scope.
        """

        if filename is None:
            filename = OPTIONS_FILENAME

        if os.path.isfile(filename):
            for key, value in json.load(fp).items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def save(self, filename=None):
        r"""
        Save the options defined in XPAT_Options instance to HD.
        """

        if filename is None:
            filename = OPTIONS_FILENAME

        values = {
            'hspace': self.hspace,
            'vspace': self.vspace,
        }
        with open(filename, 'wb') as fp:
            json.dump(values, fp)

class XPAT_OptionsDialog(c4d.gui.GeDialog):
    r"""
    This class implements the behavior of the XPAT options dialog,
    taking care of storing the options on the HD and loading them
    again on startup.
    """

    # c4d.gui.GeDialog

    def CreateLayout(self):
        return self.LoadDialogResource(res.DLG_OPTIONS)

    def InitValues(self):
        self.SetLong(res.EDT_HSPACE, options.hspace)
        self.SetLong(res.EDT_VSPACE, options.vspace)
        return True

    def Command(self, id, msg):
        if id == res.BTN_SAVE:
            options.hspace = self.GetLong(res.EDT_HSPACE)
            options.vspace = self.GetLong(res.EDT_VSPACE)
            options.save()
            self.Close()
        return True

class XPAT_Command_OpenOptionsDialog(c4d.plugins.CommandData):
    r"""
    This Cinema 4D CommandData plugin opens the XPAT options dialog
    when being executed.
    """

    PLUGIN_ID = 1029621
    PLUGIN_NAME = res.string('XPAT_COMMAND_OPENOPTIONSDIALOG')
    PLUGIN_HELP = res.string('XPAT_COMMAND_OPENOPTIONSDIALOG_HELP')

    def __init__(self):
        super(XPAT_Command_OpenOptionsDialog, self).__init__()
        self._dialog = None

    @property
    def dialog(self):
        if not self._dialog:
            self._dialog = XPAT_OptionsDialog()
        return self._dialog

    # c4dtools.plugins.Command

    # c4d.gui.CommandData

    def Execute(self, doc):
        return self.dialog.Open(c4d.DLG_TYPE_MODAL)

class XPAT_Command_AlignHorizontal(c4d.plugins.CommandData):

    PLUGIN_ID = 1029538
    PLUGIN_NAME = res.string('XPAT_COMMAND_ALIGNHORIZONTAL')
    PLUGIN_ICON = res.bitmap('res/xpresso-align-h.png')
    PLUGIN_HELP = res.string('XPAT_COMMAND_ALIGNHORIZONTAL_HELP')

    def Execute(self, doc):
        align_nodes_shortcut('horizontal', options.hspace)
        return True

class XPAT_Command_AlignVertical(c4d.plugins.CommandData):

    PLUGIN_ID = 1029539
    PLUGIN_NAME = res.string('XPAT_COMMAND_ALIGNVERTICAL')
    PLUGIN_ICON = res.bitmap('res/xpresso-align-v.png')
    PLUGIN_HELP = res.string('XPAT_COMMAND_ALIGNVERTICAL_HELP')

    def Execute(self, doc):
        align_nodes_shortcut('vertical', options.vspace)
        return True

options = XPAT_Options()

register_command(XPAT_Command_OpenOptionsDialog())
register_command(XPAT_Command_AlignHorizontal())
register_command(XPAT_Command_AlignVertical())
