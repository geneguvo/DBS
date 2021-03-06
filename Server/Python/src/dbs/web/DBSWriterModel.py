#!/usr/bin/env python
#pylint: disable=C0103
"""
DBS Rest Model module
"""

__revision__ = "$Id: DBSWriterModel.py,v 1.46 2010/08/12 19:00:01 afaq Exp $"
__version__ = "$Revision: 1.46 $"

import re
import cjson

from cherrypy import request, tools, HTTPError
from WMCore.DAOFactory import DAOFactory
from dbs.utils.dbsUtils import dbsUtils
from dbs.web.DBSReaderModel import DBSReaderModel
from dbs.utils.dbsException import dbsException, dbsExceptionCode
from dbs.utils.dbsExceptionHandler import dbsExceptionHandler
from dbs.utils.DBSInputValidation import *
from dbs.utils.DBSTransformInputType import transformInputType

import traceback

def authInsert(user, role, group, site):
    """
    Authorization function for general insert
    """
    if not role: return True
    for k, v in user['roles'].iteritems():
        for g in v['group']:
            if k in role.get(g, '').split(':'):
                return True
    return False

class DBSWriterModel(DBSReaderModel):
    """
    DBS3 Server API Documentation
    """
    def __init__(self, config):
        """
        All parameters are provided through DBSConfig module
        """

        #Dictionary with reader and writer as keys
        urls = config.database.connectUrl

        #instantiate the page with the writer_config

        if type(urls)==type({}):
            config.database.connectUrl = urls['writer']

        DBSReaderModel.__init__(self, config)

        self.security_params = config.security.params

        self.sequenceManagerDAO = self.daofactory(classname="SequenceManager")
        self.dbsDataTierInsertDAO = self.daofactory(classname="DataTier.Insert")

        self._addMethod('POST', 'primarydatasets', self.insertPrimaryDataset, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'outputconfigs', self.insertOutputConfig,  secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'acquisitioneras', self.insertAcquisitionEra, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('PUT', 'acquisitioneras', self.updateAcqEraEndDate, args=['acquisition_era_name','end_date'],
                         secured=True, security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'processingeras', self.insertProcessingEra, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'datasets', self.insertDataset, secured=True,
                        security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'blocks', self.insertBlock, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'files', self.insertFile, args=['qInserts'], secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('PUT', 'files', self.updateFile, args=['logical_file_name', 'is_file_valid', 'lost'],
                         secured=True, security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('PUT', 'datasets', self.updateDataset, args=['dataset', 'dataset_access_type'],
                         secured=True, security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('PUT', 'blocks', self.updateBlock,args=['block_name', 'open_for_writing', 'origin_site_name'],
                         secured=True, security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'datatiers', self.insertDataTier, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})
        self._addMethod('POST', 'bulkblocks', self.insertBulkBlock, secured=True,
                         security_params={'role':self.security_params, 'authzfunc':authInsert})

    def insertPrimaryDataset(self):
        """
        API to insert A primary dataset in DBS

        :param primaryDSObj: primary dataset object
        :type primaryDSObj: dict
        :key primary_ds_type: TYPE (out of valid types in DBS, MC, DATA) (Required)
        :key primary_ds_name: Name of the primary dataset (Required)

        """
        try :
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy("primds",indata)
            indata.update({"creation_date": dbsUtils().getTime(), "create_by": dbsUtils().getCreateBy() })
            self.dbsPrimaryDataset.insertPrimaryDataset(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/insertPrimaryDataset. %s\n Exception trace: \n %s" \
                        % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertOutputConfig(self):
        """
        API to insert An OutputConfig in DBS

        :param outputConfigObj: Output Config object
        :type outputConfigObj: dict
        :key app_name: App Name (Required)
        :key release_version: Release Version (Required)
        :key pset_hash: Pset Hash (Required)
        :key output_module_label: Output Module Label (Required)
        :key global_tag: Global Tag (Required)
        :key scenario: Scenario (Optional, default is None)
        :key pset_name: Pset Name (Optional, default is None)

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy("dataset_conf_list",indata)
            indata.update({"creation_date": dbsUtils().getTime(),
                           "create_by" : dbsUtils().getCreateBy()})
            self.dbsOutputConfig.insertOutputConfig(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/insertOutputConfig. %s\n. Exception trace: \n %s" \
                            % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    @inputChecks(acquisition_era_name=str, end_date=(int, str))
    def updateAcqEraEndDate(self, acquisition_era_name ="", end_date=0):
        """
        API to update the end_date of an acquisition era

        :param acquisition_era_name: acquisition_era_name to update (Required)
        :type acquisition_era_name: str
        :param end_date: end_date not zero (Required)
        :type end_date: int

        """
        try:
            self.dbsAcqEra.UpdateAcqEraEndDate( acquisition_era_name, end_date)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/update.AcqEraEndDate %s\n. Exception trace: \n %s" \
                    % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertAcquisitionEra(self):
        """
        API to insert an Acquisition Era in DBS

        :param acqEraObj: Acquisition Era object
        :type acqEraObj: dict
        :key acquisition_era_name: Acquisition Era Name (Required)
        :key start_date: start date of the acquisition era (unixtime, int) (Optional, default current date)
        :key end_date: end data of the acquisition era (unixtime, int) (Optional)

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy("acquisition_era",indata)
            indata.update({"start_date": indata.get("start_date", dbsUtils().getTime()),\
                           "creation_date": indata.get("creation_date", dbsUtils().getTime()), \
                           "create_by" : dbsUtils().getCreateBy() })
            self.dbsAcqEra.insertAcquisitionEra(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.serverError)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = " DBSWriterModel/insertAcquisitionEra. %s\n. Exception trace: \n %s" \
                        % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertProcessingEra(self):
        """
        API to insert A Processing Era in DBS

        :param procEraObj: Processing Era object
        :type procEraObj: dict
        :key processing_version: Processing Version (Required)
        :key description: Description (Optional)

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy('processing_era', indata)
            indata.update({"creation_date": indata.get("creation_date", dbsUtils().getTime()), \
                           "create_by" : dbsUtils().getCreateBy() })
            self.dbsProcEra.insertProcessingEra(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/insertProcessingEra. %s\n. Exception trace: \n %s" \
                            % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertDataset(self):
        """
        API to insert a dataset in DBS

        :param datasetObj: Dataset object
        :type datasetObj: dict
        :key primary_ds_name: Primary Dataset Name (Required)
        :key dataset: Name of the dataset (Required)
        :key dataset_access_type: Dataset Access Type (Required)
        :key processed_ds_name: Processed Dataset Name (Required)
        :key data_tier_name: Data Tier Name (Required)
        :key acquisition_era_name: Acquisition Era Name (Required)
        :key processing_version: Processing Version (Required)
        :key physics_group_name: Physics Group Name (Optional, default None)
        :key prep_id: ID of the Production and Reprocessing management tool (Optional, default None)
        :key xtcrosssection: Xtcrosssection (Optional, default None)
        :key output_configs: List(dict) with keys release_version, pset_hash, app_name, output_module_label and global tag

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy('dataset', indata)
            indata.update({"creation_date": dbsUtils().getTime(),
                            "last_modification_date" : dbsUtils().getTime(),
                            "create_by" : dbsUtils().getCreateBy() ,
                            "last_modified_by" : dbsUtils().getCreateBy() })

            # need proper validation
            self.dbsDataset.insertDataset(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = " DBSWriterModel/insertDataset. %s\n. Exception trace: \n %s" \
                        % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertBulkBlock(self):
        """
        API to insert a bulk block

        :param blockDump: Output of the block dump command
        :type blockDump: dict

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            #indata = validateJSONInput("insertBlock",indata)
            #import pdb
            #pdb.set_trace()
            indata = validateJSONInputNoCopy("blockBulk",indata)
            self.dbsBlockInsert.putBlock(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            #illegal variable name/number
            if str(ex).find("ORA-01036") != -1:
                dbsExceptionHandler("dbsException-invalid-input2", "illegal variable name/number from input",  self.logger.exception, str(ex))
            else:
                sError = "DBSWriterModel/insertBulkBlock. %s\n. Exception trace: \n %s" \
                    % (ex, traceback.format_exc())
                dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertBlock(self):
        """
        API to insert a block into DBS

        :param blockObj: Block object
        :type blockObj: dict
        :key open_for_writing: Open For Writing (1/0) (Optional, default 1)
        :key block_size: Block Size (Optional, default 0)
        :key file_count: File Count (Optional, default 0)
        :key block_name: Block Name (Required)
        :key origin_site_name: Origin Site Name (Required)

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)
            indata = validateJSONInputNoCopy("block",indata)
            self.dbsBlock.insertBlock(indata)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except Exception, ex:
            sError = "DBSWriterModel/insertBlock. %s\n. Exception trace: \n %s" \
                    % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    def insertFile(self, qInserts=False):
        """
        API to insert a list of file into DBS in DBS. Up to 10 files can be inserted in one request.

        :param qInserts: True means that inserts will be queued instead of done immediately. INSERT QUEUE Manager will perform the inserts, within few minutes.
        :type qInserts: bool
        :param filesList: List of dictionaries containing following information
        :type filesList: list of dicts
        :key logical_file_name: File to be inserted (str) (Required)
        :key is_file_valid: (optional, default = 1): (bool)
        :key block: required: /a/b/c#d (str)
        :key dataset: required: /a/b/c (str)
        :key file_type: (optional, default = EDM) one of the predefined types, (str)
        :key check_sum: (optional, default = '-1') (str)
        :key event_count: (optional, default = -1) (int)
        :key file_size: (optional, default = -1.) (float)
        :key adler32: (optional, default = '') (str)
        :key md5: (optional, default = '') (str)
        :key auto_cross_section: (optional, default = -1.) (float)
        :key file_lumi_list: (optional, default = []) [{'run_num': 123, 'lumi_section_num': 12},{}....]
        :key file_parent_list: (optional, default = []) [{'file_parent_lfn': 'mylfn'},{}....]
        :key file_assoc_list: (optional, default = []) [{'file_parent_lfn': 'mylfn'},{}....]
        :key file_output_config_list: (optional, default = []) [{'app_name':..., 'release_version':..., 'pset_hash':...., output_module_label':...},{}.....]

        """
        if qInserts in (False, 'False'): qInserts=False
        try:
            body = request.body.read()
            indata = cjson.decode(body)["files"]
            if not isinstance(indata, (list,dict)):
                 dbsExceptionHandler("dbsException-invalid-input", "Invalid Input DataType", self.logger.exception, \
                                      "insertFile expects input as list or dirc")
            businput = []
            if type(indata) == dict:
                indata = [indata]
            indata = validateJSONInputNoCopy("files",indata)
            for f in indata:
                f.update({
                     #"dataset":f["dataset"],
                     "creation_date": f.get("creation_date", dbsUtils().getTime()),
                     "create_by" : dbsUtils().getCreateBy(),
                     "last_modification_date": f.get("last_modification_date", dbsUtils().getTime()),
                     "last_modified_by": f.get("last_modified_by" , dbsUtils().getCreateBy()),
                     "file_lumi_list":f.get("file_lumi_list",[]),
                     "file_parent_list":f.get("file_parent_list",[]),
                     "file_assoc_list":f.get("assoc_list",[]),
                     "file_output_config_list":f.get("file_output_config_list",[])})
                businput.append(f)
            self.dbsFile.insertFile(businput, qInserts)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/insertFile. %s\n. Exception trace: \n %s" \
                    % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    @transformInputType('logical_file_name')
    @inputChecks(logical_file_name=(str,list), is_file_valid=(int, str), lost=(int, str, bool ))
    def updateFile(self, logical_file_name=[], is_file_valid=1, lost=0):
        """
        API to update file status

        :param logical_file_name: logical_file_name to update (Required)
        :type logical_file_name: str
        :param is_file_valid: valid=1, invalid=0 (Required)
        :type is_file_valid: bool
        :param lost: default lost=0 (optional)
        :type lost: bool

        """
        if lost in [1, True, 'True','true', '1', 'y', 'yes']:
            lost = 1
            if is_file_valid in [1, True, 'True','true', '1', 'y', 'yes']:
                dbsExceptionHandler("dbsException-invalid-input2", dbsExceptionCode["dbsException-invalid-input2"],self.logger.exception,\
                                    "Lost file must set to invalid" )
        else: lost = 0

        try:
            self.dbsFile.updateStatus(logical_file_name, is_file_valid, lost)
        except dbsException as de:
            for f in logical_file_name:
                if '*' in f or '%' in f:
                    dbsExceptionHandler("dbsException-invalid-input2", dbsExceptionCode["dbsException-invalid-input2"],self.logger.exception,"No \
                    wildcard allow in LFN" )
            self.dbsFile.updateStatus(logical_file_name, is_file_valid, lost)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel/updateFile. %s\n. Exception trace: \n %s" \
                    % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    @inputChecks(dataset=str, dataset_access_type=str)
    def updateDataset(self, dataset="", is_dataset_valid=-1, dataset_access_type=""):
        """
        API to update dataset type

        :param dataset: Dataset to update (Required)
        :type dataset: str
        :param dataset_access_type: production, deprecated, etc (Required)
        :type dataset_access_type: str

        """
        try:
            if dataset_access_type != "":
                self.dbsDataset.updateType(dataset, dataset_access_type)
            else:
                dbsExceptionHandler("dbsException-invalid-input", "DBSWriterModel/updateDataset. dataset_access_type is required.")

        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel\updateDataset. %s\n. Exception trace: \n %s" % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)

    @inputChecks(block_name=str, open_for_writing=(int,str), origin_site_name=str)
    def updateBlock(self, block_name="", open_for_writing=-1, origin_site_name=""):
        """
        API to update block status

        :param block_name: block name (Required)
        :type block_name: str
        :param open_for_writing: open_for_writing=0 (close), open_for_writing=1 (open) (Required)
        :type open_for_writing: str

        """
        if not block_name:
            dbsExceptionHandler('dbsException-invalid-input', "DBSBlock/updateBlock. Invalid block_name", self.logger)
        try:
            if open_for_writing != -1:
                self.dbsBlock.updateStatus(block_name, open_for_writing)
            if origin_site_name:
                self.dbsBlock.updateSiteName(block_name, origin_site_name)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)
        except HTTPError as he:
            raise he
        except Exception, ex:
            sError = "DBSWriterModel\updateStatus. %s\n. Exception trace: \n %s" % (ex, traceback.format_exc())
            dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'],
                                self.logger.exception, sError)

    def insertDataTier(self):
        """
        API to insert A Data Tier in DBS

        :param dataTierObj: Data Tier object
        :type dataTierObj: dict
        :key data_tier_name: Data Tier that needs to be inserted

        """
        try:
            body = request.body.read()
            indata = cjson.decode(body)

            indata = validateJSONInputNoCopy("dataTier", indata)

            indata.update({"creation_date": indata.get("creation_date", dbsUtils().getTime()), \
                           "create_by" : dbsUtils().getCreateBy()})

            conn = self.dbi.connection()
            tran = conn.begin()

            if not indata.has_key("data_tier_name"):
                dbsExceptionHandler("dbsException-invalid-input", "DBSWriterModel/insertDataTier. data_tier_name is required.")

            indata['data_tier_id'] = self.sequenceManagerDAO.increment(conn, "SEQ_DT", tran)

            indata['data_tier_name'] = indata['data_tier_name'].upper()

            self.dbsDataTierInsertDAO.execute(conn, indata, tran)
        except dbsException as de:
            dbsExceptionHandler(de.eCode, de.message, self.logger.exception, de.message)

        except HTTPError as he:
            raise he
        except Exception as ex:
            if str(ex).lower().find("unique constraint") != -1 or str(ex).lower().find("duplicate") != -1:
                # already exist
                self.logger.warning("Unique constraint violation being ignored...")
                self.logger.warning("%s" % ex)
                pass
            else:
                sError = " DBSWriterModel\insertDataTier. %s\n. Exception trace: \n %s" % (ex, traceback.format_exc())
                dbsExceptionHandler('dbsException-server-error',  dbsExceptionCode['dbsException-server-error'], self.logger.exception, sError)
        finally:
            tran.commit()
            if conn:
                conn.close()

