class Employee:
    empCount = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.empCount += 1

    def displayCount(self):
        print("Total Employee {}".format(Employee.empCount))

    def displayEmployee(self):
        print("Name : ", self.name, ", Salary: ", self.salary)


if __name__ == '__main__':
    # t1 = Employee("lh1", 10000)
    # t2 = Employee("lh2", 20000)
    # t1.displayCount()
    # t1.displayEmployee()
    # t2.displayCount()
    # t2.displayEmployee()
    for i in range(0,3):
        print(i)