from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QCalendarWidget, QFileDialog, QAbstractItemView, QListWidget,
                               QMessageBox)
from PySide6.QtCore import QLocale, QPoint, QDate
from PySide6 import QtCore
from Logs import Logs
from util import get_datetime_from_text


class LogBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logs = Logs()

        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.setWindowTitle("NASA logs browser")
        self.setFixedSize(910, 570)

        self.central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addLayout(self.__path_layout())
        central_layout.addLayout(self.__master_detail_layout())
        central_layout.addLayout(self.__nav_bar_layout())
        self.central_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_widget)

    
    def __path_layout(self):
        path_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('NASA logs path')
        open_button = QPushButton('Open')
        open_button.clicked.connect(self.__open_file)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(open_button)

        return path_layout
    

    def __master_detail_layout(self):
        master_detail_layout = QHBoxLayout()

        master_detail_layout.addLayout(self.__master_logs_layout())
        master_detail_layout.addLayout(self.__detail_log_layout())

        return master_detail_layout

    
    def __master_logs_layout(self):
        master_logs_layout = QVBoxLayout()
        date_edit_layout = QHBoxLayout()

        from_label = QLabel('From:')
        self.from_date_edit = DateEdit()
        to_label = QLabel('To:')
        self.to_date_edit = DateEdit()
        filter_button = QPushButton('Filter')
        reset_button = QPushButton('Reset')

        date_edit_layout.addWidget(from_label)
        date_edit_layout.addWidget(self.from_date_edit)
        date_edit_layout.addWidget(to_label)
        date_edit_layout.addWidget(self.to_date_edit)

        date_edit_layout.addWidget(filter_button)
        filter_button.clicked.connect(self.__show_filter_logs)
        date_edit_layout.addWidget(reset_button)
        reset_button.clicked.connect(self.__reset_filtering)

        self.logs_list = QListWidget()
        self.logs_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.logs_list.itemClicked.connect(self.__show_log_details)

        master_logs_layout.addLayout(date_edit_layout)
        master_logs_layout.addWidget(self.logs_list)

        return master_logs_layout
    

    def __detail_log_layout(self):
        detail_log_layout = QGridLayout()
        detail_log_layout.setContentsMargins(0, 100, 0, 50)
        detail_log_layout.setSpacing(10)
        detail_log_layout.setColumnMinimumWidth(0, 100)
        detail_log_layout.setColumnMinimumWidth(3, 50)

        self.host = QLineEdit()
        self.date = QLabel()
        self.time = QLabel()
        self.timezone = QLabel()
        self.status_code = QLabel()
        self.method = QLabel()
        self.resources = QLineEdit()
        self.resources_size = QLabel()

        detail_log_layout.addWidget(QLabel('Remote host:'), 0, 0)
        detail_log_layout.addWidget(self.host, 0, 1, 1, 3)

        detail_log_layout.addWidget(QLabel('Date:'), 1, 0)
        detail_log_layout.addWidget(self.date, 1, 1)

        detail_log_layout.addWidget(QLabel('Time:'), 2, 0)
        detail_log_layout.addWidget(self.time, 2, 1)
        detail_log_layout.addWidget(QLabel('Timezone:'), 2, 2)
        detail_log_layout.addWidget(self.timezone, 2, 3)

        detail_log_layout.addWidget(QLabel('Status code:'), 3, 0)
        detail_log_layout.addWidget(self.status_code, 3, 1)
        detail_log_layout.addWidget(QLabel('Method:'), 3, 2)
        detail_log_layout.addWidget(self.method, 3, 3)

        detail_log_layout.addWidget(QLabel('Resources:'), 4, 0)
        detail_log_layout.addWidget(self.resources, 4, 1, 1, 3)

        detail_log_layout.addWidget(QLabel('Size:'), 5, 0)
        detail_log_layout.addWidget(self.resources_size, 5, 1)

        return detail_log_layout
    

    def __nav_bar_layout(self):
        nav_bar_layout = QHBoxLayout()
        nav_bar_layout.setSpacing(500)
        nav_bar_layout.setContentsMargins(30, 10, 30, 10)

        self.previous_button = QPushButton("Previous")
        self.previous_button.setEnabled(False)
        self.previous_button.clicked.connect(self.__show_previous_log)

        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.__show_next_log)

        nav_bar_layout.addWidget(self.previous_button)
        nav_bar_layout.addWidget(self.next_button)

        return nav_bar_layout
    

    def __open_file(self):
        logs_path, _ = QFileDialog.getOpenFileName(self, 'Select Log File', '', 'All Files (*)')

        if logs_path:
            self.path_input.setText(logs_path)
            self.logs_list.clear()
            self.logs.read_logs(logs_path)
            if self.logs.logs:
                self.__load_logs()
                self.__set_datespans()
            else:
                self.__display_warning('WARNING', 'Incorrect file!')
        else:
            self.__display_warning('WARNING', 'File not found!')


    def __load_logs(self):
        if self.logs.logs:
            self.logs_list.addItems(self.logs.current_logs.keys())
            self.logs_list.setCurrentRow(0)
            self.__show_log_details(self.logs_list.currentItem())
        
        self.logs_list.viewport().update()


    def __show_log_details(self, log):
        details = self.logs.current_logs[log.text()]

        self.host.setText(details['ip'])
        self.date.setText(details['date'])
        self.time.setText(details['time'])
        self.timezone.setText(details['timezone'])
        self.status_code.setText(details['code'])
        self.method.setText(details['method'])
        self.resources.setText(details['path'])
        self.resources_size.setText(details['size'])
        
        i = self.logs_list.row(log)
        self.previous_button.setEnabled(i > 0)
        self.next_button.setEnabled(i < self.logs_list.count() - 1)


    def __show_previous_log(self):
        current_index = self.logs_list.currentRow()
        previous_item = self.logs_list.item(current_index - 1)
        self.logs_list.setCurrentItem(previous_item)
        self.__show_log_details(previous_item)


    def __show_next_log(self):
        current_index = self.logs_list.currentRow()
        next_item = self.logs_list.item(current_index + 1)
        self.logs_list.setCurrentItem(next_item)
        self.__show_log_details(next_item)

    
    def __set_datespans(self):
        self.min_date, self.max_date = self.logs.get_logs_datespan()

        self.from_date_edit.change_datespan(self.min_date, self.max_date)
        self.from_date_edit.set_selected_date(self.min_date)

        self.to_date_edit.change_datespan(self.min_date, self.max_date)
        self.to_date_edit.set_selected_date(self.max_date)

    
    def __show_filter_logs(self):
        from_date = get_datetime_from_text(self.from_date_edit.date_edit.text())
        to_date = get_datetime_from_text(self.to_date_edit.date_edit.text())

        if from_date <= to_date:
            self.logs.filter_logs(from_date, to_date)
            self.logs_list.clear()
            self.__load_logs()
        else:
            self.__display_warning('WARNING', 'To date must be equal or greater than from date!')


    def __reset_filtering(self):
        self.from_date_edit.set_selected_date(self.min_date)
        self.to_date_edit.set_selected_date(self.max_date)
        self.logs.reset_filtering()
        self.logs_list.clear()
        self.__load_logs()

    
    def __display_warning(self, title, text):
        warn_box = QMessageBox()
        warn_box.setIcon(QMessageBox.Icon.Warning)
        warn_box.setWindowTitle(title)
        warn_box.setText(text)
        warn_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        warn_box.exec()

            

class DateEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.date_edit = QLineEdit(self)
        self.date_edit.setReadOnly(True)

        self.calendar = QCalendarWidget(self)
        self.calendar.setWindowFlags(self.calendar.windowFlags() | QtCore.Qt.Popup)

        self.calendar.selectionChanged.connect(self.show_selected_date)

        layout = QVBoxLayout()
        layout.addWidget(self.date_edit)

        self.setLayout(layout)
        self.date_edit.mousePressEvent = self.show_calendar

    
    def show_calendar(self, event):
        date_edit_pos = self.mapToGlobal(self.date_edit.pos())
        x = date_edit_pos.x()
        y = date_edit_pos.y() + self.date_edit.height()

        calendar_size = self.calendar.sizeHint()
        screen_geometry = QApplication.primaryScreen().size()
        if y + calendar_size.height() > screen_geometry.height():
            y = date_edit_pos.y() - calendar_size.height()

        self.calendar.move(QPoint(x, y))
        self.calendar.show()


    def show_selected_date(self):
        selected_date = self.calendar.selectedDate()
        self.date_edit.setText(selected_date.toString('yyyy-MM-dd'))

    
    def change_datespan(self, min, max):
        self.calendar.setDateRange(QDate(min.date().year, min.date().month, min.date().day), 
                                   QDate(max.date().year, max.date().month, max.date().day))

    
    def set_selected_date(self, date):
        self.calendar.setSelectedDate(QDate(date.date().year, date.date().month, date.date().day))



if __name__ == '__main__':
    app = QApplication([])
    window = LogBrowser()
    window.show()
    app.exec()