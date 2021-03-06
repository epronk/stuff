import unittest
from util import *
from plaintypes import *
from fit.RowFixture import RowFixture
from engines import Engine

class OccupantList(RowFixture):
    def query(self):
        return [ {'user': 'anna', 'room': 'lotr'},
                 {'user': 'luke', 'room': 'lotr'} ]

class OccupantList3(RowFixture):
    def query(self):
        return [ {'order': 1},
                 {'order': 2} ]

class OccupantList2(RowFixture):
    def query(self):
        result = []
        
        class Any(object) : pass
        a = Any()
        a.user = 'anna'
        a.room = 'lotr'
        
        result.append(a)
        return result

class TestRowFixture1(unittest.TestCase):

    def test_with_dict(self):
        fixture = OccupantList()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr'], ['luke', 'lotr']])

    def test_with_objects(self):
        fixture = OccupantList2()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr']])

class TestRowFixture2(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.loader = CreateFixture(globals())

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_passing_table(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
            |luke |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [])
        self.assertEqual(fixture.differ.surplus, [])

    def test_one_missing_row(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
            |luke |lotr |
            |bob  |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [[Cell('bob'), Cell('lotr')]])
        self.assertEqual(fixture.differ.surplus, [])
        self.assert_(self.table.cell(0,4).is_missing)

    def test_one_surplus_row(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [])
        self.assertEqual(fixture.differ.surplus, [['luke', 'lotr']])
        self.assertEqual(len(self.table.rows), 4)

class TestRowFixture3(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.loader = CreateFixture(globals())

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_two_surplus_rows(self):
        wiki = '''
            |OccupantList3|
            |order|
            |1 |
            |2 |
        '''

        fixture = self.process(wiki)

        self.assertEqual(fixture.differ.missing, [])
        self.assertEqual(fixture.differ.surplus, [])
        self.assertEqual(len(self.table.rows), 4)
