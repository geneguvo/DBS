"""
web unittests
"""

__revision__ = "$Id: DBSReaderModel_t.py,v 1.7 2010/01/26 17:54:17 yuyi Exp $"
__version__ = "$Revision: 1.7 $"

import os, sys, imp
import json
import unittest
from dbsserver_t.utils.DBSRestApi import DBSRestApi

def importCode(code,name,add_to_sys_modules=0):
    module = imp.new_module(name)
    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module
    return module

infofile=open("info.dict","r")    
testparams=importCode(infofile, "testparams", 0).info
config = os.environ["DBS_TEST_CONFIG_READER"]
api = DBSRestApi(config)


class DBSReaderModel_t(unittest.TestCase):
    
    	
    def setUp(self):
        """setup all necessary parameters"""
	#import pdb
	#pdb.set_trace()

    def test01(self):
        """Test01 web.DBSReaderModel.listPrimaryDatasets: basic test"""
        api.list('primarydatasets')
       
    def test02(self):
	"""Test02 web.DBSReaderModel.listPrimaryDatasets: basic test"""
	api.list('primarydatasets', primary_ds_name='*')
       
    def test03(self):
        """Test03 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets')
    
    def test04(self):
        """Test04 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets', dataset='*')

    def test05(self):
        """Test05 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets', parent_dataset='*')
    
    def test06(self):
        """Test06 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets', release_version='*')

    def test07(self):
        """Test07 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets', pset_hash='*')

    def test08(self):
        """Test08 web.DBSReaderModel.listDatasets: basic test"""
        api.list('datasets', app_name='*')
    
    def test09(self):
        """Test09 web.DBSReaderModel.listDatasets: basic test"""
	api.list('datasets', output_module_label='*')

    def test10(self):
        """Test10 web.DBSReaderModel.listDatasets: basic test"""
	api.list('datasets', dataset='*', 
                                  parent_dataset='*',
                                  release_version='*',
                                  pset_hash='*',
                                  app_name='*',
                                  output_module_label='*')
    def test11(self):
        """Test11 web.DBSReaderModel.listBlocks: basic test"""
	try:
	    api.list('blocks', dataset='*')
        except:
	    pass
	else:
	    self.fail("Exception was expected and was not raised.")

    def test12(self):
        """Test12 web.DBSReaderModel.listBlocks: basic test"""
        try:
            api.list('blocks', block_name='*')
        except:
            pass
        else:
            self.fail("Exception was expected and was not raised.")

    def test13(self):
        """Test13 web.DBSReaderModel.listBlocks: basic test"""
        try:
            api.list('blocks', site_name='*')
        except:
            pass
        else:
            self.fail("Exception was expected and was not raised.")

    def test14(self):
        """Test14 web.DBSReaderModel.listBlocks: basic test"""
        try:
            api.list('blocks', dataset='*',
                                block_name='*',
                                site_name='*')
        except:
            pass
        else:
            self.fail("Exception was expected and was not raised.")


	    
    def test15(self):
        """Test15 web.DBSReaderModel.listBlocks: takes exact dataset name, not pattern"""
	try:
	    result=api.list('blocks', dataset='*')
	    #import pdb
	    #pdb.set_trace()
	except:
	    pass
	else:
	    self.fail("Exception was expected and was not raised.")
        
    def test16(self):
        """Test16 web.DBSReaderModel.listBlocks: Must raise an exception if no parameter is passed."""
	
        try:
	    api.list('blocks')
        except: 
	    pass
        else: 
	    self.fail("Exception was expected and was not raised.")
            
    def test17(self):
        """Test17 web.DBSReaderModel.listFiles: basic test"""
	try:
	    api.list('files', dataset='*')
	except:
	    pass
	else:
	    self.fail("Exception was expected and was not raised.")

    def test18(self):
        """Test18 web.DBSReaderModel.listFiles: basic test"""
	try:
	    api.list('files', block_name='*')
	except:
            pass
        else:
            self.fail("Exception was expected and was not raised.")


    def test19(self):
        """Test19 web.DBSReaderModel.listFiles: basic test"""
	try:
	    api.list('files', logical_file_name='*')
	except:
            pass
        else:
            self.fail("Exception was expected and was not raised.")
       
    def test21(self):
        """Test21 web.DBSReaderModel.listFiles: Must raise an exception if no parameter is passed."""
        try: api.list('files')
        except: pass
        else: self.fail("Exception was expected and was not raised")
            
    def test22(self):
        """Test22 web.DBSReaderModel.listDatasetParents: basic test"""
        api.list('datasetparents', dataset="*")
        
    def test23(self):
        """Test23 web.DBSReaderModel.listDatasetParents: must raise an exception if no parameter is passed"""
        try: api.list('datasetparents')
        except: 
	    pass
        else: 
	    self.fail("Exception was expected and was not raised")
            
    def test24(self):
        """Test24 web.DBSReaderModel.listOutputConfigs: basic test"""
	api.list('outputconfigurations')
    
    def test25(self):
        """Test25 web.DBSReaderModel.listOutputConfigs: basic test"""
	api.list('outputconfigurations', dataset="*")
	
    def test26(self):
        """Test26 web.DBSReaderModel.listOutputConfigs: basic test"""
        api.list('outputconfigurations', logical_file_name="*")

    def test27(self):
        """Test27 web.DBSReaderModel.listOutputConfigs: basic test"""
        api.list('outputconfigurations', release_version="*")

    def test28(self):
        """Test28 web.DBSReaderModel.listOutputConfigs: basic test"""
        api.list('outputconfigurations', pset_hash="*")

    def test29(self):
	"""Test29 web.DBSReaderModel.listOutputConfigs: basic test"""
	api.list('outputconfigurations', app_name="*")

    def test30(self):
        """Test30 web.DBSReaderModel.listOutputConfigs: basic test"""
	api.list('outputconfigurations', output_module_label="*")
 
    def test31(self):
        """Test31 web.DBSReaderModel.listOutputConfigs: basic test"""
	api.list('outputconfigurations', dataset="*",
                                              logical_file_name="*",
                                              release_version="*",
                                              pset_hash="*",
                                              app_name="*",
                                              output_module_label="*")

    def test32(self):
        """Test32 web.DBSReaderModel.listFileParents: basic test"""
        api.list('fileparents', logical_file_name="*")
    
    def test33(self):
        """Test33 web.DBSReaderModel.listFileParents: must raise an exception if no parameter is passed"""
        try: api.list('fileparents')
        except: pass
        else: self.fail("Exception was expected and was not raised")
        
    def test34(self):
        """Test34 web.DBSReaderModel.listFileLumis: basic test"""
        api.list('filelumis', logical_file_name="*")

    def test35(self):
        """Test35 web.DBSReaderModel.listFileLumis: basic test"""
        api.list('filelumis', block_name="*")

    def test36(self):
        """Test36 web.DBSReaderModel.listFileLumis: must raise an exception if no parameter is passed"""
        try: api.list('filelumis')
        except: pass
        else: self.fail("Exception was expected and was not raised")
        
if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(DBSReaderModel_t)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
        
