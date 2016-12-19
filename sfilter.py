import logging
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relation, mapper, sessionmaker
from sqlalchemy.sql import *
from sqlalchemy.ext.associationproxy import association_proxy

log = logging.getLogger('nm_test')
logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s,%(msecs)03d %(levelname)s [%(filename)s.%(funcName)s @ %(lineno)d.%(thread)d] %(message)s')

engine = create_engine('sqlite:///:memory:', echo = False, echo_pool = False)
meta = MetaData()
meta.bind = engine

developer_table = Table('developer', meta,
    Column('id', Integer, primary_key=True, autoincrement = False),
    Column('name', String),
)

project_table = Table('project', meta,
    Column('id', Integer, primary_key=True, autoincrement = True),
    Column('name', String)
)

developer_project_table = Table('developer_project', meta,
    Column('developer_id', Integer, ForeignKey('developer.id'), primary_key = True),
    Column('project_id', Integer, ForeignKey('project.id'), primary_key = True),
    Column('status', String)
)

class Developer(object):
    projects = association_proxy('developerProjects', 'projects')
    def __str__(self):
        return 'Developer id:%i, name:%s' % (self.id, self.name)

class Project(object):
    developers = association_proxy('developerProjects', 'developers')
    def __str__(self):
        return 'Project id:%i, name:%s' % (self.id, self.name)

class DeveloperProject(object):
    def __str__(self):
        return 'DeveloperProject developer:%s, project:%s, status:%s' % (self.developer_id, self.project_id, self.status)

mapper(Developer, developer_table, properties = {
    'developerProjects':relation(DeveloperProject, backref = "developers")
})

mapper(Project, project_table, properties = {
    'developerProjects':relation(DeveloperProject, backref = "projects")
})

mapper(DeveloperProject, developer_project_table)

meta.create_all(engine)
conn = engine.connect()

conn.execute(project_table.insert(),[
    {'name':'stackoverflow'},
    {'name':'superuser'},
])
conn.execute(developer_table.insert(),[
    {'name':'John'},
    {'name': 'TerryJ'},
    {'name': 'TerryG'},
    {'name': 'Eric'},
    {'name': 'Graham'},
])
conn.execute(developer_project_table.insert(),[
    {'developer_id':1, 'project_id':1, 'status':'active'},
    {'developer_id':2, 'project_id':2, 'status':'inactive'},
    {'developer_id':3, 'project_id':2, 'status':'active'},
    {'developer_id':4, 'project_id':1, 'status':'active'},
    {'developer_id':4, 'project_id':2, 'status':'active'},
    {'developer_id':5, 'project_id':1, 'status':'active'},
    {'developer_id':5, 'project_id':2, 'status':'inactive'},
])

Session = sessionmaker(bind=engine)
s = Session()

developers = s.query(Developer).filter(Developer.projects.any(Project.name.like('stackoverflow') ) )  #all()
projects = s.query(Project).limit(1).all()

for d in developers:
    log.debug(d)
    for p in d.projects:
        log.debug('    %s' % p)

for p in projects:
    log.debug(p)
    for d in p.developers:
        log.debug('    %s' % d)

