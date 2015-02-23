#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as sqlite
import os.path

import wx
import wx.grid as gridlib


class MainPanel(wx.Panel):
    # ----------------------------------------------------------------------
    """

    :param parent:
    """

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        labeler = "kereső".decode(encoding='utf-8', errors='strict',)
        buttonbox = "keresés".decode(encoding='utf-8', errors='strict')
        self.txtOne = wx.StaticText(self, -1, label=labeler, pos=(20, 10))
        self.txtPlace = wx.TextCtrl(self, pos=(20, 30))
        button = wx.Button(self, label=buttonbox, pos=(20, 70))
        button.Bind(wx.EVT_BUTTON, self.SearchButton)

    def SearchButton(self):
        """

        :param
        """
        var = self.txtPlace.GetValue()
        if len(var) == 9 or len(var) == 11:
            print "???"



class SecondPanel(gridlib.Grid, wx.Panel):
    def __init__(self, parent, db):
        gridlib.Grid.__init__(self, parent)
        self.CreateGrid(10, 10)

        self.db = db
        self.cur = self.db.con.cursor()
        if self.db.exists:
            # read labels in from DATA table
            meta = self.cur.execute("SELECT * FROM DATATABLE")
            labels = []
            for i in meta.description:
                labels.append(i[0])
            labels = labels[1:]
            for i in range(len(labels)):
                self.SetColLabelValue(i, labels[i])
            # then populate grid with data from DATA
            mind = self.cur.execute("SELECT * FROM DATATABLE ORDER BY DTindex")
            for row in mind:
                row_num = row[0]
                cells = row[1:]
                for i in range(len(cells)):
                    if cells[i] is not None and cells[i] != "null":
                        content = cells[i]
                        content.encode('UTF-8')
                        # self.SetCellValue(row_num, i, cells[i].encode('UTF-8'))
                        self.SetCellValue(row_num, i, content)
        else:
            labels = "CREATE TABLE DATATABLE\n(DTindex INTEGER PRIMARY KEY,\n"
            for i in range(self.GetNumberCols()):
                labels = labels + (self.GetColLabelValue(i) + "  string,\n")
            labels = labels[0:-1]
            labels = labels[0:-1]  # very bad string code here!
            labels += ");"
            self.cur.execute(labels)
            for i in range(self.GetNumberRows()):
                self.cur.execute("INSERT into DATATABLE (DTindex) values (%d)" % i)
            self.db.con.commit()

        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.CellContentsChanged)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.SelectRowLeftClick)
        # self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.SelectCellSelectRow)
        self.Bind(wx.grid.wx.EVT_NAVIGATION_KEY, self.SelectCellSelectRow)

    def SelectRowLeftClick(self, event):
        """

        :param event:
        """
        self.SetSelectionMode(wx.grid.Grid.SelectRows)
        event.Skip()

    def SelectCellSelectRow(self, event):
        """

        :param event:
        """
        self.SetSelectionMode(wx.grid.Grid.SelectRows)
        event.Skip()

    def CellContentsChanged(self, event):
        """

        :param event:
        """
        x = event.GetCol()
        y = event.GetRow()
        val = self.GetCellValue(y, x)
        # val.encode('UTF-8','strict')
        if val == "":
            val = "null"
        collabel = self.GetColLabelValue(x)
        insertcell = "UPDATE DATATABLE SET %s = ? WHERE DTindex = %d" % (collabel, y)
        self.cur.execute(insertcell, [val, ])  # protects against injection of dangerous 'val'
        # needs to be done for 'ColLabel' too. 'y' is fine as it's an integer
        self.db.con.commit()  # do commit here to ensure data persistence
        # also, retrieve formatting for variable and format the output
        self.SetCellValue(y, x, val)


class MainFrame(wx.Frame):
    # ----------------------------------------------------------------------
    """

    :param parent:
    :param database:
    """

    def __init__(self, parent, database):
        """Constructor
        :type self: object
        """
        # noinspection PyCallByClass
        wx.Frame.__init__(self, None, title="test", size=(940, 600))

        self.parent = parent
        exit = wx.Button(self, label="exit", pos=(800, 70))
        exit.Bind(wx.EVT_BUTTON, self.exit)
        exit.Bind(wx.EVT_CLOSE, self.exitwindow)

        self.splitter = wx.SplitterWindow(self)

        self.panelOne = MainPanel(self.splitter)
        self.panelTwo = SecondPanel(self.splitter, database)

        self.splitter.SplitHorizontally(self.panelOne, self.panelTwo)
        self.splitter.SetMinimumPaneSize(120)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, 2, wx.EXPAND)

        self.SetSizer(self.sizer)

    """def AddPanel(self):
        self.newPanel = SecondPanel(self, 1, 1)
        self.sizer.Add(self.newPanel, 1, wx.EXPAND)
        self.sizer.Layout()"""

    def exit(self, event):
        self.Close(True)

    def exitwindow(self, event):
        self.Destroy()


class GetDatabase(object):
    def __init__(self, f):
        # check db file exists

        if os.path.exists(f):
            # database already exists - need integrity check here
            self.exists = 1
        else:
            # database doesn't exist - create file & populate it
            self.exists = 0

        self.con = sqlite.connect(f)


if __name__ == "__main__":
    db = GetDatabase("Grid_SQLite_demo_db.db")
    app = wx.App()
    frame = MainFrame(None, db)
    frame.Show(True)
    app.MainLoop()