#!/usr/bin/env python
"""
This module provides FileParent.ListChild data access object.
"""
__revision__ = "$Id: ListChild.py,v 1.2 2010/06/23 21:21:24 afaq Exp $"
__version__ = "$Revision: 1.2 $"

from WMCore.Database.DBFormatter import DBFormatter
from dbs.utils.dbsExceptionHandler import dbsExceptionHandler

class ListChild(DBFormatter):
    """
    FileParent List DAO class.
    """
    def __init__(self, logger, dbi, owner=""):
        """
        Add schema owner and sql.
        """
        DBFormatter.__init__(self, logger, dbi)
        self.owner = "%s." % owner if not owner in ("", "__MYSQL__") else ""
        self.sql = \
"""
SELECT CF.LOGICAL_FILE_NAME child_logical_file_name,
       CF.FILE_ID child_file_id,
       F.LOGICAL_FILE_NAME
FROM %sFILES CF
JOIN %sFILE_PARENTS FP ON FP.THIS_FILE_ID = CF.FILE_ID
JOIN %sFILES F ON  F.FILE_ID = FP.PARENT_FILE_ID
""" % ((self.owner,)*3)

    def execute(self, conn, logical_file_names, block_name, block_id, transaction=False):
        """
        Lists all primary datasets if pattern is not provided.
        """
        if not conn:
            dbsExceptionHandler("dbsException-db-conn-failed","Oracle/FileParent/ListChild. Expects db connection from upper layer.")

        sql = self.sql
        binds = {}
        bindlist=[]
        if isinstance(logical_file_names, str):
            sql += "WHERE F.LOGICAL_FILE_NAME = :logical_file_names"
            binds = {"logical_file_names":logical_file_names}
        elif isinstance(logical_file_names, list):
            sql += "WHERE F.LOGICAL_FILE_NAME in :logical_file_names"
            for f in logical_file_names:
                binds = {"logical_file_names": f}
                bindlist.append(binds)
        elif block_name:
            sql += "WHERE F.BLOCK_NAME = :block_name"
            binds = {"block_name":block_name}
        elif block_id:
            sql += "WHERE F.BLOCK_ID = :block_id"
            binds = {"block_name":block_name}
        else:
            dbsExceptionHandler('dbsException-invalid-input', "Logical_file_names is required for listChild dao.")

        cursors = self.dbi.processData(sql, binds, conn, transaction=transaction, returnCursor=True)
        result = self.formatCursor(cursors[0])
        return result