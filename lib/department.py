# lib/department.py
from __init__ import CONN, CURSOR


class Department:

    # dictionary cache of all Department objects
    all = {}

    def __init__(self, name, location, id=None):
        # initialize attributes with validation
        self.id = id
        self.name = name
        self.location = location

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

    # property for location with validation
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("Location must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Location cannot be empty")
        self._location = value

    # creates departments table
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    # drops departments table
    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    # saves new or updated department
    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO departments (name, location)
                VALUES (?, ?)
            """
            CURSOR.execute(sql, (self.name, self.location))
            self.id = CURSOR.lastrowid
            Department.all[self.id] = self
        else:
            self.update()

        CONN.commit()

    # creates a new department instance + saves it
    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    # updates an existing DB row
    def update(self):
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    # deletes DB row and updates object state
    def delete(self):
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        Department.all.pop(self.id, None)
        self.id = None

    # returns object from DB row, using cache if possible
    @classmethod
    def instance_from_db(cls, row):
        id, name, location = row
        if id in cls.all:
            return cls.all[id]

        department = Department(name, location, id)
        cls.all[id] = department
        return department

    # returns list of all department instances
    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM departments").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # find by id
    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute(
            "SELECT * FROM departments WHERE id = ?", (id,)
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    # find by name
    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute(
            "SELECT * FROM departments WHERE name = ?", (name,)
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    # relationship: returns list of employees in this department
    def employees(self):
        from employee import Employee
        return [emp for emp in Employee.get_all() if emp.department_id == self.id]

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"
