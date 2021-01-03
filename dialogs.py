import wx
import wxmod
import re
import os

class ClipboardDialog(wx.Dialog):

  def __init__(self, parent, choices, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent
    self.init_GUI(choices)

  def init_GUI(self, choices):
    self.choices, self.columns = zip(*choices)

    # Widgets
    self.choices = wx.Choice(self, wx.ID_ANY, choices = self.choices)
    self.choices.SetSelection(0)

    cancel_btn = wx.Button(self, wx.ID_CANCEL, '&Cancelar')
    copy_btn = wx.Button(self, wx.ID_OK, '&Copiar')
    copy_btn.SetDefault()

    # Bind
    self.Bind(wx.EVT_BUTTON, self.copy_column, copy_btn)

    # Layout
    buttons_panel = wx.BoxSizer(wx.HORIZONTAL)
    buttons_panel.Add(cancel_btn, 0)
    buttons_panel.Add(copy_btn, 0, wx.LEFT, 10)

    group1 = wx.StaticBoxSizer(wx.VERTICAL, self, 'Escoge la columna que deseas copiar:')
    group1.Add(self.choices, 0, wx.EXPAND)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(group1, 0, wx.ALL, 5)
    main_sizer.Add(buttons_panel, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

    main_sizer.SetSizeHints(self)
    self.SetSizer(main_sizer)

  def copy_column(self, event):
    index = self.choices.GetCurrentSelection()
    column_n = self.columns[index]
    self.parent.list_ctrl.copy_to_clipboard(column_n)
    self.Destroy()

class FindAndReplace(wx.Dialog):

  def __init__(self, parent, column_n, *args, **kwargs):
    super().__init__(parent, title= 'Buscar y remplazar', *args, **kwargs)
    self.parent = parent
    self.column_n = column_n
    self.init_GUI()

  def init_GUI(self):
    notebook = wx.Notebook(self, style = wx.NB_FIXEDWIDTH)
    searchTab = SearchTab(notebook, self.parent, self.column_n)
    replaceTab = ReplaceTab(notebook, self.parent, self.column_n)
    notebook.AddPage(searchTab, 'Buscar')
    notebook.AddPage(replaceTab, 'Remplazar')

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(notebook, 1, wx.EXPAND|wx.ALL, 5)
    main_sizer.SetSizeHints(self)
    self.SetSizer(main_sizer)

class SearchTab(wx.Panel):

  def __init__(self, parent, parent_root, column_n, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent_root
    self.column_n = column_n
    self.init_GUI()

  def init_GUI(self):
    # Widgets

    search_label = wx.StaticText(self, wx.ID_ANY, 'Buscar:')
    self.search_entry = wx.TextCtrl(self, wx.ID_ANY)

    cancel_btn = wx.Button(self, wx.ID_CANCEL, '&Cancelar')
    search_next_item_btn = wx.Button(self, wx.ID_OK, '&Buscar siguiente')
    search_next_item_btn.SetDefault()

    # Bind
    self.Bind(wx.EVT_BUTTON, self.search_next_item, search_next_item_btn)

    # Layout
    buttons_panel = wx.BoxSizer(wx.HORIZONTAL)
    buttons_panel.Add(cancel_btn, 0)
    buttons_panel.Add(search_next_item_btn, 0, wx.LEFT, 10)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(search_label, 0, wx.ALL, 5)
    main_sizer.Add(self.search_entry, 0, wx.ALL|wx.EXPAND, 5)

    main_sizer.Add(buttons_panel, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

    self.SetSizer(main_sizer)

  def search_next_item(self, event):
    selected_index = self.parent.list_ctrl.GetFirstSelected()
    search_str = self.search_entry.GetValue()
    item_list = self.parent.list_ctrl.GetAllItemsText(self.column_n)
    start = 0 if selected_index == -1 else selected_index+1
    item_list_len = len(item_list)

    for item_n in range(start, item_list_len):
      item_str = item_list[item_n]
      if not search_str in item_str:
        continue
      self.parent.list_ctrl.UnselectAll()
      # Select only the index
      self.parent.list_ctrl.Select(item_n, 1)
      self.parent.list_ctrl.Focus(item_n)
      break

class ReplaceTab(wx.Panel):

  def __init__(self, parent, parent_root, column_n, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.parent = parent_root
    self.column_n = column_n
    self.init_GUI()

  def init_GUI(self):
    # Widgets

    search_label = wx.StaticText(self, wx.ID_ANY, 'Buscar:')
    self.search_entry = wx.TextCtrl(self, wx.ID_ANY)
    replace_label = wx.StaticText(self, wx.ID_ANY, 'Remplazar:')
    self.replace_entry = wx.TextCtrl(self, wx.ID_ANY)

    self.regex_checkbox = wx.CheckBox(self, wx.ID_ANY, label = 'Expresiones re&gulares (regex)')

    cancel_btn = wx.Button(self, wx.ID_CANCEL, '&Cancelar')
    replace_all_btn = wx.Button(self, wx.ID_OK, '&Remplazar')
    replace_all_btn.SetDefault()

    # Bind
    self.Bind(wx.EVT_BUTTON, self.replace_all, replace_all_btn)

    # Layout
    buttons_panel = wx.BoxSizer(wx.HORIZONTAL)
    buttons_panel.Add(cancel_btn, 0)
    buttons_panel.Add(replace_all_btn, 0, wx.LEFT, 10)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(search_label, 0, wx.ALL, 5)
    main_sizer.Add(self.search_entry, 0, wx.ALL|wx.EXPAND, 5)
    main_sizer.Add(replace_label, 0, wx.ALL, 5)
    main_sizer.Add(self.replace_entry, 0, wx.ALL|wx.EXPAND, 5)
    main_sizer.Add(self.regex_checkbox, 0, wx.ALL|wx.ALIGN_CENTER, 5)
    main_sizer.Add(buttons_panel, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

    self.SetSizer(main_sizer)

  def replace_all(self, event):
    search_str = self.search_entry.GetValue()
    replace_str = self.replace_entry.GetValue()
    item_list = self.parent.list_ctrl.GetAllItemsText(self.column_n)

    if not len(item_list):
      return

    if self.regex_checkbox.IsChecked():
      replacements = self.replace_regex(search_str, replace_str, item_list)
    else:
      replacements = self.replace(search_str, replace_str, item_list)
    for index, new_item_str in replacements.items():
      self.parent.list_ctrl.SetItem(index, self.column_n, new_item_str)

  def replace(self, search_str, replace_str, item_list):
    replacements = dict()
    for index, item_str in enumerate(item_list):
      if item_str.find(search_str) < 0:
        continue
      new_item_str = item_str.replace(search_str, replace_str)
      replacements[index] = new_item_str
    return replacements

  def replace_regex(self, search_str, replace_str, item_list):
    replacements = dict()
    pattern = re.compile(search_str)
    for index, item_str in enumerate(item_list):
      if pattern.search(item_str) == None:
          continue
      new_item_str = pattern.sub(replace_str, item_str)
      replacements[index] = new_item_str
    return replacements

class TableInfoDialog(wx.Dialog):

  def __init__(self, parent, id=wx.ID_ANY, title ='', subtitle='', columns=[], *args, **kwargs):
    super().__init__(parent, id, title, *args, **kwargs)
    self.parent = parent
    self.subtitle = subtitle
    self._COLUMN_NAMES = columns
    self.init_GUI()

  def init_GUI(self):
    # Widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, size=(200,100),style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES|wx.LC_VRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    cancel_btn = wx.Button(self, wx.ID_CANCEL, '&Cancelar')
    copy_btn = wx.Button(self, wx.ID_OK, '&Copiar')
    copy_btn.SetDefault()

    # Bind
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, copy_btn)

    # Layout
    buttons_panel = wx.BoxSizer(wx.HORIZONTAL)
    buttons_panel.Add(cancel_btn, 0)
    buttons_panel.Add(copy_btn, 0, wx.LEFT, 10)

    group1 = wx.StaticBoxSizer(wx.VERTICAL, self, self.subtitle)
    group1.Add(self.list_ctrl, 0, wx.EXPAND|wx.ALL, 5)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(group1, 1, wx.EXPAND|wx.ALL, 5)
    main_sizer.Add(buttons_panel, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

    main_sizer.SetSizeHints(self)
    self.SetSizer(main_sizer)

  def add_data(self, table):
    '''
    table (list of list): ((label, count),...)
    '''
    for label, count  in table:
      self.list_ctrl.AppendRow(label, count)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)
    
  def copy_to_clipboard(self, event):
    self.list_ctrl.copy_to_clipboard(-1)
  
class ExtensionSummary(wx.Dialog):

  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, title='Resumen', *args, **kwargs)
    self.init_GUI()

  def init_GUI(self):
    # Constants
    self._COLUMN_NAMES = ['ID', 'Extensión', 'Frecuencia']
    self._ID_COLUMN = 0
    self.EXTENSION_COLUMN = 1
    self.COUNT_COLUMN = 2

    # widgets
    self.list_ctrl = wxmod.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES|wx.LC_VRULES)
    for index, column_name in enumerate(self._COLUMN_NAMES):
      self.list_ctrl.InsertColumn(index, column_name, width=wx.LIST_AUTOSIZE)

    cancel_btn = wx.Button(self, wx.ID_CANCEL, '&Cancelar')
    copy_to_clipboard_btn = wx.Button(self, wx.ID_ANY, '&Copiar')

    # Bind
    self.Bind(wx.EVT_BUTTON, self.copy_to_clipboard, copy_to_clipboard_btn)

    # Layout
    buttons_panel = wx.BoxSizer(wx.HORIZONTAL)
    buttons_panel.Add(cancel_btn, 0)
    buttons_panel.Add(copy_to_clipboard_btn, 0)

    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(self.list_ctrl, 0, wx.ALL, 5)
    main_sizer.Add(buttons_panel, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

    main_sizer.SetSizeHints(self)
    self.SetSizer(main_sizer)

  def add_data(self, frequency_dict):
    count = 0
    for extension, frequency in frequency_dict.items():
      count+=1
      self.list_ctrl.AppendRow(count, extension, frequency)
    self.list_ctrl.SetALLColumnsWidth(wx.LIST_AUTOSIZE_USEHEADER)

  def copy_to_clipboard(self, event):
    self.list_ctrl.copy_to_clipboard(-1)