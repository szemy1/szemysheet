#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as sqlite
import os.path
import wx
import wx.grid as gridlib


class MainPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        labeler = "kereső"
        buttonbox = "keresés"
        self.txtOne = wx.StaticText(self, -1, label=labeler, pos=(20, 10))
        self.txtPlace = wx.TextCtrl(self, pos=(20, 30))
        button = wx.Button(self, label=buttonbox, pos=(20, 70))
        button.Bind(wx.EVT_BUTTON, self.SearchButton)

    def SearchButton(self, event):
        var = self.txtPlace.GetValue()
        if len(var) == 9 or len(var) == 11:
            print("???")


class SecondPanel(wx.Panel, gridlib.Grid):
    def __init__(self, parent, database):
        wx.Panel.__init__(self, parent)
        gridlib.Grid.__init__(self, parent)
        self.CreateGrid(10, 10)

        self.db = database
        self.cur = self.db.con.cursor()
        if self.db.exists:
            self.load_data()
        else:
            self.create_table()

        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.CellContentsChanged)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.SelectRowLeftClick)
        self.Bind(wx.EVT_KEY_DOWN, self.SelectCellSelectRow)

    def load_data(self):
        meta = self.cur.execute("SELECT * FROM DATATABLE")
        labels = [i[0] for i in meta.description][1:]
        for i, label in enumerate(labels):
            self.SetColLabelValue(i, label)
        
        mind = self.cur.execute("SELECT * FROM DATATABLE ORDER BY DTindex")
        for row in mind:
            row_num = row[0]
            cells = row[1:]
            for i, cell in enumerate(cells):
                if cell and cell != "null":
                    self.SetCellValue(row_num, i, cell)

    def create_table(self):
        columns = [self.GetColLabelValue(i) for i in range(self.GetNumberCols())]
        labels = f"CREATE TABLE DATATABLE\n(DTindex INTEGER PRIMARY KEY,\n{',\n'.join(columns)});"
        self.cur.execute(labels)
        for i in range(self.GetNumberRows()):
            self.cur.execute("INSERT INTO DATATABLE (DTindex) VALUES (?)", (i,))
        self.db.con.commit()

    def SelectRowLeftClick(self, event):
        self.SetSelectionMode(wx.grid.Grid.SelectRows)
        event.Skip()

    def SelectCellSelectRow(self, event):
        self.SetSelectionMode(wx.grid.Grid.SelectRows)
        event.Skip()

    def CellContentsChanged(self, event):
        x = event.GetCol()
        y = event.GetRow()
        val = self.GetCellValue(y, x) or "null"
        collabel = self.GetColLabelValue(x)
        insertcell = f"UPDATE DATATABLE SET {collabel} = ? WHERE DTindex = ?"
        self.cur.execute(insertcell, (val, y))
        self.db.con.commit()


class MainFrame(wx.Frame):
    def __init__(self, parent, database):
        wx.Frame.__init__(self, None, title="test", size=(940, 600))

        self.parent = parent
        exit_button = wx.Button(self, label="exit", pos=(800, 70))
        exit_button.Bind(wx.EVT_BUTTON, self.exit)
        exit_button.Bind(wx.EVT_CLOSE, self.exitwindow)

        self.splitter = wx.SplitterWindow(self)
        self.panelOne = MainPanel(self.splitter)
        self.panelTwo = SecondPanel(self.splitter, database)

        self.splitter.SplitHorizontally(self.panelOne, self.panelTwo)
        self.splitter.SetMinimumPaneSize(120)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, 2, wx.EXPAND)
        self.SetSizer(self.sizer)

    def exit(self, event):
        self.Close(True)

    def exitwindow(self, event):
        self.Destroy()


class GetDatabase:
    def __init__(self, f):
        self.exists = os.path.exists(f)
        self.con = sqlite.connect(f)


if __name__ == "__main__":
    db = GetDatabase("Grid_SQLite_demo_db.db")
    app = wx.App()
    frame = MainFrame(None, db)
    frame.Show(True)
    app.MainLoop()
