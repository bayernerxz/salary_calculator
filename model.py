"""
model.py 数据模型模块

包含员工类、迟到类、迟到计算器类、早退类、早退计算器类、旷工类、请假类。

迟到类和早退类的规定上下班时间，分别在迟到计算器类和早退计算器类中定义
"""

from datetime import *


class Stuff:
    def __init__(self, name, depart, job, attendance):
        self.name = name
        self.depart = depart
        self.job = job
        self.attendance = attendance

    def get_salary(self):
        print("获取工资对象")


class PersonAttendance:
    def __init__(self, attendance_time_dict):
        self.attendance_time_dict = attendance_time_dict
        """
        出勤时间字典格式如下，其中时间影视datetime中的时间对象
        {1:[(8:58,18:02)];
        2:[(8:58,18:02)];
        ...
        28:[(8:58,18:02)]
        """

    def get_regular_attendance_days(self):
        print("获取应出勤多少天")

    def get_real_attendance_days(self):
        print("获取实际出勤多少天")

    def get_late(self):
        print("获取迟到对象")

    def get_early_leave(self):
        print("获取早退对象")

    def get_absent(self):
        print("获取矿工对象")

    def get_leave(self):
        print("获取请假对象")

    def get_travel(self):
        print("获取出差对象")


class Late:
    """
    具体员工的迟到事件的对象
    计算规则：
        1.员工出勤晚于上班时间的为迟到
        2.每月2次迟到机会10分钟之内，不扣钱。
        3.当月第三次迟到起，每迟到一分钟，罚款10元,扣前2次迟到补交20元,扣除全勤奖。
        4.迟到在30分钟以上的，罚款50元/次。
        5.每个月有3次迟到30分钟以上的，自动离职。

    疑问：
        前两次迟到30分钟以上，第三次迟到10分钟以内，这次算不算迟到？我的理解是算。
        再一个早退那一栏里写的迟到30分钟时罚款50，可是之前写的时每分钟10块，这样30分钟就时300块了。怎么处理。
        一个月只迟到了一次 但是不到30分钟 这种怎么处理
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.count = 0
        self.loss = 0

    def handle_late_by_day(self, start_time):
        """
        计算迟到时间，再对象属性中直接修改
        :param start_time:上班到岗时间，用datetime.datetime.strptime()生成
        """
        # 判断迟到并计算迟到时间
        late_time = LateCalculator().calculate_late_time(start_time)
        # 1 没有迟到
        if late_time == 0:
            pass
        # 2 迟到时间大于30分钟，罚款50元/次
        elif late_time >= 30:
            self.loss += 50
            self.count += 1
        # 2 迟到小于10分钟且每月小于两次的
        elif late_time < 10 and self.count <= 2:
            self.count += 1
        # 3 当月第三次迟到起，每迟到一分钟，罚款10元,扣前2次迟到补交20元,扣除全勤奖
        elif late_time > 0 and self.count == 3:
            self.stuff.full_attendance = False
            self.count += 1
            self.loss += 20
            self.loss += 10 * late_time
        # 4 月迟到次数大于3次，每迟到一分钟罚款10元
        elif late_time > 0 and self.count > 3:
            self.count += 1
            self.loss += 10 * late_time


class EarlyLeave:
    """
    具体员工的早退事件的对象

    早退规则：
        1.早退在30分钟以上，罚款50元/次
        2.一个月连续3次早退30分钟，视为自动离职。
        3.早退1小时以上按旷工半天计算，扣除1天工资，扣除全勤奖。
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.count = 0
        self.loss = 0

    def handle_early_leave_by_day(self, end_time):
        """
        计算早退时间
        :param end_time:下班离岗时间，用datetime.datetime.strptime()生成
        :return:早退的分钟数
        """
        # 判断早退并计算早退时间
        early_leave_time = EarlyLeaveCalculator().calculate_early_leave_time(end_time)
        # 1.没有早退
        if early_leave_time == 0:
            pass
        # 2.早退在30分钟以上，罚款50元/次
        elif early_leave_time >= 60:
            ab = Absent(self.stuff)  # 这里有点问题，应该从这个员工的考勤对象中调用旷工对象，这里成了新建了一个对象
            ab.record_absent()
        elif early_leave_time >= 30:
            self.loss += 50
            self.count += 1
        else:
            # self.loss+=20  # 描述没有写明白，这里先跳过
            self.count += 1


class Absent:
    """
    具体员工的旷工事件的对象
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.count = 0

    def record_absent(self):
        self.count += 1


class Leave:
    """
    具体员工的请假事件的对象
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.sick_leave = 0  # 病假
        self.compassionate_leave = 0  # 事假
        self.marriage_leave = 0  # 婚嫁
        self.maternity_leave = 0  # 产假
        self.bereavement_leave = 0  # 丧假

    def add_sick_leave(self):
        self.sick_leave += 1

    def add_compassionate_leave(self):
        self.compassionate_leave += 1

    def add_marriage_leave(self):
        self.marriage_leave += 1

    def add_maternity_leave(self):
        self.maternity_leave += 1

    def add_bereavement_leave(self):
        self.bereavement_leave += 1


class Travel:
    """
    出差类
    """
    pass


class LateCalculator:
    """
    迟到计算器
    """
    REGULAR_START_TIME = datetime.strptime("09:00", "%H:%M")
    REGULAR_END_TIME = datetime.strptime("18:00", "%H:%M")

    def calculate_late_time(self, start_time):
        # 如果迟到,返回迟到的时间(分钟）
        if 0 < (start_time - self.REGULAR_START_TIME).seconds < 8 * 3600:  # 一般迟到时间不可能大于8个小时
            return (self.REGULAR_START_TIME - start_time).seconds / 60
        # 不迟到，返回0
        else:
            return 0


class EarlyLeaveCalculator:
    """
    早退计算器
    """
    REGULAR_END_TIME = datetime.strptime("18:00", "%H:%M")

    def calculate_early_leave_time(self, end_time):
        # 如果早退,返回早退的时间
        if 0 < (self.REGULAR_END_TIME - end_time).seconds < 8 * 3600:  # 一般早退时间不可能大于8个小时
            return (self.REGULAR_END_TIME - end_time).seconds
        # 不早退，返回0
        else:
            return 0
