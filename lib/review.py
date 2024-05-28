from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    all = {}

    def __init__(self, year, summary, employee_id):
        self.id = None
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year} - {self.summary}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id:
            CURSOR.execute("""
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """, (self.year, self.summary, self.employee_id, self.id))
        else:
            CURSOR.execute("""
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid

        CONN.commit()
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        new_review = cls(year, summary, employee_id)
        new_review.save()
        return new_review

    @classmethod
    def instance_from_db(cls, row):
        review_id = row[0]
        if review_id in cls.all:
            return cls.all[review_id]
        else:
            new_review = cls(row[1], row[2], row[3])
            new_review.id = review_id
            cls.all[review_id] = new_review
            return new_review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        CURSOR.execute("""
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        Review.all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        CURSOR.execute("SELECT * FROM employees WHERE id = ?", (value,))
        if CURSOR.fetchone():
            self._employee_id = value
        else:
            raise ValueError("Employee ID must be a valid id from the employees table")
