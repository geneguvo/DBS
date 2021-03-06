#!/usr/bin/env python

""" DAO Object for Services table """ 

__revision__ = "$Revision: 1.1 $"
__version__  = "$Id: Update.py,v 1.1 2010/08/02 20:41:18 afaq Exp $ "

from WMCore.Database.DBFormatter import DBFormatter
from dbs.utils.dbsExceptionHandler import dbsExceptionHandler

from sqlalchemy import exceptions

class Update(DBFormatter):
    """Service Update DAO Class."""

    def __init__(self, logger, dbi, owner):
        DBFormatter.__init__(self, logger, dbi)
        self.owner = "%s." % owner if not owner in ("", "__MYSQL__") else ""
        self.logger = logger
        self.sql = """UPDATE %sSERVICES SET TYPE=:type, LOCATION=:location, STATUS=:status, ADMIN=:admin, URI=:uri, DB=:db, VERSION=:version, LAST_CONTACT=:last_contact, ALIAS=:alias, COMMENTS=:comments WHERE NAME=:name """ % self.owner

    def execute(self, conn, daoinput, transaction = False):
        if not conn:
            dbsExceptionHandler("dbsException-db-conn-failed","Oracle/Service/Update. Expects db connection from upper layer.")

        self.dbi.processData(self.sql, daoinput, conn, transaction)

