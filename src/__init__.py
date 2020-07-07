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

from aqt import gui_hooks
from aqt import mw
from aqt.browser import Browser
from aqt.qt import (
    QKeySequence,
    Qt,
)

from .toolbar import getMenu


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail


######### Browser GUI

has_BetterSearch = None
def check_for_BetterSearch():
    global has_BetterSearch
    try:
        bs = __import__("1052724801").version
    except:
        has_BetterSearch = None
    else: 
        has_BetterSearch = isinstance(bs, int) and bs >= 2
gui_hooks.profile_did_open.append(check_for_BetterSearch)


def use_extra_line():
    # maybe useful in the future when I want to disable it for some versions
    return gc("when narrow move search bar to extra line")



searchbar = None
searchbar_index = None


def additionalInit(self):
    global searchbar
    global searchbar_index
    # self is browser
    self.togthres = gc("toggle to vertical if editor narrower than")
    self.autoswitched = False
    if self.togthres:
        self.resizeEvent = self.onWindowResized
    if gc("side-by-side is default"):
        self.form.splitter.setOrientation(Qt.Horizontal)
    
    # store lineedit and its index
    grid = self.form.gridLayout
    for idx in range(grid.count()):   
        item = grid.itemAt(idx)
        coord = grid.getItemPosition(idx)
        w = item.widget()
        name = w.objectName() if hasattr(w, "objectName") else ""
        if name == "searchEdit":
            searchbar = w
            searchbar_index = coord[1]

    #maybe move lineedit
    if not use_extra_line():
        return
    if self.form.splitter.orientation() == Qt.Horizontal:
        make_two_rows(self)
gui_hooks.browser_will_show.append(additionalInit)


def make_two_rows(self):
    # self is browser
    if searchbar and not has_BetterSearch:
        self.form.gridLayout.addWidget(searchbar, 1, 0, 1, -1)


def back_to_one_row(self):
    # self is browser
    if searchbar and not has_BetterSearch:
        self.form.gridLayout.addWidget(searchbar, 0, searchbar_index, 1, 1)


def toVertical(self):
    if self.form.splitter.orientation() == Qt.Horizontal:
        self.form.splitter.setOrientation(Qt.Vertical)
        self.autoswitched = True
        if self.sidebarDockWidget.isVisible():
            dw_width = self.sidebarDockWidget.width()
        else:
            dw_width = 0
        self.width_when_switched = self.width() - dw_width
        back_to_one_row(self)


def toHorizontal(self):
    if self.form.splitter.orientation() == Qt.Vertical:
        self.form.splitter.setOrientation(Qt.Horizontal)
        self.autoswitched = False
        make_two_rows(self)


def onWindowResized(self, event):
    # on opening no editor is shown (but self.form.splitter.sizes() returns
    # a size for the editor ...
    if not self.form.fieldsArea.isVisible():  # editor
        return
    # self.size(), self.width(), height()
    _, edi = self.form.splitter.sizes()  # if horizontal that's widths, else heights
    if self.form.splitter.orientation() == Qt.Horizontal:
        if 0 < edi < self.togthres:
                mw.progress.timer(150, lambda browser=self: toVertical(browser), False)
    else:  # Qt.Vertical
        if self.autoswitched and self.width() > self.width_when_switched:
            if self.form.splitter.orientation() == Qt.Vertical:
                mw.progress.timer(150, lambda browser=self: toHorizontal(browser), False)
Browser.onWindowResized = onWindowResized


# Browser saves splitter state (including the orientation), so that
# after uninstalling the add-on and restarting Anki you still would have
# the editor by the side. So reset the orientation before the window is closed.
def additionalClose(self):
    self.form.splitter.setOrientation(Qt.Vertical)
Browser._closeWindow = wrap(Browser._closeWindow, additionalClose, "before")


def toggle_orientation(self):
    # self is browser
    if self.form.splitter.orientation() == Qt.Horizontal:  # editor is at the bottom
        o = Qt.Vertical
        func = back_to_one_row
    else:  # editor is on the side
        o = Qt.Horizontal
        func = make_two_rows
    self.form.splitter.setOrientation(o)
    func(self)


def onSetupMenus(self):
    m = getMenu(self, "&View")
    if not hasattr(self, "menuView"):
        self.menuView = m
    a = m.addAction('toggle editor on the bottom/side')
    a.triggered.connect(lambda _, b=self: toggle_orientation(b))
    cut = gc("shortcut")
    if cut:
        a.setShortcut(QKeySequence(cut))
addHook("browser.setupMenus", onSetupMenus)
