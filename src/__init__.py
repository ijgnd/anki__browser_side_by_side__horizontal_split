"""
Add-on for Anki 2.1

Copyright: (c) 2019- ijgnd


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from anki.hooks import addHook, wrap

from aqt import mw 
from aqt.browser import Browser
from aqt.qt import *


def gc(arg, fail=False):
    return mw.addonManager.getConfig(__name__).get(arg, fail)


# wrapping Browser.__init__ didn't work with night-mode (version published on 2019-04-21)
def additionalInit(self):
    # self.form.splitter.splitterMoved.connect(self.onSplitterMoved)
    self.togthres = gc("toggle to vertical if editor narrower than")
    self.autoswitched = False
    if self.togthres:
        self.resizeEvent = self.onWindowResized
    # self.form.splitter.setStretchFactor(0,1)
    # self.form.splitter.setStretchFactor(1,1)
    if gc("side-by-side is default"):
        self.form.splitter.setOrientation(Qt.Horizontal)
Browser.setupEditor = wrap(Browser.setupEditor, additionalInit)


# def onSplitterMoved(self, pos):
#     print("splitter was moved to pos: {}".format(pos))
#     tab, edi = self.form.splitter.sizes()
#     print("new sizes: {}, {}".format(tab, edi))
# Browser.onSplitterMoved = onSplitterMoved


def onWindowResized(self, event):
    # on opening no editor is shown (but self.form.splitter.sizes() returns 
    # a size for the editor ...
    if not self.form.fieldsArea.isVisible():  # editor
        return
    # self.size(), self.width(), height()
    tab, edi = self.form.splitter.sizes()  # if horizontal that's widths, else heights
    if self.form.splitter.orientation() == Qt.Horizontal:   
        if 0 < edi < self.togthres:
            if self.form.splitter.orientation() == Qt.Horizontal:
                self.form.splitter.setOrientation(Qt.Vertical)
                self.autoswitched = True
                if self.sidebarDockWidget.isVisible():
                    dw_width = self.sidebarDockWidget.width()
                else:
                    dw_width = 0
                self.width_when_switched = self.width() - dw_width
    else:  # Qt.Vertical
        if self.autoswitched and self.width() > self.width_when_switched:
            if self.form.splitter.orientation() == Qt.Vertical:
                self.form.splitter.setOrientation(Qt.Horizontal)
                self.autoswitched = False
Browser.onWindowResized = onWindowResized


# Browser saves splitter state (including the orientation), so that
# after uninstalling the add-on and restarting Anki you still would have 
# the editor by the side. So reset the orientation before the window is closed.
def additionalClose(self):
    self.form.splitter.setOrientation(Qt.Vertical)
Browser._closeWindow = wrap(Browser._closeWindow, additionalClose, "before")


def toggle_orientation(self):
    if self.form.splitter.orientation() == Qt.Horizontal:
        o = Qt.Vertical
    else:
        o = Qt.Horizontal
    self.form.splitter.setOrientation(o)
Browser.toggle_orientation = toggle_orientation


def onSetupMenus(self):
    try:
        m = self.menuView
    except:
        self.menuView = QMenu("&View")
        self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.menuView)
        m = self.menuView
    a = m.addAction('toggle editor on the bottom/side')
    a.triggered.connect(lambda _, b=self: toggle_orientation(b))
    a.setShortcut(QKeySequence(gc("shortcut","")))
addHook("browser.setupMenus", onSetupMenus)
