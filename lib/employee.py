# lib/employee.py
from __init__ import CONN, CURSOR
from department import Department


class Employee:

    # dictionary cache of all Employee objects
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        # initialize attributes with validation
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    # property for name with validation
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Name cannot be empty")
        self._name = value

    # property for job_title with validation
    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Job title cannot be empty")
        self._job_title = value

    # property for department_id with validation
    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer")
        if Department.find_by_id(value) is None:
            raise ValueError("Department does not exist")
        self._department_id = value

    # creates employees table
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    # drops employees table
    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    # saves new or updated employee
    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()

        CONN.commit()

    # creates a new employee + saves
    @classmethod
    def create(cls, name, job_title, department_id):
        emp = cls(name, job_title, department_id)
        emp.save()
        return emp

    # updates DB row
    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    # deletes DB row + updates object state
    def delete(self):
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        Employee.all.pop(self.id, None)
        self.id = None

    # creates or retrieves cached instance from DB row
    @classmethod
    def instance_from_db(cls, row):
        id, name, job_title, department_id = row

        if id in cls.all:
            return cls.all[id]

        emp = Employee(name, job_title, department_id, id)
        cls.all[id] = emp
        return emp

    # returns list of all employees
    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # find by id
    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute(
            "SELECT * FROM employees WHERE id = ?", (id,)
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    # find by name
    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute(
            "SELECT * FROM employees WHERE name = ?", (name,)
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept {self.department_id}>"
