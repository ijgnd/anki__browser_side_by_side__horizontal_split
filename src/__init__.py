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


def additionalInit(self, mw):
    self.side_by_side = False
    if gc("side-by-side is default"):
        self.side_by_side = True
        self.form.splitter.setOrientation(Qt.Horizontal)
Browser.__init__ = wrap(Browser.__init__, additionalInit)


def toggle_orientation(self):
    if self.side_by_side:
        o = Qt.Vertical
    else:
        o = Qt.Horizontal
    self.form.splitter.setOrientation(o)
    self.side_by_side ^= True


def onSetupMenus(self):
    try:
        m = self.menuView
    except:
        self.menuView = QMenu("&View")
        action = self.menuBar().insertMenu(
            self.mw.form.menuTools.menuAction(), self.menuView)
        m = self.menuView

    a = m.addAction('toggle editor on the bottom/side')
    a.triggered.connect(lambda _, b=self: toggle_orientation(b))
    a.setShortcut(QKeySequence(gc("shortcut","")))
addHook("browser.setupMenus", onSetupMenus)
