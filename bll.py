import xlrd
from model import *
from datetime import *


class Calculator:
    """
    工资计算器类
    """
    # 考勤数据文件的存放位置
    __ATTENDANCE_FILE = "./原始文件/考勤数据.xls"
    # 需要特殊处理的日期项目
    __SPECIAL_ITEM = "请输入特殊情况，如果有多项比如1，2项都有，请输入1 2："
    __SPECIAL_ITEM += "\n1、公休"
    __SPECIAL_ITEM += "\n2、出差"
    __SPECIAL_ITEM += "\n3、病假"
    __SPECIAL_ITEM += "\n4、事假"
    __SPECIAL_ITEM += "\n5、婚假"
    __SPECIAL_ITEM += "\n6、产假"
    __SPECIAL_ITEM += "\n7、丧假"
    # 特殊日期项目输入提示
    __SPECIAL_ITEM_TIP_1 = "本月是否有特殊日期？是请输入Y或y，没有请输入N或n。"
    __SPECIAL_ITEM_TIP_2 = "请输入特殊日期（比如2月1日就输入1）。如果已经输入完成，请直接按回车键："

    def __init__(self):
        self.stuff_list = []

    def get_date_list(self, sheet):
        """
        获取指定的考勤工作表中的所有日期对象，形成列表返回
        :param sheet: 考勤工作表
        :return: 日期列表
        """
        result = []
        reference_date = sheet.cell_value(0, 0)[-10:]
        year = int(reference_date[:4])
        month = int(reference_date[5:7])
        month_days = self.__get_month_days(month, year)
        for i in range(month_days):
            result.append(datetime.strptime("%d-%d-%d" % (year, month, i + 1), "%Y-%m-%d"))
        return result

    @staticmethod
    def __get_month_days(month, year):
        """
        :param month: 月
        :param year: 年
        :return: 按年月返回当月多少天
        """
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                return 29
            else:
                return 28


class ReadAttendance:
    """
    读取考勤数据
    """
    # 日志文件的存储位置
    __LOG = "./log.txt"

    def __init__(self):
        # 记录日志
        self.f = open(self.__LOG, "w", encoding="utf-8")

    def get_stuff_list(self, sheet, date_list_):
        """
        读取考勤工作表中的数据，返回员工对象
        :param date_list_: 日期列表，作为员工对象中的考勤天数的依据
        :param sheet:考勤工作表对象
        :return: 员工对象
        """
        # 按每个员工，分别读取，并将读读取的考勤数据传递给具体的员工对象实例。将每个员工对象返回到Calculator().stuff_list中
        i = 3
        stuff_list_ = []
        while i <= sheet.nrows:
            i = self.__add_stuff(i, sheet, stuff_list_, date_list_)
        self.f.close()
        return stuff_list_

    def __add_stuff(self, i, sheet, stuff_list_, date_list_):
        # 从A4单元格开始，每两个是一个员工的考勤数据
        name = sheet.cell_value(i, 0)
        depart = sheet.cell_value(i, 1)
        job = sheet.cell_value(i, 2)
        attendance = self.__get_attendance(i, sheet, date_list_)
        stuff_list_.append(Stuff(name, depart, job, attendance))
        i += 2
        return i

    def __get_attendance(self, i, sheet, date_list_):
        attendance_time_dict = {}
        for day in range(len(date_list_)):
            # D5单元格取的休怎么处理还没有想好
            value = sheet.cell_value(i, 3 + day)
            if value:
                try:
                    start_time = datetime.strptime(value.split("\n")[0].strip(), "%H:%M")
                    end_time = datetime.strptime(value.split("\n")[1].strip(), "%H:%M")
                except Exception as e:
                    self.f.write(f"第%d行，%d号，考勤记录出错，请在考勤表中修改。\n" % (i + 1, day + 1))
                    continue
            else:
                start_time = datetime.strptime("00:00", "%H:%M")
                end_time = datetime.strptime("00:00", "%H:%M")
            attendance_time_dict[day + 1] = (start_time, end_time)
        attendance = PersonAttendance(attendance_time_dict)
        return attendance


if __name__ == '__main__':
    attendance_file = "./原始文件/考勤数据.xls"
    wb = xlrd.open_workbook(attendance_file)
    # 工作簿的第二张（索引号1）工作表为考勤数据工作表
    sh = wb.sheet_by_index(1)
    date_list = Calculator().get_date_list(sh)
    stuff_list = ReadAttendance().get_stuff_list(sh, date_list)
    for stuff in stuff_list:
        for k, v in stuff.attendance.attendance_time_dict.items():
            print(stuff.name, "%d号" % k, "上班：%s" % v[0].ctime()[11:16], "下班：%s" % v[1].ctime()[11:16])
